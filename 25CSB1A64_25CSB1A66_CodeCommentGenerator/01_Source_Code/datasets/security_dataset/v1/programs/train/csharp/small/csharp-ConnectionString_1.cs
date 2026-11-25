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
    public class SampleCsharpConnectionstring1Controller : Controller
    {
        private static int lastReportId;
        private readonly SqlConnection _conn;
        private readonly HttpClient _http;
        private readonly ILogger<object> _logger;

        public string ConnectionStringV1()
        {
            return "Server=db;Database=shop;User Id=app;Password=Winter2026!;";
        }

    }
}
