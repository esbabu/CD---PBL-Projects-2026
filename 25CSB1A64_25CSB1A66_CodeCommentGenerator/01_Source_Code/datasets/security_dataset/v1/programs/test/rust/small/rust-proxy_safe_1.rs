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

#[get("/proxy-safe")]
pub async fn proxy_safeV1(query: web::Query<Params>) -> HttpResponse {
    let url = format!("https://api.example.com/items/{}", query.name);
    let body = reqwest::get(&url).await;
    HttpResponse::Ok().body(format!("{}", body.is_ok()))
}

