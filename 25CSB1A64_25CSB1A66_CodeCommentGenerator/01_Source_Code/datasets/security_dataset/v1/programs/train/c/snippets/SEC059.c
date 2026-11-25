void f(const char *p){ if (access(p, 2) == 0) { FILE *x = fopen(p, "w"); fclose(x); } }
