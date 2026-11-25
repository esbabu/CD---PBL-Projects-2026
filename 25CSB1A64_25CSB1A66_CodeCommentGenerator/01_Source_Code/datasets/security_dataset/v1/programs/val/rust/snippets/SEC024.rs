#[get("/g")]
async fn g(q: web::Query<P>) -> String { let r = Regex::new(&q.pattern); String::new() }
