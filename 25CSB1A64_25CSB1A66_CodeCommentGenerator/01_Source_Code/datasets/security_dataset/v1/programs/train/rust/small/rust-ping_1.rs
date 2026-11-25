use actix_web::{get, post, web, HttpResponse};
use rusqlite::Connection;
use serde::Deserialize;
use std::fs;
use std::process::Command;

static mut REQUEST_COUNT: u64 = 0;

#[derive(Deserialize)]
pub struct Params {
    pub name: String,
    pub host: String,
    pub next: String,
    pub page: String,
    pub pattern: String,
}

#[get("/pingV1")]
pub async fn pingV1(query: web::Query<Params>) -> HttpResponse {
    let host = query.host.clone();
    let out = Command::new("sh").arg("-c").arg(format!("pingV1 -c 1 {}", host)).output();
    HttpResponse::Ok().body(format!("{:?}", out.is_ok()))
}

