class A { ILogger _logger; void Login(string user, string password) { _logger.LogInformation("login " + user + " " + password); } }
