class A : Controller { public void F([FromQuery] string lang) { Response.Headers.Add("Content-Language", lang); } }
