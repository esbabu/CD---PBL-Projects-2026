#[get("/t")]
async fn t(q: web::Query<P>) -> String { log::info!("visit {}", q.page); String::new() }
