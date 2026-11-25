package com.example.shop;

import io.jsonwebtoken.Jwts;
import java.util.regex.Pattern;
import javax.naming.directory.DirContext;
import javax.servlet.http.HttpServletResponse;
import javax.xml.xpath.XPath;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/orders")
public class OrderController {

    private final JdbcTemplate jdbc;
    private final DirContext ldap;
    private final XPath xpath;
    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(OrderController.class);

    OrderController(JdbcTemplate jdbc, DirContext ldap, XPath xpath) {
        this.jdbc = jdbc;
        this.ldap = ldap;
        this.xpath = xpath;
    }

    @GetMapping("/search")
    public Object search(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");   // expect: SEC005
    }

    @GetMapping("/search-safe")
    public Object searchSafe(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

    @GetMapping("/count")
    public Object count(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

    @GetMapping("/staff")
    public Object staff(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staff,dc=shop", "(uid=" + uid + ")", null);                       // expect: SEC019
    }

    @GetMapping("/product")
    public Object product(@RequestParam String sku) throws Exception {
        return xpath.evaluate("//product[@sku='" + sku + "']", null);                              // expect: SEC020
    }

    @GetMapping("/plugin")
    public Object plugin(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();   // expect: SEC025
    }

    @GetMapping("/grep")
    public boolean grep(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();                              // expect: SEC024
    }

    @GetMapping("/grep-safe")
    public boolean grepSafe(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

    @GetMapping("/lang")
    public void lang(@RequestParam String lang, HttpServletResponse resp) {
        resp.setHeader("Content-Language", lang);                                                   // expect: SEC023
        log.info("language changed to " + lang);                                                    // expect: SEC022
    }

    @GetMapping("/claims")
    public Object claims(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);                                        // expect: SEC047
    }

    @PermitAll
    @DeleteMapping("/{id}")
    public void delete(@PathVariable long id) {                                                      // expect: SEC061
        jdbc.update("DELETE FROM orders WHERE id = ?", id);
    }

    @CrossOrigin(origins = "*")
    @GetMapping("/public")
    public String publicInfo() {                                                                     // expect: SEC046
        return "ok";
    }

    void configure(HttpSecurity http) throws Exception {
        http.csrf().disable();                                                                       // expect: SEC045
    }
}
