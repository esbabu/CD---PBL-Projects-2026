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

pub fn insecure_clientV1() -> reqwest::Client {
    reqwest::Client::builder()
        .danger_accept_invalid_certs(true)
        .build()
        .unwrap()
}

