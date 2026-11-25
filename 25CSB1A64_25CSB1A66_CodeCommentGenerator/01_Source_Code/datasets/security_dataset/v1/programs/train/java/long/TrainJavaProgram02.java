import java.io.*;
import java.net.URL;
import java.security.MessageDigest;
import java.sql.*;
import java.util.Random;
import javax.crypto.Cipher;
import javax.servlet.http.*;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import io.jsonwebtoken.Jwts;
import java.util.regex.Pattern;
import javax.naming.directory.DirContext;
import javax.servlet.http.HttpServletResponse;
import javax.xml.xpath.XPath;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.web.bind.annotation.*;
import org.springframework.jdbc.core.JdbcTemplate;

public class TrainJavaProgram02 extends HttpServlet {

    private Connection conn;
    private String lastUser;
    private final JdbcTemplate jdbc = null;
    private final DirContext ldap = null;
    private final XPath xpath = null;
    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(Object.class);

        java.util.Map<String, Integer> countWords1(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/langN2")
    public void langN2(@RequestParam String langN2, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN2);
        log.info("language changed to " + langN2);
    }

    @GetMapping("/claimsN3")
    public Object claimsN3(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

        double averageOf4(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        boolean isLeapYear5(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth5(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear5(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    protected void doGetN6(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

    void pingSafeN7(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

        String formatAmount8(long cents) {
            long whole = cents / 100;
            long rest = Math.abs(cents % 100);
            StringBuilder sb = new StringBuilder();
            sb.append(whole).append('.');
            if (rest < 10) {
                sb.append('0');
            }
            sb.append(rest);
            return sb.toString();
        }

        boolean isLeapYear9(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth9(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear9(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    byte[] encryptBlockN10(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

        java.util.List<Integer> mergeSorted11(java.util.List<Integer> a, java.util.List<Integer> b) {
            java.util.List<Integer> out = new java.util.ArrayList<>();
            int i = 0;
            int j = 0;
            while (i < a.size() && j < b.size()) {
                if (a.get(i) <= b.get(j)) {
                    out.add(a.get(i++));
                } else {
                    out.add(b.get(j++));
                }
            }
            while (i < a.size()) {
                out.add(a.get(i++));
            }
            while (j < b.size()) {
                out.add(b.get(j++));
            }
            return out;
        }

        java.util.Map<String, Integer> countWords12(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/staffN13")
    public Object staffN13(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN13,dc=shop", "(uid=" + uid + ")", null);
    }

        java.util.Map<String, Integer> countWords14(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        int clampValue15(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        java.util.Map<String, Integer> countWords16(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/search-safe")
    public Object searchSafeN17(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

        int clampValue18(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    @GetMapping("/langN19")
    public void langN19(@RequestParam String langN19, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN19);
        log.info("language changed to " + langN19);
    }

    byte[] encryptBlockN20(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    Connection connectN21() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

        double averageOf22(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        String formatAmount23(long cents) {
            long whole = cents / 100;
            long rest = Math.abs(cents % 100);
            StringBuilder sb = new StringBuilder();
            sb.append(whole).append('.');
            if (rest < 10) {
                sb.append('0');
            }
            sb.append(rest);
            return sb.toString();
        }

    void pingSafeN24(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

    @GetMapping("/countN25")
    public Object countN25(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

    void restoreN26(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        boolean isLeapYear27(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth27(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear27(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        java.util.Map<String, Integer> countWords28(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.List<Integer> mergeSorted29(java.util.List<Integer> a, java.util.List<Integer> b) {
            java.util.List<Integer> out = new java.util.ArrayList<>();
            int i = 0;
            int j = 0;
            while (i < a.size() && j < b.size()) {
                if (a.get(i) <= b.get(j)) {
                    out.add(a.get(i++));
                } else {
                    out.add(b.get(j++));
                }
            }
            while (i < a.size()) {
                out.add(a.get(i++));
            }
            while (j < b.size()) {
                out.add(b.get(j++));
            }
            return out;
        }

    @GetMapping("/claimsN30")
    public Object claimsN30(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

        java.util.Map<String, Integer> countWords31(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/pluginN32")
    public Object pluginN32(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

        int clampValue33(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    @GetMapping("/langN34")
    public void langN34(@RequestParam String langN34, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN34);
        log.info("language changed to " + langN34);
    }

        java.util.List<Integer> mergeSorted35(java.util.List<Integer> a, java.util.List<Integer> b) {
            java.util.List<Integer> out = new java.util.ArrayList<>();
            int i = 0;
            int j = 0;
            while (i < a.size() && j < b.size()) {
                if (a.get(i) <= b.get(j)) {
                    out.add(a.get(i++));
                } else {
                    out.add(b.get(j++));
                }
            }
            while (i < a.size()) {
                out.add(a.get(i++));
            }
            while (j < b.size()) {
                out.add(b.get(j++));
            }
            return out;
        }

    @GetMapping("/search-safe")
    public Object searchSafeN36(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

    @GetMapping("/searchN37")
    public Object searchN37(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

        java.util.Map<String, Integer> countWords38(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.Map<String, Integer> countWords39(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/searchN40")
    public Object searchN40(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

    void downloadN41(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    @GetMapping("/grepN42")
    public boolean grepN42(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    void auditN43(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN43");
        log.info("login " + user + " " + password);
    }

    byte[] encryptN44(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

        java.util.List<Integer> mergeSorted45(java.util.List<Integer> a, java.util.List<Integer> b) {
            java.util.List<Integer> out = new java.util.ArrayList<>();
            int i = 0;
            int j = 0;
            while (i < a.size() && j < b.size()) {
                if (a.get(i) <= b.get(j)) {
                    out.add(a.get(i++));
                } else {
                    out.add(b.get(j++));
                }
            }
            while (i < a.size()) {
                out.add(a.get(i++));
            }
            while (j < b.size()) {
                out.add(b.get(j++));
            }
            return out;
        }

    @GetMapping("/searchN46")
    public Object searchN46(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

        java.util.Map<String, Integer> countWords47(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.Map<String, Integer> countWords48(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void pingN49(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("pingN49 -c 1 " + host);
    }

    @GetMapping("/pluginN50")
    public Object pluginN50(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

        double averageOf51(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        boolean isLeapYear52(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth52(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear52(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void fetchN53(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

    @GetMapping("/grepN54")
    public boolean grepN54(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    @GetMapping("/staffN55")
    public Object staffN55(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN55,dc=shop", "(uid=" + uid + ")", null);
    }

        String formatAmount56(long cents) {
            long whole = cents / 100;
            long rest = Math.abs(cents % 100);
            StringBuilder sb = new StringBuilder();
            sb.append(whole).append('.');
            if (rest < 10) {
                sb.append('0');
            }
            sb.append(rest);
            return sb.toString();
        }

    @GetMapping("/grep-safe")
    public boolean grepSafeN57(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

        boolean isLeapYear58(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth58(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear58(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        String formatAmount59(long cents) {
            long whole = cents / 100;
            long rest = Math.abs(cents % 100);
            StringBuilder sb = new StringBuilder();
            sb.append(whole).append('.');
            if (rest < 10) {
                sb.append('0');
            }
            sb.append(rest);
            return sb.toString();
        }

        java.util.Map<String, Integer> countWords60(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void pingN61(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("pingN61 -c 1 " + host);
    }

    @GetMapping("/grep-safe")
    public boolean grepSafeN62(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

    void fetchSafeN63(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        int clampValue64(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    Connection connectN65() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

        double averageOf66(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.List<Integer> mergeSorted67(java.util.List<Integer> a, java.util.List<Integer> b) {
            java.util.List<Integer> out = new java.util.ArrayList<>();
            int i = 0;
            int j = 0;
            while (i < a.size() && j < b.size()) {
                if (a.get(i) <= b.get(j)) {
                    out.add(a.get(i++));
                } else {
                    out.add(b.get(j++));
                }
            }
            while (i < a.size()) {
                out.add(a.get(i++));
            }
            while (j < b.size()) {
                out.add(b.get(j++));
            }
            return out;
        }

    @GetMapping("/staffN68")
    public Object staffN68(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN68,dc=shop", "(uid=" + uid + ")", null);
    }

        double averageOf69(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        String formatAmount70(long cents) {
            long whole = cents / 100;
            long rest = Math.abs(cents % 100);
            StringBuilder sb = new StringBuilder();
            sb.append(whole).append('.');
            if (rest < 10) {
                sb.append('0');
            }
            sb.append(rest);
            return sb.toString();
        }

        int clampValue71(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    Connection connectN72() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

    byte[] encryptSafeN73(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        return c.doFinal(data);
    }

    @GetMapping("/grepN74")
    public boolean grepN74(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    protected void doGetN75(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

    byte[] encryptBlockN76(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    void downloadSafeN77(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

        java.util.List<Integer> mergeSorted78(java.util.List<Integer> a, java.util.List<Integer> b) {
            java.util.List<Integer> out = new java.util.ArrayList<>();
            int i = 0;
            int j = 0;
            while (i < a.size() && j < b.size()) {
                if (a.get(i) <= b.get(j)) {
                    out.add(a.get(i++));
                } else {
                    out.add(b.get(j++));
                }
            }
            while (i < a.size()) {
                out.add(a.get(i++));
            }
            while (j < b.size()) {
                out.add(b.get(j++));
            }
            return out;
        }

    @GetMapping("/grep-safe")
    public boolean grepSafeN79(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

        double averageOf80(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        int clampValue81(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    String generateResetTokenN82() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

        java.util.Map<String, Integer> countWords83(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void backN84(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

        String formatAmount85(long cents) {
            long whole = cents / 100;
            long rest = Math.abs(cents % 100);
            StringBuilder sb = new StringBuilder();
            sb.append(whole).append('.');
            if (rest < 10) {
                sb.append('0');
            }
            sb.append(rest);
            return sb.toString();
        }

    Connection connectN86() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

    void backN87(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

    void fetchN88(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

        java.util.Map<String, Integer> countWords89(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.List<Integer> mergeSorted90(java.util.List<Integer> a, java.util.List<Integer> b) {
            java.util.List<Integer> out = new java.util.ArrayList<>();
            int i = 0;
            int j = 0;
            while (i < a.size() && j < b.size()) {
                if (a.get(i) <= b.get(j)) {
                    out.add(a.get(i++));
                } else {
                    out.add(b.get(j++));
                }
            }
            while (i < a.size()) {
                out.add(a.get(i++));
            }
            while (j < b.size()) {
                out.add(b.get(j++));
            }
            return out;
        }

    void auditN91(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN91");
        log.info("login " + user + " " + password);
    }

    @GetMapping("/langN92")
    public void langN92(@RequestParam String langN92, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN92);
        log.info("language changed to " + langN92);
    }

    byte[] encryptBlockN93(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    @GetMapping("/countN94")
    public Object countN94(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

    @GetMapping("/searchN95")
    public Object searchN95(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

    void pingSafeN96(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

    protected void doGetN97(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

    @GetMapping("/langN98")
    public void langN98(@RequestParam String langN98, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN98);
        log.info("language changed to " + langN98);
    }

        boolean isLeapYear99(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth99(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear99(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        int clampValue100(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        int clampValue101(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        java.util.Map<String, Integer> countWords102(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    String generateResetTokenN103() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

    @GetMapping("/pluginN104")
    public Object pluginN104(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

    byte[] encryptSafeN105(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        return c.doFinal(data);
    }

        java.util.List<Integer> mergeSorted106(java.util.List<Integer> a, java.util.List<Integer> b) {
            java.util.List<Integer> out = new java.util.ArrayList<>();
            int i = 0;
            int j = 0;
            while (i < a.size() && j < b.size()) {
                if (a.get(i) <= b.get(j)) {
                    out.add(a.get(i++));
                } else {
                    out.add(b.get(j++));
                }
            }
            while (i < a.size()) {
                out.add(a.get(i++));
            }
            while (j < b.size()) {
                out.add(b.get(j++));
            }
            return out;
        }

    void downloadN107(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    byte[] encryptBlockN108(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    byte[] encryptN109(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

        String formatAmount110(long cents) {
            long whole = cents / 100;
            long rest = Math.abs(cents % 100);
            StringBuilder sb = new StringBuilder();
            sb.append(whole).append('.');
            if (rest < 10) {
                sb.append('0');
            }
            sb.append(rest);
            return sb.toString();
        }

    void auditN111(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN111");
        log.info("login " + user + " " + password);
    }

    void pingN112(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("pingN112 -c 1 " + host);
    }

    void pingN113(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("pingN113 -c 1 " + host);
    }

    void restoreN114(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        int clampValue115(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        java.util.List<Integer> mergeSorted116(java.util.List<Integer> a, java.util.List<Integer> b) {
            java.util.List<Integer> out = new java.util.ArrayList<>();
            int i = 0;
            int j = 0;
            while (i < a.size() && j < b.size()) {
                if (a.get(i) <= b.get(j)) {
                    out.add(a.get(i++));
                } else {
                    out.add(b.get(j++));
                }
            }
            while (i < a.size()) {
                out.add(a.get(i++));
            }
            while (j < b.size()) {
                out.add(b.get(j++));
            }
            return out;
        }

    @GetMapping("/countN117")
    public Object countN117(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

        String formatAmount118(long cents) {
            long whole = cents / 100;
            long rest = Math.abs(cents % 100);
            StringBuilder sb = new StringBuilder();
            sb.append(whole).append('.');
            if (rest < 10) {
                sb.append('0');
            }
            sb.append(rest);
            return sb.toString();
        }

        int clampValue119(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    void fetchN120(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

    @GetMapping("/langN121")
    public void langN121(@RequestParam String langN121, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN121);
        log.info("language changed to " + langN121);
    }

    void restoreN122(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

    byte[] encryptN123(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

        boolean isLeapYear124(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth124(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear124(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    @GetMapping("/countN125")
    public Object countN125(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

        boolean isLeapYear126(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth126(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear126(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    @GetMapping("/staffN127")
    public Object staffN127(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN127,dc=shop", "(uid=" + uid + ")", null);
    }

    void fetchSafeN128(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        boolean isLeapYear129(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth129(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear129(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        String formatAmount130(long cents) {
            long whole = cents / 100;
            long rest = Math.abs(cents % 100);
            StringBuilder sb = new StringBuilder();
            sb.append(whole).append('.');
            if (rest < 10) {
                sb.append('0');
            }
            sb.append(rest);
            return sb.toString();
        }

        double averageOf131(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    @GetMapping("/claimsN132")
    public Object claimsN132(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    void backN133(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

        double averageOf134(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.Map<String, Integer> countWords135(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        double averageOf136(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        double averageOf137(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.Map<String, Integer> countWords138(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        int clampValue139(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

}
