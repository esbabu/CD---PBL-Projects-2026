"""Every (rule, language) pair claimed by ``security.coverage`` is exercised here or by the
language fixtures. Each snippet is a small but realistic program with one vulnerability;
the expected rule is written by hand from what the code does."""
import glob
import os
import re

import pytest

from src.multilang.analyzer import analyze_file, analyze_source
from src.security.coverage import rule_languages

HERE = os.path.dirname(__file__)

C_SNIPPETS = {
    "SEC002": 'void f(void){ char *h = getenv("HOOK"); system(h); }',
    "SEC003": 'const char *connect_db(void){ const char *password = "Sup3rS3cret!"; return password; }',
    "SEC004": 'void f(const unsigned char *d, unsigned long n, unsigned char *o){ MD5(d, n, o); }',
    "SEC005": ('void f(MYSQL *conn){ char name[64]; char q[256]; fgets(name, sizeof name, stdin);'
               ' sprintf(q, "SELECT * FROM t WHERE n = \'%s\'", name); mysql_query(conn, q); }'),
    "SEC011": 'int session_key(void){ return rand(); }',
    "SEC013": 'void f(void){ char *p = getenv("LOGFILE"); FILE *fp = fopen(p, "r"); fclose(fp); }',
    "SEC018": 'void f(const char *p){ xmlDocPtr d = xmlReadFile(p, NULL, XML_PARSE_NOENT); }',
    "SEC019": ('void f(LDAP *ld){ char filter[128]; fgets(filter, sizeof filter, stdin);'
               ' ldap_search_s(ld, "dc=corp", 2, filter, 0, 0, 0); }'),
    "SEC025": 'void f(void){ void *h = dlopen(getenv("PLUGIN"), 2); }',
    "SEC026": 'void f(int s){ char m[128]; recv(s, m, sizeof m, 0); printf(m); }',
    "SEC030": 'void f(CURL *c){ curl_easy_setopt(c, CURLOPT_SSL_VERIFYPEER, 0L); }',
    "SEC031": 'void f(SSL_CTX *ctx){ SSL_CTX_set_verify(ctx, SSL_VERIFY_NONE, NULL); }',
    "SEC032": 'SSL_CTX *f(void){ return SSL_CTX_new(TLSv1_method()); }',
    "SEC033": 'const EVP_CIPHER *f(void){ return EVP_des_cbc(); }',
    "SEC034": 'const EVP_CIPHER *f(void){ return EVP_aes_128_ecb(); }',
    "SEC035": 'void *f(void){ return RSA_generate_key(1024, 65537, NULL, NULL); }',
    "SEC037": 'void f(void){ char name[64]; tmpnam(name); }',
    "SEC050": 'void login(const char *user, const char *password){ printf("login %s %s\\n", user, password); }',
    "SEC051": 'void f(void){ char b[32]; gets(b); }',
    "SEC052": 'void f(int argc, char **argv){ char b[16]; strcpy(b, argv[1]); }',
    "SEC053": ('void f(int s){ char h[8]; char b[64]; recv(s, h, sizeof h, 0); int n = atoi(h);'
               ' memcpy(b, h, n); }'),
    "SEC054": 'int f(int s){ int t[4] = {0}; char x[4]; recv(s, x, sizeof x, 0); return t[atoi(x)]; }',
    "SEC055": ('void *f(int s){ char c[8]; recv(s, c, sizeof c, 0); size_t n = strtoul(c, NULL, 10);'
               ' return malloc(n * 16); }'),
    "SEC056": 'void f(char *p){ free(p); p[0] = 1; }',
    "SEC057": 'void f(char *p){ free(p); free(p); }',
    "SEC058": 'char *f(unsigned n){ char *p = malloc(n); p[0] = 0; return p; }',
    "SEC059": 'void f(const char *p){ if (access(p, 2) == 0) { FILE *x = fopen(p, "w"); fclose(x); } }',
}
CPP_ONLY = {
    "SEC009": ('void load(){ std::string data; std::cin >> data; std::istringstream ss(data);'
               ' boost::archive::text_iarchive ia(ss); }'),
    "SEC049": 'void f(){ try { risky(); } catch (...) { } }',
}

SNIPPETS = {
    ("java", "SEC001"): ('class A { void f(HttpServletRequest req) throws Exception {'
                         ' ScriptEngine e = mgr.getEngineByName("js"); e.eval(req.getParameter("expr")); } }'),
    ("java", "SEC032"): 'class A { Object f() throws Exception { return SSLContext.getInstance("TLSv1"); } }',
    ("java", "SEC035"): ('class A { void f() throws Exception { KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");'
                         ' kpg.initialize(1024); } }'),
    ("java", "SEC036"): 'class A { Object f() { return new IvParameterSpec("1234567890abcdef".getBytes()); } }',
    ("java", "SEC044"): 'class A { void f(Cookie c) { c.setSecure(false); } }',
    ("csharp", "SEC011"): 'class A { int MakeToken() { var token = new Random().Next(); return token; } }',
    ("csharp", "SEC014"): ('class HomeController : Controller { public void Hi([FromQuery] string name)'
                           ' { Response.Write("<b>" + name + "</b>"); } }'),
    ("csharp", "SEC019"): ('class A : Controller { public object F([FromQuery] string uid)'
                           ' { return new DirectorySearcher("(uid=" + uid + ")").FindOne(); } }'),
    ("csharp", "SEC020"): ('class A : Controller { public object F([FromQuery] string n, XmlDocument doc)'
                           ' { return doc.SelectNodes("//user[@name=\'" + n + "\']"); } }'),
    ("csharp", "SEC023"): ('class A : Controller { public void F([FromQuery] string lang)'
                           ' { Response.Headers.Add("Content-Language", lang); } }'),
    ("csharp", "SEC025"): 'class A : Controller { public object F([FromQuery] string t) { return Type.GetType(t); } }',
    ("csharp", "SEC028"): ('class A : Controller { public void F([FromQuery] string n)'
                           ' { HttpContext.Session.SetString("user", n); } }'),
    ("csharp", "SEC029"): 'class Startup { void Configure(IApplicationBuilder app) { app.UseDeveloperExceptionPage(); } }',
    ("csharp", "SEC032"): 'class A { void F(HttpClientHandler h) { h.SslProtocols = SslProtocols.Tls; } }',
    ("csharp", "SEC034"): 'class A { void F(Aes aes) { aes.Mode = CipherMode.ECB; } }',
    ("csharp", "SEC035"): 'class A { object F() { return new RSACryptoServiceProvider(1024); } }',
    ("csharp", "SEC036"): 'class A { void F(Aes aes) { aes.IV = Encoding.UTF8.GetBytes("1234567890abcdef"); } }',
    ("csharp", "SEC045"): 'class A : Controller { [IgnoreAntiforgeryToken] [HttpPost] public void Save() { } }',
    ("csharp", "SEC046"): 'class A { void F(CorsPolicyBuilder p) { p.AllowAnyOrigin(); } }',
    ("csharp", "SEC047"): 'class A { object F() { return new TokenValidationParameters { ValidateIssuerSigningKey = false }; } }',
    ("csharp", "SEC049"): 'class A { void F() { try { Run(); } catch (Exception) { } } }',
    ("csharp", "SEC050"): ('class A { ILogger _logger; void Login(string user, string password)'
                           ' { _logger.LogInformation("login " + user + " " + password); } }'),
    ("csharp", "SEC059"): 'class A { void F(string path) { if (!File.Exists(path)) { File.WriteAllText(path, "x"); } } }',
    ("csharp", "SEC060"): 'class A { unsafe void F(byte[] b) { fixed (byte* p = b) { *p = 1; } } }',
    ("rust", "SEC009"): ('#[post("/load")]\nasync fn load(body: Bytes) -> String {'
                         ' let s: State = bincode::deserialize(&body).unwrap(); String::new() }'),
    ("rust", "SEC014"): ('#[get("/hi")]\nasync fn hi(q: web::Query<P>) -> HttpResponse {'
                         ' HttpResponse::Ok().content_type("text/html").body(format!("<p>{}</p>", q.name)) }'),
    ("rust", "SEC017"): '#[get("/go")]\nasync fn go(q: Query<P>) -> Redirect { Redirect::to(&q.next) }',
    ("rust", "SEC022"): '#[get("/t")]\nasync fn t(q: web::Query<P>) -> String { log::info!("visit {}", q.page); String::new() }',
    ("rust", "SEC024"): '#[get("/g")]\nasync fn g(q: web::Query<P>) -> String { let r = Regex::new(&q.pattern); String::new() }',
    ("rust", "SEC033"): 'fn enc(key: &[u8]) { let c = Des::new_from_slice(key); let d = Des::new(key); }',
    ("rust", "SEC034"): 'fn enc(key: &[u8]) { let c = Ecb::new(key); }',
    ("rust", "SEC035"): 'fn keygen() { let k = RsaPrivateKey::new(&mut rng, 1024); }',
    ("rust", "SEC046"): 'fn cors() -> Cors { Cors::permissive() }',
    ("rust", "SEC047"): 'fn claims(t: &str) { let c = jsonwebtoken::dangerous_insecure_decode::<Claims>(t); }',
    ("rust", "SEC050"): 'fn login(user: &str, password: &str) { println!("login {} {}", user, password); }',
    ("rust", "SEC059"): ('fn save(p: &str) { let path = Path::new(p); if !path.exists() {'
                         ' let f = File::create(path); } }'),
    ("cobol", "SEC014"): (
        "       IDENTIFICATION DIVISION.\n       PROGRAM-ID. WEBECHO.\n       DATA DIVISION.\n"
        "       WORKING-STORAGE SECTION.\n       01 WS-NAME PIC X(40).\n       01 WS-OUT PIC X(80).\n"
        "       PROCEDURE DIVISION.\n       MAIN-PARA.\n"
        "           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-NAME) END-EXEC.\n"
        "           STRING '<p>' WS-NAME '</p>' DELIMITED BY SIZE INTO WS-OUT.\n"
        "           EXEC CICS WEB SEND FROM(WS-OUT) END-EXEC.\n           GOBACK.\n"),
}
for rid, code in C_SNIPPETS.items():
    SNIPPETS[("c", rid)] = code
    SNIPPETS[("cpp", rid)] = code
for rid, code in CPP_ONLY.items():
    SNIPPETS[("cpp", rid)] = code


@pytest.mark.parametrize("lang,rule", sorted(SNIPPETS), ids=[f"{l}-{r}" for l, r in sorted(SNIPPETS)])
def test_snippet_reports_its_rule(lang, rule):
    rep = analyze_source(SNIPPETS[(lang, rule)], f"snippet.{lang}", lang)
    assert rep.parse_error is None
    assert rule in {f.rule_id for f in rep.active()}, [(f.rule_id, f.line, f.message) for f in rep.active()]


def _fixture_pairs():
    ext = {"java": "java", "cs": "csharp", "c": "c", "cpp": "cpp", "rs": "rust", "cbl": "cobol"}
    pairs = set()
    for f in glob.glob(os.path.join(HERE, "multilang_fixtures", "*", "*.*")):
        lang = ext[f.rsplit(".", 1)[1]]
        pairs |= {(x.rule_id, lang) for x in analyze_file(f).active()}
    return pairs


def test_every_claimed_pair_is_exercised():
    tested = _fixture_pairs() | {(r, l) for l, r in SNIPPETS}
    claimed = {(rid, l) for rid, langs in rule_languages().items() for l in langs if l != "python"}
    assert claimed - tested == set()
