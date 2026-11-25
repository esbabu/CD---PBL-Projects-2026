       IDENTIFICATION DIVISION.
       PROGRAM-ID. S96582.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-CUST2           PIC X(10).
       01  WS-SQL2            PIC X(200).
       01  WS-NAME2           PIC X(30).
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       QUERY-CUSTOMER-SAFE2.
           ACCEPT WS-CUST2.
           EXEC SQL
               SELECT NAME INTO :WS-NAME2 FROM CUST WHERE ID = :WS-CUST2
           END-EXEC.

