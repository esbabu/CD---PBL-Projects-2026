       IDENTIFICATION DIVISION.
       PROGRAM-ID. S06002.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-IDX2            PIC 99.
       01  WS-TAB2.
           05  WS-ENTRY2      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT2            PIC X(10).
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       LOOKUP-ENTRY-SAFE2.
           ACCEPT WS-IDX2.
           IF WS-IDX2 > 0 AND WS-IDX2 NOT > 10
               MOVE WS-ENTRY2(WS-IDX2) TO WS-OUT2
           END-IF.

