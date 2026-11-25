class A : Controller { public void F([FromQuery] string n) { HttpContext.Session.SetString("user", n); } }
