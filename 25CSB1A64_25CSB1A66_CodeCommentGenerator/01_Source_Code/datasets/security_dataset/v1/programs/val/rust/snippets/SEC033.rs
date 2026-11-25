fn enc(key: &[u8]) { let c = Des::new_from_slice(key); let d = Des::new(key); }
