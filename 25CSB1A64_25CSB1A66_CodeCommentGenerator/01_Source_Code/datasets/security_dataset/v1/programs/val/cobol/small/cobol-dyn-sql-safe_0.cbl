       IDENTIFICATION DIVISION.
       PROGRAM-ID. S96580.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-CUST0           PIC X(10).
       01  WS-SQL0            PIC X(200).
       01  WS-NAME0           PIC X(30).
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       QUERY-CUSTOMER-SAFE0.
           ACCEPT WS-CUST0.
           EXEC SQL
               SELECT NAME INTO :WS-NAME0 FROM CUST WHERE ID = :WS-CUST0
           END-EXEC.

