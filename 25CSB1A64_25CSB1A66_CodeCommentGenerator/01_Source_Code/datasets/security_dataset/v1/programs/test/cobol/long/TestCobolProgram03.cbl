       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTE03.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-IDX2            PIC 99.
       01  WS-TAB2.
           05  WS-ENTRY2      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT2            PIC X(10).
       01  WS-TARGET3         PIC X(8).
       01  WS-IDX6            PIC 99.
       01  WS-TAB6.
           05  WS-ENTRY6      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT6            PIC X(10).
       01  WS-TARGET7         PIC X(8).
       01  WS-TARGET10         PIC X(8).
       01  WS-TARGET13         PIC X(8).
       01  WS-TARGET15         PIC X(8).
       01  WS-TARGET16         PIC X(8).
       01  WS-TARGET18         PIC X(8).
       01  WS-IDX20            PIC 99.
       01  WS-TAB20.
           05  WS-ENTRY20      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT20            PIC X(10).
       01  WS-IDX21            PIC 99.
       01  WS-TAB21.
           05  WS-ENTRY21      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT21            PIC X(10).
       01  WS-IDX24            PIC 99.
       01  WS-TAB24.
           05  WS-ENTRY24      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT24            PIC X(10).
       01  WS-TARGET26         PIC X(8).
       01  WS-TARGET29         PIC X(8).
       01  WS-TARGET30         PIC X(8).
       01  WS-IDX31            PIC 99.
       01  WS-TAB31.
           05  WS-ENTRY31      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT31            PIC X(10).
       01  WS-IDX33            PIC 99.
       01  WS-TAB33.
           05  WS-ENTRY33      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT33            PIC X(10).
       01  WS-IDX35            PIC 99.
       01  WS-TAB35.
           05  WS-ENTRY35      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT35            PIC X(10).
       01  WS-IDX37            PIC 99.
       01  WS-TAB37.
           05  WS-ENTRY37      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT37            PIC X(10).
       01  WS-IDX38            PIC 99.
       01  WS-TAB38.
           05  WS-ENTRY38      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT38            PIC X(10).
       01  WS-TARGET40         PIC X(8).
       01  WS-IDX41            PIC 99.
       01  WS-TAB41.
           05  WS-ENTRY41      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT41            PIC X(10).
       01  WS-TARGET42         PIC X(8).
       01  WS-IDX45            PIC 99.
       01  WS-TAB45.
           05  WS-ENTRY45      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT45            PIC X(10).
       01  WS-IDX54            PIC 99.
       01  WS-TAB54.
           05  WS-ENTRY54      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT54            PIC X(10).
       01  WS-TARGET55         PIC X(8).
       01  WS-IDX56            PIC 99.
       01  WS-TAB56.
           05  WS-ENTRY56      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT56            PIC X(10).
       01  WS-IDX57            PIC 99.
       01  WS-TAB57.
           05  WS-ENTRY57      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT57            PIC X(10).
       01  WS-TARGET61         PIC X(8).
       01  WS-IDX65            PIC 99.
       01  WS-TAB65.
           05  WS-ENTRY65      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT65            PIC X(10).
       01  WS-TARGET67         PIC X(8).
       01  WS-TARGET68         PIC X(8).
       01  WS-TARGET69         PIC X(8).
       01  WS-TARGET72         PIC X(8).
       01  WS-IDX74            PIC 99.
       01  WS-TAB74.
           05  WS-ENTRY74      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT74            PIC X(10).
       01  WS-TARGET75         PIC X(8).
       01  WS-IDX76            PIC 99.
       01  WS-TAB76.
           05  WS-ENTRY76      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT76            PIC X(10).
       01  WS-TARGET79         PIC X(8).
       01  WS-IDX84            PIC 99.
       01  WS-TAB84.
           05  WS-ENTRY84      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT84            PIC X(10).
       01  WS-IDX87            PIC 99.
       01  WS-TAB87.
           05  WS-ENTRY87      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT87            PIC X(10).
       01  WS-IDX88            PIC 99.
       01  WS-TAB88.
           05  WS-ENTRY88      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT88            PIC X(10).
       01  WS-TARGET91         PIC X(8).
       01  WS-TARGET92         PIC X(8).
       01  WS-IDX93            PIC 99.
       01  WS-TAB93.
           05  WS-ENTRY93      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT93            PIC X(10).
       01  WS-IDX95            PIC 99.
       01  WS-TAB95.
           05  WS-ENTRY95      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT95            PIC X(10).
       01  WS-IDX96            PIC 99.
       01  WS-TAB96.
           05  WS-ENTRY96      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT96            PIC X(10).
       01  WS-IDX97            PIC 99.
       01  WS-TAB97.
           05  WS-ENTRY97      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT97            PIC X(10).
       01  WS-IDX100            PIC 99.
       01  WS-TAB100.
           05  WS-ENTRY100      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT100            PIC X(10).
       01  WS-IDX101            PIC 99.
       01  WS-TAB101.
           05  WS-ENTRY101      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT101            PIC X(10).
       01  WS-IDX103            PIC 99.
       01  WS-TAB103.
           05  WS-ENTRY103      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT103            PIC X(10).
       01  WS-IDX104            PIC 99.
       01  WS-TAB104.
           05  WS-ENTRY104      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT104            PIC X(10).
       01  WS-TARGET105         PIC X(8).
       01  WS-IDX107            PIC 99.
       01  WS-TAB107.
           05  WS-ENTRY107      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT107            PIC X(10).
       01  WS-TARGET108         PIC X(8).
       01  WS-TARGET109         PIC X(8).
       01  WS-TARGET110         PIC X(8).
       01  WS-IDX111            PIC 99.
       01  WS-TAB111.
           05  WS-ENTRY111      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT111            PIC X(10).
       01  WS-TARGET112         PIC X(8).
       01  WS-IDX113            PIC 99.
       01  WS-TAB113.
           05  WS-ENTRY113      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT113            PIC X(10).
       01  WS-IDX115            PIC 99.
       01  WS-TAB115.
           05  WS-ENTRY115      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT115            PIC X(10).
       01  WS-IDX116            PIC 99.
       01  WS-TAB116.
           05  WS-ENTRY116      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT116            PIC X(10).
       01  WS-TARGET117         PIC X(8).
       01  WS-TARGET120         PIC X(8).
       01  WS-TARGET121         PIC X(8).
       01  WS-TARGET122         PIC X(8).
       01  WS-IDX124            PIC 99.
       01  WS-TAB124.
           05  WS-ENTRY124      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT124            PIC X(10).
       01  WS-IDX125            PIC 99.
       01  WS-TAB125.
           05  WS-ENTRY125      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT125            PIC X(10).
       01  WS-TARGET129         PIC X(8).
       01  WS-IDX132            PIC 99.
       01  WS-TAB132.
           05  WS-ENTRY132      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT132            PIC X(10).
       01  WS-TARGET134         PIC X(8).
       01  WS-IDX135            PIC 99.
       01  WS-TAB135.
           05  WS-ENTRY135      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT135            PIC X(10).
       01  WS-IDX138            PIC 99.
       01  WS-TAB138.
           05  WS-ENTRY138      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT138            PIC X(10).
       01  WS-IDX139            PIC 99.
       01  WS-TAB139.
           05  WS-ENTRY139      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT139            PIC X(10).
       01  WS-TARGET141         PIC X(8).
       01  WS-CODE1           PIC 9 VALUE 1.
       01  WS-STATUS1         PIC X(6) VALUE SPACES.
       01  WS-TITLE4          PIC X(20) VALUE SPACES.
       01  WS-HEADER4         PIC X(40) VALUE SPACES.
       01  WS-TITLE5          PIC X(20) VALUE SPACES.
       01  WS-HEADER5         PIC X(40) VALUE SPACES.
       01  WS-TITLE8          PIC X(20) VALUE SPACES.
       01  WS-HEADER8         PIC X(40) VALUE SPACES.
       01  WS-CODE9           PIC 9 VALUE 1.
       01  WS-STATUS9         PIC X(6) VALUE SPACES.
       01  WS-TOTAL11          PIC 9(6) VALUE 0.
       01  WS-K11              PIC 99 VALUE 0.
       01  WS-AVERAGE11        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL12          PIC 9(6) VALUE 0.
       01  WS-K12              PIC 99 VALUE 0.
       01  WS-AVERAGE12        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE14          PIC X(20) VALUE SPACES.
       01  WS-HEADER14         PIC X(40) VALUE SPACES.
       01  WS-TITLE17          PIC X(20) VALUE SPACES.
       01  WS-HEADER17         PIC X(40) VALUE SPACES.
       01  WS-TOTAL19          PIC 9(6) VALUE 0.
       01  WS-K19              PIC 99 VALUE 0.
       01  WS-AVERAGE19        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL22          PIC 9(6) VALUE 0.
       01  WS-K22              PIC 99 VALUE 0.
       01  WS-AVERAGE22        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT23         PIC 9(6) VALUE 500.
       01  WS-FLAG23           PIC X VALUE 'N'.
       01  WS-TITLE25          PIC X(20) VALUE SPACES.
       01  WS-HEADER25         PIC X(40) VALUE SPACES.
       01  WS-TOTAL27          PIC 9(6) VALUE 0.
       01  WS-K27              PIC 99 VALUE 0.
       01  WS-AVERAGE27        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL28          PIC 9(6) VALUE 0.
       01  WS-K28              PIC 99 VALUE 0.
       01  WS-AVERAGE28        PIC 9(6)V99 VALUE 0.
       01  WS-CODE32           PIC 9 VALUE 1.
       01  WS-STATUS32         PIC X(6) VALUE SPACES.
       01  WS-TITLE34          PIC X(20) VALUE SPACES.
       01  WS-HEADER34         PIC X(40) VALUE SPACES.
       01  WS-TOTAL36          PIC 9(6) VALUE 0.
       01  WS-K36              PIC 99 VALUE 0.
       01  WS-AVERAGE36        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT39         PIC 9(6) VALUE 500.
       01  WS-FLAG39           PIC X VALUE 'N'.
       01  WS-AMOUNT43         PIC 9(6) VALUE 500.
       01  WS-FLAG43           PIC X VALUE 'N'.
       01  WS-CODE44           PIC 9 VALUE 1.
       01  WS-STATUS44         PIC X(6) VALUE SPACES.
       01  WS-CODE46           PIC 9 VALUE 1.
       01  WS-STATUS46         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT47         PIC 9(6) VALUE 500.
       01  WS-FLAG47           PIC X VALUE 'N'.
       01  WS-CODE48           PIC 9 VALUE 1.
       01  WS-STATUS48         PIC X(6) VALUE SPACES.
       01  WS-TOTAL49          PIC 9(6) VALUE 0.
       01  WS-K49              PIC 99 VALUE 0.
       01  WS-AVERAGE49        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL50          PIC 9(6) VALUE 0.
       01  WS-K50              PIC 99 VALUE 0.
       01  WS-AVERAGE50        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL51          PIC 9(6) VALUE 0.
       01  WS-K51              PIC 99 VALUE 0.
       01  WS-AVERAGE51        PIC 9(6)V99 VALUE 0.
       01  WS-CODE52           PIC 9 VALUE 1.
       01  WS-STATUS52         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT53         PIC 9(6) VALUE 500.
       01  WS-FLAG53           PIC X VALUE 'N'.
       01  WS-TOTAL58          PIC 9(6) VALUE 0.
       01  WS-K58              PIC 99 VALUE 0.
       01  WS-AVERAGE58        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT59         PIC 9(6) VALUE 500.
       01  WS-FLAG59           PIC X VALUE 'N'.
       01  WS-CODE60           PIC 9 VALUE 1.
       01  WS-STATUS60         PIC X(6) VALUE SPACES.
       01  WS-TOTAL62          PIC 9(6) VALUE 0.
       01  WS-K62              PIC 99 VALUE 0.
       01  WS-AVERAGE62        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE63          PIC X(20) VALUE SPACES.
       01  WS-HEADER63         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT64         PIC 9(6) VALUE 500.
       01  WS-FLAG64           PIC X VALUE 'N'.
       01  WS-TITLE66          PIC X(20) VALUE SPACES.
       01  WS-HEADER66         PIC X(40) VALUE SPACES.
       01  WS-TITLE70          PIC X(20) VALUE SPACES.
       01  WS-HEADER70         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT71         PIC 9(6) VALUE 500.
       01  WS-FLAG71           PIC X VALUE 'N'.
       01  WS-CODE73           PIC 9 VALUE 1.
       01  WS-STATUS73         PIC X(6) VALUE SPACES.
       01  WS-TOTAL77          PIC 9(6) VALUE 0.
       01  WS-K77              PIC 99 VALUE 0.
       01  WS-AVERAGE77        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE78          PIC X(20) VALUE SPACES.
       01  WS-HEADER78         PIC X(40) VALUE SPACES.
       01  WS-TOTAL80          PIC 9(6) VALUE 0.
       01  WS-K80              PIC 99 VALUE 0.
       01  WS-AVERAGE80        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE81          PIC X(20) VALUE SPACES.
       01  WS-HEADER81         PIC X(40) VALUE SPACES.
       01  WS-CODE82           PIC 9 VALUE 1.
       01  WS-STATUS82         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT83         PIC 9(6) VALUE 500.
       01  WS-FLAG83           PIC X VALUE 'N'.
       01  WS-TITLE85          PIC X(20) VALUE SPACES.
       01  WS-HEADER85         PIC X(40) VALUE SPACES.
       01  WS-TOTAL86          PIC 9(6) VALUE 0.
       01  WS-K86              PIC 99 VALUE 0.
       01  WS-AVERAGE86        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL89          PIC 9(6) VALUE 0.
       01  WS-K89              PIC 99 VALUE 0.
       01  WS-AVERAGE89        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT90         PIC 9(6) VALUE 500.
       01  WS-FLAG90           PIC X VALUE 'N'.
       01  WS-CODE94           PIC 9 VALUE 1.
       01  WS-STATUS94         PIC X(6) VALUE SPACES.
       01  WS-CODE98           PIC 9 VALUE 1.
       01  WS-STATUS98         PIC X(6) VALUE SPACES.
       01  WS-TITLE99          PIC X(20) VALUE SPACES.
       01  WS-HEADER99         PIC X(40) VALUE SPACES.
       01  WS-TITLE102          PIC X(20) VALUE SPACES.
       01  WS-HEADER102         PIC X(40) VALUE SPACES.
       01  WS-TITLE106          PIC X(20) VALUE SPACES.
       01  WS-HEADER106         PIC X(40) VALUE SPACES.
       01  WS-TITLE114          PIC X(20) VALUE SPACES.
       01  WS-HEADER114         PIC X(40) VALUE SPACES.
       01  WS-CODE118           PIC 9 VALUE 1.
       01  WS-STATUS118         PIC X(6) VALUE SPACES.
       01  WS-TOTAL119          PIC 9(6) VALUE 0.
       01  WS-K119              PIC 99 VALUE 0.
       01  WS-AVERAGE119        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT123         PIC 9(6) VALUE 500.
       01  WS-FLAG123           PIC X VALUE 'N'.
       01  WS-AMOUNT126         PIC 9(6) VALUE 500.
       01  WS-FLAG126           PIC X VALUE 'N'.
       01  WS-CODE127           PIC 9 VALUE 1.
       01  WS-STATUS127         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT128         PIC 9(6) VALUE 500.
       01  WS-FLAG128           PIC X VALUE 'N'.
       01  WS-TOTAL130          PIC 9(6) VALUE 0.
       01  WS-K130              PIC 99 VALUE 0.
       01  WS-AVERAGE130        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT131         PIC 9(6) VALUE 500.
       01  WS-FLAG131           PIC X VALUE 'N'.
       01  WS-CODE133           PIC 9 VALUE 1.
       01  WS-STATUS133         PIC X(6) VALUE SPACES.
       01  WS-TITLE136          PIC X(20) VALUE SPACES.
       01  WS-HEADER136         PIC X(40) VALUE SPACES.
       01  WS-TITLE137          PIC X(20) VALUE SPACES.
       01  WS-HEADER137         PIC X(40) VALUE SPACES.
       01  WS-TITLE140          PIC X(20) VALUE SPACES.
       01  WS-HEADER140         PIC X(40) VALUE SPACES.
       01  WS-CODE142           PIC 9 VALUE 1.
       01  WS-STATUS142         PIC X(6) VALUE SPACES.
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       FORMAT-HEADER4.
           MOVE 'MONTHLY REPORT' TO WS-TITLE4.
           STRING WS-TITLE4 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER4.
           DISPLAY WS-HEADER4.

       LOOKUP-ENTRY-SAFE6.
           ACCEPT WS-IDX6.
           IF WS-IDX6 > 0 AND WS-IDX6 NOT > 10
               MOVE WS-ENTRY6(WS-IDX6) TO WS-OUT6
           END-IF.

       LOOKUP-ENTRY33.
           ACCEPT WS-IDX33.
           MOVE WS-ENTRY33(WS-IDX33) TO WS-OUT33.

       TRANSFER-SAFE40.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY54.
           ACCEPT WS-IDX54.
           MOVE WS-ENTRY54(WS-IDX54) TO WS-OUT54.

       TRANSFER-SAFE29.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CLASSIFY-CODE46.
           EVALUATE WS-CODE46
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS46
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS46
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS46
           END-EVALUATE.

       CHECK-LIMIT71.
           IF WS-AMOUNT71 > 1000
               MOVE 'Y' TO WS-FLAG71
           ELSE
               MOVE 'N' TO WS-FLAG71
           END-IF.

       FORMAT-HEADER25.
           MOVE 'MONTHLY REPORT' TO WS-TITLE25.
           STRING WS-TITLE25 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER25.
           DISPLAY WS-HEADER25.

       CLASSIFY-CODE44.
           EVALUATE WS-CODE44
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS44
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS44
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS44
           END-EVALUATE.

       FORMAT-HEADER63.
           MOVE 'MONTHLY REPORT' TO WS-TITLE63.
           STRING WS-TITLE63 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER63.
           DISPLAY WS-HEADER63.

       TRANSFER-SAFE13.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY139.
           ACCEPT WS-IDX139.
           MOVE WS-ENTRY139(WS-IDX139) TO WS-OUT139.

       TRANSFER55.
           EXEC CICS RECEIVE INTO(WS-TARGET55) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET55) END-EXEC.

       TRANSFER-SAFE120.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CLASSIFY-CODE127.
           EVALUATE WS-CODE127
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS127
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS127
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS127
           END-EVALUATE.

       LOOKUP-ENTRY21.
           ACCEPT WS-IDX21.
           MOVE WS-ENTRY21(WS-IDX21) TO WS-OUT21.

       CLASSIFY-CODE32.
           EVALUATE WS-CODE32
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS32
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS32
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS32
           END-EVALUATE.

       LOOKUP-ENTRY-SAFE124.
           ACCEPT WS-IDX124.
           IF WS-IDX124 > 0 AND WS-IDX124 NOT > 10
               MOVE WS-ENTRY124(WS-IDX124) TO WS-OUT124
           END-IF.

       TRANSFER72.
           EXEC CICS RECEIVE INTO(WS-TARGET72) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET72) END-EXEC.

       LOOKUP-ENTRY-SAFE2.
           ACCEPT WS-IDX2.
           IF WS-IDX2 > 0 AND WS-IDX2 NOT > 10
               MOVE WS-ENTRY2(WS-IDX2) TO WS-OUT2
           END-IF.

       LOOKUP-ENTRY-SAFE135.
           ACCEPT WS-IDX135.
           IF WS-IDX135 > 0 AND WS-IDX135 NOT > 10
               MOVE WS-ENTRY135(WS-IDX135) TO WS-OUT135
           END-IF.

       FORMAT-HEADER8.
           MOVE 'MONTHLY REPORT' TO WS-TITLE8.
           STRING WS-TITLE8 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER8.
           DISPLAY WS-HEADER8.

       CLASSIFY-CODE52.
           EVALUATE WS-CODE52
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS52
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS52
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS52
           END-EVALUATE.

       LOOKUP-ENTRY100.
           ACCEPT WS-IDX100.
           MOVE WS-ENTRY100(WS-IDX100) TO WS-OUT100.

       TRANSFER-SAFE129.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       COMPUTE-TOTALS119.
           MOVE 0 TO WS-TOTAL119.
           PERFORM VARYING WS-K119 FROM 1 BY 1 UNTIL WS-K119 > 10
               ADD WS-K119 TO WS-TOTAL119
           END-PERFORM.
           COMPUTE WS-AVERAGE119 = WS-TOTAL119 / 10.

       TRANSFER-SAFE92.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CLASSIFY-CODE94.
           EVALUATE WS-CODE94
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS94
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS94
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS94
           END-EVALUATE.

       TRANSFER-SAFE141.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE18.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CHECK-LIMIT43.
           IF WS-AMOUNT43 > 1000
               MOVE 'Y' TO WS-FLAG43
           ELSE
               MOVE 'N' TO WS-FLAG43
           END-IF.

       COMPUTE-TOTALS80.
           MOVE 0 TO WS-TOTAL80.
           PERFORM VARYING WS-K80 FROM 1 BY 1 UNTIL WS-K80 > 10
               ADD WS-K80 TO WS-TOTAL80
           END-PERFORM.
           COMPUTE WS-AVERAGE80 = WS-TOTAL80 / 10.

       LOOKUP-ENTRY104.
           ACCEPT WS-IDX104.
           MOVE WS-ENTRY104(WS-IDX104) TO WS-OUT104.

       COMPUTE-TOTALS49.
           MOVE 0 TO WS-TOTAL49.
           PERFORM VARYING WS-K49 FROM 1 BY 1 UNTIL WS-K49 > 10
               ADD WS-K49 TO WS-TOTAL49
           END-PERFORM.
           COMPUTE WS-AVERAGE49 = WS-TOTAL49 / 10.

       FORMAT-HEADER114.
           MOVE 'MONTHLY REPORT' TO WS-TITLE114.
           STRING WS-TITLE114 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER114.
           DISPLAY WS-HEADER114.

       LOOKUP-ENTRY-SAFE97.
           ACCEPT WS-IDX97.
           IF WS-IDX97 > 0 AND WS-IDX97 NOT > 10
               MOVE WS-ENTRY97(WS-IDX97) TO WS-OUT97
           END-IF.

       COMPUTE-TOTALS22.
           MOVE 0 TO WS-TOTAL22.
           PERFORM VARYING WS-K22 FROM 1 BY 1 UNTIL WS-K22 > 10
               ADD WS-K22 TO WS-TOTAL22
           END-PERFORM.
           COMPUTE WS-AVERAGE22 = WS-TOTAL22 / 10.

       FORMAT-HEADER34.
           MOVE 'MONTHLY REPORT' TO WS-TITLE34.
           STRING WS-TITLE34 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER34.
           DISPLAY WS-HEADER34.

       LOOKUP-ENTRY65.
           ACCEPT WS-IDX65.
           MOVE WS-ENTRY65(WS-IDX65) TO WS-OUT65.

       TRANSFER121.
           EXEC CICS RECEIVE INTO(WS-TARGET121) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET121) END-EXEC.

       CLASSIFY-CODE133.
           EVALUATE WS-CODE133
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS133
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS133
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS133
           END-EVALUATE.

       CHECK-LIMIT131.
           IF WS-AMOUNT131 > 1000
               MOVE 'Y' TO WS-FLAG131
           ELSE
               MOVE 'N' TO WS-FLAG131
           END-IF.

       LOOKUP-ENTRY-SAFE56.
           ACCEPT WS-IDX56.
           IF WS-IDX56 > 0 AND WS-IDX56 NOT > 10
               MOVE WS-ENTRY56(WS-IDX56) TO WS-OUT56
           END-IF.

       TRANSFER-SAFE117.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE15.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CHECK-LIMIT47.
           IF WS-AMOUNT47 > 1000
               MOVE 'Y' TO WS-FLAG47
           ELSE
               MOVE 'N' TO WS-FLAG47
           END-IF.

       LOOKUP-ENTRY31.
           ACCEPT WS-IDX31.
           MOVE WS-ENTRY31(WS-IDX31) TO WS-OUT31.

       LOOKUP-ENTRY24.
           ACCEPT WS-IDX24.
           MOVE WS-ENTRY24(WS-IDX24) TO WS-OUT24.

       CLASSIFY-CODE142.
           EVALUATE WS-CODE142
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS142
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS142
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS142
           END-EVALUATE.

       COMPUTE-TOTALS50.
           MOVE 0 TO WS-TOTAL50.
           PERFORM VARYING WS-K50 FROM 1 BY 1 UNTIL WS-K50 > 10
               ADD WS-K50 TO WS-TOTAL50
           END-PERFORM.
           COMPUTE WS-AVERAGE50 = WS-TOTAL50 / 10.

       TRANSFER-SAFE110.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE91.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY-SAFE76.
           ACCEPT WS-IDX76.
           IF WS-IDX76 > 0 AND WS-IDX76 NOT > 10
               MOVE WS-ENTRY76(WS-IDX76) TO WS-OUT76
           END-IF.

       FORMAT-HEADER70.
           MOVE 'MONTHLY REPORT' TO WS-TITLE70.
           STRING WS-TITLE70 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER70.
           DISPLAY WS-HEADER70.

       COMPUTE-TOTALS58.
           MOVE 0 TO WS-TOTAL58.
           PERFORM VARYING WS-K58 FROM 1 BY 1 UNTIL WS-K58 > 10
               ADD WS-K58 TO WS-TOTAL58
           END-PERFORM.
           COMPUTE WS-AVERAGE58 = WS-TOTAL58 / 10.

       TRANSFER-SAFE16.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE69.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY107.
           ACCEPT WS-IDX107.
           MOVE WS-ENTRY107(WS-IDX107) TO WS-OUT107.

       TRANSFER-SAFE7.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE105.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       FORMAT-HEADER66.
           MOVE 'MONTHLY REPORT' TO WS-TITLE66.
           STRING WS-TITLE66 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER66.
           DISPLAY WS-HEADER66.

       TRANSFER-SAFE134.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY-SAFE20.
           ACCEPT WS-IDX20.
           IF WS-IDX20 > 0 AND WS-IDX20 NOT > 10
               MOVE WS-ENTRY20(WS-IDX20) TO WS-OUT20
           END-IF.

       CHECK-LIMIT83.
           IF WS-AMOUNT83 > 1000
               MOVE 'Y' TO WS-FLAG83
           ELSE
               MOVE 'N' TO WS-FLAG83
           END-IF.

       CLASSIFY-CODE9.
           EVALUATE WS-CODE9
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS9
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS9
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS9
           END-EVALUATE.

       LOOKUP-ENTRY-SAFE101.
           ACCEPT WS-IDX101.
           IF WS-IDX101 > 0 AND WS-IDX101 NOT > 10
               MOVE WS-ENTRY101(WS-IDX101) TO WS-OUT101
           END-IF.

       CLASSIFY-CODE118.
           EVALUATE WS-CODE118
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS118
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS118
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS118
           END-EVALUATE.

       LOOKUP-ENTRY-SAFE116.
           ACCEPT WS-IDX116.
           IF WS-IDX116 > 0 AND WS-IDX116 NOT > 10
               MOVE WS-ENTRY116(WS-IDX116) TO WS-OUT116
           END-IF.

       TRANSFER-SAFE61.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CHECK-LIMIT53.
           IF WS-AMOUNT53 > 1000
               MOVE 'Y' TO WS-FLAG53
           ELSE
               MOVE 'N' TO WS-FLAG53
           END-IF.

       COMPUTE-TOTALS89.
           MOVE 0 TO WS-TOTAL89.
           PERFORM VARYING WS-K89 FROM 1 BY 1 UNTIL WS-K89 > 10
               ADD WS-K89 TO WS-TOTAL89
           END-PERFORM.
           COMPUTE WS-AVERAGE89 = WS-TOTAL89 / 10.

       LOOKUP-ENTRY-SAFE87.
           ACCEPT WS-IDX87.
           IF WS-IDX87 > 0 AND WS-IDX87 NOT > 10
               MOVE WS-ENTRY87(WS-IDX87) TO WS-OUT87
           END-IF.

       COMPUTE-TOTALS51.
           MOVE 0 TO WS-TOTAL51.
           PERFORM VARYING WS-K51 FROM 1 BY 1 UNTIL WS-K51 > 10
               ADD WS-K51 TO WS-TOTAL51
           END-PERFORM.
           COMPUTE WS-AVERAGE51 = WS-TOTAL51 / 10.

       FORMAT-HEADER136.
           MOVE 'MONTHLY REPORT' TO WS-TITLE136.
           STRING WS-TITLE136 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER136.
           DISPLAY WS-HEADER136.

       CHECK-LIMIT23.
           IF WS-AMOUNT23 > 1000
               MOVE 'Y' TO WS-FLAG23
           ELSE
               MOVE 'N' TO WS-FLAG23
           END-IF.

       LOOKUP-ENTRY57.
           ACCEPT WS-IDX57.
           MOVE WS-ENTRY57(WS-IDX57) TO WS-OUT57.

       FORMAT-HEADER137.
           MOVE 'MONTHLY REPORT' TO WS-TITLE137.
           STRING WS-TITLE137 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER137.
           DISPLAY WS-HEADER137.

       COMPUTE-TOTALS12.
           MOVE 0 TO WS-TOTAL12.
           PERFORM VARYING WS-K12 FROM 1 BY 1 UNTIL WS-K12 > 10
               ADD WS-K12 TO WS-TOTAL12
           END-PERFORM.
           COMPUTE WS-AVERAGE12 = WS-TOTAL12 / 10.

       CLASSIFY-CODE48.
           EVALUATE WS-CODE48
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS48
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS48
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS48
           END-EVALUATE.

       LOOKUP-ENTRY84.
           ACCEPT WS-IDX84.
           MOVE WS-ENTRY84(WS-IDX84) TO WS-OUT84.

       LOOKUP-ENTRY-SAFE113.
           ACCEPT WS-IDX113.
           IF WS-IDX113 > 0 AND WS-IDX113 NOT > 10
               MOVE WS-ENTRY113(WS-IDX113) TO WS-OUT113
           END-IF.

       LOOKUP-ENTRY-SAFE103.
           ACCEPT WS-IDX103.
           IF WS-IDX103 > 0 AND WS-IDX103 NOT > 10
               MOVE WS-ENTRY103(WS-IDX103) TO WS-OUT103
           END-IF.

       TRANSFER-SAFE26.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CLASSIFY-CODE73.
           EVALUATE WS-CODE73
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS73
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS73
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS73
           END-EVALUATE.

       COMPUTE-TOTALS62.
           MOVE 0 TO WS-TOTAL62.
           PERFORM VARYING WS-K62 FROM 1 BY 1 UNTIL WS-K62 > 10
               ADD WS-K62 TO WS-TOTAL62
           END-PERFORM.
           COMPUTE WS-AVERAGE62 = WS-TOTAL62 / 10.

       LOOKUP-ENTRY-SAFE41.
           ACCEPT WS-IDX41.
           IF WS-IDX41 > 0 AND WS-IDX41 NOT > 10
               MOVE WS-ENTRY41(WS-IDX41) TO WS-OUT41
           END-IF.

       COMPUTE-TOTALS27.
           MOVE 0 TO WS-TOTAL27.
           PERFORM VARYING WS-K27 FROM 1 BY 1 UNTIL WS-K27 > 10
               ADD WS-K27 TO WS-TOTAL27
           END-PERFORM.
           COMPUTE WS-AVERAGE27 = WS-TOTAL27 / 10.

       FORMAT-HEADER106.
           MOVE 'MONTHLY REPORT' TO WS-TITLE106.
           STRING WS-TITLE106 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER106.
           DISPLAY WS-HEADER106.

       TRANSFER-SAFE30.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       FORMAT-HEADER102.
           MOVE 'MONTHLY REPORT' TO WS-TITLE102.
           STRING WS-TITLE102 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER102.
           DISPLAY WS-HEADER102.

       TRANSFER-SAFE79.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY111.
           ACCEPT WS-IDX111.
           MOVE WS-ENTRY111(WS-IDX111) TO WS-OUT111.

       FORMAT-HEADER78.
           MOVE 'MONTHLY REPORT' TO WS-TITLE78.
           STRING WS-TITLE78 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER78.
           DISPLAY WS-HEADER78.

       CLASSIFY-CODE1.
           EVALUATE WS-CODE1
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS1
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS1
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS1
           END-EVALUATE.

       LOOKUP-ENTRY-SAFE93.
           ACCEPT WS-IDX93.
           IF WS-IDX93 > 0 AND WS-IDX93 NOT > 10
               MOVE WS-ENTRY93(WS-IDX93) TO WS-OUT93
           END-IF.

       COMPUTE-TOTALS130.
           MOVE 0 TO WS-TOTAL130.
           PERFORM VARYING WS-K130 FROM 1 BY 1 UNTIL WS-K130 > 10
               ADD WS-K130 TO WS-TOTAL130
           END-PERFORM.
           COMPUTE WS-AVERAGE130 = WS-TOTAL130 / 10.

       CLASSIFY-CODE60.
           EVALUATE WS-CODE60
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS60
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS60
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS60
           END-EVALUATE.

       FORMAT-HEADER5.
           MOVE 'MONTHLY REPORT' TO WS-TITLE5.
           STRING WS-TITLE5 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER5.
           DISPLAY WS-HEADER5.

       LOOKUP-ENTRY95.
           ACCEPT WS-IDX95.
           MOVE WS-ENTRY95(WS-IDX95) TO WS-OUT95.

       LOOKUP-ENTRY-SAFE38.
           ACCEPT WS-IDX38.
           IF WS-IDX38 > 0 AND WS-IDX38 NOT > 10
               MOVE WS-ENTRY38(WS-IDX38) TO WS-OUT38
           END-IF.

       TRANSFER-SAFE10.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CHECK-LIMIT123.
           IF WS-AMOUNT123 > 1000
               MOVE 'Y' TO WS-FLAG123
           ELSE
               MOVE 'N' TO WS-FLAG123
           END-IF.

       LOOKUP-ENTRY-SAFE74.
           ACCEPT WS-IDX74.
           IF WS-IDX74 > 0 AND WS-IDX74 NOT > 10
               MOVE WS-ENTRY74(WS-IDX74) TO WS-OUT74
           END-IF.

       COMPUTE-TOTALS77.
           MOVE 0 TO WS-TOTAL77.
           PERFORM VARYING WS-K77 FROM 1 BY 1 UNTIL WS-K77 > 10
               ADD WS-K77 TO WS-TOTAL77
           END-PERFORM.
           COMPUTE WS-AVERAGE77 = WS-TOTAL77 / 10.

       LOOKUP-ENTRY88.
           ACCEPT WS-IDX88.
           MOVE WS-ENTRY88(WS-IDX88) TO WS-OUT88.

       TRANSFER-SAFE109.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       COMPUTE-TOTALS19.
           MOVE 0 TO WS-TOTAL19.
           PERFORM VARYING WS-K19 FROM 1 BY 1 UNTIL WS-K19 > 10
               ADD WS-K19 TO WS-TOTAL19
           END-PERFORM.
           COMPUTE WS-AVERAGE19 = WS-TOTAL19 / 10.

       LOOKUP-ENTRY37.
           ACCEPT WS-IDX37.
           MOVE WS-ENTRY37(WS-IDX37) TO WS-OUT37.

       TRANSFER122.
           EXEC CICS RECEIVE INTO(WS-TARGET122) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET122) END-EXEC.

       COMPUTE-TOTALS28.
           MOVE 0 TO WS-TOTAL28.
           PERFORM VARYING WS-K28 FROM 1 BY 1 UNTIL WS-K28 > 10
               ADD WS-K28 TO WS-TOTAL28
           END-PERFORM.
           COMPUTE WS-AVERAGE28 = WS-TOTAL28 / 10.

       LOOKUP-ENTRY-SAFE45.
           ACCEPT WS-IDX45.
           IF WS-IDX45 > 0 AND WS-IDX45 NOT > 10
               MOVE WS-ENTRY45(WS-IDX45) TO WS-OUT45
           END-IF.

       TRANSFER-SAFE68.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY-SAFE125.
           ACCEPT WS-IDX125.
           IF WS-IDX125 > 0 AND WS-IDX125 NOT > 10
               MOVE WS-ENTRY125(WS-IDX125) TO WS-OUT125
           END-IF.

       CHECK-LIMIT128.
           IF WS-AMOUNT128 > 1000
               MOVE 'Y' TO WS-FLAG128
           ELSE
               MOVE 'N' TO WS-FLAG128
           END-IF.

       CHECK-LIMIT64.
           IF WS-AMOUNT64 > 1000
               MOVE 'Y' TO WS-FLAG64
           ELSE
               MOVE 'N' TO WS-FLAG64
           END-IF.

       FORMAT-HEADER99.
           MOVE 'MONTHLY REPORT' TO WS-TITLE99.
           STRING WS-TITLE99 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER99.
           DISPLAY WS-HEADER99.

       TRANSFER42.
           EXEC CICS RECEIVE INTO(WS-TARGET42) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET42) END-EXEC.

       COMPUTE-TOTALS11.
           MOVE 0 TO WS-TOTAL11.
           PERFORM VARYING WS-K11 FROM 1 BY 1 UNTIL WS-K11 > 10
               ADD WS-K11 TO WS-TOTAL11
           END-PERFORM.
           COMPUTE WS-AVERAGE11 = WS-TOTAL11 / 10.

       TRANSFER-SAFE75.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CHECK-LIMIT90.
           IF WS-AMOUNT90 > 1000
               MOVE 'Y' TO WS-FLAG90
           ELSE
               MOVE 'N' TO WS-FLAG90
           END-IF.

       LOOKUP-ENTRY35.
           ACCEPT WS-IDX35.
           MOVE WS-ENTRY35(WS-IDX35) TO WS-OUT35.

       CLASSIFY-CODE82.
           EVALUATE WS-CODE82
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS82
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS82
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS82
           END-EVALUATE.

       FORMAT-HEADER17.
           MOVE 'MONTHLY REPORT' TO WS-TITLE17.
           STRING WS-TITLE17 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER17.
           DISPLAY WS-HEADER17.

       FORMAT-HEADER81.
           MOVE 'MONTHLY REPORT' TO WS-TITLE81.
           STRING WS-TITLE81 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER81.
           DISPLAY WS-HEADER81.

       LOOKUP-ENTRY-SAFE138.
           ACCEPT WS-IDX138.
           IF WS-IDX138 > 0 AND WS-IDX138 NOT > 10
               MOVE WS-ENTRY138(WS-IDX138) TO WS-OUT138
           END-IF.

       CHECK-LIMIT126.
           IF WS-AMOUNT126 > 1000
               MOVE 'Y' TO WS-FLAG126
           ELSE
               MOVE 'N' TO WS-FLAG126
           END-IF.

       FORMAT-HEADER140.
           MOVE 'MONTHLY REPORT' TO WS-TITLE140.
           STRING WS-TITLE140 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER140.
           DISPLAY WS-HEADER140.

       COMPUTE-TOTALS86.
           MOVE 0 TO WS-TOTAL86.
           PERFORM VARYING WS-K86 FROM 1 BY 1 UNTIL WS-K86 > 10
               ADD WS-K86 TO WS-TOTAL86
           END-PERFORM.
           COMPUTE WS-AVERAGE86 = WS-TOTAL86 / 10.

       TRANSFER-SAFE108.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       FORMAT-HEADER85.
           MOVE 'MONTHLY REPORT' TO WS-TITLE85.
           STRING WS-TITLE85 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER85.
           DISPLAY WS-HEADER85.

       TRANSFER-SAFE67.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER112.
           EXEC CICS RECEIVE INTO(WS-TARGET112) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET112) END-EXEC.

       TRANSFER3.
           EXEC CICS RECEIVE INTO(WS-TARGET3) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET3) END-EXEC.

       FORMAT-HEADER14.
           MOVE 'MONTHLY REPORT' TO WS-TITLE14.
           STRING WS-TITLE14 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER14.
           DISPLAY WS-HEADER14.

       LOOKUP-ENTRY-SAFE132.
           ACCEPT WS-IDX132.
           IF WS-IDX132 > 0 AND WS-IDX132 NOT > 10
               MOVE WS-ENTRY132(WS-IDX132) TO WS-OUT132
           END-IF.

       CHECK-LIMIT59.
           IF WS-AMOUNT59 > 1000
               MOVE 'Y' TO WS-FLAG59
           ELSE
               MOVE 'N' TO WS-FLAG59
           END-IF.

       CHECK-LIMIT39.
           IF WS-AMOUNT39 > 1000
               MOVE 'Y' TO WS-FLAG39
           ELSE
               MOVE 'N' TO WS-FLAG39
           END-IF.

       LOOKUP-ENTRY115.
           ACCEPT WS-IDX115.
           MOVE WS-ENTRY115(WS-IDX115) TO WS-OUT115.

       LOOKUP-ENTRY96.
           ACCEPT WS-IDX96.
           MOVE WS-ENTRY96(WS-IDX96) TO WS-OUT96.

       CLASSIFY-CODE98.
           EVALUATE WS-CODE98
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS98
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS98
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS98
           END-EVALUATE.

       COMPUTE-TOTALS36.
           MOVE 0 TO WS-TOTAL36.
           PERFORM VARYING WS-K36 FROM 1 BY 1 UNTIL WS-K36 > 10
               ADD WS-K36 TO WS-TOTAL36
           END-PERFORM.
           COMPUTE WS-AVERAGE36 = WS-TOTAL36 / 10.

