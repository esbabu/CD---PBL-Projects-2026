#[get("/go")]
async fn go(q: Query<P>) -> Redirect { Redirect::to(&q.next) }
