       IDENTIFICATION DIVISION.
       PROGRAM-ID. S24182.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-FORM2           PIC X(40).
       01  WS-PAGE2           PIC X(80).
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       ECHO-NAME-SAFE2.
           MOVE '<p>Thank you</p>' TO WS-PAGE2.
           EXEC CICS WEB SEND FROM(WS-PAGE2) END-EXEC.

