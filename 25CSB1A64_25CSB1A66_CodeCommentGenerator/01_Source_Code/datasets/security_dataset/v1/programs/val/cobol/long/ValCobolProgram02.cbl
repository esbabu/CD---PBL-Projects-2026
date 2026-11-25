       IDENTIFICATION DIVISION.
       PROGRAM-ID. LVA02.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-PROG3           PIC X(8).
       01  WS-DATA3           PIC X(50).
       01  WS-CHOICE3         PIC X.
       01  WS-PROG4           PIC X(8).
       01  WS-DATA4           PIC X(50).
       01  WS-CHOICE4         PIC X.
       01  WS-CUST5           PIC X(10).
       01  WS-SQL5            PIC X(200).
       01  WS-NAME5           PIC X(30).
       01  WS-PROG9           PIC X(8).
       01  WS-DATA9           PIC X(50).
       01  WS-CHOICE9         PIC X.
       01  WS-PROG10           PIC X(8).
       01  WS-DATA10           PIC X(50).
       01  WS-CHOICE10         PIC X.
       01  WS-PROG11           PIC X(8).
       01  WS-DATA11           PIC X(50).
       01  WS-CHOICE11         PIC X.
       01  WS-CUST12           PIC X(10).
       01  WS-SQL12            PIC X(200).
       01  WS-NAME12           PIC X(30).
       01  WS-PROG13           PIC X(8).
       01  WS-DATA13           PIC X(50).
       01  WS-CHOICE13         PIC X.
       01  WS-CUST16           PIC X(10).
       01  WS-SQL16            PIC X(200).
       01  WS-NAME16           PIC X(30).
       01  WS-PROG17           PIC X(8).
       01  WS-DATA17           PIC X(50).
       01  WS-CHOICE17         PIC X.
       01  WS-PROG25           PIC X(8).
       01  WS-DATA25           PIC X(50).
       01  WS-CHOICE25         PIC X.
       01  WS-PROG26           PIC X(8).
       01  WS-DATA26           PIC X(50).
       01  WS-CHOICE26         PIC X.
       01  WS-CUST28           PIC X(10).
       01  WS-SQL28            PIC X(200).
       01  WS-NAME28           PIC X(30).
       01  WS-CUST29           PIC X(10).
       01  WS-SQL29            PIC X(200).
       01  WS-NAME29           PIC X(30).
       01  WS-PROG30           PIC X(8).
       01  WS-DATA30           PIC X(50).
       01  WS-CHOICE30         PIC X.
       01  WS-PROG32           PIC X(8).
       01  WS-DATA32           PIC X(50).
       01  WS-CHOICE32         PIC X.
       01  WS-PROG37           PIC X(8).
       01  WS-DATA37           PIC X(50).
       01  WS-CHOICE37         PIC X.
       01  WS-PROG40           PIC X(8).
       01  WS-DATA40           PIC X(50).
       01  WS-CHOICE40         PIC X.
       01  WS-CUST41           PIC X(10).
       01  WS-SQL41            PIC X(200).
       01  WS-NAME41           PIC X(30).
       01  WS-CUST43           PIC X(10).
       01  WS-SQL43            PIC X(200).
       01  WS-NAME43           PIC X(30).
       01  WS-CUST45           PIC X(10).
       01  WS-SQL45            PIC X(200).
       01  WS-NAME45           PIC X(30).
       01  WS-CUST46           PIC X(10).
       01  WS-SQL46            PIC X(200).
       01  WS-NAME46           PIC X(30).
       01  WS-CUST47           PIC X(10).
       01  WS-SQL47            PIC X(200).
       01  WS-NAME47           PIC X(30).
       01  WS-CUST48           PIC X(10).
       01  WS-SQL48            PIC X(200).
       01  WS-NAME48           PIC X(30).
       01  WS-CUST49           PIC X(10).
       01  WS-SQL49            PIC X(200).
       01  WS-NAME49           PIC X(30).
       01  WS-PROG50           PIC X(8).
       01  WS-DATA50           PIC X(50).
       01  WS-CHOICE50         PIC X.
       01  WS-CUST51           PIC X(10).
       01  WS-SQL51            PIC X(200).
       01  WS-NAME51           PIC X(30).
       01  WS-CUST52           PIC X(10).
       01  WS-SQL52            PIC X(200).
       01  WS-NAME52           PIC X(30).
       01  WS-CUST55           PIC X(10).
       01  WS-SQL55            PIC X(200).
       01  WS-NAME55           PIC X(30).
       01  WS-PROG58           PIC X(8).
       01  WS-DATA58           PIC X(50).
       01  WS-CHOICE58         PIC X.
       01  WS-PROG59           PIC X(8).
       01  WS-DATA59           PIC X(50).
       01  WS-CHOICE59         PIC X.
       01  WS-PROG60           PIC X(8).
       01  WS-DATA60           PIC X(50).
       01  WS-CHOICE60         PIC X.
       01  WS-PROG61           PIC X(8).
       01  WS-DATA61           PIC X(50).
       01  WS-CHOICE61         PIC X.
       01  WS-CUST62           PIC X(10).
       01  WS-SQL62            PIC X(200).
       01  WS-NAME62           PIC X(30).
       01  WS-PROG63           PIC X(8).
       01  WS-DATA63           PIC X(50).
       01  WS-CHOICE63         PIC X.
       01  WS-PROG66           PIC X(8).
       01  WS-DATA66           PIC X(50).
       01  WS-CHOICE66         PIC X.
       01  WS-CUST67           PIC X(10).
       01  WS-SQL67            PIC X(200).
       01  WS-NAME67           PIC X(30).
       01  WS-CUST68           PIC X(10).
       01  WS-SQL68            PIC X(200).
       01  WS-NAME68           PIC X(30).
       01  WS-PROG70           PIC X(8).
       01  WS-DATA70           PIC X(50).
       01  WS-CHOICE70         PIC X.
       01  WS-PROG73           PIC X(8).
       01  WS-DATA73           PIC X(50).
       01  WS-CHOICE73         PIC X.
       01  WS-CUST74           PIC X(10).
       01  WS-SQL74            PIC X(200).
       01  WS-NAME74           PIC X(30).
       01  WS-PROG75           PIC X(8).
       01  WS-DATA75           PIC X(50).
       01  WS-CHOICE75         PIC X.
       01  WS-CUST76           PIC X(10).
       01  WS-SQL76            PIC X(200).
       01  WS-NAME76           PIC X(30).
       01  WS-PROG77           PIC X(8).
       01  WS-DATA77           PIC X(50).
       01  WS-CHOICE77         PIC X.
       01  WS-CUST78           PIC X(10).
       01  WS-SQL78            PIC X(200).
       01  WS-NAME78           PIC X(30).
       01  WS-PROG82           PIC X(8).
       01  WS-DATA82           PIC X(50).
       01  WS-CHOICE82         PIC X.
       01  WS-PROG84           PIC X(8).
       01  WS-DATA84           PIC X(50).
       01  WS-CHOICE84         PIC X.
       01  WS-CUST85           PIC X(10).
       01  WS-SQL85            PIC X(200).
       01  WS-NAME85           PIC X(30).
       01  WS-CUST87           PIC X(10).
       01  WS-SQL87            PIC X(200).
       01  WS-NAME87           PIC X(30).
       01  WS-PROG89           PIC X(8).
       01  WS-DATA89           PIC X(50).
       01  WS-CHOICE89         PIC X.
       01  WS-PROG90           PIC X(8).
       01  WS-DATA90           PIC X(50).
       01  WS-CHOICE90         PIC X.
       01  WS-PROG91           PIC X(8).
       01  WS-DATA91           PIC X(50).
       01  WS-CHOICE91         PIC X.
       01  WS-PROG92           PIC X(8).
       01  WS-DATA92           PIC X(50).
       01  WS-CHOICE92         PIC X.
       01  WS-CUST94           PIC X(10).
       01  WS-SQL94            PIC X(200).
       01  WS-NAME94           PIC X(30).
       01  WS-PROG101           PIC X(8).
       01  WS-DATA101           PIC X(50).
       01  WS-CHOICE101         PIC X.
       01  WS-PROG102           PIC X(8).
       01  WS-DATA102           PIC X(50).
       01  WS-CHOICE102         PIC X.
       01  WS-CUST103           PIC X(10).
       01  WS-SQL103            PIC X(200).
       01  WS-NAME103           PIC X(30).
       01  WS-PROG105           PIC X(8).
       01  WS-DATA105           PIC X(50).
       01  WS-CHOICE105         PIC X.
       01  WS-CUST106           PIC X(10).
       01  WS-SQL106            PIC X(200).
       01  WS-NAME106           PIC X(30).
       01  WS-PROG108           PIC X(8).
       01  WS-DATA108           PIC X(50).
       01  WS-CHOICE108         PIC X.
       01  WS-CUST109           PIC X(10).
       01  WS-SQL109            PIC X(200).
       01  WS-NAME109           PIC X(30).
       01  WS-PROG111           PIC X(8).
       01  WS-DATA111           PIC X(50).
       01  WS-CHOICE111         PIC X.
       01  WS-CUST112           PIC X(10).
       01  WS-SQL112            PIC X(200).
       01  WS-NAME112           PIC X(30).
       01  WS-CUST113           PIC X(10).
       01  WS-SQL113            PIC X(200).
       01  WS-NAME113           PIC X(30).
       01  WS-PROG114           PIC X(8).
       01  WS-DATA114           PIC X(50).
       01  WS-CHOICE114         PIC X.
       01  WS-CUST115           PIC X(10).
       01  WS-SQL115            PIC X(200).
       01  WS-NAME115           PIC X(30).
       01  WS-CUST116           PIC X(10).
       01  WS-SQL116            PIC X(200).
       01  WS-NAME116           PIC X(30).
       01  WS-CUST117           PIC X(10).
       01  WS-SQL117            PIC X(200).
       01  WS-NAME117           PIC X(30).
       01  WS-CODE1           PIC 9 VALUE 1.
       01  WS-STATUS1         PIC X(6) VALUE SPACES.
       01  WS-TOTAL2          PIC 9(6) VALUE 0.
       01  WS-K2              PIC 99 VALUE 0.
       01  WS-AVERAGE2        PIC 9(6)V99 VALUE 0.
       01  WS-CODE6           PIC 9 VALUE 1.
       01  WS-STATUS6         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT7         PIC 9(6) VALUE 500.
       01  WS-FLAG7           PIC X VALUE 'N'.
       01  WS-TITLE8          PIC X(20) VALUE SPACES.
       01  WS-HEADER8         PIC X(40) VALUE SPACES.
       01  WS-TITLE14          PIC X(20) VALUE SPACES.
       01  WS-HEADER14         PIC X(40) VALUE SPACES.
       01  WS-TOTAL15          PIC 9(6) VALUE 0.
       01  WS-K15              PIC 99 VALUE 0.
       01  WS-AVERAGE15        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE18          PIC X(20) VALUE SPACES.
       01  WS-HEADER18         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT19         PIC 9(6) VALUE 500.
       01  WS-FLAG19           PIC X VALUE 'N'.
       01  WS-TITLE20          PIC X(20) VALUE SPACES.
       01  WS-HEADER20         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT21         PIC 9(6) VALUE 500.
       01  WS-FLAG21           PIC X VALUE 'N'.
       01  WS-AMOUNT22         PIC 9(6) VALUE 500.
       01  WS-FLAG22           PIC X VALUE 'N'.
       01  WS-AMOUNT23         PIC 9(6) VALUE 500.
       01  WS-FLAG23           PIC X VALUE 'N'.
       01  WS-AMOUNT24         PIC 9(6) VALUE 500.
       01  WS-FLAG24           PIC X VALUE 'N'.
       01  WS-TOTAL27          PIC 9(6) VALUE 0.
       01  WS-K27              PIC 99 VALUE 0.
       01  WS-AVERAGE27        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL31          PIC 9(6) VALUE 0.
       01  WS-K31              PIC 99 VALUE 0.
       01  WS-AVERAGE31        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT33         PIC 9(6) VALUE 500.
       01  WS-FLAG33           PIC X VALUE 'N'.
       01  WS-CODE34           PIC 9 VALUE 1.
       01  WS-STATUS34         PIC X(6) VALUE SPACES.
       01  WS-CODE35           PIC 9 VALUE 1.
       01  WS-STATUS35         PIC X(6) VALUE SPACES.
       01  WS-TITLE36          PIC X(20) VALUE SPACES.
       01  WS-HEADER36         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT38         PIC 9(6) VALUE 500.
       01  WS-FLAG38           PIC X VALUE 'N'.
       01  WS-TITLE39          PIC X(20) VALUE SPACES.
       01  WS-HEADER39         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT42         PIC 9(6) VALUE 500.
       01  WS-FLAG42           PIC X VALUE 'N'.
       01  WS-TITLE44          PIC X(20) VALUE SPACES.
       01  WS-HEADER44         PIC X(40) VALUE SPACES.
       01  WS-CODE53           PIC 9 VALUE 1.
       01  WS-STATUS53         PIC X(6) VALUE SPACES.
       01  WS-TITLE54          PIC X(20) VALUE SPACES.
       01  WS-HEADER54         PIC X(40) VALUE SPACES.
       01  WS-TITLE56          PIC X(20) VALUE SPACES.
       01  WS-HEADER56         PIC X(40) VALUE SPACES.
       01  WS-TOTAL57          PIC 9(6) VALUE 0.
       01  WS-K57              PIC 99 VALUE 0.
       01  WS-AVERAGE57        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT64         PIC 9(6) VALUE 500.
       01  WS-FLAG64           PIC X VALUE 'N'.
       01  WS-TITLE65          PIC X(20) VALUE SPACES.
       01  WS-HEADER65         PIC X(40) VALUE SPACES.
       01  WS-TOTAL69          PIC 9(6) VALUE 0.
       01  WS-K69              PIC 99 VALUE 0.
       01  WS-AVERAGE69        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE71          PIC X(20) VALUE SPACES.
       01  WS-HEADER71         PIC X(40) VALUE SPACES.
       01  WS-CODE72           PIC 9 VALUE 1.
       01  WS-STATUS72         PIC X(6) VALUE SPACES.
       01  WS-TITLE79          PIC X(20) VALUE SPACES.
       01  WS-HEADER79         PIC X(40) VALUE SPACES.
       01  WS-CODE80           PIC 9 VALUE 1.
       01  WS-STATUS80         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT81         PIC 9(6) VALUE 500.
       01  WS-FLAG81           PIC X VALUE 'N'.
       01  WS-TOTAL83          PIC 9(6) VALUE 0.
       01  WS-K83              PIC 99 VALUE 0.
       01  WS-AVERAGE83        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL86          PIC 9(6) VALUE 0.
       01  WS-K86              PIC 99 VALUE 0.
       01  WS-AVERAGE86        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT88         PIC 9(6) VALUE 500.
       01  WS-FLAG88           PIC X VALUE 'N'.
       01  WS-TITLE93          PIC X(20) VALUE SPACES.
       01  WS-HEADER93         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT95         PIC 9(6) VALUE 500.
       01  WS-FLAG95           PIC X VALUE 'N'.
       01  WS-CODE96           PIC 9 VALUE 1.
       01  WS-STATUS96         PIC X(6) VALUE SPACES.
       01  WS-TOTAL97          PIC 9(6) VALUE 0.
       01  WS-K97              PIC 99 VALUE 0.
       01  WS-AVERAGE97        PIC 9(6)V99 VALUE 0.
       01  WS-CODE98           PIC 9 VALUE 1.
       01  WS-STATUS98         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT99         PIC 9(6) VALUE 500.
       01  WS-FLAG99           PIC X VALUE 'N'.
       01  WS-TOTAL100          PIC 9(6) VALUE 0.
       01  WS-K100              PIC 99 VALUE 0.
       01  WS-AVERAGE100        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE104          PIC X(20) VALUE SPACES.
       01  WS-HEADER104         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT107         PIC 9(6) VALUE 500.
       01  WS-FLAG107           PIC X VALUE 'N'.
       01  WS-CODE110           PIC 9 VALUE 1.
       01  WS-STATUS110         PIC X(6) VALUE SPACES.
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       CLASSIFY-CODE1.
           EVALUATE WS-CODE1
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS1
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS1
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS1
           END-EVALUATE.

       RUN-HANDLER90.
           ACCEPT WS-PROG90.
           CALL WS-PROG90 USING WS-DATA90.

       COMPUTE-TOTALS100.
           MOVE 0 TO WS-TOTAL100.
           PERFORM VARYING WS-K100 FROM 1 BY 1 UNTIL WS-K100 > 10
               ADD WS-K100 TO WS-TOTAL100
           END-PERFORM.
           COMPUTE WS-AVERAGE100 = WS-TOTAL100 / 10.

       CLASSIFY-CODE35.
           EVALUATE WS-CODE35
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS35
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS35
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS35
           END-EVALUATE.

       FORMAT-HEADER56.
           MOVE 'MONTHLY REPORT' TO WS-TITLE56.
           STRING WS-TITLE56 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER56.
           DISPLAY WS-HEADER56.

       QUERY-CUSTOMER-SAFE112.
           ACCEPT WS-CUST112.
           EXEC SQL
               SELECT NAME INTO :WS-NAME112 FROM CUST WHERE ID = :WS-CUST112
           END-EXEC.

       QUERY-CUSTOMER-SAFE52.
           ACCEPT WS-CUST52.
           EXEC SQL
               SELECT NAME INTO :WS-NAME52 FROM CUST WHERE ID = :WS-CUST52
           END-EXEC.

       CHECK-LIMIT95.
           IF WS-AMOUNT95 > 1000
               MOVE 'Y' TO WS-FLAG95
           ELSE
               MOVE 'N' TO WS-FLAG95
           END-IF.

       CLASSIFY-CODE96.
           EVALUATE WS-CODE96
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS96
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS96
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS96
           END-EVALUATE.

       CLASSIFY-CODE110.
           EVALUATE WS-CODE110
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS110
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS110
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS110
           END-EVALUATE.

       RUN-HANDLER-SAFE91.
           ACCEPT WS-CHOICE91.
           IF WS-CHOICE91 = 'A'
               CALL 'HANDLERA' USING WS-DATA91
           ELSE
               CALL 'HANDLERB' USING WS-DATA91
           END-IF.

       RUN-HANDLER-SAFE105.
           ACCEPT WS-CHOICE105.
           IF WS-CHOICE105 = 'A'
               CALL 'HANDLERA' USING WS-DATA105
           ELSE
               CALL 'HANDLERB' USING WS-DATA105
           END-IF.

       QUERY-CUSTOMER-SAFE113.
           ACCEPT WS-CUST113.
           EXEC SQL
               SELECT NAME INTO :WS-NAME113 FROM CUST WHERE ID = :WS-CUST113
           END-EXEC.

       FORMAT-HEADER20.
           MOVE 'MONTHLY REPORT' TO WS-TITLE20.
           STRING WS-TITLE20 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER20.
           DISPLAY WS-HEADER20.

       CHECK-LIMIT7.
           IF WS-AMOUNT7 > 1000
               MOVE 'Y' TO WS-FLAG7
           ELSE
               MOVE 'N' TO WS-FLAG7
           END-IF.

       RUN-HANDLER-SAFE40.
           ACCEPT WS-CHOICE40.
           IF WS-CHOICE40 = 'A'
               CALL 'HANDLERA' USING WS-DATA40
           ELSE
               CALL 'HANDLERB' USING WS-DATA40
           END-IF.

       RUN-HANDLER-SAFE111.
           ACCEPT WS-CHOICE111.
           IF WS-CHOICE111 = 'A'
               CALL 'HANDLERA' USING WS-DATA111
           ELSE
               CALL 'HANDLERB' USING WS-DATA111
           END-IF.

       RUN-HANDLER-SAFE11.
           ACCEPT WS-CHOICE11.
           IF WS-CHOICE11 = 'A'
               CALL 'HANDLERA' USING WS-DATA11
           ELSE
               CALL 'HANDLERB' USING WS-DATA11
           END-IF.

       COMPUTE-TOTALS31.
           MOVE 0 TO WS-TOTAL31.
           PERFORM VARYING WS-K31 FROM 1 BY 1 UNTIL WS-K31 > 10
               ADD WS-K31 TO WS-TOTAL31
           END-PERFORM.
           COMPUTE WS-AVERAGE31 = WS-TOTAL31 / 10.

       QUERY-CUSTOMER-SAFE116.
           ACCEPT WS-CUST116.
           EXEC SQL
               SELECT NAME INTO :WS-NAME116 FROM CUST WHERE ID = :WS-CUST116
           END-EXEC.

       RUN-HANDLER92.
           ACCEPT WS-PROG92.
           CALL WS-PROG92 USING WS-DATA92.

       RUN-HANDLER-SAFE13.
           ACCEPT WS-CHOICE13.
           IF WS-CHOICE13 = 'A'
               CALL 'HANDLERA' USING WS-DATA13
           ELSE
               CALL 'HANDLERB' USING WS-DATA13
           END-IF.

       RUN-HANDLER108.
           ACCEPT WS-PROG108.
           CALL WS-PROG108 USING WS-DATA108.

       FORMAT-HEADER79.
           MOVE 'MONTHLY REPORT' TO WS-TITLE79.
           STRING WS-TITLE79 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER79.
           DISPLAY WS-HEADER79.

       RUN-HANDLER25.
           ACCEPT WS-PROG25.
           CALL WS-PROG25 USING WS-DATA25.

       RUN-HANDLER-SAFE61.
           ACCEPT WS-CHOICE61.
           IF WS-CHOICE61 = 'A'
               CALL 'HANDLERA' USING WS-DATA61
           ELSE
               CALL 'HANDLERB' USING WS-DATA61
           END-IF.

       RUN-HANDLER84.
           ACCEPT WS-PROG84.
           CALL WS-PROG84 USING WS-DATA84.

       FORMAT-HEADER18.
           MOVE 'MONTHLY REPORT' TO WS-TITLE18.
           STRING WS-TITLE18 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER18.
           DISPLAY WS-HEADER18.

       QUERY-CUSTOMER-SAFE41.
           ACCEPT WS-CUST41.
           EXEC SQL
               SELECT NAME INTO :WS-NAME41 FROM CUST WHERE ID = :WS-CUST41
           END-EXEC.

       RUN-HANDLER-SAFE3.
           ACCEPT WS-CHOICE3.
           IF WS-CHOICE3 = 'A'
               CALL 'HANDLERA' USING WS-DATA3
           ELSE
               CALL 'HANDLERB' USING WS-DATA3
           END-IF.

       QUERY-CUSTOMER-SAFE76.
           ACCEPT WS-CUST76.
           EXEC SQL
               SELECT NAME INTO :WS-NAME76 FROM CUST WHERE ID = :WS-CUST76
           END-EXEC.

       QUERY-CUSTOMER5.
           ACCEPT WS-CUST5.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST5 "'"
               DELIMITED BY SIZE INTO WS-SQL5.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL5 END-EXEC.

       RUN-HANDLER4.
           ACCEPT WS-PROG4.
           CALL WS-PROG4 USING WS-DATA4.

       QUERY-CUSTOMER-SAFE94.
           ACCEPT WS-CUST94.
           EXEC SQL
               SELECT NAME INTO :WS-NAME94 FROM CUST WHERE ID = :WS-CUST94
           END-EXEC.

       RUN-HANDLER50.
           ACCEPT WS-PROG50.
           CALL WS-PROG50 USING WS-DATA50.

       QUERY-CUSTOMER-SAFE16.
           ACCEPT WS-CUST16.
           EXEC SQL
               SELECT NAME INTO :WS-NAME16 FROM CUST WHERE ID = :WS-CUST16
           END-EXEC.

       QUERY-CUSTOMER78.
           ACCEPT WS-CUST78.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST78 "'"
               DELIMITED BY SIZE INTO WS-SQL78.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL78 END-EXEC.

       RUN-HANDLER73.
           ACCEPT WS-PROG73.
           CALL WS-PROG73 USING WS-DATA73.

       COMPUTE-TOTALS69.
           MOVE 0 TO WS-TOTAL69.
           PERFORM VARYING WS-K69 FROM 1 BY 1 UNTIL WS-K69 > 10
               ADD WS-K69 TO WS-TOTAL69
           END-PERFORM.
           COMPUTE WS-AVERAGE69 = WS-TOTAL69 / 10.

       QUERY-CUSTOMER-SAFE12.
           ACCEPT WS-CUST12.
           EXEC SQL
               SELECT NAME INTO :WS-NAME12 FROM CUST WHERE ID = :WS-CUST12
           END-EXEC.

       RUN-HANDLER32.
           ACCEPT WS-PROG32.
           CALL WS-PROG32 USING WS-DATA32.

       FORMAT-HEADER93.
           MOVE 'MONTHLY REPORT' TO WS-TITLE93.
           STRING WS-TITLE93 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER93.
           DISPLAY WS-HEADER93.

       RUN-HANDLER30.
           ACCEPT WS-PROG30.
           CALL WS-PROG30 USING WS-DATA30.

       QUERY-CUSTOMER-SAFE55.
           ACCEPT WS-CUST55.
           EXEC SQL
               SELECT NAME INTO :WS-NAME55 FROM CUST WHERE ID = :WS-CUST55
           END-EXEC.

       RUN-HANDLER-SAFE77.
           ACCEPT WS-CHOICE77.
           IF WS-CHOICE77 = 'A'
               CALL 'HANDLERA' USING WS-DATA77
           ELSE
               CALL 'HANDLERB' USING WS-DATA77
           END-IF.

       QUERY-CUSTOMER106.
           ACCEPT WS-CUST106.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST106 "'"
               DELIMITED BY SIZE INTO WS-SQL106.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL106 END-EXEC.

       RUN-HANDLER63.
           ACCEPT WS-PROG63.
           CALL WS-PROG63 USING WS-DATA63.

       RUN-HANDLER-SAFE89.
           ACCEPT WS-CHOICE89.
           IF WS-CHOICE89 = 'A'
               CALL 'HANDLERA' USING WS-DATA89
           ELSE
               CALL 'HANDLERB' USING WS-DATA89
           END-IF.

       CHECK-LIMIT81.
           IF WS-AMOUNT81 > 1000
               MOVE 'Y' TO WS-FLAG81
           ELSE
               MOVE 'N' TO WS-FLAG81
           END-IF.

       CLASSIFY-CODE98.
           EVALUATE WS-CODE98
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS98
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS98
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS98
           END-EVALUATE.

       QUERY-CUSTOMER47.
           ACCEPT WS-CUST47.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST47 "'"
               DELIMITED BY SIZE INTO WS-SQL47.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL47 END-EXEC.

       QUERY-CUSTOMER-SAFE49.
           ACCEPT WS-CUST49.
           EXEC SQL
               SELECT NAME INTO :WS-NAME49 FROM CUST WHERE ID = :WS-CUST49
           END-EXEC.

       FORMAT-HEADER65.
           MOVE 'MONTHLY REPORT' TO WS-TITLE65.
           STRING WS-TITLE65 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER65.
           DISPLAY WS-HEADER65.

       QUERY-CUSTOMER109.
           ACCEPT WS-CUST109.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST109 "'"
               DELIMITED BY SIZE INTO WS-SQL109.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL109 END-EXEC.

       FORMAT-HEADER8.
           MOVE 'MONTHLY REPORT' TO WS-TITLE8.
           STRING WS-TITLE8 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER8.
           DISPLAY WS-HEADER8.

       QUERY-CUSTOMER-SAFE85.
           ACCEPT WS-CUST85.
           EXEC SQL
               SELECT NAME INTO :WS-NAME85 FROM CUST WHERE ID = :WS-CUST85
           END-EXEC.

       CLASSIFY-CODE34.
           EVALUATE WS-CODE34
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS34
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS34
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS34
           END-EVALUATE.

       CLASSIFY-CODE53.
           EVALUATE WS-CODE53
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS53
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS53
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS53
           END-EVALUATE.

       QUERY-CUSTOMER-SAFE68.
           ACCEPT WS-CUST68.
           EXEC SQL
               SELECT NAME INTO :WS-NAME68 FROM CUST WHERE ID = :WS-CUST68
           END-EXEC.

       COMPUTE-TOTALS2.
           MOVE 0 TO WS-TOTAL2.
           PERFORM VARYING WS-K2 FROM 1 BY 1 UNTIL WS-K2 > 10
               ADD WS-K2 TO WS-TOTAL2
           END-PERFORM.
           COMPUTE WS-AVERAGE2 = WS-TOTAL2 / 10.

       CHECK-LIMIT23.
           IF WS-AMOUNT23 > 1000
               MOVE 'Y' TO WS-FLAG23
           ELSE
               MOVE 'N' TO WS-FLAG23
           END-IF.

       FORMAT-HEADER54.
           MOVE 'MONTHLY REPORT' TO WS-TITLE54.
           STRING WS-TITLE54 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER54.
           DISPLAY WS-HEADER54.

       QUERY-CUSTOMER-SAFE115.
           ACCEPT WS-CUST115.
           EXEC SQL
               SELECT NAME INTO :WS-NAME115 FROM CUST WHERE ID = :WS-CUST115
           END-EXEC.

       COMPUTE-TOTALS57.
           MOVE 0 TO WS-TOTAL57.
           PERFORM VARYING WS-K57 FROM 1 BY 1 UNTIL WS-K57 > 10
               ADD WS-K57 TO WS-TOTAL57
           END-PERFORM.
           COMPUTE WS-AVERAGE57 = WS-TOTAL57 / 10.

       FORMAT-HEADER39.
           MOVE 'MONTHLY REPORT' TO WS-TITLE39.
           STRING WS-TITLE39 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER39.
           DISPLAY WS-HEADER39.

       CHECK-LIMIT88.
           IF WS-AMOUNT88 > 1000
               MOVE 'Y' TO WS-FLAG88
           ELSE
               MOVE 'N' TO WS-FLAG88
           END-IF.

       RUN-HANDLER114.
           ACCEPT WS-PROG114.
           CALL WS-PROG114 USING WS-DATA114.

       QUERY-CUSTOMER87.
           ACCEPT WS-CUST87.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST87 "'"
               DELIMITED BY SIZE INTO WS-SQL87.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL87 END-EXEC.

       RUN-HANDLER59.
           ACCEPT WS-PROG59.
           CALL WS-PROG59 USING WS-DATA59.

       RUN-HANDLER-SAFE101.
           ACCEPT WS-CHOICE101.
           IF WS-CHOICE101 = 'A'
               CALL 'HANDLERA' USING WS-DATA101
           ELSE
               CALL 'HANDLERB' USING WS-DATA101
           END-IF.

       QUERY-CUSTOMER-SAFE46.
           ACCEPT WS-CUST46.
           EXEC SQL
               SELECT NAME INTO :WS-NAME46 FROM CUST WHERE ID = :WS-CUST46
           END-EXEC.

       FORMAT-HEADER104.
           MOVE 'MONTHLY REPORT' TO WS-TITLE104.
           STRING WS-TITLE104 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER104.
           DISPLAY WS-HEADER104.

       CLASSIFY-CODE72.
           EVALUATE WS-CODE72
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS72
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS72
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS72
           END-EVALUATE.

       QUERY-CUSTOMER45.
           ACCEPT WS-CUST45.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST45 "'"
               DELIMITED BY SIZE INTO WS-SQL45.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL45 END-EXEC.

       QUERY-CUSTOMER-SAFE67.
           ACCEPT WS-CUST67.
           EXEC SQL
               SELECT NAME INTO :WS-NAME67 FROM CUST WHERE ID = :WS-CUST67
           END-EXEC.

       RUN-HANDLER102.
           ACCEPT WS-PROG102.
           CALL WS-PROG102 USING WS-DATA102.

       QUERY-CUSTOMER28.
           ACCEPT WS-CUST28.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST28 "'"
               DELIMITED BY SIZE INTO WS-SQL28.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL28 END-EXEC.

       QUERY-CUSTOMER74.
           ACCEPT WS-CUST74.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST74 "'"
               DELIMITED BY SIZE INTO WS-SQL74.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL74 END-EXEC.

       CHECK-LIMIT21.
           IF WS-AMOUNT21 > 1000
               MOVE 'Y' TO WS-FLAG21
           ELSE
               MOVE 'N' TO WS-FLAG21
           END-IF.

       RUN-HANDLER82.
           ACCEPT WS-PROG82.
           CALL WS-PROG82 USING WS-DATA82.

       CHECK-LIMIT42.
           IF WS-AMOUNT42 > 1000
               MOVE 'Y' TO WS-FLAG42
           ELSE
               MOVE 'N' TO WS-FLAG42
           END-IF.

       CHECK-LIMIT22.
           IF WS-AMOUNT22 > 1000
               MOVE 'Y' TO WS-FLAG22
           ELSE
               MOVE 'N' TO WS-FLAG22
           END-IF.

       CHECK-LIMIT24.
           IF WS-AMOUNT24 > 1000
               MOVE 'Y' TO WS-FLAG24
           ELSE
               MOVE 'N' TO WS-FLAG24
           END-IF.

       RUN-HANDLER-SAFE26.
           ACCEPT WS-CHOICE26.
           IF WS-CHOICE26 = 'A'
               CALL 'HANDLERA' USING WS-DATA26
           ELSE
               CALL 'HANDLERB' USING WS-DATA26
           END-IF.

       QUERY-CUSTOMER-SAFE103.
           ACCEPT WS-CUST103.
           EXEC SQL
               SELECT NAME INTO :WS-NAME103 FROM CUST WHERE ID = :WS-CUST103
           END-EXEC.

       CHECK-LIMIT107.
           IF WS-AMOUNT107 > 1000
               MOVE 'Y' TO WS-FLAG107
           ELSE
               MOVE 'N' TO WS-FLAG107
           END-IF.

       RUN-HANDLER37.
           ACCEPT WS-PROG37.
           CALL WS-PROG37 USING WS-DATA37.

       FORMAT-HEADER44.
           MOVE 'MONTHLY REPORT' TO WS-TITLE44.
           STRING WS-TITLE44 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER44.
           DISPLAY WS-HEADER44.

       RUN-HANDLER-SAFE66.
           ACCEPT WS-CHOICE66.
           IF WS-CHOICE66 = 'A'
               CALL 'HANDLERA' USING WS-DATA66
           ELSE
               CALL 'HANDLERB' USING WS-DATA66
           END-IF.

       QUERY-CUSTOMER51.
           ACCEPT WS-CUST51.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST51 "'"
               DELIMITED BY SIZE INTO WS-SQL51.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL51 END-EXEC.

       RUN-HANDLER60.
           ACCEPT WS-PROG60.
           CALL WS-PROG60 USING WS-DATA60.

       RUN-HANDLER-SAFE10.
           ACCEPT WS-CHOICE10.
           IF WS-CHOICE10 = 'A'
               CALL 'HANDLERA' USING WS-DATA10
           ELSE
               CALL 'HANDLERB' USING WS-DATA10
           END-IF.

       QUERY-CUSTOMER-SAFE43.
           ACCEPT WS-CUST43.
           EXEC SQL
               SELECT NAME INTO :WS-NAME43 FROM CUST WHERE ID = :WS-CUST43
           END-EXEC.

       FORMAT-HEADER71.
           MOVE 'MONTHLY REPORT' TO WS-TITLE71.
           STRING WS-TITLE71 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER71.
           DISPLAY WS-HEADER71.

       COMPUTE-TOTALS83.
           MOVE 0 TO WS-TOTAL83.
           PERFORM VARYING WS-K83 FROM 1 BY 1 UNTIL WS-K83 > 10
               ADD WS-K83 TO WS-TOTAL83
           END-PERFORM.
           COMPUTE WS-AVERAGE83 = WS-TOTAL83 / 10.

       CHECK-LIMIT33.
           IF WS-AMOUNT33 > 1000
               MOVE 'Y' TO WS-FLAG33
           ELSE
               MOVE 'N' TO WS-FLAG33
           END-IF.

       RUN-HANDLER-SAFE70.
           ACCEPT WS-CHOICE70.
           IF WS-CHOICE70 = 'A'
               CALL 'HANDLERA' USING WS-DATA70
           ELSE
               CALL 'HANDLERB' USING WS-DATA70
           END-IF.

       QUERY-CUSTOMER-SAFE48.
           ACCEPT WS-CUST48.
           EXEC SQL
               SELECT NAME INTO :WS-NAME48 FROM CUST WHERE ID = :WS-CUST48
           END-EXEC.

       RUN-HANDLER-SAFE17.
           ACCEPT WS-CHOICE17.
           IF WS-CHOICE17 = 'A'
               CALL 'HANDLERA' USING WS-DATA17
           ELSE
               CALL 'HANDLERB' USING WS-DATA17
           END-IF.

       CHECK-LIMIT99.
           IF WS-AMOUNT99 > 1000
               MOVE 'Y' TO WS-FLAG99
           ELSE
               MOVE 'N' TO WS-FLAG99
           END-IF.

       RUN-HANDLER-SAFE9.
           ACCEPT WS-CHOICE9.
           IF WS-CHOICE9 = 'A'
               CALL 'HANDLERA' USING WS-DATA9
           ELSE
               CALL 'HANDLERB' USING WS-DATA9
           END-IF.

       QUERY-CUSTOMER117.
           ACCEPT WS-CUST117.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST117 "'"
               DELIMITED BY SIZE INTO WS-SQL117.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL117 END-EXEC.

       CHECK-LIMIT19.
           IF WS-AMOUNT19 > 1000
               MOVE 'Y' TO WS-FLAG19
           ELSE
               MOVE 'N' TO WS-FLAG19
           END-IF.

       COMPUTE-TOTALS97.
           MOVE 0 TO WS-TOTAL97.
           PERFORM VARYING WS-K97 FROM 1 BY 1 UNTIL WS-K97 > 10
               ADD WS-K97 TO WS-TOTAL97
           END-PERFORM.
           COMPUTE WS-AVERAGE97 = WS-TOTAL97 / 10.

       COMPUTE-TOTALS86.
           MOVE 0 TO WS-TOTAL86.
           PERFORM VARYING WS-K86 FROM 1 BY 1 UNTIL WS-K86 > 10
               ADD WS-K86 TO WS-TOTAL86
           END-PERFORM.
           COMPUTE WS-AVERAGE86 = WS-TOTAL86 / 10.

       QUERY-CUSTOMER62.
           ACCEPT WS-CUST62.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST62 "'"
               DELIMITED BY SIZE INTO WS-SQL62.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL62 END-EXEC.

       CLASSIFY-CODE6.
           EVALUATE WS-CODE6
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS6
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS6
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS6
           END-EVALUATE.

       CLASSIFY-CODE80.
           EVALUATE WS-CODE80
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS80
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS80
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS80
           END-EVALUATE.

       RUN-HANDLER-SAFE58.
           ACCEPT WS-CHOICE58.
           IF WS-CHOICE58 = 'A'
               CALL 'HANDLERA' USING WS-DATA58
           ELSE
               CALL 'HANDLERB' USING WS-DATA58
           END-IF.

       COMPUTE-TOTALS15.
           MOVE 0 TO WS-TOTAL15.
           PERFORM VARYING WS-K15 FROM 1 BY 1 UNTIL WS-K15 > 10
               ADD WS-K15 TO WS-TOTAL15
           END-PERFORM.
           COMPUTE WS-AVERAGE15 = WS-TOTAL15 / 10.

       FORMAT-HEADER36.
           MOVE 'MONTHLY REPORT' TO WS-TITLE36.
           STRING WS-TITLE36 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER36.
           DISPLAY WS-HEADER36.

       CHECK-LIMIT64.
           IF WS-AMOUNT64 > 1000
               MOVE 'Y' TO WS-FLAG64
           ELSE
               MOVE 'N' TO WS-FLAG64
           END-IF.

       FORMAT-HEADER14.
           MOVE 'MONTHLY REPORT' TO WS-TITLE14.
           STRING WS-TITLE14 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER14.
           DISPLAY WS-HEADER14.

       COMPUTE-TOTALS27.
           MOVE 0 TO WS-TOTAL27.
           PERFORM VARYING WS-K27 FROM 1 BY 1 UNTIL WS-K27 > 10
               ADD WS-K27 TO WS-TOTAL27
           END-PERFORM.
           COMPUTE WS-AVERAGE27 = WS-TOTAL27 / 10.

       CHECK-LIMIT38.
           IF WS-AMOUNT38 > 1000
               MOVE 'Y' TO WS-FLAG38
           ELSE
               MOVE 'N' TO WS-FLAG38
           END-IF.

       QUERY-CUSTOMER29.
           ACCEPT WS-CUST29.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST29 "'"
               DELIMITED BY SIZE INTO WS-SQL29.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL29 END-EXEC.

       RUN-HANDLER-SAFE75.
           ACCEPT WS-CHOICE75.
           IF WS-CHOICE75 = 'A'
               CALL 'HANDLERA' USING WS-DATA75
           ELSE
               CALL 'HANDLERB' USING WS-DATA75
           END-IF.

