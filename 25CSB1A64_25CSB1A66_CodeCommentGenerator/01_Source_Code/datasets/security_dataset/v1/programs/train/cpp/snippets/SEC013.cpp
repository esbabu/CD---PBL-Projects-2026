void f(void){ char *p = getenv("LOGFILE"); FILE *fp = fopen(p, "r"); fclose(fp); }
