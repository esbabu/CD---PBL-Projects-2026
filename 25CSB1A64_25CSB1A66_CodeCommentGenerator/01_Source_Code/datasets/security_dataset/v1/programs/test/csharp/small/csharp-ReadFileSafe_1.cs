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
    public class SampleCsharpReadfilesafe1Controller : Controller
    {
        private static int lastReportId;
        private readonly SqlConnection _conn;
        private readonly HttpClient _http;
        private readonly ILogger<object> _logger;

        [HttpGet("file-safe")]
        public IActionResult ReadFileSafeV1([FromQuery] string name)
        {
            string text = System.IO.File.ReadAllText(Path.Combine("/srv/reports", Path.GetFileName(name)));
            return Ok(text.Length);
        }

    }
}
