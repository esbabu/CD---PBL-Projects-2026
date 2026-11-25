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

#[get("/file")]
pub async fn read_file(query: web::Query<Params>) -> HttpResponse {
    let path = format!("/srv/files/{}", query.name);
    let text = fs::read_to_string(&path).unwrap_or_default();
    HttpResponse::Ok().body(text.len().to_string())
}

