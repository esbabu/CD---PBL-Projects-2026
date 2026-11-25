using System;
using System.Data.SqlClient;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Runtime.Serialization.Formatters.Binary;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Xml;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace Shop.Web.Controllers
{
    [ApiController]
    [Authorize]
    [Route("reports")]
    public class ReportsController : Controller
    {
        private static int lastReportId;
        private readonly SqlConnection _conn;
        private readonly HttpClient _http;
        private readonly ILogger<ReportsController> _logger;

        public ReportsController(SqlConnection conn, HttpClient http, ILogger<ReportsController> logger)
        {
            _conn = conn;
            _http = http;
            _logger = logger;
        }

        [HttpGet("by-customer")]
        public IActionResult ByCustomer([FromQuery] string customer)
        {
            var cmd = new SqlCommand("SELECT * FROM Reports WHERE Customer = '" + customer + "'", _conn);   // expect: SEC005
            return Ok(cmd.ExecuteScalar());
        }

        [HttpGet("by-customer-safe")]
        public IActionResult ByCustomerSafe([FromQuery] string customer)
        {
            var cmd = new SqlCommand("SELECT * FROM Reports WHERE Customer = @c", _conn);
            cmd.Parameters.AddWithValue("@c", customer);
            return Ok(cmd.ExecuteScalar());
        }

        [HttpGet("export")]
        public IActionResult Export([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);                                       // expect: SEC002
            return Ok();
        }

        [HttpGet("file")]
        public IActionResult ReadFile([FromQuery] string name)
        {
            string text = System.IO.File.ReadAllText(Path.Combine("/srv/reports", name));                      // expect: SEC013
            return Content(text);
        }

        [HttpGet("file-safe")]
        public IActionResult ReadFileSafe([FromQuery] string name)
        {
            string text = System.IO.File.ReadAllText(Path.Combine("/srv/reports", Path.GetFileName(name)));
            return Ok(text.Length);
        }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> Proxy([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);                                                     // expect: SEC016
            return Ok(body.Length);
        }

        [HttpGet("go")]
        public IActionResult Go([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);                                                                         // expect: SEC017
        }

        [HttpPost("import")]
        public IActionResult Import()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);                                                // expect: SEC009
            return Ok();
        }

        [HttpGet("search")]
        public IActionResult Search([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);                                              // expect: SEC024
            _logger.LogInformation("search for " + pattern);                                                     // expect: SEC022
            return Ok(hit);
        }

        [HttpGet("search-safe")]
        public IActionResult SearchSafe([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

        [AllowAnonymous]
        [HttpDelete("{id}")]
        public IActionResult Delete(int id)                                                                     // expect: SEC061
        {
            lastReportId = id;                                                                                  // expect: SEC063
            return NoContent();
        }

        public string Checksum(byte[] data)
        {
            using var md5 = MD5.Create();                                                                       // expect: SEC004
            return Convert.ToBase64String(md5.ComputeHash(data));
        }

        public string ChecksumSafe(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        public byte[] Encrypt(byte[] data)
        {
            using var des = DES.Create();                                                                       // expect: SEC033
            return des.CreateEncryptor().TransformFinalBlock(data, 0, data.Length);
        }

        public XmlDocument LoadXml(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };                                   // expect: SEC018
            doc.LoadXml(xml);
            return doc;
        }

        public void TrustEverything(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;             // expect: SEC031
        }

        public string ConnectionString()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";                                  // expect: SEC003
        }

        public void SetCookie(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true }); // expect: SEC044
        }

        public int ParseCount(string text)
        {
            try
            {
                return int.Parse(text);
            }
            catch (FormatException)
            {                                                                                                   // (not empty)
                return 0;
            }
        }
    }
}
