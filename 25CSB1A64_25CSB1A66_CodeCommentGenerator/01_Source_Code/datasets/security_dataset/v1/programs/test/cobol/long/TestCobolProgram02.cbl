       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTE02.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-TARGET1         PIC X(8).
       01  WS-IDX2            PIC 99.
       01  WS-TAB2.
           05  WS-ENTRY2      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT2            PIC X(10).
       01  WS-TARGET3         PIC X(8).
       01  WS-IDX4            PIC 99.
       01  WS-TAB4.
           05  WS-ENTRY4      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT4            PIC X(10).
       01  WS-IDX5            PIC 99.
       01  WS-TAB5.
           05  WS-ENTRY5      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT5            PIC X(10).
       01  WS-TARGET7         PIC X(8).
       01  WS-IDX9            PIC 99.
       01  WS-TAB9.
           05  WS-ENTRY9      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT9            PIC X(10).
       01  WS-IDX10            PIC 99.
       01  WS-TAB10.
           05  WS-ENTRY10      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT10            PIC X(10).
       01  WS-TARGET13         PIC X(8).
       01  WS-TARGET15         PIC X(8).
       01  WS-IDX16            PIC 99.
       01  WS-TAB16.
           05  WS-ENTRY16      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT16            PIC X(10).
       01  WS-IDX18            PIC 99.
       01  WS-TAB18.
           05  WS-ENTRY18      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT18            PIC X(10).
       01  WS-TARGET19         PIC X(8).
       01  WS-IDX23            PIC 99.
       01  WS-TAB23.
           05  WS-ENTRY23      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT23            PIC X(10).
       01  WS-IDX25            PIC 99.
       01  WS-TAB25.
           05  WS-ENTRY25      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT25            PIC X(10).
       01  WS-IDX28            PIC 99.
       01  WS-TAB28.
           05  WS-ENTRY28      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT28            PIC X(10).
       01  WS-TARGET31         PIC X(8).
       01  WS-IDX33            PIC 99.
       01  WS-TAB33.
           05  WS-ENTRY33      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT33            PIC X(10).
       01  WS-IDX34            PIC 99.
       01  WS-TAB34.
           05  WS-ENTRY34      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT34            PIC X(10).
       01  WS-TARGET37         PIC X(8).
       01  WS-TARGET38         PIC X(8).
       01  WS-IDX39            PIC 99.
       01  WS-TAB39.
           05  WS-ENTRY39      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT39            PIC X(10).
       01  WS-TARGET40         PIC X(8).
       01  WS-IDX41            PIC 99.
       01  WS-TAB41.
           05  WS-ENTRY41      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT41            PIC X(10).
       01  WS-IDX42            PIC 99.
       01  WS-TAB42.
           05  WS-ENTRY42      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT42            PIC X(10).
       01  WS-IDX43            PIC 99.
       01  WS-TAB43.
           05  WS-ENTRY43      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT43            PIC X(10).
       01  WS-IDX45            PIC 99.
       01  WS-TAB45.
           05  WS-ENTRY45      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT45            PIC X(10).
       01  WS-IDX46            PIC 99.
       01  WS-TAB46.
           05  WS-ENTRY46      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT46            PIC X(10).
       01  WS-TARGET47         PIC X(8).
       01  WS-TARGET49         PIC X(8).
       01  WS-TARGET52         PIC X(8).
       01  WS-IDX54            PIC 99.
       01  WS-TAB54.
           05  WS-ENTRY54      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT54            PIC X(10).
       01  WS-TARGET57         PIC X(8).
       01  WS-IDX62            PIC 99.
       01  WS-TAB62.
           05  WS-ENTRY62      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT62            PIC X(10).
       01  WS-TARGET65         PIC X(8).
       01  WS-IDX68            PIC 99.
       01  WS-TAB68.
           05  WS-ENTRY68      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT68            PIC X(10).
       01  WS-IDX71            PIC 99.
       01  WS-TAB71.
           05  WS-ENTRY71      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT71            PIC X(10).
       01  WS-IDX72            PIC 99.
       01  WS-TAB72.
           05  WS-ENTRY72      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT72            PIC X(10).
       01  WS-TARGET74         PIC X(8).
       01  WS-IDX75            PIC 99.
       01  WS-TAB75.
           05  WS-ENTRY75      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT75            PIC X(10).
       01  WS-IDX76            PIC 99.
       01  WS-TAB76.
           05  WS-ENTRY76      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT76            PIC X(10).
       01  WS-IDX78            PIC 99.
       01  WS-TAB78.
           05  WS-ENTRY78      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT78            PIC X(10).
       01  WS-TARGET80         PIC X(8).
       01  WS-TARGET82         PIC X(8).
       01  WS-TARGET83         PIC X(8).
       01  WS-TARGET86         PIC X(8).
       01  WS-TARGET87         PIC X(8).
       01  WS-IDX89            PIC 99.
       01  WS-TAB89.
           05  WS-ENTRY89      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT89            PIC X(10).
       01  WS-IDX90            PIC 99.
       01  WS-TAB90.
           05  WS-ENTRY90      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT90            PIC X(10).
       01  WS-TARGET91         PIC X(8).
       01  WS-TARGET92         PIC X(8).
       01  WS-IDX94            PIC 99.
       01  WS-TAB94.
           05  WS-ENTRY94      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT94            PIC X(10).
       01  WS-IDX95            PIC 99.
       01  WS-TAB95.
           05  WS-ENTRY95      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT95            PIC X(10).
       01  WS-IDX96            PIC 99.
       01  WS-TAB96.
           05  WS-ENTRY96      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT96            PIC X(10).
       01  WS-TARGET100         PIC X(8).
       01  WS-IDX102            PIC 99.
       01  WS-TAB102.
           05  WS-ENTRY102      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT102            PIC X(10).
       01  WS-IDX105            PIC 99.
       01  WS-TAB105.
           05  WS-ENTRY105      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT105            PIC X(10).
       01  WS-TARGET109         PIC X(8).
       01  WS-IDX110            PIC 99.
       01  WS-TAB110.
           05  WS-ENTRY110      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT110            PIC X(10).
       01  WS-IDX111            PIC 99.
       01  WS-TAB111.
           05  WS-ENTRY111      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT111            PIC X(10).
       01  WS-TARGET115         PIC X(8).
       01  WS-TARGET117         PIC X(8).
       01  WS-TARGET121         PIC X(8).
       01  WS-TARGET122         PIC X(8).
       01  WS-IDX123            PIC 99.
       01  WS-TAB123.
           05  WS-ENTRY123      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT123            PIC X(10).
       01  WS-IDX124            PIC 99.
       01  WS-TAB124.
           05  WS-ENTRY124      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT124            PIC X(10).
       01  WS-IDX126            PIC 99.
       01  WS-TAB126.
           05  WS-ENTRY126      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT126            PIC X(10).
       01  WS-IDX127            PIC 99.
       01  WS-TAB127.
           05  WS-ENTRY127      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT127            PIC X(10).
       01  WS-TARGET129         PIC X(8).
       01  WS-IDX130            PIC 99.
       01  WS-TAB130.
           05  WS-ENTRY130      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT130            PIC X(10).
       01  WS-IDX132            PIC 99.
       01  WS-TAB132.
           05  WS-ENTRY132      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT132            PIC X(10).
       01  WS-TARGET133         PIC X(8).
       01  WS-TARGET134         PIC X(8).
       01  WS-IDX135            PIC 99.
       01  WS-TAB135.
           05  WS-ENTRY135      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT135            PIC X(10).
       01  WS-TARGET136         PIC X(8).
       01  WS-IDX137            PIC 99.
       01  WS-TAB137.
           05  WS-ENTRY137      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT137            PIC X(10).
       01  WS-AMOUNT6         PIC 9(6) VALUE 500.
       01  WS-FLAG6           PIC X VALUE 'N'.
       01  WS-TITLE8          PIC X(20) VALUE SPACES.
       01  WS-HEADER8         PIC X(40) VALUE SPACES.
       01  WS-CODE11           PIC 9 VALUE 1.
       01  WS-STATUS11         PIC X(6) VALUE SPACES.
       01  WS-TOTAL12          PIC 9(6) VALUE 0.
       01  WS-K12              PIC 99 VALUE 0.
       01  WS-AVERAGE12        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT14         PIC 9(6) VALUE 500.
       01  WS-FLAG14           PIC X VALUE 'N'.
       01  WS-TITLE17          PIC X(20) VALUE SPACES.
       01  WS-HEADER17         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT20         PIC 9(6) VALUE 500.
       01  WS-FLAG20           PIC X VALUE 'N'.
       01  WS-AMOUNT21         PIC 9(6) VALUE 500.
       01  WS-FLAG21           PIC X VALUE 'N'.
       01  WS-AMOUNT22         PIC 9(6) VALUE 500.
       01  WS-FLAG22           PIC X VALUE 'N'.
       01  WS-TOTAL24          PIC 9(6) VALUE 0.
       01  WS-K24              PIC 99 VALUE 0.
       01  WS-AVERAGE24        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL26          PIC 9(6) VALUE 0.
       01  WS-K26              PIC 99 VALUE 0.
       01  WS-AVERAGE26        PIC 9(6)V99 VALUE 0.
       01  WS-CODE27           PIC 9 VALUE 1.
       01  WS-STATUS27         PIC X(6) VALUE SPACES.
       01  WS-CODE29           PIC 9 VALUE 1.
       01  WS-STATUS29         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT30         PIC 9(6) VALUE 500.
       01  WS-FLAG30           PIC X VALUE 'N'.
       01  WS-TOTAL32          PIC 9(6) VALUE 0.
       01  WS-K32              PIC 99 VALUE 0.
       01  WS-AVERAGE32        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE35          PIC X(20) VALUE SPACES.
       01  WS-HEADER35         PIC X(40) VALUE SPACES.
       01  WS-CODE36           PIC 9 VALUE 1.
       01  WS-STATUS36         PIC X(6) VALUE SPACES.
       01  WS-TOTAL44          PIC 9(6) VALUE 0.
       01  WS-K44              PIC 99 VALUE 0.
       01  WS-AVERAGE44        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL48          PIC 9(6) VALUE 0.
       01  WS-K48              PIC 99 VALUE 0.
       01  WS-AVERAGE48        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT50         PIC 9(6) VALUE 500.
       01  WS-FLAG50           PIC X VALUE 'N'.
       01  WS-TITLE51          PIC X(20) VALUE SPACES.
       01  WS-HEADER51         PIC X(40) VALUE SPACES.
       01  WS-TITLE53          PIC X(20) VALUE SPACES.
       01  WS-HEADER53         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT55         PIC 9(6) VALUE 500.
       01  WS-FLAG55           PIC X VALUE 'N'.
       01  WS-CODE56           PIC 9 VALUE 1.
       01  WS-STATUS56         PIC X(6) VALUE SPACES.
       01  WS-TOTAL58          PIC 9(6) VALUE 0.
       01  WS-K58              PIC 99 VALUE 0.
       01  WS-AVERAGE58        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL59          PIC 9(6) VALUE 0.
       01  WS-K59              PIC 99 VALUE 0.
       01  WS-AVERAGE59        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT60         PIC 9(6) VALUE 500.
       01  WS-FLAG60           PIC X VALUE 'N'.
       01  WS-TITLE61          PIC X(20) VALUE SPACES.
       01  WS-HEADER61         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT63         PIC 9(6) VALUE 500.
       01  WS-FLAG63           PIC X VALUE 'N'.
       01  WS-AMOUNT64         PIC 9(6) VALUE 500.
       01  WS-FLAG64           PIC X VALUE 'N'.
       01  WS-AMOUNT66         PIC 9(6) VALUE 500.
       01  WS-FLAG66           PIC X VALUE 'N'.
       01  WS-AMOUNT67         PIC 9(6) VALUE 500.
       01  WS-FLAG67           PIC X VALUE 'N'.
       01  WS-TOTAL69          PIC 9(6) VALUE 0.
       01  WS-K69              PIC 99 VALUE 0.
       01  WS-AVERAGE69        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE70          PIC X(20) VALUE SPACES.
       01  WS-HEADER70         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT73         PIC 9(6) VALUE 500.
       01  WS-FLAG73           PIC X VALUE 'N'.
       01  WS-CODE77           PIC 9 VALUE 1.
       01  WS-STATUS77         PIC X(6) VALUE SPACES.
       01  WS-TITLE79          PIC X(20) VALUE SPACES.
       01  WS-HEADER79         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT81         PIC 9(6) VALUE 500.
       01  WS-FLAG81           PIC X VALUE 'N'.
       01  WS-TOTAL84          PIC 9(6) VALUE 0.
       01  WS-K84              PIC 99 VALUE 0.
       01  WS-AVERAGE84        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL85          PIC 9(6) VALUE 0.
       01  WS-K85              PIC 99 VALUE 0.
       01  WS-AVERAGE85        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT88         PIC 9(6) VALUE 500.
       01  WS-FLAG88           PIC X VALUE 'N'.
       01  WS-AMOUNT93         PIC 9(6) VALUE 500.
       01  WS-FLAG93           PIC X VALUE 'N'.
       01  WS-TITLE97          PIC X(20) VALUE SPACES.
       01  WS-HEADER97         PIC X(40) VALUE SPACES.
       01  WS-TITLE98          PIC X(20) VALUE SPACES.
       01  WS-HEADER98         PIC X(40) VALUE SPACES.
       01  WS-CODE99           PIC 9 VALUE 1.
       01  WS-STATUS99         PIC X(6) VALUE SPACES.
       01  WS-TITLE101          PIC X(20) VALUE SPACES.
       01  WS-HEADER101         PIC X(40) VALUE SPACES.
       01  WS-TITLE103          PIC X(20) VALUE SPACES.
       01  WS-HEADER103         PIC X(40) VALUE SPACES.
       01  WS-TITLE104          PIC X(20) VALUE SPACES.
       01  WS-HEADER104         PIC X(40) VALUE SPACES.
       01  WS-TITLE106          PIC X(20) VALUE SPACES.
       01  WS-HEADER106         PIC X(40) VALUE SPACES.
       01  WS-TITLE107          PIC X(20) VALUE SPACES.
       01  WS-HEADER107         PIC X(40) VALUE SPACES.
       01  WS-TITLE108          PIC X(20) VALUE SPACES.
       01  WS-HEADER108         PIC X(40) VALUE SPACES.
       01  WS-CODE112           PIC 9 VALUE 1.
       01  WS-STATUS112         PIC X(6) VALUE SPACES.
       01  WS-TOTAL113          PIC 9(6) VALUE 0.
       01  WS-K113              PIC 99 VALUE 0.
       01  WS-AVERAGE113        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL114          PIC 9(6) VALUE 0.
       01  WS-K114              PIC 99 VALUE 0.
       01  WS-AVERAGE114        PIC 9(6)V99 VALUE 0.
       01  WS-CODE116           PIC 9 VALUE 1.
       01  WS-STATUS116         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT118         PIC 9(6) VALUE 500.
       01  WS-FLAG118           PIC X VALUE 'N'.
       01  WS-AMOUNT119         PIC 9(6) VALUE 500.
       01  WS-FLAG119           PIC X VALUE 'N'.
       01  WS-CODE120           PIC 9 VALUE 1.
       01  WS-STATUS120         PIC X(6) VALUE SPACES.
       01  WS-TITLE125          PIC X(20) VALUE SPACES.
       01  WS-HEADER125         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT128         PIC 9(6) VALUE 500.
       01  WS-FLAG128           PIC X VALUE 'N'.
       01  WS-TOTAL131          PIC 9(6) VALUE 0.
       01  WS-K131              PIC 99 VALUE 0.
       01  WS-AVERAGE131        PIC 9(6)V99 VALUE 0.
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       LOOKUP-ENTRY-SAFE46.
           ACCEPT WS-IDX46.
           IF WS-IDX46 > 0 AND WS-IDX46 NOT > 10
               MOVE WS-ENTRY46(WS-IDX46) TO WS-OUT46
           END-IF.

       LOOKUP-ENTRY-SAFE54.
           ACCEPT WS-IDX54.
           IF WS-IDX54 > 0 AND WS-IDX54 NOT > 10
               MOVE WS-ENTRY54(WS-IDX54) TO WS-OUT54
           END-IF.

       LOOKUP-ENTRY4.
           ACCEPT WS-IDX4.
           MOVE WS-ENTRY4(WS-IDX4) TO WS-OUT4.

       TRANSFER-SAFE52.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       FORMAT-HEADER79.
           MOVE 'MONTHLY REPORT' TO WS-TITLE79.
           STRING WS-TITLE79 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER79.
           DISPLAY WS-HEADER79.

       COMPUTE-TOTALS24.
           MOVE 0 TO WS-TOTAL24.
           PERFORM VARYING WS-K24 FROM 1 BY 1 UNTIL WS-K24 > 10
               ADD WS-K24 TO WS-TOTAL24
           END-PERFORM.
           COMPUTE WS-AVERAGE24 = WS-TOTAL24 / 10.

       COMPUTE-TOTALS84.
           MOVE 0 TO WS-TOTAL84.
           PERFORM VARYING WS-K84 FROM 1 BY 1 UNTIL WS-K84 > 10
               ADD WS-K84 TO WS-TOTAL84
           END-PERFORM.
           COMPUTE WS-AVERAGE84 = WS-TOTAL84 / 10.

       LOOKUP-ENTRY94.
           ACCEPT WS-IDX94.
           MOVE WS-ENTRY94(WS-IDX94) TO WS-OUT94.

       TRANSFER-SAFE57.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CHECK-LIMIT88.
           IF WS-AMOUNT88 > 1000
               MOVE 'Y' TO WS-FLAG88
           ELSE
               MOVE 'N' TO WS-FLAG88
           END-IF.

       TRANSFER117.
           EXEC CICS RECEIVE INTO(WS-TARGET117) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET117) END-EXEC.

       TRANSFER100.
           EXEC CICS RECEIVE INTO(WS-TARGET100) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET100) END-EXEC.

       TRANSFER15.
           EXEC CICS RECEIVE INTO(WS-TARGET15) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET15) END-EXEC.

       TRANSFER49.
           EXEC CICS RECEIVE INTO(WS-TARGET49) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET49) END-EXEC.

       CHECK-LIMIT66.
           IF WS-AMOUNT66 > 1000
               MOVE 'Y' TO WS-FLAG66
           ELSE
               MOVE 'N' TO WS-FLAG66
           END-IF.

       CHECK-LIMIT6.
           IF WS-AMOUNT6 > 1000
               MOVE 'Y' TO WS-FLAG6
           ELSE
               MOVE 'N' TO WS-FLAG6
           END-IF.

       LOOKUP-ENTRY130.
           ACCEPT WS-IDX130.
           MOVE WS-ENTRY130(WS-IDX130) TO WS-OUT130.

       LOOKUP-ENTRY-SAFE75.
           ACCEPT WS-IDX75.
           IF WS-IDX75 > 0 AND WS-IDX75 NOT > 10
               MOVE WS-ENTRY75(WS-IDX75) TO WS-OUT75
           END-IF.

       TRANSFER-SAFE136.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY78.
           ACCEPT WS-IDX78.
           MOVE WS-ENTRY78(WS-IDX78) TO WS-OUT78.

       FORMAT-HEADER70.
           MOVE 'MONTHLY REPORT' TO WS-TITLE70.
           STRING WS-TITLE70 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER70.
           DISPLAY WS-HEADER70.

       LOOKUP-ENTRY111.
           ACCEPT WS-IDX111.
           MOVE WS-ENTRY111(WS-IDX111) TO WS-OUT111.

       FORMAT-HEADER106.
           MOVE 'MONTHLY REPORT' TO WS-TITLE106.
           STRING WS-TITLE106 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER106.
           DISPLAY WS-HEADER106.

       LOOKUP-ENTRY10.
           ACCEPT WS-IDX10.
           MOVE WS-ENTRY10(WS-IDX10) TO WS-OUT10.

       LOOKUP-ENTRY68.
           ACCEPT WS-IDX68.
           MOVE WS-ENTRY68(WS-IDX68) TO WS-OUT68.

       CHECK-LIMIT55.
           IF WS-AMOUNT55 > 1000
               MOVE 'Y' TO WS-FLAG55
           ELSE
               MOVE 'N' TO WS-FLAG55
           END-IF.

       CHECK-LIMIT128.
           IF WS-AMOUNT128 > 1000
               MOVE 'Y' TO WS-FLAG128
           ELSE
               MOVE 'N' TO WS-FLAG128
           END-IF.

       COMPUTE-TOTALS69.
           MOVE 0 TO WS-TOTAL69.
           PERFORM VARYING WS-K69 FROM 1 BY 1 UNTIL WS-K69 > 10
               ADD WS-K69 TO WS-TOTAL69
           END-PERFORM.
           COMPUTE WS-AVERAGE69 = WS-TOTAL69 / 10.

       LOOKUP-ENTRY-SAFE105.
           ACCEPT WS-IDX105.
           IF WS-IDX105 > 0 AND WS-IDX105 NOT > 10
               MOVE WS-ENTRY105(WS-IDX105) TO WS-OUT105
           END-IF.

       LOOKUP-ENTRY-SAFE41.
           ACCEPT WS-IDX41.
           IF WS-IDX41 > 0 AND WS-IDX41 NOT > 10
               MOVE WS-ENTRY41(WS-IDX41) TO WS-OUT41
           END-IF.

       LOOKUP-ENTRY-SAFE9.
           ACCEPT WS-IDX9.
           IF WS-IDX9 > 0 AND WS-IDX9 NOT > 10
               MOVE WS-ENTRY9(WS-IDX9) TO WS-OUT9
           END-IF.

       COMPUTE-TOTALS26.
           MOVE 0 TO WS-TOTAL26.
           PERFORM VARYING WS-K26 FROM 1 BY 1 UNTIL WS-K26 > 10
               ADD WS-K26 TO WS-TOTAL26
           END-PERFORM.
           COMPUTE WS-AVERAGE26 = WS-TOTAL26 / 10.

       FORMAT-HEADER103.
           MOVE 'MONTHLY REPORT' TO WS-TITLE103.
           STRING WS-TITLE103 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER103.
           DISPLAY WS-HEADER103.

       TRANSFER1.
           EXEC CICS RECEIVE INTO(WS-TARGET1) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET1) END-EXEC.

       CHECK-LIMIT30.
           IF WS-AMOUNT30 > 1000
               MOVE 'Y' TO WS-FLAG30
           ELSE
               MOVE 'N' TO WS-FLAG30
           END-IF.

       CHECK-LIMIT22.
           IF WS-AMOUNT22 > 1000
               MOVE 'Y' TO WS-FLAG22
           ELSE
               MOVE 'N' TO WS-FLAG22
           END-IF.

       TRANSFER92.
           EXEC CICS RECEIVE INTO(WS-TARGET92) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET92) END-EXEC.

       LOOKUP-ENTRY72.
           ACCEPT WS-IDX72.
           MOVE WS-ENTRY72(WS-IDX72) TO WS-OUT72.

       CHECK-LIMIT21.
           IF WS-AMOUNT21 > 1000
               MOVE 'Y' TO WS-FLAG21
           ELSE
               MOVE 'N' TO WS-FLAG21
           END-IF.

       TRANSFER3.
           EXEC CICS RECEIVE INTO(WS-TARGET3) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET3) END-EXEC.

       TRANSFER37.
           EXEC CICS RECEIVE INTO(WS-TARGET37) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET37) END-EXEC.

       LOOKUP-ENTRY2.
           ACCEPT WS-IDX2.
           MOVE WS-ENTRY2(WS-IDX2) TO WS-OUT2.

       CHECK-LIMIT63.
           IF WS-AMOUNT63 > 1000
               MOVE 'Y' TO WS-FLAG63
           ELSE
               MOVE 'N' TO WS-FLAG63
           END-IF.

       COMPUTE-TOTALS113.
           MOVE 0 TO WS-TOTAL113.
           PERFORM VARYING WS-K113 FROM 1 BY 1 UNTIL WS-K113 > 10
               ADD WS-K113 TO WS-TOTAL113
           END-PERFORM.
           COMPUTE WS-AVERAGE113 = WS-TOTAL113 / 10.

       FORMAT-HEADER104.
           MOVE 'MONTHLY REPORT' TO WS-TITLE104.
           STRING WS-TITLE104 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER104.
           DISPLAY WS-HEADER104.

       CLASSIFY-CODE29.
           EVALUATE WS-CODE29
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS29
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS29
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS29
           END-EVALUATE.

       LOOKUP-ENTRY-SAFE96.
           ACCEPT WS-IDX96.
           IF WS-IDX96 > 0 AND WS-IDX96 NOT > 10
               MOVE WS-ENTRY96(WS-IDX96) TO WS-OUT96
           END-IF.

       TRANSFER-SAFE83.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY-SAFE89.
           ACCEPT WS-IDX89.
           IF WS-IDX89 > 0 AND WS-IDX89 NOT > 10
               MOVE WS-ENTRY89(WS-IDX89) TO WS-OUT89
           END-IF.

       LOOKUP-ENTRY62.
           ACCEPT WS-IDX62.
           MOVE WS-ENTRY62(WS-IDX62) TO WS-OUT62.

       CHECK-LIMIT67.
           IF WS-AMOUNT67 > 1000
               MOVE 'Y' TO WS-FLAG67
           ELSE
               MOVE 'N' TO WS-FLAG67
           END-IF.

       FORMAT-HEADER108.
           MOVE 'MONTHLY REPORT' TO WS-TITLE108.
           STRING WS-TITLE108 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER108.
           DISPLAY WS-HEADER108.

       TRANSFER133.
           EXEC CICS RECEIVE INTO(WS-TARGET133) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET133) END-EXEC.

       TRANSFER80.
           EXEC CICS RECEIVE INTO(WS-TARGET80) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET80) END-EXEC.

       LOOKUP-ENTRY39.
           ACCEPT WS-IDX39.
           MOVE WS-ENTRY39(WS-IDX39) TO WS-OUT39.

       TRANSFER19.
           EXEC CICS RECEIVE INTO(WS-TARGET19) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET19) END-EXEC.

       COMPUTE-TOTALS85.
           MOVE 0 TO WS-TOTAL85.
           PERFORM VARYING WS-K85 FROM 1 BY 1 UNTIL WS-K85 > 10
               ADD WS-K85 TO WS-TOTAL85
           END-PERFORM.
           COMPUTE WS-AVERAGE85 = WS-TOTAL85 / 10.

       TRANSFER74.
           EXEC CICS RECEIVE INTO(WS-TARGET74) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET74) END-EXEC.

       LOOKUP-ENTRY45.
           ACCEPT WS-IDX45.
           MOVE WS-ENTRY45(WS-IDX45) TO WS-OUT45.

       FORMAT-HEADER35.
           MOVE 'MONTHLY REPORT' TO WS-TITLE35.
           STRING WS-TITLE35 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER35.
           DISPLAY WS-HEADER35.

       LOOKUP-ENTRY33.
           ACCEPT WS-IDX33.
           MOVE WS-ENTRY33(WS-IDX33) TO WS-OUT33.

       CHECK-LIMIT50.
           IF WS-AMOUNT50 > 1000
               MOVE 'Y' TO WS-FLAG50
           ELSE
               MOVE 'N' TO WS-FLAG50
           END-IF.

       LOOKUP-ENTRY43.
           ACCEPT WS-IDX43.
           MOVE WS-ENTRY43(WS-IDX43) TO WS-OUT43.

       FORMAT-HEADER125.
           MOVE 'MONTHLY REPORT' TO WS-TITLE125.
           STRING WS-TITLE125 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER125.
           DISPLAY WS-HEADER125.

       CLASSIFY-CODE56.
           EVALUATE WS-CODE56
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS56
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS56
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS56
           END-EVALUATE.

       TRANSFER47.
           EXEC CICS RECEIVE INTO(WS-TARGET47) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET47) END-EXEC.

       LOOKUP-ENTRY-SAFE102.
           ACCEPT WS-IDX102.
           IF WS-IDX102 > 0 AND WS-IDX102 NOT > 10
               MOVE WS-ENTRY102(WS-IDX102) TO WS-OUT102
           END-IF.

       LOOKUP-ENTRY90.
           ACCEPT WS-IDX90.
           MOVE WS-ENTRY90(WS-IDX90) TO WS-OUT90.

       TRANSFER129.
           EXEC CICS RECEIVE INTO(WS-TARGET129) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET129) END-EXEC.

       LOOKUP-ENTRY127.
           ACCEPT WS-IDX127.
           MOVE WS-ENTRY127(WS-IDX127) TO WS-OUT127.

       TRANSFER82.
           EXEC CICS RECEIVE INTO(WS-TARGET82) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET82) END-EXEC.

       LOOKUP-ENTRY-SAFE25.
           ACCEPT WS-IDX25.
           IF WS-IDX25 > 0 AND WS-IDX25 NOT > 10
               MOVE WS-ENTRY25(WS-IDX25) TO WS-OUT25
           END-IF.

       CHECK-LIMIT14.
           IF WS-AMOUNT14 > 1000
               MOVE 'Y' TO WS-FLAG14
           ELSE
               MOVE 'N' TO WS-FLAG14
           END-IF.

       COMPUTE-TOTALS59.
           MOVE 0 TO WS-TOTAL59.
           PERFORM VARYING WS-K59 FROM 1 BY 1 UNTIL WS-K59 > 10
               ADD WS-K59 TO WS-TOTAL59
           END-PERFORM.
           COMPUTE WS-AVERAGE59 = WS-TOTAL59 / 10.

       FORMAT-HEADER53.
           MOVE 'MONTHLY REPORT' TO WS-TITLE53.
           STRING WS-TITLE53 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER53.
           DISPLAY WS-HEADER53.

       CHECK-LIMIT20.
           IF WS-AMOUNT20 > 1000
               MOVE 'Y' TO WS-FLAG20
           ELSE
               MOVE 'N' TO WS-FLAG20
           END-IF.

       CHECK-LIMIT119.
           IF WS-AMOUNT119 > 1000
               MOVE 'Y' TO WS-FLAG119
           ELSE
               MOVE 'N' TO WS-FLAG119
           END-IF.

       TRANSFER-SAFE65.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       FORMAT-HEADER101.
           MOVE 'MONTHLY REPORT' TO WS-TITLE101.
           STRING WS-TITLE101 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER101.
           DISPLAY WS-HEADER101.

       LOOKUP-ENTRY18.
           ACCEPT WS-IDX18.
           MOVE WS-ENTRY18(WS-IDX18) TO WS-OUT18.

       TRANSFER13.
           EXEC CICS RECEIVE INTO(WS-TARGET13) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET13) END-EXEC.

       TRANSFER87.
           EXEC CICS RECEIVE INTO(WS-TARGET87) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET87) END-EXEC.

       LOOKUP-ENTRY-SAFE28.
           ACCEPT WS-IDX28.
           IF WS-IDX28 > 0 AND WS-IDX28 NOT > 10
               MOVE WS-ENTRY28(WS-IDX28) TO WS-OUT28
           END-IF.

       CHECK-LIMIT118.
           IF WS-AMOUNT118 > 1000
               MOVE 'Y' TO WS-FLAG118
           ELSE
               MOVE 'N' TO WS-FLAG118
           END-IF.

       LOOKUP-ENTRY76.
           ACCEPT WS-IDX76.
           MOVE WS-ENTRY76(WS-IDX76) TO WS-OUT76.

       TRANSFER40.
           EXEC CICS RECEIVE INTO(WS-TARGET40) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET40) END-EXEC.

       LOOKUP-ENTRY123.
           ACCEPT WS-IDX123.
           MOVE WS-ENTRY123(WS-IDX123) TO WS-OUT123.

       CHECK-LIMIT81.
           IF WS-AMOUNT81 > 1000
               MOVE 'Y' TO WS-FLAG81
           ELSE
               MOVE 'N' TO WS-FLAG81
           END-IF.

       TRANSFER-SAFE7.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CHECK-LIMIT93.
           IF WS-AMOUNT93 > 1000
               MOVE 'Y' TO WS-FLAG93
           ELSE
               MOVE 'N' TO WS-FLAG93
           END-IF.

       COMPUTE-TOTALS114.
           MOVE 0 TO WS-TOTAL114.
           PERFORM VARYING WS-K114 FROM 1 BY 1 UNTIL WS-K114 > 10
               ADD WS-K114 TO WS-TOTAL114
           END-PERFORM.
           COMPUTE WS-AVERAGE114 = WS-TOTAL114 / 10.

       CLASSIFY-CODE27.
           EVALUATE WS-CODE27
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS27
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS27
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS27
           END-EVALUATE.

       LOOKUP-ENTRY-SAFE126.
           ACCEPT WS-IDX126.
           IF WS-IDX126 > 0 AND WS-IDX126 NOT > 10
               MOVE WS-ENTRY126(WS-IDX126) TO WS-OUT126
           END-IF.

       FORMAT-HEADER17.
           MOVE 'MONTHLY REPORT' TO WS-TITLE17.
           STRING WS-TITLE17 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER17.
           DISPLAY WS-HEADER17.

       CLASSIFY-CODE116.
           EVALUATE WS-CODE116
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS116
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS116
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS116
           END-EVALUATE.

       LOOKUP-ENTRY34.
           ACCEPT WS-IDX34.
           MOVE WS-ENTRY34(WS-IDX34) TO WS-OUT34.

       LOOKUP-ENTRY-SAFE5.
           ACCEPT WS-IDX5.
           IF WS-IDX5 > 0 AND WS-IDX5 NOT > 10
               MOVE WS-ENTRY5(WS-IDX5) TO WS-OUT5
           END-IF.

       COMPUTE-TOTALS12.
           MOVE 0 TO WS-TOTAL12.
           PERFORM VARYING WS-K12 FROM 1 BY 1 UNTIL WS-K12 > 10
               ADD WS-K12 TO WS-TOTAL12
           END-PERFORM.
           COMPUTE WS-AVERAGE12 = WS-TOTAL12 / 10.

       LOOKUP-ENTRY-SAFE132.
           ACCEPT WS-IDX132.
           IF WS-IDX132 > 0 AND WS-IDX132 NOT > 10
               MOVE WS-ENTRY132(WS-IDX132) TO WS-OUT132
           END-IF.

       LOOKUP-ENTRY95.
           ACCEPT WS-IDX95.
           MOVE WS-ENTRY95(WS-IDX95) TO WS-OUT95.

       FORMAT-HEADER8.
           MOVE 'MONTHLY REPORT' TO WS-TITLE8.
           STRING WS-TITLE8 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER8.
           DISPLAY WS-HEADER8.

       COMPUTE-TOTALS131.
           MOVE 0 TO WS-TOTAL131.
           PERFORM VARYING WS-K131 FROM 1 BY 1 UNTIL WS-K131 > 10
               ADD WS-K131 TO WS-TOTAL131
           END-PERFORM.
           COMPUTE WS-AVERAGE131 = WS-TOTAL131 / 10.

       TRANSFER-SAFE122.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE38.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE86.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CLASSIFY-CODE11.
           EVALUATE WS-CODE11
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS11
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS11
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS11
           END-EVALUATE.

       CHECK-LIMIT60.
           IF WS-AMOUNT60 > 1000
               MOVE 'Y' TO WS-FLAG60
           ELSE
               MOVE 'N' TO WS-FLAG60
           END-IF.

       LOOKUP-ENTRY42.
           ACCEPT WS-IDX42.
           MOVE WS-ENTRY42(WS-IDX42) TO WS-OUT42.

       FORMAT-HEADER107.
           MOVE 'MONTHLY REPORT' TO WS-TITLE107.
           STRING WS-TITLE107 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER107.
           DISPLAY WS-HEADER107.

       FORMAT-HEADER51.
           MOVE 'MONTHLY REPORT' TO WS-TITLE51.
           STRING WS-TITLE51 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER51.
           DISPLAY WS-HEADER51.

       LOOKUP-ENTRY-SAFE137.
           ACCEPT WS-IDX137.
           IF WS-IDX137 > 0 AND WS-IDX137 NOT > 10
               MOVE WS-ENTRY137(WS-IDX137) TO WS-OUT137
           END-IF.

       LOOKUP-ENTRY-SAFE124.
           ACCEPT WS-IDX124.
           IF WS-IDX124 > 0 AND WS-IDX124 NOT > 10
               MOVE WS-ENTRY124(WS-IDX124) TO WS-OUT124
           END-IF.

       LOOKUP-ENTRY-SAFE71.
           ACCEPT WS-IDX71.
           IF WS-IDX71 > 0 AND WS-IDX71 NOT > 10
               MOVE WS-ENTRY71(WS-IDX71) TO WS-OUT71
           END-IF.

       TRANSFER-SAFE31.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER121.
           EXEC CICS RECEIVE INTO(WS-TARGET121) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET121) END-EXEC.

       COMPUTE-TOTALS58.
           MOVE 0 TO WS-TOTAL58.
           PERFORM VARYING WS-K58 FROM 1 BY 1 UNTIL WS-K58 > 10
               ADD WS-K58 TO WS-TOTAL58
           END-PERFORM.
           COMPUTE WS-AVERAGE58 = WS-TOTAL58 / 10.

       LOOKUP-ENTRY-SAFE135.
           ACCEPT WS-IDX135.
           IF WS-IDX135 > 0 AND WS-IDX135 NOT > 10
               MOVE WS-ENTRY135(WS-IDX135) TO WS-OUT135
           END-IF.

       COMPUTE-TOTALS32.
           MOVE 0 TO WS-TOTAL32.
           PERFORM VARYING WS-K32 FROM 1 BY 1 UNTIL WS-K32 > 10
               ADD WS-K32 TO WS-TOTAL32
           END-PERFORM.
           COMPUTE WS-AVERAGE32 = WS-TOTAL32 / 10.

       LOOKUP-ENTRY-SAFE23.
           ACCEPT WS-IDX23.
           IF WS-IDX23 > 0 AND WS-IDX23 NOT > 10
               MOVE WS-ENTRY23(WS-IDX23) TO WS-OUT23
           END-IF.

       CLASSIFY-CODE36.
           EVALUATE WS-CODE36
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS36
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS36
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS36
           END-EVALUATE.

       FORMAT-HEADER98.
           MOVE 'MONTHLY REPORT' TO WS-TITLE98.
           STRING WS-TITLE98 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER98.
           DISPLAY WS-HEADER98.

       CLASSIFY-CODE77.
           EVALUATE WS-CODE77
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS77
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS77
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS77
           END-EVALUATE.

       CLASSIFY-CODE120.
           EVALUATE WS-CODE120
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS120
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS120
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS120
           END-EVALUATE.

       FORMAT-HEADER97.
           MOVE 'MONTHLY REPORT' TO WS-TITLE97.
           STRING WS-TITLE97 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER97.
           DISPLAY WS-HEADER97.

       CLASSIFY-CODE99.
           EVALUATE WS-CODE99
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS99
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS99
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS99
           END-EVALUATE.

       COMPUTE-TOTALS44.
           MOVE 0 TO WS-TOTAL44.
           PERFORM VARYING WS-K44 FROM 1 BY 1 UNTIL WS-K44 > 10
               ADD WS-K44 TO WS-TOTAL44
           END-PERFORM.
           COMPUTE WS-AVERAGE44 = WS-TOTAL44 / 10.

       TRANSFER115.
           EXEC CICS RECEIVE INTO(WS-TARGET115) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET115) END-EXEC.

       TRANSFER109.
           EXEC CICS RECEIVE INTO(WS-TARGET109) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET109) END-EXEC.

       CHECK-LIMIT73.
           IF WS-AMOUNT73 > 1000
               MOVE 'Y' TO WS-FLAG73
           ELSE
               MOVE 'N' TO WS-FLAG73
           END-IF.

       LOOKUP-ENTRY16.
           ACCEPT WS-IDX16.
           MOVE WS-ENTRY16(WS-IDX16) TO WS-OUT16.

       CHECK-LIMIT64.
           IF WS-AMOUNT64 > 1000
               MOVE 'Y' TO WS-FLAG64
           ELSE
               MOVE 'N' TO WS-FLAG64
           END-IF.

       FORMAT-HEADER61.
           MOVE 'MONTHLY REPORT' TO WS-TITLE61.
           STRING WS-TITLE61 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER61.
           DISPLAY WS-HEADER61.

       COMPUTE-TOTALS48.
           MOVE 0 TO WS-TOTAL48.
           PERFORM VARYING WS-K48 FROM 1 BY 1 UNTIL WS-K48 > 10
               ADD WS-K48 TO WS-TOTAL48
           END-PERFORM.
           COMPUTE WS-AVERAGE48 = WS-TOTAL48 / 10.

       TRANSFER-SAFE91.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE134.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CLASSIFY-CODE112.
           EVALUATE WS-CODE112
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS112
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS112
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS112
           END-EVALUATE.

       LOOKUP-ENTRY110.
           ACCEPT WS-IDX110.
           MOVE WS-ENTRY110(WS-IDX110) TO WS-OUT110.

