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

#[get("/pageV1")]
pub async fn pageV1(query: web::Query<Params>) -> HttpResponse {
    let n: usize = query.name.parse().unwrap();
    HttpResponse::Ok().body(n.to_string())
}

