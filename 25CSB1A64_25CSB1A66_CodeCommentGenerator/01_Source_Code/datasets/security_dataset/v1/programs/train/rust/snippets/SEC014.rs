#[get("/hi")]
async fn hi(q: web::Query<P>) -> HttpResponse { HttpResponse::Ok().content_type("text/html").body(format!("<p>{}</p>", q.name)) }
