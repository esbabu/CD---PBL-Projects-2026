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

public class TrainJavaProgram07 extends HttpServlet {

    private Connection conn;
    private String lastUser;
    private final JdbcTemplate jdbc = null;
    private final DirContext ldap = null;
    private final XPath xpath = null;
    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(Object.class);

    byte[] encryptBlockN1(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

        String formatAmount2(long cents) {
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

        java.util.Map<String, Integer> countWords3(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void restoreN4(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        String formatAmount5(long cents) {
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

        String formatAmount6(long cents) {
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

        java.util.List<Integer> mergeSorted7(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        double averageOf8(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    @GetMapping("/grep-safe")
    public boolean grepSafeN9(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

    @GetMapping("/langN10")
    public void langN10(@RequestParam String langN10, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN10);
        log.info("language changed to " + langN10);
    }

    @GetMapping("/countN11")
    public Object countN11(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

        java.util.List<Integer> mergeSorted12(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    Connection connectN13() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

        int clampValue14(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        boolean isLeapYear15(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth15(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear15(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void fetchSafeN16(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        int clampValue17(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        String formatAmount18(long cents) {
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

    @GetMapping("/claimsN19")
    public Object claimsN19(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    void fetchSafeN20(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        double averageOf21(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.List<Integer> mergeSorted22(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    void backN24(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

    @GetMapping("/grepN25")
    public boolean grepN25(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

        double averageOf26(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    void auditN27(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN27");
        log.info("login " + user + " " + password);
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

    String generateResetTokenN29() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

        String formatAmount30(long cents) {
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
    public boolean grepSafeN31(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

    byte[] encryptBlockN32(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    @GetMapping("/searchN33")
    public Object searchN33(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

        String formatAmount34(long cents) {
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

        String formatAmount35(long cents) {
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

    String generateResetTokenN36() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

        String formatAmount37(long cents) {
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

        java.util.List<Integer> mergeSorted38(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        boolean isLeapYear39(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth39(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear39(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void downloadN40(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

        java.util.Map<String, Integer> countWords41(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/countN42")
    public Object countN42(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

        java.util.Map<String, Integer> countWords43(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.List<Integer> mergeSorted44(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        boolean isLeapYear45(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth45(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear45(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void backN46(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

    @GetMapping("/staffN47")
    public Object staffN47(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN47,dc=shop", "(uid=" + uid + ")", null);
    }

    void downloadSafeN48(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    void fetchSafeN49(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

    @GetMapping("/claimsN50")
    public Object claimsN50(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    byte[] encryptBlockN51(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    @GetMapping("/langN52")
    public void langN52(@RequestParam String langN52, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN52);
        log.info("language changed to " + langN52);
    }

        double averageOf53(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.List<Integer> mergeSorted54(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        java.util.Map<String, Integer> countWords55(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void auditN56(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN56");
        log.info("login " + user + " " + password);
    }

    void auditN57(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN57");
        log.info("login " + user + " " + password);
    }

    void writeReportN58(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);
            out.write(data);
        }
    }

        java.util.Map<String, Integer> countWords59(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void downloadSafeN60(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

        int clampValue61(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    byte[] encryptBlockN62(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    byte[] encryptBlockN63(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    void fetchSafeN64(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        String formatAmount65(long cents) {
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

    String generateResetTokenN66() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

    @GetMapping("/searchN67")
    public Object searchN67(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

    byte[] encryptBlockN68(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

        java.util.List<Integer> mergeSorted69(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        int clampValue70(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        double averageOf71(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.List<Integer> mergeSorted72(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    void pingSafeN73(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

    @GetMapping("/search-safe")
    public Object searchSafeN74(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

    void writeReportN75(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);
            out.write(data);
        }
    }

    @GetMapping("/pluginN76")
    public Object pluginN76(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

    @GetMapping("/grepN77")
    public boolean grepN77(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    byte[] encryptBlockN78(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
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

        String formatAmount81(long cents) {
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

    void downloadSafeN82(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    void writeReportN83(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);
            out.write(data);
        }
    }

    void fetchN84(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

    void auditN85(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN85");
        log.info("login " + user + " " + password);
    }

        String formatAmount86(long cents) {
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

    byte[] encryptBlockN87(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    void auditN88(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN88");
        log.info("login " + user + " " + password);
    }

        String formatAmount89(long cents) {
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

        boolean isLeapYear90(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth90(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear90(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        boolean isLeapYear91(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth91(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear91(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    String generateResetTokenN92() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

    protected void doGetN93(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

    String generateResetTokenN94() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

        double averageOf95(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.List<Integer> mergeSorted96(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    String generateResetTokenN97() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

    @GetMapping("/search-safe")
    public Object searchSafeN98(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

        double averageOf99(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        boolean isLeapYear100(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth100(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear100(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        java.util.List<Integer> mergeSorted101(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        double averageOf102(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.List<Integer> mergeSorted103(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    @GetMapping("/langN104")
    public void langN104(@RequestParam String langN104, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN104);
        log.info("language changed to " + langN104);
    }

    Connection connectN105() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

    @GetMapping("/search-safe")
    public Object searchSafeN106(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

    protected void doGetN107(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

    @GetMapping("/claimsN108")
    public Object claimsN108(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    byte[] encryptN109(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

    @GetMapping("/search-safe")
    public Object searchSafeN110(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

    @GetMapping("/grepN111")
    public boolean grepN111(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    @GetMapping("/grep-safe")
    public boolean grepSafeN112(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

    @GetMapping("/claimsN113")
    public Object claimsN113(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    void restoreN114(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        boolean isLeapYear115(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth115(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear115(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    @GetMapping("/staffN116")
    public Object staffN116(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN116,dc=shop", "(uid=" + uid + ")", null);
    }

        String formatAmount117(long cents) {
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

        double averageOf118(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        String formatAmount119(long cents) {
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

        java.util.List<Integer> mergeSorted120(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    void auditN121(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN121");
        log.info("login " + user + " " + password);
    }

        java.util.Map<String, Integer> countWords122(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.List<Integer> mergeSorted123(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    byte[] encryptN124(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

    void fetchN125(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

        java.util.List<Integer> mergeSorted126(java.util.List<Integer> a, java.util.List<Integer> b) {
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
    public Object searchSafeN127(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

        java.util.Map<String, Integer> countWords128(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void downloadSafeN129(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

        boolean isLeapYear130(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth130(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear130(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        int clampValue131(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        java.util.List<Integer> mergeSorted132(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    protected void doGetN133(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

    @GetMapping("/searchN134")
    public Object searchN134(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

        double averageOf135(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    @GetMapping("/claimsN136")
    public Object claimsN136(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
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

    @GetMapping("/grep-safe")
    public boolean grepSafeN138(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

        boolean isLeapYear139(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth139(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear139(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        int clampValue140(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    @GetMapping("/langN141")
    public void langN141(@RequestParam String langN141, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN141);
        log.info("language changed to " + langN141);
    }

    @GetMapping("/grepN142")
    public boolean grepN142(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    @GetMapping("/grepN143")
    public boolean grepN143(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    @GetMapping("/grepN144")
    public boolean grepN144(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    @GetMapping("/countN145")
    public Object countN145(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

    void auditN146(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN146");
        log.info("login " + user + " " + password);
    }

    void restoreN147(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

    byte[] encryptBlockN148(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    byte[] encryptN149(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

        int clampValue150(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    Connection connectN151() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

        java.util.List<Integer> mergeSorted152(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        String formatAmount153(long cents) {
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

        java.util.Map<String, Integer> countWords154(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        String formatAmount155(long cents) {
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

        java.util.List<Integer> mergeSorted156(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        int clampValue157(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    void downloadN158(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

}
