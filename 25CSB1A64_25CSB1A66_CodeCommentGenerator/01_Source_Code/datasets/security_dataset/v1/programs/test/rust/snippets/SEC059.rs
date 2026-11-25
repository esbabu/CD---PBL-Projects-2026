fn save(p: &str) { let path = Path::new(p); if !path.exists() { let f = File::create(path); } }
