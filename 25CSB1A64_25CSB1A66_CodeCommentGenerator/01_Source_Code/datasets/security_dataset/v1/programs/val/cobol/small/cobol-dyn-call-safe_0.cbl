       IDENTIFICATION DIVISION.
       PROGRAM-ID. S07740.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-PROG0           PIC X(8).
       01  WS-DATA0           PIC X(50).
       01  WS-CHOICE0         PIC X.
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       RUN-HANDLER-SAFE0.
           ACCEPT WS-CHOICE0.
           IF WS-CHOICE0 = 'A'
               CALL 'HANDLERA' USING WS-DATA0
           ELSE
               CALL 'HANDLERB' USING WS-DATA0
           END-IF.

