void f(MYSQL *conn){ char name[64]; char q[256]; fgets(name, sizeof name, stdin); sprintf(q, "SELECT * FROM t WHERE n = '%s'", name); mysql_query(conn, q); }
