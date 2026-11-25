void f(LDAP *ld){ char filter[128]; fgets(filter, sizeof filter, stdin); ldap_search_s(ld, "dc=corp", 2, filter, 0, 0, 0); }
