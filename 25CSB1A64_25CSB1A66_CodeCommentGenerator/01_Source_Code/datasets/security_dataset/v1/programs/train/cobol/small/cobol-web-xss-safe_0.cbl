       IDENTIFICATION DIVISION.
       PROGRAM-ID. S24180.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-FORM0           PIC X(40).
       01  WS-PAGE0           PIC X(80).
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       ECHO-NAME-SAFE0.
           MOVE '<p>Thank you</p>' TO WS-PAGE0.
           EXEC CICS WEB SEND FROM(WS-PAGE0) END-EXEC.

