"""
Ordinary (secure) code used to grow long dataset programs to 1,000-2,000 lines
==============================================================================
Per language: everyday utility functions with no security-relevant data flow —
arithmetic, collections, parsing of constants, small state machines. ``__N__``
is replaced by a unique number. They carry no labels; any finding the analyzer
reports inside them is counted as a false positive in the evaluation.
"""

JAVA = [
    '''    int clampValue__N__(int value, int low, int high) {
        if (value < low) {
            return low;
        }
        if (value > high) {
            return high;
        }
        return value;
    }
''',
    '''    double averageOf__N__(java.util.List<Integer> values) {
        if (values.isEmpty()) {
            return 0.0;
        }
        long total = 0;
        for (int v : values) {
            total += v;
        }
        return (double) total / values.size();
    }
''',
    '''    java.util.Map<String, Integer> countWords__N__(String text) {
        java.util.Map<String, Integer> counts = new java.util.HashMap<>();
        for (String word : text.toLowerCase().split("\\\\s+")) {
            if (word.isEmpty()) {
                continue;
            }
            counts.merge(word, 1, Integer::sum);
        }
        return counts;
    }
''',
    '''    String formatAmount__N__(long cents) {
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
''',
    '''    boolean isLeapYear__N__(int year) {
        return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
    }

    int daysInMonth__N__(int year, int month) {
        switch (month) {
            case 2:
                return isLeapYear__N__(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
        }
    }
''',
    '''    java.util.List<Integer> mergeSorted__N__(java.util.List<Integer> a, java.util.List<Integer> b) {
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
''',
]

CSHARP = [
    '''        public int ClampValue__N__(int value, int low, int high)
        {
            if (value < low)
            {
                return low;
            }
            return value > high ? high : value;
        }
''',
    '''        public double AverageOf__N__(System.Collections.Generic.List<int> values)
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
''',
    '''        public string FormatAmount__N__(long cents)
        {
            var whole = cents / 100;
            var rest = System.Math.Abs(cents % 100);
            return whole + "." + rest.ToString("00");
        }
''',
    '''        public System.Collections.Generic.Dictionary<string, int> CountWords__N__(string text)
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
''',
    '''        public bool IsLeapYear__N__(int year)
        {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        public int DaysInMonth__N__(int year, int month)
        {
            switch (month)
            {
                case 2:
                    return IsLeapYear__N__(year) ? 29 : 28;
                case 4:
                case 6:
                case 9:
                case 11:
                    return 30;
                default:
                    return 31;
            }
        }
''',
]

C = [
    '''int clamp_value__N__(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}
''',
    '''double average_of__N__(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}
''',
    '''int is_leap_year__N__(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month__N__(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year__N__(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}
''',
    '''size_t count_char__N__(const char *text, char c) {
    size_t n = 0;
    while (*text != '\\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}
''',
    '''void reverse_ints__N__(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}
''',
]

CPP = [
    '''    int clampValue__N__(int value, int low, int high) {
        if (value < low) {
            return low;
        }
        return value > high ? high : value;
    }
''',
    '''    double averageOf__N__(const std::vector<int> &values) {
        if (values.empty()) {
            return 0.0;
        }
        long total = 0;
        for (int v : values) {
            total += v;
        }
        return static_cast<double>(total) / values.size();
    }
''',
    '''    std::string joinWords__N__(const std::vector<std::string> &words, const std::string &sep) {
        std::string out;
        for (size_t i = 0; i < words.size(); ++i) {
            if (i > 0) {
                out += sep;
            }
            out += words[i];
        }
        return out;
    }
''',
    '''    bool isLeapYear__N__(int year) {
        return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
    }

    int daysInMonth__N__(int year, int month) {
        switch (month) {
        case 2:
            return isLeapYear__N__(year) ? 29 : 28;
        case 4: case 6: case 9: case 11:
            return 30;
        default:
            return 31;
        }
    }
''',
]

RUST = [
    '''pub fn clamp_value__N__(value: i64, low: i64, high: i64) -> i64 {
    if value < low {
        return low;
    }
    if value > high {
        return high;
    }
    value
}
''',
    '''pub fn average_of__N__(values: &[i64]) -> f64 {
    if values.is_empty() {
        return 0.0;
    }
    let total: i64 = values.iter().sum();
    total as f64 / values.len() as f64
}
''',
    '''pub fn count_words__N__(text: &str) -> std::collections::HashMap<String, usize> {
    let mut counts = std::collections::HashMap::new();
    for word in text.split_whitespace() {
        *counts.entry(word.to_lowercase()).or_insert(0) += 1;
    }
    counts
}
''',
    '''pub fn is_leap_year__N__(year: i32) -> bool {
    (year % 4 == 0 && year % 100 != 0) || year % 400 == 0
}

pub fn days_in_month__N__(year: i32, month: u32) -> u32 {
    match month {
        2 => {
            if is_leap_year__N__(year) {
                29
            } else {
                28
            }
        }
        4 | 6 | 9 | 11 => 30,
        _ => 31,
    }
}
''',
    '''pub fn format_amount__N__(cents: i64) -> String {
    let whole = cents / 100;
    let rest = (cents % 100).abs();
    format!("{}.{:02}", whole, rest)
}
''',
]

# COBOL: (paragraph text, data items it needs)
COBOL = [
    ('''       COMPUTE-TOTALS__N__.
           MOVE 0 TO WS-TOTAL__N__.
           PERFORM VARYING WS-K__N__ FROM 1 BY 1 UNTIL WS-K__N__ > 10
               ADD WS-K__N__ TO WS-TOTAL__N__
           END-PERFORM.
           COMPUTE WS-AVERAGE__N__ = WS-TOTAL__N__ / 10.
''', ["       01  WS-TOTAL__N__          PIC 9(6) VALUE 0.",
      "       01  WS-K__N__              PIC 99 VALUE 0.",
      "       01  WS-AVERAGE__N__        PIC 9(6)V99 VALUE 0."]),
    ('''       CLASSIFY-CODE__N__.
           EVALUATE WS-CODE__N__
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS__N__
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS__N__
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS__N__
           END-EVALUATE.
''', ["       01  WS-CODE__N__           PIC 9 VALUE 1.",
      "       01  WS-STATUS__N__         PIC X(6) VALUE SPACES."]),
    ('''       FORMAT-HEADER__N__.
           MOVE 'MONTHLY REPORT' TO WS-TITLE__N__.
           STRING WS-TITLE__N__ DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER__N__.
           DISPLAY WS-HEADER__N__.
''', ["       01  WS-TITLE__N__          PIC X(20) VALUE SPACES.",
      "       01  WS-HEADER__N__         PIC X(40) VALUE SPACES."]),
    ('''       CHECK-LIMIT__N__.
           IF WS-AMOUNT__N__ > 1000
               MOVE 'Y' TO WS-FLAG__N__
           ELSE
               MOVE 'N' TO WS-FLAG__N__
           END-IF.
''', ["       01  WS-AMOUNT__N__         PIC 9(6) VALUE 500.",
      "       01  WS-FLAG__N__           PIC X VALUE 'N'."]),
]

FILLERS = {"java": JAVA, "csharp": CSHARP, "c": C, "cpp": CPP, "rust": RUST}
