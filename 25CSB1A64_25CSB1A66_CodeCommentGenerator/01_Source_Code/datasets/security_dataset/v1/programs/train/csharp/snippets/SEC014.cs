class HomeController : Controller { public void Hi([FromQuery] string name) { Response.Write("<b>" + name + "</b>"); } }
