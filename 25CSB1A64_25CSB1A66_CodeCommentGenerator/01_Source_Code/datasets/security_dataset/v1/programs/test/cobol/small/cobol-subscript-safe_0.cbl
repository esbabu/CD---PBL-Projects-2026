       IDENTIFICATION DIVISION.
       PROGRAM-ID. S06000.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-IDX0            PIC 99.
       01  WS-TAB0.
           05  WS-ENTRY0      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT0            PIC X(10).
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       LOOKUP-ENTRY-SAFE0.
           ACCEPT WS-IDX0.
           IF WS-IDX0 > 0 AND WS-IDX0 NOT > 10
               MOVE WS-ENTRY0(WS-IDX0) TO WS-OUT0
           END-IF.

