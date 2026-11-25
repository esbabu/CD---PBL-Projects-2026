int f(int s){ int t[4] = {0}; char x[4]; recv(s, x, sizeof x, 0); return t[atoi(x)]; }
