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
    public class SampleCsharpEncrypt1Controller : Controller
    {
        private static int lastReportId;
        private readonly SqlConnection _conn;
        private readonly HttpClient _http;
        private readonly ILogger<object> _logger;

        public byte[] EncryptV1(byte[] data)
        {
            using var des = DES.Create();
            return des.CreateEncryptor().TransformFinalBlock(data, 0, data.Length);
        }

    }
}
