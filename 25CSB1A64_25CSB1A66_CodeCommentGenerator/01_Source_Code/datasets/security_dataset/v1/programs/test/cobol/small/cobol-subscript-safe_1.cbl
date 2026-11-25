       IDENTIFICATION DIVISION.
       PROGRAM-ID. S06001.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-IDX1            PIC 99.
       01  WS-TAB1.
           05  WS-ENTRY1      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT1            PIC X(10).
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       LOOKUP-ENTRY-SAFE1.
           ACCEPT WS-IDX1.
           IF WS-IDX1 > 0 AND WS-IDX1 NOT > 10
               MOVE WS-ENTRY1(WS-IDX1) TO WS-OUT1
           END-IF.

