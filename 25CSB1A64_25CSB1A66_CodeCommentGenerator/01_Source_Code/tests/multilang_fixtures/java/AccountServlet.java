package com.example.bank;

import java.io.*;
import java.net.URL;
import java.security.MessageDigest;
import java.sql.*;
import java.util.Random;
import javax.crypto.Cipher;
import javax.servlet.http.*;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

/** Account portal servlet: each method below is either vulnerable (marked expect) or a safe twin. */
public class AccountServlet extends HttpServlet {

    private Connection conn;
    private String lastUser;                     // shared across requests

    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        lastUser = id;                                                        // expect: SEC063
        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT * FROM accounts WHERE id = '" + id + "'");   // expect: SEC005
            resp.getWriter().println("<p>Account " + id + "</p>");               // expect: SEC014
        } catch (SQLException e) {                                              // expect: SEC049
        }
    }

    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String id = req.getParameter("id");
        try {
            PreparedStatement ps = conn.prepareStatement("SELECT * FROM accounts WHERE id = ?");
            ps.setString(1, id);
            ps.executeQuery();
        } catch (SQLException e) {
            throw new IOException(e);
        }
        resp.getWriter().println(org.owasp.encoder.Encode.forHtml(id));
    }

    void ping(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        Runtime.getRuntime().exec("ping -c 1 " + host);                        // expect: SEC002
    }

    void pingSafe(HttpServletRequest req) throws IOException {
        String host = req.getParameter("host");
        if (!host.matches("[a-z0-9.]+")) {
            return;
        }
        Runtime.getRuntime().exec(new String[]{"ping", "-c", "1", host});
    }

    void download(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("file");
        FileInputStream in = new FileInputStream("/srv/reports/" + name);     // expect: SEC013
        in.close();
    }

    void downloadSafe(HttpServletRequest req) throws IOException {
        String name = org.apache.commons.io.FilenameUtils.getName(req.getParameter("file"));
        FileInputStream in = new FileInputStream("/srv/reports/" + name);
        in.close();
    }

    void fetch(HttpServletRequest req) throws IOException {
        String target = req.getParameter("url");
        new URL(target).openStream();                                          // expect: SEC016
    }

    void fetchSafe(HttpServletRequest req) throws IOException {
        String item = req.getParameter("item");
        new URL("https://api.example-bank.com/items/" + item).openStream();
    }

    void back(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.sendRedirect(req.getParameter("next"));                           // expect: SEC017
    }

    void restore(HttpServletRequest req) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(req.getInputStream());
        Object state = ois.readObject();                                       // expect: SEC009
    }

    void remember(HttpServletRequest req) {
        req.getSession().setAttribute("user", req.getParameter("user"));       // expect: SEC028
    }

    String passwordHash(String password) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");                   // expect: SEC004
        return new String(md.digest(password.getBytes()));
    }

    String passwordHashSafe(String password) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        return new String(md.digest(password.getBytes()));
    }

    byte[] encrypt(byte[] key, byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");                 // expect: SEC033
        return c.doFinal(data);
    }

    byte[] encryptBlock(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");                 // expect: SEC034
        return c.doFinal(data);
    }

    byte[] encryptSafe(byte[] data) throws Exception {
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        return c.doFinal(data);
    }

    String generateResetToken() {
        Random r = new Random();                                                // expect: SEC011
        return Long.toHexString(r.nextLong());
    }

    Connection connect() throws SQLException {
        return DriverManager.getConnection("jdbc:mysql://db/bank", "app", "S3cr3tPass!");   // expect: SEC003
    }

    void parseXml(InputStream in) throws Exception {
        DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();        // expect: SEC018
        DocumentBuilder b = f.newDocumentBuilder();
        b.parse(in);
    }

    void parseXmlSafe(InputStream in) throws Exception {
        DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
        f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        f.newDocumentBuilder().parse(in);
    }

    void writeReport(String path, byte[] data) throws IOException {
        File f = new File(path);
        if (!f.exists()) {
            FileOutputStream out = new FileOutputStream(f);                     // expect: SEC059
            out.write(data);
        }
    }

    void audit(String user, String password) {
        java.util.logging.Logger log = java.util.logging.Logger.getLogger("audit");
        log.info("login " + user + " " + password);                             // expect: SEC050
    }
}
