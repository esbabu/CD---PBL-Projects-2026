void f(int s){ char h[8]; char b[64]; recv(s, h, sizeof h, 0); int n = atoi(h); memcpy(b, h, n); }
