class A : Controller { public object F([FromQuery] string t) { return Type.GetType(t); } }
