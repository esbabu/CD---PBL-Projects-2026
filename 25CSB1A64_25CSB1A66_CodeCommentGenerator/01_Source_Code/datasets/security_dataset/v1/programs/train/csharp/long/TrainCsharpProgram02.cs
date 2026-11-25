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
    public class TrainCsharpProgram02Controller : Controller
    {
        private static int lastReportId;
        private readonly SqlConnection _conn;
        private readonly HttpClient _http;
        private readonly ILogger<object> _logger;

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN1([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords2(string text)
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

                public int ClampValue3(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public bool IsLeapYear4(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth4(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear4(year) ? 29 : 28;
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
        public IActionResult ImportN5()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

        [HttpPost("import")]
        public IActionResult ImportN6()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

        [HttpPost("import")]
        public IActionResult ImportN7()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

                public double AverageOf8(System.Collections.Generic.List<int> values)
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
        public IActionResult GoN9([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN10([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords11(string text)
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

                public int ClampValue12(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        public string ChecksumSafeN13(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        public string ChecksumN14(byte[] data)
        {
            using var md5 = MD5.Create();
            return Convert.ToBase64String(md5.ComputeHash(data));
        }

                public string FormatAmount15(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public int ClampValue16(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public bool IsLeapYear17(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth17(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear17(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        public void TrustEverythingN18(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

        public string ChecksumSafeN19(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN20([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN21([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

                public double AverageOf22(System.Collections.Generic.List<int> values)
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

        public void SetCookieN23(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

                public string FormatAmount24(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public bool IsLeapYear25(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth25(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear25(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public string FormatAmount26(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

        [HttpGet("go")]
        public IActionResult GoN27([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN28([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

                public double AverageOf29(System.Collections.Generic.List<int> values)
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

        public int ParseCountN30(string text)
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

        [HttpGet("export")]
        public IActionResult ExportN31([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

        public int ParseCountN32(string text)
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

                public bool IsLeapYear33(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth33(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear33(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN34([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

        public string ChecksumN35(byte[] data)
        {
            using var md5 = MD5.Create();
            return Convert.ToBase64String(md5.ComputeHash(data));
        }

                public string FormatAmount36(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public string FormatAmount37(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public bool IsLeapYear38(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth38(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear38(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
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

                public string FormatAmount40(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public double AverageOf41(System.Collections.Generic.List<int> values)
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

        public string ChecksumSafeN42(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN43([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

        public void TrustEverythingN44(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

        public string ConnectionStringN45()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

        [HttpGet("export")]
        public IActionResult ExportN46([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords47(string text)
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
        public IActionResult ImportN48()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

        public void SetCookieN49(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

        [HttpPost("import")]
        public IActionResult ImportN50()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
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

        public int ParseCountN52(string text)
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

        public void TrustEverythingN53(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

                public int ClampValue54(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public string FormatAmount55(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public bool IsLeapYear56(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth56(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear56(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        public XmlDocument LoadXmlN57(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN57(xml);
            return doc;
        }

        [HttpGet("go")]
        public IActionResult GoN58([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

                public bool IsLeapYear59(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth59(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear59(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        public void SetCookieN60(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

        [HttpGet("search")]
        public IActionResult SearchN61([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

        [HttpGet("search")]
        public IActionResult SearchN62([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
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

        [HttpGet("search")]
        public IActionResult SearchN64([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

                public int ClampValue65(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        public string ChecksumN66(byte[] data)
        {
            using var md5 = MD5.Create();
            return Convert.ToBase64String(md5.ComputeHash(data));
        }

        public string ChecksumSafeN67(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN68([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

                public double AverageOf69(System.Collections.Generic.List<int> values)
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

        public int ParseCountN70(string text)
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

        [HttpGet("search")]
        public IActionResult SearchN71([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

        [HttpGet("export")]
        public IActionResult ExportN72([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

        public int ParseCountN73(string text)
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

                public string FormatAmount74(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public bool IsLeapYear75(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth75(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear75(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        [HttpGet("go")]
        public IActionResult GoN76([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

        public XmlDocument LoadXmlN77(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN77(xml);
            return doc;
        }

                public bool IsLeapYear78(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth78(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear78(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public System.Collections.Generic.Dictionary<string, int> CountWords79(string text)
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

        public string ChecksumN80(byte[] data)
        {
            using var md5 = MD5.Create();
            return Convert.ToBase64String(md5.ComputeHash(data));
        }

                public string FormatAmount81(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

        public string ChecksumN82(byte[] data)
        {
            using var md5 = MD5.Create();
            return Convert.ToBase64String(md5.ComputeHash(data));
        }

                public int ClampValue83(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public System.Collections.Generic.Dictionary<string, int> CountWords84(string text)
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

                public double AverageOf85(System.Collections.Generic.List<int> values)
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

                public double AverageOf86(System.Collections.Generic.List<int> values)
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

        public string ConnectionStringN87()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

        public void TrustEverythingN88(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

                public int ClampValue89(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public string FormatAmount90(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

        [HttpGet("export")]
        public IActionResult ExportN91([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords92(string text)
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
        public IActionResult ImportN93()
        {
            var formatter = new BinaryFormatter();
            object report = formatter.Deserialize(Request.Body);
            return Ok();
        }

        public int ParseCountN94(string text)
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
        public IActionResult SearchSafeN95([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

                public int ClampValue96(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        public void TrustEverythingN97(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

        public XmlDocument LoadXmlN98(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN98(xml);
            return doc;
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords99(string text)
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

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN100([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

                public double AverageOf101(System.Collections.Generic.List<int> values)
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

        public string ChecksumSafeN102(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        [HttpGet("search")]
        public IActionResult SearchN103([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

        public string ChecksumSafeN104(byte[] data)
        {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(data));
        }

        [HttpGet("go")]
        public IActionResult GoN105([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

        public int ParseCountN106(string text)
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

                public System.Collections.Generic.Dictionary<string, int> CountWords107(string text)
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

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN108([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

        public string ConnectionStringN109()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

                public double AverageOf110(System.Collections.Generic.List<int> values)
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

                public int ClampValue111(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("search")]
        public IActionResult SearchN112([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

                public int ClampValue113(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("search")]
        public IActionResult SearchN114([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", pattern);
            _logger.LogInformation("search for " + pattern);
            return Ok(hit);
        }

                public int ClampValue115(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("search-safe")]
        public IActionResult SearchSafeN116([FromQuery] string pattern)
        {
            bool hit = Regex.IsMatch("quarterly report", Regex.Escape(pattern));
            return Ok(hit);
        }

        public void TrustEverythingN117(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords118(string text)
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

        public void TrustEverythingN119(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

        public void SetCookieN120(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

        public string ConnectionStringN121()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

        [HttpGet("export")]
        public IActionResult ExportN122([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

        [HttpGet("export")]
        public IActionResult ExportN123([FromQuery] string format)
        {
            Process.Start("/usr/bin/report-tool", "--format " + format);
            return Ok();
        }

        public string ChecksumN124(byte[] data)
        {
            using var md5 = MD5.Create();
            return Convert.ToBase64String(md5.ComputeHash(data));
        }

                public bool IsLeapYear125(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth125(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear125(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        public XmlDocument LoadXmlN126(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN126(xml);
            return doc;
        }

                public bool IsLeapYear127(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth127(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear127(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public bool IsLeapYear128(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth128(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear128(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public bool IsLeapYear129(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth129(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear129(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public double AverageOf130(System.Collections.Generic.List<int> values)
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

                public System.Collections.Generic.Dictionary<string, int> CountWords132(string text)
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

                public int ClampValue133(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public bool IsLeapYear134(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth134(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear134(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public int ClampValue135(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        public void TrustEverythingN136(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

        [HttpGet("go")]
        public IActionResult GoN137([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

        public void TrustEverythingN138(HttpClientHandler handler)
        {
            handler.ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true;
        }

                public bool IsLeapYear139(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth139(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear139(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

                public double AverageOf140(System.Collections.Generic.List<int> values)
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

                public string FormatAmount141(long cents)
                {
                    var whole = cents / 100;
                    var rest = System.Math.Abs(cents % 100);
                    return whole + "." + rest.ToString("00");
                }

                public int ClampValue142(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        public void SetCookieN143(HttpResponse response, string session)
        {
            response.Cookies.Append("session", session, new CookieOptions { Secure = false, HttpOnly = true });
        }

                public System.Collections.Generic.Dictionary<string, int> CountWords144(string text)
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

        public XmlDocument LoadXmlN145(string xml)
        {
            var doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXmlN145(xml);
            return doc;
        }

                public int ClampValue146(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

                public int ClampValue147(int value, int low, int high)
                {
                    if (value < low)
                    {
                        return low;
                    }
                    return value > high ? high : value;
                }

        [HttpGet("proxy")]
        public async System.Threading.Tasks.Task<IActionResult> ProxyN148([FromQuery] string url)
        {
            string body = await _http.GetStringAsync(url);
            return Ok(body.Length);
        }

                public bool IsLeapYear149(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth149(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear149(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

        [HttpGet("go")]
        public IActionResult GoN150([FromQuery] string returnUrl)
        {
            return Redirect(returnUrl);
        }

        public string ChecksumN151(byte[] data)
        {
            using var md5 = MD5.Create();
            return Convert.ToBase64String(md5.ComputeHash(data));
        }

        public string ConnectionStringN152()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

                public bool IsLeapYear153(int year)
                {
                    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
                }

                public int DaysInMonth153(int year, int month)
                {
                    switch (month)
                    {
                        case 2:
                            return IsLeapYear153(year) ? 29 : 28;
                        case 4:
                        case 6:
                        case 9:
                        case 11:
                            return 30;
                        default:
                            return 31;
                    }
                }

    }
}
