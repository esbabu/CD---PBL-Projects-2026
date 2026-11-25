class A : Controller { public object F([FromQuery] string uid) { return new DirectorySearcher("(uid=" + uid + ")").FindOne(); } }
