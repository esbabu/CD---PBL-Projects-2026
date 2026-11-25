#[post("/load")]
async fn load(body: Bytes) -> String { let s: State = bincode::deserialize(&body).unwrap(); String::new() }
