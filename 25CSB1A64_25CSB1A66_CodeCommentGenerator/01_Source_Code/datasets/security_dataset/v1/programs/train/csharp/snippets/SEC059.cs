class A { void F(string path) { if (!File.Exists(path)) { File.WriteAllText(path, "x"); } } }
