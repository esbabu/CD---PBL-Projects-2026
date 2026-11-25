//! HTTP handlers of a small actix-web service. Vulnerable lines are marked "expect".
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
}

#[get("/ping")]
pub async fn ping(query: web::Query<Params>) -> HttpResponse {
    let host = query.host.clone();
    let out = Command::new("sh").arg("-c").arg(format!("ping -c 1 {}", host)).output();   // expect: SEC002
    HttpResponse::Ok().body(format!("{:?}", out.is_ok()))
}

#[get("/ping-safe")]
pub async fn ping_safe(query: web::Query<Params>) -> HttpResponse {
    let host = query.host.clone();
    let out = Command::new("ping").arg("-c").arg("1").arg(&host).output();
    HttpResponse::Ok().body(format!("{:?}", out.is_ok()))
}

#[get("/user")]
pub async fn find_user(query: web::Query<Params>, conn: web::Data<Connection>) -> HttpResponse {
    let sql = format!("SELECT id FROM users WHERE name = '{}'", query.name);
    let n = conn.execute(&sql, []).unwrap_or(0);                                          // expect: SEC005
    HttpResponse::Ok().body(n.to_string())
}

#[get("/user-safe")]
pub async fn find_user_safe(query: web::Query<Params>, conn: web::Data<Connection>) -> HttpResponse {
    let n = conn.execute("SELECT id FROM users WHERE name = ?1", [&query.name]).unwrap_or(0);
    HttpResponse::Ok().body(n.to_string())
}

#[get("/file")]
pub async fn read_file(query: web::Query<Params>) -> HttpResponse {
    let path = format!("/srv/files/{}", query.name);
    let text = fs::read_to_string(&path).unwrap_or_default();                               // expect: SEC013
    HttpResponse::Ok().body(text.len().to_string())
}

#[get("/proxy")]
pub async fn proxy(query: web::Query<Params>) -> HttpResponse {
    let body = reqwest::get(&query.host).await;                                             // expect: SEC016
    HttpResponse::Ok().body(format!("{}", body.is_ok()))
}

#[get("/proxy-safe")]
pub async fn proxy_safe(query: web::Query<Params>) -> HttpResponse {
    let url = format!("https://api.example.com/items/{}", query.name);
    let body = reqwest::get(&url).await;
    HttpResponse::Ok().body(format!("{}", body.is_ok()))
}

#[get("/page")]
pub async fn page(query: web::Query<Params>) -> HttpResponse {
    let n: usize = query.name.parse().unwrap();                                              // expect: SEC062
    HttpResponse::Ok().body(n.to_string())
}

#[post("/count")]
pub async fn count() -> HttpResponse {
    unsafe {
        REQUEST_COUNT += 1;                                                                  // expect: SEC063
    }
    HttpResponse::Ok().finish()
}

pub fn first_byte(data: &[u8]) -> u8 {
    let p = data.as_ptr();
    unsafe { *p }                                                                            // expect: SEC060
}

pub fn first_byte_safe(data: &[u8]) -> u8 {
    data.first().copied().unwrap_or(0)
}

pub fn insecure_client() -> reqwest::Client {
    reqwest::Client::builder()
        .danger_accept_invalid_certs(true)                                                   // expect: SEC030
        .build()
        .unwrap()
}

pub fn checksum(data: &[u8]) -> String {
    format!("{:x}", md5::compute(data))                                                      // expect: SEC004
}

pub fn connect() -> String {
    let password = "hunter2-prod-2026";                                                      // expect: SEC003
    format!("postgres://app@db/shop?pw={}", password.len())
}
