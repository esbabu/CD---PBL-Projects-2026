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
    public class SampleCsharpBycustomersafe0Controller : Controller
    {
        private static int lastReportId;
        private readonly SqlConnection _conn;
        private readonly HttpClient _http;
        private readonly ILogger<object> _logger;

        [HttpGet("by-customer-safe")]
        public IActionResult ByCustomerSafe([FromQuery] string customer)
        {
            var cmd = new SqlCommand("SELECT * FROM Reports WHERE Customer = @c", _conn);
            cmd.Parameters.AddWithValue("@c", customer);
            return Ok(cmd.ExecuteScalar());
        }

    }
}
