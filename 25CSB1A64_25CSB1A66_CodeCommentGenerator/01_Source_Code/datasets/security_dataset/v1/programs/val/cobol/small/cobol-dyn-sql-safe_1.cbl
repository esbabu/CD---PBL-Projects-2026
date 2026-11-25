       IDENTIFICATION DIVISION.
       PROGRAM-ID. S96581.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-CUST1           PIC X(10).
       01  WS-SQL1            PIC X(200).
       01  WS-NAME1           PIC X(30).
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       QUERY-CUSTOMER-SAFE1.
           ACCEPT WS-CUST1.
           EXEC SQL
               SELECT NAME INTO :WS-NAME1 FROM CUST WHERE ID = :WS-CUST1
           END-EXEC.

