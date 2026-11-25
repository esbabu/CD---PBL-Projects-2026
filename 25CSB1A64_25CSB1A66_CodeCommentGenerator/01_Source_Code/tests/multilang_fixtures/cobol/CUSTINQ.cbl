      *> CUSTINQ: customer inquiry transaction (fixed format).
      *> Vulnerable statements are marked "expect"; safe twins follow.
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CUSTINQ.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT REPORT-FILE ASSIGN TO DYNAMIC WS-REPORT-PATH
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  REPORT-FILE.
       01  REPORT-LINE            PIC X(80).
       WORKING-STORAGE SECTION.
       01  WS-CUST-ID             PIC X(10).
       01  WS-SAFE-ID             PIC X(10).
       01  WS-SQL                 PIC X(200).
       01  WS-PROG                PIC X(8).
       01  WS-CMD                 PIC X(100).
       01  WS-REPORT-PATH         PIC X(60).
       01  WS-IDX                 PIC 99.
       01  WS-SAFE-IDX            PIC 99.
       01  WS-DB-PASSWORD         PIC X(12) VALUE 'Tiger2026!'.         expect: SEC003
       01  WS-TABLE.
           05  WS-ENTRY           PIC X(10) OCCURS 10 TIMES.
       01  WS-NAME                PIC X(10).
       LINKAGE SECTION.
       01  LK-REQUEST             PIC X(50).
       PROCEDURE DIVISION USING LK-REQUEST.
       MAIN-PARA.
           ACCEPT WS-CUST-ID.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST-ID "'"
               DELIMITED BY SIZE INTO WS-SQL.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL END-EXEC.                expect: SEC005
           PERFORM SAFE-QUERY.
           PERFORM RUN-PLUGIN.
           PERFORM LOOKUP.
           PERFORM WRITE-REPORT.
           GOBACK.

       SAFE-QUERY.
           ACCEPT WS-SAFE-ID.
           EXEC SQL
               SELECT NAME INTO :WS-NAME FROM CUST WHERE ID = :WS-SAFE-ID
           END-EXEC.

       RUN-PLUGIN.
           MOVE LK-REQUEST(1:8) TO WS-PROG.
           CALL WS-PROG USING WS-CUST-ID.                                expect: SEC025
           STRING "convert " LK-REQUEST DELIMITED BY SIZE INTO WS-CMD.
           CALL 'SYSTEM' USING WS-CMD.                                   expect: SEC002

       LOOKUP.
           ACCEPT WS-IDX.
           MOVE WS-ENTRY(WS-IDX) TO WS-NAME.                             expect: SEC054
           ACCEPT WS-SAFE-IDX.
           IF WS-SAFE-IDX > 0 AND WS-SAFE-IDX NOT > 10
               MOVE WS-ENTRY(WS-SAFE-IDX) TO WS-NAME
           END-IF.

       WRITE-REPORT.
           MOVE LK-REQUEST TO WS-REPORT-PATH.
           OPEN OUTPUT REPORT-FILE.                                      expect: SEC013
           DISPLAY 'DB PASSWORD ' WS-DB-PASSWORD.                        expect: SEC050
           CLOSE REPORT-FILE.
