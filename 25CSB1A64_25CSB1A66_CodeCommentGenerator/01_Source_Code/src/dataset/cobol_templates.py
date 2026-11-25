"""
COBOL vulnerable / safe paragraph templates (hand-written; no public labelled COBOL corpus exists)
===================================================================================================
Each entry: (template id, rule, vulnerable paragraph, safe paragraph, WORKING-STORAGE items,
LINKAGE items). The line the rule must report ends with ``#!``. ``__N__`` makes names unique.
"""

TEMPLATES = [
    ("cobol-dyn-sql", "SEC005",
     '''       QUERY-CUSTOMER__N__.
           ACCEPT WS-CUST__N__.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST__N__ "'"
               DELIMITED BY SIZE INTO WS-SQL__N__.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL__N__ END-EXEC.  #!
''',
     '''       QUERY-CUSTOMER-SAFE__N__.
           ACCEPT WS-CUST__N__.
           EXEC SQL
               SELECT NAME INTO :WS-NAME__N__ FROM CUST WHERE ID = :WS-CUST__N__
           END-EXEC.
''',
     ["       01  WS-CUST__N__           PIC X(10).", "       01  WS-SQL__N__            PIC X(200).",
      "       01  WS-NAME__N__           PIC X(30)."], []),
    ("cobol-prepare", "SEC005",
     '''       PREPARE-QUERY__N__.
           MOVE LK-FILTER__N__ TO WS-STMT__N__.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT__N__ END-EXEC.  #!
''',
     '''       PREPARE-QUERY-SAFE__N__.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT__N__.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT__N__ END-EXEC.
''',
     ["       01  WS-STMT__N__           PIC X(200)."], ["       01  LK-FILTER__N__         PIC X(100)."]),
    ("cobol-dyn-call", "SEC025",
     '''       RUN-HANDLER__N__.
           ACCEPT WS-PROG__N__.
           CALL WS-PROG__N__ USING WS-DATA__N__.  #!
''',
     '''       RUN-HANDLER-SAFE__N__.
           ACCEPT WS-CHOICE__N__.
           IF WS-CHOICE__N__ = 'A'
               CALL 'HANDLERA' USING WS-DATA__N__
           ELSE
               CALL 'HANDLERB' USING WS-DATA__N__
           END-IF.
''',
     ["       01  WS-PROG__N__           PIC X(8).", "       01  WS-DATA__N__           PIC X(50).",
      "       01  WS-CHOICE__N__         PIC X."], []),
    ("cobol-system", "SEC002",
     '''       CONVERT-FILE__N__.
           STRING "convert " LK-NAME__N__ DELIMITED BY SIZE INTO WS-CMD__N__.
           CALL 'SYSTEM' USING WS-CMD__N__.  #!
''',
     '''       CONVERT-FILE-SAFE__N__.
           MOVE "convert /srv/in/report.txt" TO WS-CMD__N__.
           CALL 'SYSTEM' USING WS-CMD__N__.
''',
     ["       01  WS-CMD__N__            PIC X(100)."], ["       01  LK-NAME__N__           PIC X(40)."]),
    ("cobol-subscript", "SEC054",
     '''       LOOKUP-ENTRY__N__.
           ACCEPT WS-IDX__N__.
           MOVE WS-ENTRY__N__(WS-IDX__N__) TO WS-OUT__N__.  #!
''',
     '''       LOOKUP-ENTRY-SAFE__N__.
           ACCEPT WS-IDX__N__.
           IF WS-IDX__N__ > 0 AND WS-IDX__N__ NOT > 10
               MOVE WS-ENTRY__N__(WS-IDX__N__) TO WS-OUT__N__
           END-IF.
''',
     ["       01  WS-IDX__N__            PIC 99.", "       01  WS-TAB__N__.",
      "           05  WS-ENTRY__N__      PIC X(10) OCCURS 10 TIMES.", "       01  WS-OUT__N__            PIC X(10)."],
     []),
    ("cobol-refmod", "SEC054",
     '''       EXTRACT-FIELD__N__.
           ACCEPT WS-POS__N__.
           MOVE WS-RECORD__N__(WS-POS__N__:5) TO WS-PART__N__.  #!
''',
     '''       EXTRACT-FIELD-SAFE__N__.
           ACCEPT WS-POS__N__.
           IF WS-POS__N__ IS NUMERIC AND WS-POS__N__ > 0 AND WS-POS__N__ < 76
               MOVE WS-RECORD__N__(WS-POS__N__:5) TO WS-PART__N__
           END-IF.
''',
     ["       01  WS-POS__N__            PIC 99.", "       01  WS-RECORD__N__         PIC X(80).",
      "       01  WS-PART__N__           PIC X(5)."], []),
    ("cobol-secret", "SEC003",
     '''       CONNECT-DB__N__.
           MOVE WS-DB-PASSWORD__N__ TO WS-CONN-PW__N__.
''',
     '''       CONNECT-DB-SAFE__N__.
           ACCEPT WS-CONN-PW__N__ FROM ENVIRONMENT 'DB_PASSWORD'.
''',
     ["       01  WS-DB-PASSWORD__N__    PIC X(12) VALUE 'Tiger2026!'.  #!",
      "       01  WS-CONN-PW__N__        PIC X(12)."], []),
    ("cobol-display-secret", "SEC050",
     '''       LOG-LOGIN__N__.
           DISPLAY 'LOGIN ' WS-USER__N__ ' ' WS-PASSWORD-IN__N__.  #!
''',
     '''       LOG-LOGIN-SAFE__N__.
           DISPLAY 'LOGIN ' WS-USER__N__.
''',
     ["       01  WS-USER__N__           PIC X(10).", "       01  WS-PASSWORD-IN__N__    PIC X(12)."], []),
    ("cobol-web-xss", "SEC014",
     '''       ECHO-NAME__N__.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM__N__) END-EXEC.
           STRING '<p>' WS-FORM__N__ '</p>' DELIMITED BY SIZE INTO WS-PAGE__N__.
           EXEC CICS WEB SEND FROM(WS-PAGE__N__) END-EXEC.  #!
''',
     '''       ECHO-NAME-SAFE__N__.
           MOVE '<p>Thank you</p>' TO WS-PAGE__N__.
           EXEC CICS WEB SEND FROM(WS-PAGE__N__) END-EXEC.
''',
     ["       01  WS-FORM__N__           PIC X(40).", "       01  WS-PAGE__N__           PIC X(80)."], []),
    ("cobol-xctl", "SEC025",
     '''       TRANSFER__N__.
           EXEC CICS RECEIVE INTO(WS-TARGET__N__) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET__N__) END-EXEC.  #!
''',
     '''       TRANSFER-SAFE__N__.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.
''',
     ["       01  WS-TARGET__N__         PIC X(8)."], []),
    ("cobol-dyn-file", "SEC013",
     '''       WRITE-EXPORT__N__.
           MOVE LK-PATH__N__ TO WS-EXPORT-PATH__N__.
           OPEN OUTPUT EXPORT-FILE__N__.  #!
           CLOSE EXPORT-FILE__N__.
''',
     '''       WRITE-EXPORT-SAFE__N__.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH__N__.
           OPEN OUTPUT EXPORT-FILE__N__.
           CLOSE EXPORT-FILE__N__.
''',
     ["       01  WS-EXPORT-PATH__N__    PIC X(60)."], ["       01  LK-PATH__N__           PIC X(60)."]),
]
