"""
Per-language taint specifications
==================================
Sources, sinks, sanitizers and propagation facts for Java, C, C++, C#, Rust
and COBOL, written as data so the taint engine (``taint.py``) stays
language-neutral.

Matching a call
---------------
Every lowered call has a ``callee`` (``Statement.executeQuery`` when the
receiver's declared type is known, otherwise the dotted chain as written,
``Runtime.getRuntime.exec``), a ``chain`` and a ``method``. A pattern matches

* ``"Statement.executeQuery"`` — callee or chain equals it or ends with ``.<it>``
  (exact resolution → high confidence);
* ``"*.executeQuery"`` — any call of that method name whose receiver type is
  unknown (method-name resolution → medium confidence).

Contexts are the same names the Python analyzer uses (``sql``, ``shell``, …)
plus three for memory safety: ``buffer`` (length of copied data), ``size``
(allocation size / copy length) and ``index`` (array index).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Tuple

INJECTION = frozenset({"sql", "shell", "html", "path", "url", "redirect", "xml", "ldap", "xpath", "log", "header",
                       "regex", "code", "deserialization", "format", "trust", "buffer"})
MEMORY = frozenset({"size", "index"})
ALL = INJECTION | MEMORY


@dataclass(frozen=True)
class Source:
    patterns: Tuple[str, ...]
    description: str
    trust: str = "remote"                  # remote | local
    out_args: Tuple[int, ...] = ()         # C-style: these argument variables receive the data
    from_arg: Optional[int] = None         # first out arg index; all following args (scanf)
    kind: str = "call"                     # call | attr | param_type | param_annotation


@dataclass(frozen=True)
class Sink:
    rule_id: str
    patterns: Tuple[str, ...]
    args: Tuple = (0,)                     # positions; "*" = every argument
    kwargs: Tuple[str, ...] = ()
    use_receiver: bool = False
    operation: str = ""
    context: Optional[str] = None          # defaults to the rule's context
    condition: Optional[str] = None        # url (fixed destination exempt) | shell_program | format_nonliteral


@dataclass(frozen=True)
class Sanitizer:
    patterns: Tuple[str, ...]
    clears: FrozenSet[str]
    note: str


@dataclass
class LanguageSpec:
    language: str
    sources: List[Source]
    sinks: List[Sink]
    sanitizers: List[Sanitizer]
    clean_methods: FrozenSet[str] = frozenset()     # results never carry taint
    mutators: FrozenSet[str] = frozenset()          # receiver absorbs argument taint
    copy_into: Dict[str, Tuple[int, Tuple[int, ...]]] = field(default_factory=dict)   # C: dst ← srcs
    strlen_funcs: FrozenSet[str] = frozenset({"strlen", "strnlen", "wcslen", "size", "length", "len", "Length",
                                              "Count", "capacity"})
    alloc_funcs: FrozenSet[str] = frozenset()
    free_funcs: FrozenSet[str] = frozenset()


NUMERIC = frozenset(ALL - MEMORY)          # numeric conversion: no injection, but size/index stay dangerous

_CLEAN_COMMON = frozenset({
    "length", "size", "isEmpty", "equals", "equalsIgnoreCase", "hashCode", "compareTo", "contains", "startsWith",
    "endsWith", "indexOf", "lastIndexOf", "matches", "is_empty", "len", "starts_with", "ends_with", "eq",
    "Equals", "Contains", "StartsWith", "EndsWith", "IndexOf", "Count", "Any", "IsNullOrEmpty",
    "IsNullOrWhiteSpace", "CompareTo", "GetHashCode", "is_some", "is_none", "is_ok", "is_err", "exists",
    "isPresent", "hasNext", "next_back", "count", "strcmp", "strncmp", "memcmp", "strcasecmp", "strlen",
    "close", "Close", "Dispose", "flush", "Flush",
})
_MUTATORS_COMMON = frozenset({
    "append", "insert", "push", "push_str", "extend", "add", "put", "putAll", "addAll", "write", "print",
    "Append", "AppendLine", "AppendFormat", "Insert", "Add", "AddRange", "Write", "WriteLine", "extend_from_slice",
    "push_back", "emplace_back",
})

# ---------------------------------------------------------------------------
# Java
# ---------------------------------------------------------------------------
JAVA = LanguageSpec(
    "java",
    sources=[
        Source(("HttpServletRequest.getParameter", "HttpServletRequest.getParameterValues",
                "HttpServletRequest.getParameterMap", "HttpServletRequest.getHeader",
                "HttpServletRequest.getHeaders", "HttpServletRequest.getQueryString",
                "HttpServletRequest.getCookies", "HttpServletRequest.getInputStream",
                "HttpServletRequest.getReader", "HttpServletRequest.getPathInfo",
                "HttpServletRequest.getRequestURI", "HttpServletRequest.getRequestURL",
                "ServletRequest.getParameter", "*.getParameter", "*.getParameterValues", "*.getQueryString",
                "*.getHeader", "*.getCookies", "Cookie.getValue", "*.getInputStream"),
               "HTTP request data (servlet API)"),
        Source(("Scanner.nextLine", "Scanner.next", "BufferedReader.readLine", "Console.readLine",
                "*.nextLine", "*.readLine"), "interactive / stream input"),
        Source(("System.getenv", "System.getProperty"), "environment / system property", trust="local"),
        Source(("@RequestParam", "@PathVariable", "@RequestBody", "@RequestHeader", "@CookieValue",
                "@ModelAttribute", "@QueryParam", "@PathParam", "@FormParam", "@HeaderParam"),
               "HTTP parameter bound by the web framework", kind="param_annotation"),
    ],
    sinks=[
        Sink("SEC002", ("Runtime.getRuntime.exec", "Runtime.exec", "*.exec"), args="*", operation="OS command execution",
             condition="exec_receiver"),
        Sink("SEC002", ("new ProcessBuilder", "ProcessBuilder.command"), args="*", operation="process creation"),
        Sink("SEC005", ("Statement.executeQuery", "Statement.execute", "Statement.executeUpdate",
                        "Statement.addBatch", "Statement.executeLargeUpdate", "Connection.prepareStatement",
                        "Connection.prepareCall", "Connection.nativeSQL", "JdbcTemplate.query",
                        "JdbcTemplate.queryForObject", "JdbcTemplate.queryForList", "JdbcTemplate.update",
                        "JdbcTemplate.execute", "EntityManager.createQuery", "EntityManager.createNativeQuery",
                        "Session.createQuery", "Session.createSQLQuery", "*.executeQuery", "*.executeUpdate",
                        "*.prepareStatement", "*.createNativeQuery", "*.addBatch", "*.queryForList",
                        "*.queryForObject"), args=(0,), operation="SQL execution"),
        Sink("SEC013", ("new File", "new FileInputStream", "new FileOutputStream", "new FileReader", "new FileWriter",
                        "new RandomAccessFile", "Paths.get", "Path.of", "Files.readAllBytes", "Files.readAllLines",
                        "Files.newInputStream", "Files.newOutputStream", "Files.write", "Files.delete",
                        "Files.copy", "Files.move", "Files.readString", "Files.newBufferedReader"),
             args=(0,), operation="file-system access"),
        Sink("SEC014", ("PrintWriter.print", "PrintWriter.println", "PrintWriter.write", "PrintWriter.printf",
                        "PrintWriter.format", "HttpServletResponse.getWriter.print",
                        "HttpServletResponse.getWriter.println", "HttpServletResponse.getWriter.write",
                        "*.getWriter.print", "*.getWriter.println", "*.getWriter.write", "*.getWriter.printf",
                        "ServletOutputStream.print", "ServletOutputStream.println"),
             args="*", operation="HTTP response body"),
        Sink("SEC016", ("new URL", "URI.create", "new URI", "HttpRequest.newBuilder.uri", "RestTemplate.getForObject",
                        "RestTemplate.getForEntity", "RestTemplate.postForObject", "RestTemplate.exchange",
                        "WebClient.create", "HttpGet", "new HttpGet", "new HttpPost"),
             args=(0,), operation="outbound HTTP request", condition="url"),
        Sink("SEC017", ("HttpServletResponse.sendRedirect", "*.sendRedirect"), args=(0,), operation="HTTP redirect",
             condition="url"),
        Sink("SEC009", ("ObjectInputStream.readObject", "ObjectInputStream.readUnshared", "XMLDecoder.readObject",
                        "XStream.fromXML", "Yaml.load",
                        "ObjectMapper.enableDefaultTyping"), args=(0,), use_receiver=True, operation="deserialization"),
        Sink("SEC019", ("DirContext.search", "InitialDirContext.search", "LdapTemplate.search", "*.search"),
             args=(1,), operation="LDAP search"),
        Sink("SEC020", ("XPath.evaluate", "XPath.compile", "*.evaluate", "*.compile"), args=(0,),
             operation="XPath evaluation", context="xpath", condition="xpath_receiver"),
        Sink("SEC022", ("Logger.info", "Logger.warn", "Logger.error", "Logger.debug", "Logger.trace", "Logger.fatal",
                        "Logger.log", "Logger.warning", "Logger.severe", "*.info", "*.warn", "*.error", "*.debug"),
             args="*", operation="log write", condition="logger_receiver"),
        Sink("SEC023", ("HttpServletResponse.setHeader", "HttpServletResponse.addHeader", "*.setHeader",
                        "*.addHeader"), args=(1,), operation="HTTP response header"),
        Sink("SEC024", ("Pattern.compile", "String.matches", "String.replaceAll", "String.split"), args=(0,),
             operation="regular-expression compilation"),
        Sink("SEC025", ("Class.forName", "ClassLoader.loadClass", "*.loadClass"), args=(0,),
             operation="class loading by name"),
        Sink("SEC028", ("HttpSession.setAttribute", "HttpSession.putValue", "*.getSession.setAttribute"),
             args=(0, 1), operation="session state"),
        Sink("SEC001", ("ScriptEngine.eval", "*.eval", "GroovyShell.evaluate", "ExpressionParser.parseExpression",
                        "SpelExpressionParser.parseExpression", "Ognl.getValue", "MVEL.eval"), args=(0,),
             operation="dynamic code / expression evaluation"),
    ],
    sanitizers=[
        Sanitizer(("Integer.parseInt", "Integer.valueOf", "Long.parseLong", "Long.valueOf", "Double.parseDouble",
                   "Float.parseFloat", "Short.parseShort", "Boolean.parseBoolean", "UUID.fromString",
                   "Integer.decode"), NUMERIC, "conversion to a number"),
        Sanitizer(("ESAPI.encoder.encodeForHTML", "StringEscapeUtils.escapeHtml4", "StringEscapeUtils.escapeHtml",
                   "HtmlUtils.htmlEscape", "Encode.forHtml", "Encode.forHtmlContent", "Encode.forHtmlAttribute"),
                  frozenset({"html"}), "HTML escaping"),
        Sanitizer(("ESAPI.encoder.encodeForSQL",), frozenset({"sql"}), "SQL escaping (ESAPI)"),
        Sanitizer(("ESAPI.encoder.encodeForLDAP", "LdapEncoder.filterEncode", "LdapNameBuilder"),
                  frozenset({"ldap"}), "LDAP filter escaping"),
        Sanitizer(("FilenameUtils.getName", "Paths.get.getFileName", "*.getFileName"),
                  frozenset({"path"}), "reduces the value to a bare file name"),
        Sanitizer(("URLEncoder.encode",), frozenset({"html", "sql", "shell", "header", "log", "ldap", "xpath"}),
                  "URL percent-encoding"),
        Sanitizer(("Pattern.quote",), frozenset({"regex"}), "regular-expression quoting"),
    ],
    clean_methods=_CLEAN_COMMON,
    mutators=_MUTATORS_COMMON,
)

# ---------------------------------------------------------------------------
# C# (.NET / ASP.NET Core)
# ---------------------------------------------------------------------------
CSHARP = LanguageSpec(
    "csharp",
    sources=[
        Source(("Request.Query", "Request.Form", "Request.Headers", "Request.Cookies", "Request.QueryString",
                "Request.Body", "Request.Path", "Request.RouteValues", "HttpContext.Request.Query",
                "HttpContext.Request.Form", "Request.Params", "Request.ServerVariables"),
               "HTTP request data (ASP.NET)", kind="attr"),
        Source(("Console.ReadLine", "Console.Read", "StreamReader.ReadLine", "StreamReader.ReadToEnd",
                "*.ReadToEndAsync", "*.ReadLine"), "interactive / stream input"),
        Source(("Environment.GetEnvironmentVariable", "Environment.GetCommandLineArgs"),
               "environment / command line", trust="local"),
        Source(("[FromQuery", "[FromBody", "[FromForm", "[FromRoute", "[FromHeader"),
               "HTTP parameter bound by ASP.NET model binding", kind="param_annotation"),
    ],
    sinks=[
        Sink("SEC002", ("Process.Start", "new ProcessStartInfo"), args="*", kwargs=("FileName", "Arguments"),
             operation="process execution"),
        Sink("SEC005", ("new SqlCommand", "new OleDbCommand", "new OdbcCommand", "new NpgsqlCommand",
                        "new MySqlCommand", "new SqliteCommand", "SqlCommand.ExecuteReader", "*.ExecuteSqlRaw",
                        "*.ExecuteSqlRawAsync", "*.FromSqlRaw", "*.ExecuteSqlCommand", "*.SqlQuery",
                        "Database.ExecuteSqlRaw", "*.Query", "*.Execute", "*.QueryFirst", "*.QueryAsync",
                        "*.ExecuteAsync"), args=(0,), kwargs=("CommandText",), operation="SQL execution",
             condition="sql_receiver"),
        Sink("SEC013", ("File.ReadAllText", "File.ReadAllBytes", "File.ReadAllLines", "File.WriteAllText",
                        "File.WriteAllBytes", "File.Open", "File.OpenRead", "File.OpenWrite", "File.Delete",
                        "File.Create", "File.Copy", "File.Move", "File.AppendAllText", "Directory.Delete",
                        "Directory.GetFiles", "new FileStream", "new StreamReader", "new StreamWriter",
                        "new FileInfo", "PhysicalFile", "*.PhysicalFile"), args=(0,), operation="file-system access"),
        Sink("SEC014", ("Response.Write", "HttpResponse.WriteAsync", "Html.Raw", "new HtmlString",
                        "new HtmlContentBuilder.AppendHtml", "*.AppendHtml"), args=(0,),
             operation="HTTP response body (HTML)"),
        Sink("SEC016", ("HttpClient.GetAsync", "HttpClient.GetStringAsync", "HttpClient.PostAsync",
                        "HttpClient.GetByteArrayAsync", "HttpClient.GetStreamAsync", "HttpClient.SendAsync",
                        "WebRequest.Create", "HttpWebRequest.Create", "new WebClient.DownloadString",
                        "WebClient.DownloadString", "*.GetStringAsync", "*.GetAsync"), args=(0,),
             operation="outbound HTTP request", condition="url"),
        Sink("SEC017", ("Redirect", "*.Redirect", "RedirectPermanent", "Response.Redirect", "new RedirectResult"),
             args=(0,), operation="HTTP redirect", condition="url"),
        Sink("SEC009", ("BinaryFormatter.Deserialize", "SoapFormatter.Deserialize", "NetDataContractSerializer.Deserialize",
                        "LosFormatter.Deserialize", "ObjectStateFormatter.Deserialize", "JavaScriptSerializer.Deserialize",
                        "*.Deserialize"), args=(0,), operation="deserialization", condition="deser_receiver"),
        Sink("SEC019", ("new DirectorySearcher", "DirectorySearcher.FindOne", "DirectorySearcher.FindAll"),
             args=(0,), kwargs=("Filter",), operation="LDAP search"),
        Sink("SEC020", ("XmlDocument.SelectNodes", "XmlDocument.SelectSingleNode", "XmlNode.SelectNodes",
                        "XPathNavigator.Select", "XPathNavigator.Evaluate", "*.SelectNodes", "*.SelectSingleNode"),
             args=(0,), operation="XPath evaluation"),
        Sink("SEC022", ("ILogger.LogInformation", "ILogger.LogWarning", "ILogger.LogError", "ILogger.LogDebug",
                        "*.LogInformation", "*.LogWarning", "*.LogError", "*.LogDebug", "*.LogCritical"),
             args="*", operation="log write"),
        Sink("SEC023", ("Response.Headers.Add", "Response.AppendHeader", "Response.AddHeader", "*.Headers.Append"),
             args=(1,), operation="HTTP response header"),
        Sink("SEC024", ("new Regex", "Regex.Match", "Regex.IsMatch", "Regex.Matches", "Regex.Replace"),
             args=(0,), operation="regular-expression compilation", condition="regex_static"),
        Sink("SEC025", ("Type.GetType", "Assembly.Load", "Assembly.LoadFrom", "Activator.CreateInstance",
                        "Assembly.GetType"), args=(0,), operation="type / assembly loading by name"),
        Sink("SEC028", ("ISession.SetString", "Session.SetString", "*.Session.SetString", "*.SetString"),
             args=(0, 1), operation="session state", condition="session_receiver"),
    ],
    sanitizers=[
        Sanitizer(("int.Parse", "Int32.Parse", "long.Parse", "Int64.Parse", "Convert.ToInt32", "Convert.ToInt64",
                   "double.Parse", "Guid.Parse", "decimal.Parse", "int.TryParse", "Int32.TryParse", "bool.Parse"),
                  NUMERIC, "conversion to a number"),
        Sanitizer(("HtmlEncoder.Default.Encode", "HttpUtility.HtmlEncode", "WebUtility.HtmlEncode",
                   "AntiXssEncoder.HtmlEncode", "Encoder.HtmlEncode"), frozenset({"html"}), "HTML encoding"),
        Sanitizer(("Path.GetFileName",), frozenset({"path"}), "reduces the value to a bare file name"),
        Sanitizer(("Uri.EscapeDataString", "HttpUtility.UrlEncode", "WebUtility.UrlEncode"),
                  frozenset({"html", "sql", "shell", "header", "log", "ldap", "xpath"}), "URL percent-encoding"),
        Sanitizer(("Regex.Escape",), frozenset({"regex"}), "regular-expression escaping"),
    ],
    clean_methods=_CLEAN_COMMON,
    mutators=_MUTATORS_COMMON,
)

# ---------------------------------------------------------------------------
# C and C++
# ---------------------------------------------------------------------------
_C_SOURCES = [
    Source(("gets", "gets_s"), "standard input (gets)", out_args=(0,)),
    Source(("fgets", "fgetws"), "file / standard input (fgets)", out_args=(0,)),
    Source(("scanf", "vscanf"), "standard input (scanf)", from_arg=1),
    Source(("fscanf", "sscanf"), "formatted input (fscanf/sscanf)", from_arg=2),
    Source(("read",), "file descriptor read", out_args=(1,)),
    Source(("recv", "recvfrom", "recvmsg"), "network socket (recv)", out_args=(1,)),
    Source(("fread",), "file read (fread)", out_args=(0,)),
    Source(("std.getline",), "input stream (std::getline)", out_args=(1,)),
    Source(("getline", "getdelim"), "input line (getline)", out_args=(0,)),
    Source(("std.cin>>",), "standard input (std::cin)"),
    Source(("getenv", "secure_getenv", "std.getenv"), "environment variable", trust="local"),
    Source(("main#argv",), "command-line argument", trust="local", kind="param_type"),
]
_C_SINKS = [
    Sink("SEC002", ("system", "popen", "_popen", "_wsystem", "std.system"), args=(0,),
         operation="shell command execution"),
    Sink("SEC002", ("execl", "execlp", "execle", "execv", "execvp", "execve"), args=(0,),
         operation="program execution"),
    Sink("SEC013", ("fopen", "open", "creat", "unlink", "remove", "rename", "opendir", "std.ifstream",
                    "std.ofstream", "new std.ifstream", "new ifstream", "new ofstream", "freopen", "access",
                    "stat", "chmod", "truncate"), args=(0,), operation="file-system access"),
    Sink("SEC026", ("printf", "vprintf", "wprintf", "syslog#1", "fprintf#1", "vfprintf#1", "sprintf#1",
                    "vsprintf#1", "snprintf#2", "vsnprintf#2", "dprintf#1", "err#1", "warn#0"),
         args=(0,), operation="format string", context="format"),
    Sink("SEC052", ("strcpy", "strcat", "wcscpy", "wcscat", "lstrcpy", "lstrcat", "StrCpy", "_mbscpy",
                    "std.strcpy"), args=(1,), operation="unbounded copy into a fixed buffer", context="buffer"),
    Sink("SEC052", ("sprintf", "vsprintf"), args=(2, 3, 4, 5, 6), operation="unbounded formatted write",
         context="buffer"),
    Sink("SEC053", ("memcpy", "memmove", "strncpy", "strncat", "wmemcpy", "std.memcpy", "bcopy"), args=(2,),
         operation="copy length", context="size"),
    Sink("SEC055", ("malloc", "alloca", "_alloca", "valloc", "std.malloc"), args=(0,), operation="allocation size",
         context="size"),
    Sink("SEC055", ("calloc",), args=(0, 1), operation="allocation size", context="size"),
    Sink("SEC055", ("realloc",), args=(1,), operation="allocation size", context="size"),
    Sink("SEC019", ("ldap_search_s", "ldap_search_ext_s", "ldap_search", "ldap_search_st"), args=(3,),
         operation="LDAP search",
         context="ldap"),
    Sink("SEC005", ("mysql_query", "mysql_real_query", "sqlite3_exec", "sqlite3_prepare_v2", "sqlite3_prepare",
                    "PQexec", "SQLExecDirect", "OCIStmtPrepare"), args=(1,), operation="SQL execution", context="sql"),
    Sink("SEC025", ("dlopen", "LoadLibraryA", "LoadLibraryW", "LoadLibrary"), args=(0,),
         operation="library loading by name", context="code"),
]
_C_SANITIZERS = [
    Sanitizer(("atoi", "atol", "atoll", "strtol", "strtoul", "strtoll", "strtoull", "strtod", "atof",
               "std.stoi", "std.stol", "std.stoul", "stoi", "stol"), NUMERIC, "conversion to a number"),
    Sanitizer(("basename", "PathFindFileNameA"), frozenset({"path"}), "reduces the value to a bare file name"),
    Sanitizer(("mysql_real_escape_string", "PQescapeLiteral", "PQescapeStringConn", "sqlite3_mprintf#q"),
              frozenset({"sql"}), "SQL escaping"),
]
_C_COPY = {"strcpy": (0, (1,)), "strcat": (0, (1,)), "strncpy": (0, (1,)), "strncat": (0, (1,)),
           "memcpy": (0, (1,)), "memmove": (0, (1,)), "sprintf": (0, (2, 3, 4, 5, 6)),
           "snprintf": (0, (3, 4, 5, 6, 7)), "wcscpy": (0, (1,)), "strdup": (-1, (0,)), "strndup": (-1, (0,))}
C = LanguageSpec("c", _C_SOURCES, _C_SINKS, _C_SANITIZERS, clean_methods=_CLEAN_COMMON | {"sizeof"},
                 mutators=frozenset(), copy_into=_C_COPY,
                 alloc_funcs=frozenset({"malloc", "calloc", "realloc", "strdup", "strndup", "aligned_alloc"}),
                 free_funcs=frozenset({"free", "cfree", "g_free", "kfree"}))
CPP = LanguageSpec(
    "cpp", _C_SOURCES, _C_SINKS + [
        Sink("SEC009", ("boost.archive.text_iarchive", "new text_iarchive", "new binary_iarchive", "text_iarchive"),
             args=(0,), operation="deserialization", context="deserialization"),
    ], _C_SANITIZERS, clean_methods=_CLEAN_COMMON | {"sizeof"},
    mutators=_MUTATORS_COMMON | {"assign", "append", "operator+="}, copy_into=_C_COPY,
    alloc_funcs=frozenset({"malloc", "calloc", "realloc", "strdup", "new"}),
    free_funcs=frozenset({"free", "delete", "delete[]"}))

# ---------------------------------------------------------------------------
# Rust
# ---------------------------------------------------------------------------
RUST = LanguageSpec(
    "rust",
    sources=[
        Source(("std.env.args", "env.args", "std.env.args_os", "env::args"), "command-line argument", trust="local"),
        Source(("std.env.var", "env.var", "std.env.var_os", "env.var_os"), "environment variable", trust="local"),
        Source(("Stdin.read_line", "stdin.read_line", "io.stdin.read_line", "std.io.stdin.read_line",
                "*.read_line", "*.read_to_string", "*.read_to_end"), "standard input / stream",
               out_args=(0,), kind="call"),
        Source(("HttpRequest.query_string", "HttpRequest.match_info", "HttpRequest.headers", "*.query_string",
                "*.match_info"), "HTTP request data (actix-web)"),
        Source(("Query", "Json", "Form", "Path", "web.Query", "web.Json", "web.Form", "web.Path", "Bytes",
                "RawQuery"), "HTTP extractor (web framework)", kind="param_type"),
        Source(("TcpStream.read", "UdpSocket.recv_from", "*.recv_from"), "network socket", out_args=(0,)),
    ],
    sinks=[
        Sink("SEC002", ("Command.new",), args=(0,), operation="program execution"),
        Sink("SEC002", ("*.arg", "*.args"), args=(0,), operation="process argument", condition="shell_program"),
        Sink("SEC005", ("*.execute", "*.query", "*.query_row", "*.query_map", "*.prepare", "sqlx.query",
                        "sqlx.query_as", "diesel.sql_query", "sql_query", "*.batch_execute", "*.simple_query"),
             args=(0,), operation="SQL execution", condition="sql_receiver"),
        Sink("SEC013", ("File.open", "File.create", "fs.read_to_string", "fs.read", "fs.write", "fs.remove_file",
                        "fs.remove_dir_all", "std.fs.read_to_string", "std.fs.write", "std.fs.remove_file",
                        "OpenOptions.open", "*.open", "fs.copy", "fs.rename", "fs.create_dir_all",
                        "NamedFile.open"), args=(0,), operation="file-system access", condition="path_receiver"),
        Sink("SEC016", ("reqwest.get", "reqwest.blocking.get", "Client.get", "Client.post", "*.get_url",
                        "ureq.get", "ureq.post", "surf.get"), args=(0,), operation="outbound HTTP request",
             condition="url"),
        Sink("SEC017", ("Redirect.to", "Redirect.temporary", "Redirect.permanent", "Redirect.see_other",
                        "HttpResponse.Found.append_header"), args=(0,), operation="HTTP redirect", condition="url"),
        Sink("SEC014", ("Html", "Html.from", "*.body"), args=(0,),
             operation="HTML response body", condition="html_body"),
        Sink("SEC009", ("bincode.deserialize", "serde_pickle.from_slice", "rmp_serde.from_slice",
                        "serde_yaml.from_str"), args=(0,), operation="deserialization"),
        Sink("SEC062", ("*.parse.unwrap", "*.parse.expect"), args=(), use_receiver=True,
             operation="parse of untrusted input that panics on failure", context="index",
             condition="panic_parse"),
        Sink("SEC022", ("log.info", "log.warn", "log.error", "log.debug", "info!", "warn!", "error!", "debug!",
                        "log.info!", "log.warn!", "log.error!"), args="*", operation="log write"),
        Sink("SEC024", ("Regex.new", "regex.Regex.new", "RegexBuilder.new"), args=(0,),
             operation="regular-expression compilation"),
    ],
    sanitizers=[
        Sanitizer(("*.parse",), NUMERIC, "parse into a typed value"),
        Sanitizer(("html_escape.encode_text", "htmlescape.encode_minimal", "ammonia.clean", "encode_safe",
                   "askama.escape"), frozenset({"html"}), "HTML escaping"),
        Sanitizer(("Path.file_name", "*.file_name"), frozenset({"path"}), "reduces the value to a bare file name"),
        Sanitizer(("urlencoding.encode", "utf8_percent_encode"), frozenset({"html", "sql", "shell", "header", "log"}),
                  "URL percent-encoding"),
        Sanitizer(("regex.escape",), frozenset({"regex"}), "regular-expression escaping"),
    ],
    clean_methods=_CLEAN_COMMON | {"len", "is_empty", "chars.count", "as_ptr"},
    mutators=_MUTATORS_COMMON,
)

# ---------------------------------------------------------------------------
# COBOL (statements are lowered to calls by cobol.py)
# ---------------------------------------------------------------------------
COBOL = LanguageSpec(
    "cobol",
    sources=[
        Source(("ACCEPT",), "terminal / console input (ACCEPT)"),
        Source(("CICS.RECEIVE", "CICS.WEB.RECEIVE", "CICS.WEB.READ"), "CICS terminal / web input"),
        Source(("LINKAGE",), "LINKAGE SECTION parameter (data passed by the caller)", trust="local",
               kind="param_type"),
        Source(("READ",), "record read from a file", trust="local", out_args=(0,)),
    ],
    sinks=[
        Sink("SEC005", ("SQL.EXECUTE-IMMEDIATE", "SQL.PREPARE"), args=(0,), operation="dynamic SQL", context="sql"),
        Sink("SEC002", ("CALL.SYSTEM", "CALL.CBL_EXEC_RUN_UNIT", "CALL.C$SYSTEM"), args="*",
             operation="operating-system command", context="shell"),
        Sink("SEC025", ("CALL.DYNAMIC", "CICS.LINK", "CICS.XCTL"), args=(0,),
             operation="program selected at run time", context="code"),
        Sink("SEC013", ("ASSIGN.DYNAMIC", "OPEN.DYNAMIC"), args=(0,), operation="file selected at run time",
             context="path"),
        Sink("SEC054", ("REFMOD",), args=(0, 1), operation="reference modification offset / length",
             context="index"),
        Sink("SEC014", ("CICS.WEB.SEND", "CICS.SEND"), args=(0,), operation="web / terminal response", context="html"),
    ],
    sanitizers=[
        Sanitizer(("NUMVAL", "NUMVAL-C", "FUNCTION.NUMVAL", "FUNCTION.NUMVAL-C"), NUMERIC, "conversion to a number"),
    ],
)

SPECS: Dict[str, LanguageSpec] = {s.language: s for s in (JAVA, CSHARP, C, CPP, RUST, COBOL)}
