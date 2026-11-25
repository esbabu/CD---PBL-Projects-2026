class A : Controller { public object F([FromQuery] string n, XmlDocument doc) { return doc.SelectNodes("//user[@name='" + n + "']"); } }
