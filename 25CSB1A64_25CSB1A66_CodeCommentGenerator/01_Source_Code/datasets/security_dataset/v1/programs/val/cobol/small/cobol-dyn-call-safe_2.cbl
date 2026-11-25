       IDENTIFICATION DIVISION.
       PROGRAM-ID. S07742.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-PROG2           PIC X(8).
       01  WS-DATA2           PIC X(50).
       01  WS-CHOICE2         PIC X.
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       RUN-HANDLER-SAFE2.
           ACCEPT WS-CHOICE2.
           IF WS-CHOICE2 = 'A'
               CALL 'HANDLERA' USING WS-DATA2
           ELSE
               CALL 'HANDLERB' USING WS-DATA2
           END-IF.

