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

namespace Dataset.Generated
{
    [ApiController]
    [Authorize]
    public class TrainCsharpProgram05Controller : Controller
    {
        private static int lastReportId;
        private readonly SqlConnection _conn;
        private readonly HttpClient _http;
        private readonly ILogger<object> _logger;

                public string FormatAmount1(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public string FormatAmount2(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public bool IsLeapYear3(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth3(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear3(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN4([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

                public int ClampValue5(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("search")]
        public IActionResult SearchN6([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

                public int ClampValue7(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public int ClampValue8(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpPost("import")]
        public IActionResult ImportN9()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

        [HttpGet("go")]
        public IActionResult GoN10([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

                public bool IsLeapYear11(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth11(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear11(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public double AverageOf12(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

        public int ParseCountN13(string text)
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

                public string FormatAmount14(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN15([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

                public double AverageOf16(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

        [HttpPost("import")]
        public IActionResult ImportN17()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN18([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords19(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

                public int ClampValue20(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public double AverageOf21(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

        public XmlDocument LoadXmlN22(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN22(xml);
            return doc;
        }

        public string ChecksumN23(byte[] data)
        {
            using var md5 = MD5.Create();
            return Convert.ToBase64String(md5.ComputeHash(data));
        }

        public void SetCookieN24(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

                public double AverageOf25(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

        [HttpGet("export")]
        public IActionResult ExportN26([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

        public void SetCookieN27(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

        public void TrustEverythingN28(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

        public int ParseCountN29(string text)
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

                public string FormatAmount30(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public double AverageOf31(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

                public int ClampValue32(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("go")]
        public IActionResult GoN33([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

                public string FormatAmount34(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public double AverageOf35(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

        [HttpGet("go")]
        public IActionResult GoN36([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

        public XmlDocument LoadXmlN37(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN37(xml);
            return doc;
        }

        public int ParseCountN38(string text)
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

                public int ClampValue39(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public System.Collections.Generic.Dictionary<string, int> CountWords40(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

                public System.Collections.Generic.Dictionary<string, int> CountWords41(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

                public double AverageOf42(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

                public int ClampValue43(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public bool IsLeapYear44(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth44(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear44(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public int ClampValue45(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public int ClampValue46(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("search")]
        public IActionResult SearchN47([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

        [HttpGet("export")]
        public IActionResult ExportN48([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

        [HttpGet("export")]
        public IActionResult ExportN49([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

                public int ClampValue50(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public double AverageOf51(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

                public double AverageOf52(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

                public int ClampValue53(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN54([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

                public bool IsLeapYear55(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth55(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear55(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public int ClampValue56(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public int ClampValue57(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public int ClampValue58(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("search")]
        public IActionResult SearchN59([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

        public int ParseCountN60(string text)
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

                public int ClampValue61(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        public XmlDocument LoadXmlN62(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN62(xml);
            return doc;
        }

                public bool IsLeapYear63(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth63(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear63(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        [HttpPost("import")]
        public IActionResult ImportN64()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

        public string ConnectionStringN65()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

        [HttpGet("search")]
        public IActionResult SearchN66([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

        public void SetCookieN67(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

        public string ChecksumSafeN68(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        [HttpGet("go")]
        public IActionResult GoN69([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

        [HttpGet("export")]
        public IActionResult ExportN70([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

                public double AverageOf71(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

                public string FormatAmount72(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

        [HttpGet("search")]
        public IActionResult SearchN73([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

                public bool IsLeapYear74(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth74(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear74(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public double AverageOf75(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

                public int ClampValue76(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN77([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

        public XmlDocument LoadXmlN78(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN78(xml);
            return doc;
        }

                public string FormatAmount79(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

        [HttpGet("search")]
        public IActionResult SearchN80([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

        public string ChecksumSafeN81(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        [HttpPost("import")]
        public IActionResult ImportN82()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

        public string ChecksumN83(byte[] data)
        {
            using var md5 = MD5.Create();
            return Convert.ToBase64String(md5.ComputeHash(data));
        }

                public bool IsLeapYear84(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth84(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear84(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN85([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

                public string FormatAmount86(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public bool IsLeapYear87(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth87(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear87(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public bool IsLeapYear88(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth88(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear88(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        [HttpGet("search")]
        public IActionResult SearchN89([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

        [HttpGet("go")]
        public IActionResult GoN90([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

                public int ClampValue91(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        public void TrustEverythingN92(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords93(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

        [HttpPost("import")]
        public IActionResult ImportN94()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

                public int ClampValue95(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        public string ChecksumSafeN96(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        public string ConnectionStringN97()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

        public int ParseCountN98(string text)
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

        public string ConnectionStringN99()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords100(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

        public void TrustEverythingN101(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

                public bool IsLeapYear102(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth102(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear102(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public string FormatAmount103(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public int ClampValue104(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        public string ConnectionStringN105()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords106(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

        [HttpGet("go")]
        public IActionResult GoN107([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

                public double AverageOf108(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

        public string ConnectionStringN109()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords110(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

                public System.Collections.Generic.Dictionary<string, int> CountWords111(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

        public XmlDocument LoadXmlN112(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN112(xml);
            return doc;
        }

        [HttpGet("go")]
        public IActionResult GoN113([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN114([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

        public int ParseCountN115(string text)
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

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN116([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

                public string FormatAmount117(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public string FormatAmount118(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public string FormatAmount119(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

        [HttpGet("go")]
        public IActionResult GoN120([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

                public bool IsLeapYear121(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth121(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear121(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        public XmlDocument LoadXmlN122(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN122(xml);
            return doc;
        }

                public bool IsLeapYear123(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth123(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear123(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        [HttpPost("import")]
        public IActionResult ImportN124()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

                public int ClampValue125(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public int ClampValue126(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public int ClampValue127(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public string FormatAmount128(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN129([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

                public string FormatAmount130(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public double AverageOf131(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

                public bool IsLeapYear132(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth132(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear132(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public int ClampValue133(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpPost("import")]
        public IActionResult ImportN134()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

        public int ParseCountN135(string text)
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

        public string ConnectionStringN136()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

                public double AverageOf137(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

                public bool IsLeapYear138(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth138(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear138(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public System.Collections.Generic.Dictionary<string, int> CountWords139(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

                public int ClampValue140(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN141([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

        [HttpPost("import")]
        public IActionResult ImportN142()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

                public int ClampValue143(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpPost("import")]
        public IActionResult ImportN144()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

                public int ClampValue145(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public bool IsLeapYear146(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth146(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear146(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public int ClampValue147(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public int ClampValue148(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public double AverageOf149(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN150([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

                public string FormatAmount151(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

        public void SetCookieN152(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

                public double AverageOf153(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN154([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

        [HttpGet("go")]
        public IActionResult GoN155([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

        [HttpGet("export")]
        public IActionResult ExportN156([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

                public bool IsLeapYear157(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth157(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear157(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public string FormatAmount158(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public string FormatAmount159(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public System.Collections.Generic.Dictionary<string, int> CountWords160(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

                public int ClampValue161(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        public string ConnectionStringN162()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN163([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN164([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

        public string ConnectionStringN165()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

                public int ClampValue166(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public int ClampValue167(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public bool IsLeapYear168(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth168(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear168(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        [HttpGet("search")]
        public IActionResult SearchN169([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

        public string ChecksumSafeN170(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        public void TrustEverythingN171(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

                public int ClampValue172(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public System.Collections.Generic.Dictionary<string, int> CountWords173(string text)
                {
                    var counts = new System.Collections.Generic.Dictionary<string, int>();
                    foreach (var word in text.ToLowerInvariant().Split(' '))
                    {
                        if (word.Length == 0)
                        {
                            continue;
                        }
                        counts[word] = counts.TryGetValue(word, out var n) ? n + 1 : 1;
                    }
                    return counts;
                }

        public string ConnectionStringN174()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

        public void SetCookieN175(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

                public double AverageOf176(System.Collections.Generic.List<int> values)
                {
                    if (values.Count == 0)
                    {
                        return 0.0;
                    }
                    long total = 0;
                    foreach (var v in values)
                    {
                        total += v;
                    }
                    return (double)total / values.Count;
                }

        public void TrustEverythingN177(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

                public string FormatAmount178(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

        [HttpPost("import")]
        public IActionResult ImportN179()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

                public string FormatAmount180(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public bool IsLeapYear181(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth181(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear181(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        public void SetCookieN182(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

        [HttpGet("search")]
        public IActionResult SearchN183([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

                public int ClampValue184(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("search")]
        public IActionResult SearchN185([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN186([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

        [HttpGet("go")]
        public IActionResult GoN187([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

                public bool IsLeapYear188(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth188(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear188(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public bool IsLeapYear189(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth189(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear189(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public string FormatAmount190(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public int ClampValue191(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

    }
}
