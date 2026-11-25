       IDENTIFICATION DIVISION.
       PROGRAM-ID. S75952.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-CMD2            PIC X(100).
       LINKAGE SECTION.
       01  LK-NAME2           PIC X(40).
       PROCEDURE DIVISION USING LK-NAME2.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       CONVERT-FILE-SAFE2.
           MOVE "convert /srv/in/report.txt" TO WS-CMD2.
           CALL 'SYSTEM' USING WS-CMD2.

