       IDENTIFICATION DIVISION.
       PROGRAM-ID. S24181.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-FORM1           PIC X(40).
       01  WS-PAGE1           PIC X(80).
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       ECHO-NAME-SAFE1.
           MOVE '<p>Thank you</p>' TO WS-PAGE1.
           EXEC CICS WEB SEND FROM(WS-PAGE1) END-EXEC.

