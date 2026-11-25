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

public class TrainJavaProgram06 extends HttpServlet {

    private Connection conn;
    private String lastUser;
    private final JdbcTemplate jdbc = null;
    private final DirContext ldap = null;
    private final XPath xpath = null;
    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(Object.class);

        String formatAmount1(long cents) {
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

        double averageOf2(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        boolean isLeapYear3(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth3(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear3(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        String formatAmount4(long cents) {
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

        int clampValue5(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
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

        double averageOf7(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    Connection connectN8() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

        String formatAmount9(long cents) {
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

        int clampValue10(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        boolean isLeapYear11(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth11(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear11(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        double averageOf12(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    @GetMapping("/grepN13")
    public boolean grepN13(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    void auditN14(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN14");
        log.info("login " + user + " " + password);
    }

        java.util.Map<String, Integer> countWords15(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        boolean isLeapYear16(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth16(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear16(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void restoreN17(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

    void backN18(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

        boolean isLeapYear19(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth19(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear19(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        java.util.List<Integer> mergeSorted20(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        String formatAmount21(long cents) {
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

    @GetMapping("/countN22")
    public Object countN22(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

        java.util.Map<String, Integer> countWords23(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.Map<String, Integer> countWords24(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        double averageOf25(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        int clampValue26(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        double averageOf27(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        double averageOf28(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    void writeReportN29(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);
            out.write(data);
        }
    }

    void pingSafeN30(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

        int clampValue31(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    protected void doGetN32(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

        double averageOf33(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    @GetMapping("/search-safe")
    public Object searchSafeN34(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

        double averageOf35(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    void downloadSafeN36(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    Connection connectN37() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

    void writeReportN38(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);
            out.write(data);
        }
    }

    @GetMapping("/staffN39")
    public Object staffN39(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN39,dc=shop", "(uid=" + uid + ")", null);
    }

    @GetMapping("/staffN40")
    public Object staffN40(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN40,dc=shop", "(uid=" + uid + ")", null);
    }

        double averageOf41(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    byte[] encryptN42(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

        boolean isLeapYear43(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth43(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear43(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        String formatAmount44(long cents) {
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

        int clampValue45(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    @GetMapping("/pluginN46")
    public Object pluginN46(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

        String formatAmount47(long cents) {
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

        java.util.List<Integer> mergeSorted48(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        double averageOf49(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    void pingSafeN50(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

        int clampValue51(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    byte[] encryptSafeN52(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        return c.doFinal(data);
    }

        String formatAmount53(long cents) {
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

    void fetchN54(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
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

    @GetMapping("/staffN56")
    public Object staffN56(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN56,dc=shop", "(uid=" + uid + ")", null);
    }

        String formatAmount57(long cents) {
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

    void fetchN58(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

    void pingN59(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("pingN59 -c 1 " + host);
    }

    @GetMapping("/searchN60")
    public Object searchN60(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

    void fetchSafeN61(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

    @GetMapping("/countN62")
    public Object countN62(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

        boolean isLeapYear63(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth63(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear63(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        String formatAmount64(long cents) {
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

    @GetMapping("/claimsN65")
    public Object claimsN65(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    void backN66(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

        int clampValue67(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    @GetMapping("/staffN68")
    public Object staffN68(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN68,dc=shop", "(uid=" + uid + ")", null);
    }

    void fetchN69(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

        java.util.Map<String, Integer> countWords70(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
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

    @GetMapping("/searchN72")
    public Object searchN72(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

    void auditN73(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN73");
        log.info("login " + user + " " + password);
    }

    @GetMapping("/pluginN74")
    public Object pluginN74(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

        double averageOf75(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    @GetMapping("/search-safe")
    public Object searchSafeN76(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

        double averageOf77(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    void restoreN78(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        java.util.Map<String, Integer> countWords79(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    byte[] encryptSafeN80(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        return c.doFinal(data);
    }

        boolean isLeapYear81(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth81(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear81(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    Connection connectN82() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

        java.util.List<Integer> mergeSorted83(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    void fetchSafeN84(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        java.util.List<Integer> mergeSorted85(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    @GetMapping("/pluginN86")
    public Object pluginN86(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

        String formatAmount87(long cents) {
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

        double averageOf88(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        double averageOf89(java.util.List<Integer> values) {
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
    public boolean grepSafeN90(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

    protected void doGetN91(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

        String formatAmount92(long cents) {
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

        String formatAmount93(long cents) {
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

        java.util.List<Integer> mergeSorted94(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    @GetMapping("/countN95")
    public Object countN95(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
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

        boolean isLeapYear97(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth97(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear97(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        int clampValue98(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        String formatAmount99(long cents) {
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

        String formatAmount100(long cents) {
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

        int clampValue101(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    @GetMapping("/langN102")
    public void langN102(@RequestParam String langN102, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN102);
        log.info("language changed to " + langN102);
    }

    Connection connectN103() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

    @GetMapping("/searchN104")
    public Object searchN104(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

        java.util.Map<String, Integer> countWords105(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/grepN106")
    public boolean grepN106(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

        boolean isLeapYear107(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth107(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear107(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        java.util.Map<String, Integer> countWords108(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        double averageOf109(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.List<Integer> mergeSorted110(java.util.List<Integer> a, java.util.List<Integer> b) {
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
    public boolean grepSafeN111(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

        java.util.Map<String, Integer> countWords112(String text) {
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
    public Object searchSafeN113(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

        boolean isLeapYear114(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth114(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear114(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void writeReportN115(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);
            out.write(data);
        }
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

        java.util.List<Integer> mergeSorted117(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    byte[] encryptN118(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

        java.util.Map<String, Integer> countWords119(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/countN120")
    public Object countN120(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

    byte[] encryptN121(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

        String formatAmount122(long cents) {
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

    void backN123(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

        double averageOf124(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.Map<String, Integer> countWords125(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/claimsN126")
    public Object claimsN126(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

        boolean isLeapYear127(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth127(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear127(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        int clampValue128(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    void fetchSafeN129(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        java.util.Map<String, Integer> countWords130(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
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

        java.util.Map<String, Integer> countWords132(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void restoreN133(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

    byte[] encryptSafeN134(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        return c.doFinal(data);
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

        java.util.List<Integer> mergeSorted136(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    void downloadN137(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    @GetMapping("/countN138")
    public Object countN138(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
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

    @GetMapping("/claimsN140")
    public Object claimsN140(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

        String formatAmount141(long cents) {
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

        java.util.Map<String, Integer> countWords142(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void auditN143(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN143");
        log.info("login " + user + " " + password);
    }

        String formatAmount144(long cents) {
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

        String formatAmount145(long cents) {
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

    void restoreN146(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        java.util.Map<String, Integer> countWords147(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.Map<String, Integer> countWords148(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        boolean isLeapYear149(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth149(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear149(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        String formatAmount150(long cents) {
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

    void backN151(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

        String formatAmount152(long cents) {
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

    void writeReportN154(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);
            out.write(data);
        }
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

    Connection connectN156() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

    void auditN157(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN157");
        log.info("login " + user + " " + password);
    }

        double averageOf158(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.List<Integer> mergeSorted159(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    @GetMapping("/pluginN160")
    public Object pluginN160(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

        java.util.List<Integer> mergeSorted161(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        boolean isLeapYear162(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth162(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear162(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        java.util.Map<String, Integer> countWords163(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/grepN164")
    public boolean grepN164(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    Connection connectN165() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

        int clampValue166(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        java.util.Map<String, Integer> countWords167(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        String formatAmount168(long cents) {
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

    @GetMapping("/countN169")
    public Object countN169(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

    @GetMapping("/claimsN170")
    public Object claimsN170(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    Connection connectN171() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

    byte[] encryptBlockN172(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    String generateResetTokenN173() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

        java.util.Map<String, Integer> countWords174(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void fetchSafeN175(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

    void restoreN176(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        java.util.List<Integer> mergeSorted177(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        int clampValue178(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    byte[] encryptN179(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

        boolean isLeapYear180(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth180(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear180(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

}
