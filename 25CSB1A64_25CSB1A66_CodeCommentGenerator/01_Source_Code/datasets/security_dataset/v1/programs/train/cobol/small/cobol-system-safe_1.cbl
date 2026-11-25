       IDENTIFICATION DIVISION.
       PROGRAM-ID. S75951.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-CMD1            PIC X(100).
       LINKAGE SECTION.
       01  LK-NAME1           PIC X(40).
       PROCEDURE DIVISION USING LK-NAME1.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       CONVERT-FILE-SAFE1.
           MOVE "convert /srv/in/report.txt" TO WS-CMD1.
           CALL 'SYSTEM' USING WS-CMD1.

