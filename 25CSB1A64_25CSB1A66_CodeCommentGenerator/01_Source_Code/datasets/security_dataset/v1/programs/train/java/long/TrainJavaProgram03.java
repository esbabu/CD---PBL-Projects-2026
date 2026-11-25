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

public class TrainJavaProgram03 extends HttpServlet {

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

    @GetMapping("/grepN2")
    public boolean grepN2(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
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

        java.util.Map<String, Integer> countWords4(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void auditN5(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN5");
        log.info("login " + user + " " + password);
    }

        int clampValue6(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    @GetMapping("/searchN7")
    public Object searchN7(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
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

        double averageOf9(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    byte[] encryptBlockN10(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    @GetMapping("/searchN11")
    public Object searchN11(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
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

        String formatAmount13(long cents) {
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

    byte[] encryptBlockN14(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
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

        int clampValue16(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
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

    void fetchSafeN19(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        double averageOf20(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
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

    void backN22(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

    void restoreN23(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        java.util.List<Integer> mergeSorted24(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    void restoreN25(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
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

    void backN28(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

        boolean isLeapYear29(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth29(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear29(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        java.util.Map<String, Integer> countWords30(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        String formatAmount31(long cents) {
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

        java.util.Map<String, Integer> countWords32(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.List<Integer> mergeSorted33(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    protected void doGetN34(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

    void pingN35(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("pingN35 -c 1 " + host);
    }

        double averageOf36(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    void pingN37(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("pingN37 -c 1 " + host);
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

    void pingN39(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("pingN39 -c 1 " + host);
    }

    byte[] encryptSafeN40(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        return c.doFinal(data);
    }

    void pingSafeN41(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

        boolean isLeapYear42(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth42(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear42(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
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

    void downloadN44(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
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

        java.util.Map<String, Integer> countWords46(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    byte[] encryptBlockN47(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

        boolean isLeapYear48(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth48(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear48(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    String generateResetTokenN49() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

    @GetMapping("/search-safe")
    public Object searchSafeN50(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
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

        int clampValue53(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        java.util.Map<String, Integer> countWords54(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void auditN55(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN55");
        log.info("login " + user + " " + password);
    }

    @GetMapping("/grepN56")
    public boolean grepN56(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

        boolean isLeapYear57(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth57(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear57(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
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

    void pingSafeN60(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

    void fetchN61(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

        double averageOf62(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        int clampValue63(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        boolean isLeapYear64(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth64(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear64(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        int clampValue65(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
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

    @GetMapping("/staffN67")
    public Object staffN67(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN67,dc=shop", "(uid=" + uid + ")", null);
    }

        double averageOf68(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    protected void doGetN69(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

    String generateResetTokenN70() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

        String formatAmount71(long cents) {
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

        java.util.Map<String, Integer> countWords72(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/searchN73")
    public Object searchN73(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

        java.util.Map<String, Integer> countWords74(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void fetchSafeN75(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        java.util.Map<String, Integer> countWords76(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.List<Integer> mergeSorted77(java.util.List<Integer> a, java.util.List<Integer> b) {
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
    public Object searchSafeN78(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
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

    @GetMapping("/staffN80")
    public Object staffN80(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN80,dc=shop", "(uid=" + uid + ")", null);
    }

        double averageOf81(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    void backN82(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
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

        boolean isLeapYear84(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth84(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear84(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    @GetMapping("/staffN85")
    public Object staffN85(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN85,dc=shop", "(uid=" + uid + ")", null);
    }

    void fetchN86(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

    void downloadN87(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    void restoreN88(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        int clampValue89(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    void auditN90(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN90");
        log.info("login " + user + " " + password);
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

    @GetMapping("/grep-safe")
    public boolean grepSafeN92(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

    byte[] encryptBlockN93(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    void downloadN94(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    void writeReportN95(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);
            out.write(data);
        }
    }

        int clampValue96(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    @GetMapping("/search-safe")
    public Object searchSafeN97(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

    @GetMapping("/grep-safe")
    public boolean grepSafeN98(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

    byte[] encryptBlockN99(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    byte[] encryptSafeN100(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        return c.doFinal(data);
    }

        String formatAmount101(long cents) {
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

    @GetMapping("/grep-safe")
    public boolean grepSafeN103(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

    byte[] encryptN104(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

    void auditN105(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN105");
        log.info("login " + user + " " + password);
    }

    @GetMapping("/langN106")
    public void langN106(@RequestParam String langN106, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN106);
        log.info("language changed to " + langN106);
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

    byte[] encryptBlockN108(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

    String generateResetTokenN109() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

        int clampValue110(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    void pingSafeN111(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

    void downloadSafeN112(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

        boolean isLeapYear113(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth113(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear113(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void fetchN114(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

    void backN115(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

    @GetMapping("/countN116")
    public Object countN116(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

        boolean isLeapYear117(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth117(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear117(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    @GetMapping("/countN118")
    public Object countN118(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

    void fetchSafeN119(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        boolean isLeapYear120(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth120(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear120(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    @GetMapping("/grepN121")
    public boolean grepN121(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

        boolean isLeapYear122(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth122(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear122(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    @GetMapping("/searchN123")
    public Object searchN123(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

        int clampValue124(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        boolean isLeapYear125(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth125(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear125(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        java.util.Map<String, Integer> countWords126(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    @GetMapping("/grepN127")
    public boolean grepN127(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
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

        java.util.Map<String, Integer> countWords129(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        double averageOf130(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        java.util.List<Integer> mergeSorted131(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        String formatAmount133(long cents) {
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

    void writeReportN134(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);
            out.write(data);
        }
    }

    void downloadSafeN135(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    void auditN136(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN136");
        log.info("login " + user + " " + password);
    }

    @GetMapping("/pluginN137")
    public Object pluginN137(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

        double averageOf138(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    @GetMapping("/staffN139")
    public Object staffN139(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN139,dc=shop", "(uid=" + uid + ")", null);
    }

    byte[] encryptN140(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

    void pingSafeN141(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

    @GetMapping("/claimsN142")
    public Object claimsN142(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    void restoreN143(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

    void downloadSafeN144(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    void restoreN145(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

    @GetMapping("/claimsN146")
    public Object claimsN146(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

        double averageOf147(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    @GetMapping("/staffN148")
    public Object staffN148(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN148,dc=shop", "(uid=" + uid + ")", null);
    }

    void downloadSafeN149(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

        double averageOf150(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        String formatAmount151(long cents) {
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

    void fetchSafeN152(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

    void writeReportN153(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);
            out.write(data);
        }
    }

    Connection connectN154() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

        java.util.Map<String, Integer> countWords155(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void fetchN156(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

    void downloadN157(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

        int clampValue158(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        String formatAmount159(long cents) {
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

    void backN160(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

    @GetMapping("/claimsN161")
    public Object claimsN161(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    @GetMapping("/grepN162")
    public boolean grepN162(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    @GetMapping("/claimsN163")
    public Object claimsN163(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    void downloadSafeN164(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    @GetMapping("/countN165")
    public Object countN165(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

    protected void doGetN166(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

        int clampValue167(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    void auditN168(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN168");
        log.info("login " + user + " " + password);
    }

    Connection connectN169() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

    void fetchN170(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

}
