       IDENTIFICATION DIVISION.
       PROGRAM-ID. S07741.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-PROG1           PIC X(8).
       01  WS-DATA1           PIC X(50).
       01  WS-CHOICE1         PIC X.
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       RUN-HANDLER-SAFE1.
           ACCEPT WS-CHOICE1.
           IF WS-CHOICE1 = 'A'
               CALL 'HANDLERA' USING WS-DATA1
           ELSE
               CALL 'HANDLERB' USING WS-DATA1
           END-IF.

