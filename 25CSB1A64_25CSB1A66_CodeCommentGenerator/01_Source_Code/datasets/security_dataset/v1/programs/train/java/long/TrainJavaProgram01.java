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

public class TrainJavaProgram01 extends HttpServlet {

    private Connection conn;
    private String lastUser;
    private final JdbcTemplate jdbc = null;
    private final DirContext ldap = null;
    private final XPath xpath = null;
    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(Object.class);

        int clampValue1(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    void restoreN2(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
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

        java.util.Map<String, Integer> countWords6(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        boolean isLeapYear7(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth7(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear7(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
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

    Connection connectN9() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

    void pingSafeN10(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

    @GetMapping("/grep-safe")
    public boolean grepSafeN11(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
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

    void restoreN14(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        String formatAmount15(long cents) {
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

    @GetMapping("/claimsN16")
    public Object claimsN16(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

        java.util.Map<String, Integer> countWords17(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
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

    byte[] encryptN19(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

    void pingN20(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("pingN20 -c 1 " + host);
    }

        java.util.List<Integer> mergeSorted21(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    @GetMapping("/pluginN22")
    public Object pluginN22(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

    @GetMapping("/pluginN23")
    public Object pluginN23(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

    @GetMapping("/searchN24")
    public Object searchN24(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

        java.util.List<Integer> mergeSorted25(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    @GetMapping("/langN26")
    public void langN26(@RequestParam String langN26, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN26);
        log.info("language changed to " + langN26);
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

    void pingSafeN28(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
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

        int clampValue30(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
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

        double averageOf32(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
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

        java.util.List<Integer> mergeSorted34(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    void downloadN35(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    byte[] encryptSafeN36(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        return c.doFinal(data);
    }

    Connection connectN37() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");
    }

        String formatAmount38(long cents) {
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

    String generateResetTokenN40() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
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

    @GetMapping("/staffN42")
    public Object staffN42(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN42,dc=shop", "(uid=" + uid + ")", null);
    }

    @GetMapping("/claimsN43")
    public Object claimsN43(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    void pingSafeN44(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

        String formatAmount45(long cents) {
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

    byte[] encryptN46(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
        return c.doFinal(data);
    }

        boolean isLeapYear47(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth47(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear47(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void downloadN48(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

        String formatAmount49(long cents) {
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

        java.util.List<Integer> mergeSorted50(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    @GetMapping("/grepN51")
    public boolean grepN51(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

        java.util.Map<String, Integer> countWords52(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.List<Integer> mergeSorted53(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    byte[] encryptSafeN54(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        return c.doFinal(data);
    }

    @GetMapping("/countN55")
    public Object countN55(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

        boolean isLeapYear56(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth56(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear56(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    @GetMapping("/pluginN57")
    public Object pluginN57(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

        int clampValue58(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    protected void doGetN59(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

        java.util.List<Integer> mergeSorted60(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    @GetMapping("/countN61")
    public Object countN61(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

        String formatAmount62(long cents) {
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

    void restoreN63(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        java.util.List<Integer> mergeSorted64(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        java.util.List<Integer> mergeSorted65(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    void fetchN66(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

        double averageOf67(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    void restoreN68(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        int clampValue69(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
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

    @GetMapping("/grep-safe")
    public boolean grepSafeN71(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

        int clampValue72(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    void fetchSafeN73(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

    void pingSafeN74(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

    void pingN75(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("pingN75 -c 1 " + host);
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

        boolean isLeapYear78(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth78(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear78(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void backN79(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

    void downloadSafeN80(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    void backN81(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

        String formatAmount82(long cents) {
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

        boolean isLeapYear83(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth83(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear83(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        String formatAmount84(long cents) {
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

    @GetMapping("/searchN85")
    public Object searchN85(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = '" + customer + "'");
    }

        boolean isLeapYear86(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth86(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear86(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void downloadSafeN87(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    @GetMapping("/langN88")
    public void langN88(@RequestParam String langN88, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN88);
        log.info("language changed to " + langN88);
    }

    void fetchN89(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

        double averageOf90(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

        double averageOf91(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    protected void doGetN92(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

    void fetchN93(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();
    }

        int clampValue94(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        java.util.Map<String, Integer> countWords95(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

    void fetchSafeN96(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

        String formatAmount97(long cents) {
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

        java.util.List<Integer> mergeSorted98(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    void restoreN99(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

    void backN100(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));
    }

        double averageOf101(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    byte[] encryptBlockN102(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
        return c.doFinal(data);
    }

        String formatAmount103(long cents) {
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

    void restoreN104(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

    @GetMapping("/grepN105")
    public boolean grepN105(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

        double averageOf106(java.util.List<Integer> values) {
            if (values.isEmpty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return (double) total / values.size();
        }

    String generateResetTokenN107() {
        Random r = new Random();
        return Long.toHexString(r.nextLong());
    }

    @GetMapping("/staffN108")
    public Object staffN108(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN108,dc=shop", "(uid=" + uid + ")", null);
    }

        java.util.Map<String, Integer> countWords109(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.Map<String, Integer> countWords110(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        int clampValue111(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        int clampValue112(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    @GetMapping("/claimsN113")
    public Object claimsN113(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

        int clampValue114(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

        String formatAmount115(long cents) {
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

    void downloadN116(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

        java.util.Map<String, Integer> countWords117(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
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

    void auditN119(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN119");
        log.info("login " + user + " " + password);
    }

    void pingSafeN120(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

    @GetMapping("/pluginN121")
    public Object pluginN121(@RequestParam String name) throws Exception {
        return Class.forName("com.example.plugins." + name).getDeclaredConstructor().newInstance();
    }

        int clampValue122(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
        }

    void fetchSafeN123(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
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

    void auditN127(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN127");
        log.info("login " + user + " " + password);
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

        int clampValue129(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            if (value > high) {
                return high;
            }
            return value;
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

    void fetchSafeN131(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
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

        java.util.List<Integer> mergeSorted133(java.util.List<Integer> a, java.util.List<Integer> b) {
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

        java.util.List<Integer> mergeSorted134(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    @GetMapping("/claimsN135")
    public Object claimsN135(@RequestHeader("Authorization") String token) {
        return Jwts.parser().setSigningKey("k").parse(token);
    }

    @GetMapping("/langN136")
    public void langN136(@RequestParam String langN136, HttpServletResponse resp) {
        resp.setHeader("Content-Language", langN136);
        log.info("language changed to " + langN136);
    }

    void auditN137(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("auditN137");
        log.info("login " + user + " " + password);
    }

        java.util.List<Integer> mergeSorted138(java.util.List<Integer> a, java.util.List<Integer> b) {
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
    public boolean grepSafeN139(@RequestParam String pattern) {
        return Pattern.compile(Pattern.quote(pattern)).matcher("order notes").find();
    }

        java.util.Map<String, Integer> countWords140(String text) {
            java.util.Map<String, Integer> counts = new java.util.HashMap<>();
            for (String word : text.toLowerCase().split("\\s+")) {
                if (word.isEmpty()) {
                    continue;
                }
                counts.merge(word, 1, Integer::sum);
            }
            return counts;
        }

        java.util.Map<String, Integer> countWords141(String text) {
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
    public Object searchSafeN142(@RequestParam String customer) {
        return jdbc.queryForList("SELECT * FROM orders WHERE customer = ?", customer);
    }

    @GetMapping("/staffN143")
    public Object staffN143(@RequestParam String uid) throws Exception {
        return ldap.search("ou=staffN143,dc=shop", "(uid=" + uid + ")", null);
    }

    void restoreN144(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();
    }

        boolean isLeapYear145(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth145(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear145(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

        java.util.List<Integer> mergeSorted146(java.util.List<Integer> a, java.util.List<Integer> b) {
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

    @GetMapping("/grepN148")
    public boolean grepN148(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    @GetMapping("/grepN149")
    public boolean grepN149(@RequestParam String pattern) {
        return Pattern.compile(pattern).matcher("order notes").find();
    }

    protected void doGetN150(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");
            resp.getWriter().println("<p>Account " + id + "</p>");
        } catch (SQLException e) {
        }
    }

        boolean isLeapYear151(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth151(int year, int month) {
            switch (month) {
                case 2:
                    return isLeapYear151(year) ? 29 : 28;
                case 4: case 6: case 9: case 11:
                    return 30;
                default:
                    return 31;
            }
        }

    void downloadSafeN152(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    @GetMapping("/countN153")
    public Object countN153(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
    }

        String formatAmount154(long cents) {
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

    @GetMapping("/countN156")
    public Object countN156(@RequestParam String status) {
        if (!status.equals("open")) {
            return 0;
        }
        return jdbc.queryForList("SELECT * FROM orders WHERE status = '" + status + "'");
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

}
