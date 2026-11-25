       IDENTIFICATION DIVISION.
       PROGRAM-ID. S75950.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-CMD0            PIC X(100).
       LINKAGE SECTION.
       01  LK-NAME0           PIC X(40).
       PROCEDURE DIVISION USING LK-NAME0.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       CONVERT-FILE-SAFE0.
           MOVE "convert /srv/in/report.txt" TO WS-CMD0.
           CALL 'SYSTEM' USING WS-CMD0.

