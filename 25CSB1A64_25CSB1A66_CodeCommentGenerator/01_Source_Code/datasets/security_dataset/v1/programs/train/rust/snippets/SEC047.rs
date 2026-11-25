fn claims(t: &str) { let c = jsonwebtoken::dangerous_insecure_decode::<Claims>(t); }
