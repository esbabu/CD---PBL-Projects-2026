void *f(int s){ char c[8]; recv(s, c, sizeof c, 0); size_t n = strtoul(c, NULL, 10); return malloc(n * 16); }
