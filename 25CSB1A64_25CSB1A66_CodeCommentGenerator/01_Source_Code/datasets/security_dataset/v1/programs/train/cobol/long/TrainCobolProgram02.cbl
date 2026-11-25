       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTR02.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EXPORT-FILE25 ASSIGN TO DYNAMIC WS-EXPORT-PATH25
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE42 ASSIGN TO DYNAMIC WS-EXPORT-PATH42
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE54 ASSIGN TO DYNAMIC WS-EXPORT-PATH54
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE55 ASSIGN TO DYNAMIC WS-EXPORT-PATH55
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE66 ASSIGN TO DYNAMIC WS-EXPORT-PATH66
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE94 ASSIGN TO DYNAMIC WS-EXPORT-PATH94
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE98 ASSIGN TO DYNAMIC WS-EXPORT-PATH98
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE99 ASSIGN TO DYNAMIC WS-EXPORT-PATH99
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE117 ASSIGN TO DYNAMIC WS-EXPORT-PATH117
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE124 ASSIGN TO DYNAMIC WS-EXPORT-PATH124
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE131 ASSIGN TO DYNAMIC WS-EXPORT-PATH131
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE135 ASSIGN TO DYNAMIC WS-EXPORT-PATH135
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  EXPORT-FILE25.
       01  EXPORT-LINE25         PIC X(80).
       FD  EXPORT-FILE42.
       01  EXPORT-LINE42         PIC X(80).
       FD  EXPORT-FILE54.
       01  EXPORT-LINE54         PIC X(80).
       FD  EXPORT-FILE55.
       01  EXPORT-LINE55         PIC X(80).
       FD  EXPORT-FILE66.
       01  EXPORT-LINE66         PIC X(80).
       FD  EXPORT-FILE94.
       01  EXPORT-LINE94         PIC X(80).
       FD  EXPORT-FILE98.
       01  EXPORT-LINE98         PIC X(80).
       FD  EXPORT-FILE99.
       01  EXPORT-LINE99         PIC X(80).
       FD  EXPORT-FILE117.
       01  EXPORT-LINE117         PIC X(80).
       FD  EXPORT-FILE124.
       01  EXPORT-LINE124         PIC X(80).
       FD  EXPORT-FILE131.
       01  EXPORT-LINE131         PIC X(80).
       FD  EXPORT-FILE135.
       01  EXPORT-LINE135         PIC X(80).
       WORKING-STORAGE SECTION.
       01  WS-USER1           PIC X(10).
       01  WS-PASSWORD-IN1    PIC X(12).
       01  WS-USER2           PIC X(10).
       01  WS-PASSWORD-IN2    PIC X(12).
       01  WS-DB-PASSWORD6    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW6        PIC X(12).
       01  WS-FORM10           PIC X(40).
       01  WS-PAGE10           PIC X(80).
       01  WS-POS11            PIC 99.
       01  WS-RECORD11         PIC X(80).
       01  WS-PART11           PIC X(5).
       01  WS-FORM13           PIC X(40).
       01  WS-PAGE13           PIC X(80).
       01  WS-CMD15            PIC X(100).
       01  WS-STMT17           PIC X(200).
       01  WS-DB-PASSWORD18    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW18        PIC X(12).
       01  WS-DB-PASSWORD19    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW19        PIC X(12).
       01  WS-STMT21           PIC X(200).
       01  WS-USER22           PIC X(10).
       01  WS-PASSWORD-IN22    PIC X(12).
       01  WS-USER23           PIC X(10).
       01  WS-PASSWORD-IN23    PIC X(12).
       01  WS-EXPORT-PATH25    PIC X(60).
       01  WS-STMT26           PIC X(200).
       01  WS-POS30            PIC 99.
       01  WS-RECORD30         PIC X(80).
       01  WS-PART30           PIC X(5).
       01  WS-CMD31            PIC X(100).
       01  WS-CMD32            PIC X(100).
       01  WS-STMT33           PIC X(200).
       01  WS-CMD35            PIC X(100).
       01  WS-POS38            PIC 99.
       01  WS-RECORD38         PIC X(80).
       01  WS-PART38           PIC X(5).
       01  WS-DB-PASSWORD39    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW39        PIC X(12).
       01  WS-USER40           PIC X(10).
       01  WS-PASSWORD-IN40    PIC X(12).
       01  WS-FORM41           PIC X(40).
       01  WS-PAGE41           PIC X(80).
       01  WS-EXPORT-PATH42    PIC X(60).
       01  WS-CMD43            PIC X(100).
       01  WS-FORM44           PIC X(40).
       01  WS-PAGE44           PIC X(80).
       01  WS-CMD45            PIC X(100).
       01  WS-FORM46           PIC X(40).
       01  WS-PAGE46           PIC X(80).
       01  WS-USER47           PIC X(10).
       01  WS-PASSWORD-IN47    PIC X(12).
       01  WS-POS48            PIC 99.
       01  WS-RECORD48         PIC X(80).
       01  WS-PART48           PIC X(5).
       01  WS-EXPORT-PATH54    PIC X(60).
       01  WS-EXPORT-PATH55    PIC X(60).
       01  WS-FORM57           PIC X(40).
       01  WS-PAGE57           PIC X(80).
       01  WS-POS59            PIC 99.
       01  WS-RECORD59         PIC X(80).
       01  WS-PART59           PIC X(5).
       01  WS-DB-PASSWORD61    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW61        PIC X(12).
       01  WS-EXPORT-PATH66    PIC X(60).
       01  WS-CMD67            PIC X(100).
       01  WS-STMT68           PIC X(200).
       01  WS-POS69            PIC 99.
       01  WS-RECORD69         PIC X(80).
       01  WS-PART69           PIC X(5).
       01  WS-USER74           PIC X(10).
       01  WS-PASSWORD-IN74    PIC X(12).
       01  WS-CMD77            PIC X(100).
       01  WS-DB-PASSWORD78    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW78        PIC X(12).
       01  WS-POS79            PIC 99.
       01  WS-RECORD79         PIC X(80).
       01  WS-PART79           PIC X(5).
       01  WS-STMT80           PIC X(200).
       01  WS-USER82           PIC X(10).
       01  WS-PASSWORD-IN82    PIC X(12).
       01  WS-DB-PASSWORD83    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW83        PIC X(12).
       01  WS-USER85           PIC X(10).
       01  WS-PASSWORD-IN85    PIC X(12).
       01  WS-USER89           PIC X(10).
       01  WS-PASSWORD-IN89    PIC X(12).
       01  WS-USER91           PIC X(10).
       01  WS-PASSWORD-IN91    PIC X(12).
       01  WS-FORM92           PIC X(40).
       01  WS-PAGE92           PIC X(80).
       01  WS-STMT93           PIC X(200).
       01  WS-EXPORT-PATH94    PIC X(60).
       01  WS-CMD96            PIC X(100).
       01  WS-DB-PASSWORD97    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW97        PIC X(12).
       01  WS-EXPORT-PATH98    PIC X(60).
       01  WS-EXPORT-PATH99    PIC X(60).
       01  WS-FORM101           PIC X(40).
       01  WS-PAGE101           PIC X(80).
       01  WS-DB-PASSWORD106    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW106        PIC X(12).
       01  WS-USER107           PIC X(10).
       01  WS-PASSWORD-IN107    PIC X(12).
       01  WS-STMT109           PIC X(200).
       01  WS-FORM110           PIC X(40).
       01  WS-PAGE110           PIC X(80).
       01  WS-DB-PASSWORD112    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW112        PIC X(12).
       01  WS-FORM113           PIC X(40).
       01  WS-PAGE113           PIC X(80).
       01  WS-EXPORT-PATH117    PIC X(60).
       01  WS-FORM123           PIC X(40).
       01  WS-PAGE123           PIC X(80).
       01  WS-EXPORT-PATH124    PIC X(60).
       01  WS-DB-PASSWORD130    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW130        PIC X(12).
       01  WS-EXPORT-PATH131    PIC X(60).
       01  WS-CMD133            PIC X(100).
       01  WS-DB-PASSWORD134    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW134        PIC X(12).
       01  WS-EXPORT-PATH135    PIC X(60).
       01  WS-USER137           PIC X(10).
       01  WS-PASSWORD-IN137    PIC X(12).
       01  WS-USER138           PIC X(10).
       01  WS-PASSWORD-IN138    PIC X(12).
       01  WS-USER141           PIC X(10).
       01  WS-PASSWORD-IN141    PIC X(12).
       01  WS-FORM144           PIC X(40).
       01  WS-PAGE144           PIC X(80).
       01  WS-FORM148           PIC X(40).
       01  WS-PAGE148           PIC X(80).
       01  WS-POS150            PIC 99.
       01  WS-RECORD150         PIC X(80).
       01  WS-PART150           PIC X(5).
       01  WS-TOTAL3          PIC 9(6) VALUE 0.
       01  WS-K3              PIC 99 VALUE 0.
       01  WS-AVERAGE3        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT4         PIC 9(6) VALUE 500.
       01  WS-FLAG4           PIC X VALUE 'N'.
       01  WS-AMOUNT5         PIC 9(6) VALUE 500.
       01  WS-FLAG5           PIC X VALUE 'N'.
       01  WS-AMOUNT7         PIC 9(6) VALUE 500.
       01  WS-FLAG7           PIC X VALUE 'N'.
       01  WS-AMOUNT8         PIC 9(6) VALUE 500.
       01  WS-FLAG8           PIC X VALUE 'N'.
       01  WS-TOTAL9          PIC 9(6) VALUE 0.
       01  WS-K9              PIC 99 VALUE 0.
       01  WS-AVERAGE9        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT12         PIC 9(6) VALUE 500.
       01  WS-FLAG12           PIC X VALUE 'N'.
       01  WS-TITLE14          PIC X(20) VALUE SPACES.
       01  WS-HEADER14         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT16         PIC 9(6) VALUE 500.
       01  WS-FLAG16           PIC X VALUE 'N'.
       01  WS-CODE20           PIC 9 VALUE 1.
       01  WS-STATUS20         PIC X(6) VALUE SPACES.
       01  WS-TITLE24          PIC X(20) VALUE SPACES.
       01  WS-HEADER24         PIC X(40) VALUE SPACES.
       01  WS-TITLE27          PIC X(20) VALUE SPACES.
       01  WS-HEADER27         PIC X(40) VALUE SPACES.
       01  WS-CODE28           PIC 9 VALUE 1.
       01  WS-STATUS28         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT29         PIC 9(6) VALUE 500.
       01  WS-FLAG29           PIC X VALUE 'N'.
       01  WS-TITLE34          PIC X(20) VALUE SPACES.
       01  WS-HEADER34         PIC X(40) VALUE SPACES.
       01  WS-CODE36           PIC 9 VALUE 1.
       01  WS-STATUS36         PIC X(6) VALUE SPACES.
       01  WS-TOTAL37          PIC 9(6) VALUE 0.
       01  WS-K37              PIC 99 VALUE 0.
       01  WS-AVERAGE37        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL49          PIC 9(6) VALUE 0.
       01  WS-K49              PIC 99 VALUE 0.
       01  WS-AVERAGE49        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL50          PIC 9(6) VALUE 0.
       01  WS-K50              PIC 99 VALUE 0.
       01  WS-AVERAGE50        PIC 9(6)V99 VALUE 0.
       01  WS-CODE51           PIC 9 VALUE 1.
       01  WS-STATUS51         PIC X(6) VALUE SPACES.
       01  WS-TOTAL52          PIC 9(6) VALUE 0.
       01  WS-K52              PIC 99 VALUE 0.
       01  WS-AVERAGE52        PIC 9(6)V99 VALUE 0.
       01  WS-CODE53           PIC 9 VALUE 1.
       01  WS-STATUS53         PIC X(6) VALUE SPACES.
       01  WS-TITLE56          PIC X(20) VALUE SPACES.
       01  WS-HEADER56         PIC X(40) VALUE SPACES.
       01  WS-TOTAL58          PIC 9(6) VALUE 0.
       01  WS-K58              PIC 99 VALUE 0.
       01  WS-AVERAGE58        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE60          PIC X(20) VALUE SPACES.
       01  WS-HEADER60         PIC X(40) VALUE SPACES.
       01  WS-CODE62           PIC 9 VALUE 1.
       01  WS-STATUS62         PIC X(6) VALUE SPACES.
       01  WS-TOTAL63          PIC 9(6) VALUE 0.
       01  WS-K63              PIC 99 VALUE 0.
       01  WS-AVERAGE63        PIC 9(6)V99 VALUE 0.
       01  WS-CODE64           PIC 9 VALUE 1.
       01  WS-STATUS64         PIC X(6) VALUE SPACES.
       01  WS-TITLE65          PIC X(20) VALUE SPACES.
       01  WS-HEADER65         PIC X(40) VALUE SPACES.
       01  WS-TOTAL70          PIC 9(6) VALUE 0.
       01  WS-K70              PIC 99 VALUE 0.
       01  WS-AVERAGE70        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE71          PIC X(20) VALUE SPACES.
       01  WS-HEADER71         PIC X(40) VALUE SPACES.
       01  WS-TITLE72          PIC X(20) VALUE SPACES.
       01  WS-HEADER72         PIC X(40) VALUE SPACES.
       01  WS-TITLE73          PIC X(20) VALUE SPACES.
       01  WS-HEADER73         PIC X(40) VALUE SPACES.
       01  WS-TITLE75          PIC X(20) VALUE SPACES.
       01  WS-HEADER75         PIC X(40) VALUE SPACES.
       01  WS-TITLE76          PIC X(20) VALUE SPACES.
       01  WS-HEADER76         PIC X(40) VALUE SPACES.
       01  WS-TOTAL81          PIC 9(6) VALUE 0.
       01  WS-K81              PIC 99 VALUE 0.
       01  WS-AVERAGE81        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL84          PIC 9(6) VALUE 0.
       01  WS-K84              PIC 99 VALUE 0.
       01  WS-AVERAGE84        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL86          PIC 9(6) VALUE 0.
       01  WS-K86              PIC 99 VALUE 0.
       01  WS-AVERAGE86        PIC 9(6)V99 VALUE 0.
       01  WS-CODE87           PIC 9 VALUE 1.
       01  WS-STATUS87         PIC X(6) VALUE SPACES.
       01  WS-TITLE88          PIC X(20) VALUE SPACES.
       01  WS-HEADER88         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT90         PIC 9(6) VALUE 500.
       01  WS-FLAG90           PIC X VALUE 'N'.
       01  WS-CODE95           PIC 9 VALUE 1.
       01  WS-STATUS95         PIC X(6) VALUE SPACES.
       01  WS-CODE100           PIC 9 VALUE 1.
       01  WS-STATUS100         PIC X(6) VALUE SPACES.
       01  WS-TITLE102          PIC X(20) VALUE SPACES.
       01  WS-HEADER102         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT103         PIC 9(6) VALUE 500.
       01  WS-FLAG103           PIC X VALUE 'N'.
       01  WS-CODE104           PIC 9 VALUE 1.
       01  WS-STATUS104         PIC X(6) VALUE SPACES.
       01  WS-TITLE105          PIC X(20) VALUE SPACES.
       01  WS-HEADER105         PIC X(40) VALUE SPACES.
       01  WS-TITLE108          PIC X(20) VALUE SPACES.
       01  WS-HEADER108         PIC X(40) VALUE SPACES.
       01  WS-TOTAL111          PIC 9(6) VALUE 0.
       01  WS-K111              PIC 99 VALUE 0.
       01  WS-AVERAGE111        PIC 9(6)V99 VALUE 0.
       01  WS-CODE114           PIC 9 VALUE 1.
       01  WS-STATUS114         PIC X(6) VALUE SPACES.
       01  WS-TOTAL115          PIC 9(6) VALUE 0.
       01  WS-K115              PIC 99 VALUE 0.
       01  WS-AVERAGE115        PIC 9(6)V99 VALUE 0.
       01  WS-CODE116           PIC 9 VALUE 1.
       01  WS-STATUS116         PIC X(6) VALUE SPACES.
       01  WS-CODE118           PIC 9 VALUE 1.
       01  WS-STATUS118         PIC X(6) VALUE SPACES.
       01  WS-CODE119           PIC 9 VALUE 1.
       01  WS-STATUS119         PIC X(6) VALUE SPACES.
       01  WS-TOTAL120          PIC 9(6) VALUE 0.
       01  WS-K120              PIC 99 VALUE 0.
       01  WS-AVERAGE120        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT121         PIC 9(6) VALUE 500.
       01  WS-FLAG121           PIC X VALUE 'N'.
       01  WS-TOTAL122          PIC 9(6) VALUE 0.
       01  WS-K122              PIC 99 VALUE 0.
       01  WS-AVERAGE122        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE125          PIC X(20) VALUE SPACES.
       01  WS-HEADER125         PIC X(40) VALUE SPACES.
       01  WS-TOTAL126          PIC 9(6) VALUE 0.
       01  WS-K126              PIC 99 VALUE 0.
       01  WS-AVERAGE126        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE127          PIC X(20) VALUE SPACES.
       01  WS-HEADER127         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT128         PIC 9(6) VALUE 500.
       01  WS-FLAG128           PIC X VALUE 'N'.
       01  WS-CODE129           PIC 9 VALUE 1.
       01  WS-STATUS129         PIC X(6) VALUE SPACES.
       01  WS-TITLE132          PIC X(20) VALUE SPACES.
       01  WS-HEADER132         PIC X(40) VALUE SPACES.
       01  WS-TOTAL136          PIC 9(6) VALUE 0.
       01  WS-K136              PIC 99 VALUE 0.
       01  WS-AVERAGE136        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL139          PIC 9(6) VALUE 0.
       01  WS-K139              PIC 99 VALUE 0.
       01  WS-AVERAGE139        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE140          PIC X(20) VALUE SPACES.
       01  WS-HEADER140         PIC X(40) VALUE SPACES.
       01  WS-TOTAL142          PIC 9(6) VALUE 0.
       01  WS-K142              PIC 99 VALUE 0.
       01  WS-AVERAGE142        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT143         PIC 9(6) VALUE 500.
       01  WS-FLAG143           PIC X VALUE 'N'.
       01  WS-TITLE145          PIC X(20) VALUE SPACES.
       01  WS-HEADER145         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT146         PIC 9(6) VALUE 500.
       01  WS-FLAG146           PIC X VALUE 'N'.
       01  WS-TOTAL147          PIC 9(6) VALUE 0.
       01  WS-K147              PIC 99 VALUE 0.
       01  WS-AVERAGE147        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT149         PIC 9(6) VALUE 500.
       01  WS-FLAG149           PIC X VALUE 'N'.
       01  WS-TITLE151          PIC X(20) VALUE SPACES.
       01  WS-HEADER151         PIC X(40) VALUE SPACES.
       01  WS-CODE152           PIC 9 VALUE 1.
       01  WS-STATUS152         PIC X(6) VALUE SPACES.
       LINKAGE SECTION.
       01  LK-NAME15           PIC X(40).
       01  LK-FILTER17         PIC X(100).
       01  LK-FILTER21         PIC X(100).
       01  LK-PATH25           PIC X(60).
       01  LK-FILTER26         PIC X(100).
       01  LK-NAME31           PIC X(40).
       01  LK-NAME32           PIC X(40).
       01  LK-FILTER33         PIC X(100).
       01  LK-NAME35           PIC X(40).
       01  LK-PATH42           PIC X(60).
       01  LK-NAME43           PIC X(40).
       01  LK-NAME45           PIC X(40).
       01  LK-PATH54           PIC X(60).
       01  LK-PATH55           PIC X(60).
       01  LK-PATH66           PIC X(60).
       01  LK-NAME67           PIC X(40).
       01  LK-FILTER68         PIC X(100).
       01  LK-NAME77           PIC X(40).
       01  LK-FILTER80         PIC X(100).
       01  LK-FILTER93         PIC X(100).
       01  LK-PATH94           PIC X(60).
       01  LK-NAME96           PIC X(40).
       01  LK-PATH98           PIC X(60).
       01  LK-PATH99           PIC X(60).
       01  LK-FILTER109         PIC X(100).
       01  LK-PATH117           PIC X(60).
       01  LK-PATH124           PIC X(60).
       01  LK-PATH131           PIC X(60).
       01  LK-NAME133           PIC X(40).
       01  LK-PATH135           PIC X(60).
       PROCEDURE DIVISION USING LK-NAME15 LK-FILTER17 LK-FILTER21 LK-PATH25 LK-FILTER26 LK-NAME31 LK-NAME32 LK-FILTER33 LK-NAME35 LK-PATH42 LK-NAME43 LK-NAME45 LK-PATH54 LK-PATH55 LK-PATH66 LK-NAME67 LK-FILTER68 LK-NAME77 LK-FILTER80 LK-FILTER93 LK-PATH94 LK-NAME96 LK-PATH98 LK-PATH99 LK-FILTER109 LK-PATH117 LK-PATH124 LK-PATH131 LK-NAME133 LK-PATH135.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       PREPARE-QUERY21.
           MOVE LK-FILTER21 TO WS-STMT21.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT21 END-EXEC.

       EXTRACT-FIELD69.
           ACCEPT WS-POS69.
           MOVE WS-RECORD69(WS-POS69:5) TO WS-PART69.

       COMPUTE-TOTALS52.
           MOVE 0 TO WS-TOTAL52.
           PERFORM VARYING WS-K52 FROM 1 BY 1 UNTIL WS-K52 > 10
               ADD WS-K52 TO WS-TOTAL52
           END-PERFORM.
           COMPUTE WS-AVERAGE52 = WS-TOTAL52 / 10.

       EXTRACT-FIELD-SAFE79.
           ACCEPT WS-POS79.
           IF WS-POS79 IS NUMERIC AND WS-POS79 > 0 AND WS-POS79 < 76
               MOVE WS-RECORD79(WS-POS79:5) TO WS-PART79
           END-IF.

       CHECK-LIMIT149.
           IF WS-AMOUNT149 > 1000
               MOVE 'Y' TO WS-FLAG149
           ELSE
               MOVE 'N' TO WS-FLAG149
           END-IF.

       COMPUTE-TOTALS81.
           MOVE 0 TO WS-TOTAL81.
           PERFORM VARYING WS-K81 FROM 1 BY 1 UNTIL WS-K81 > 10
               ADD WS-K81 TO WS-TOTAL81
           END-PERFORM.
           COMPUTE WS-AVERAGE81 = WS-TOTAL81 / 10.

       PREPARE-QUERY93.
           MOVE LK-FILTER93 TO WS-STMT93.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT93 END-EXEC.

       FORMAT-HEADER151.
           MOVE 'MONTHLY REPORT' TO WS-TITLE151.
           STRING WS-TITLE151 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER151.
           DISPLAY WS-HEADER151.

       FORMAT-HEADER71.
           MOVE 'MONTHLY REPORT' TO WS-TITLE71.
           STRING WS-TITLE71 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER71.
           DISPLAY WS-HEADER71.

       WRITE-EXPORT55.
           MOVE LK-PATH55 TO WS-EXPORT-PATH55.
           OPEN OUTPUT EXPORT-FILE55.
           CLOSE EXPORT-FILE55.

       COMPUTE-TOTALS86.
           MOVE 0 TO WS-TOTAL86.
           PERFORM VARYING WS-K86 FROM 1 BY 1 UNTIL WS-K86 > 10
               ADD WS-K86 TO WS-TOTAL86
           END-PERFORM.
           COMPUTE WS-AVERAGE86 = WS-TOTAL86 / 10.

       CONVERT-FILE-SAFE45.
           MOVE "convert /srv/in/report.txt" TO WS-CMD45.
           CALL 'SYSTEM' USING WS-CMD45.

       CLASSIFY-CODE53.
           EVALUATE WS-CODE53
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS53
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS53
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS53
           END-EVALUATE.

       EXTRACT-FIELD150.
           ACCEPT WS-POS150.
           MOVE WS-RECORD150(WS-POS150:5) TO WS-PART150.

       COMPUTE-TOTALS126.
           MOVE 0 TO WS-TOTAL126.
           PERFORM VARYING WS-K126 FROM 1 BY 1 UNTIL WS-K126 > 10
               ADD WS-K126 TO WS-TOTAL126
           END-PERFORM.
           COMPUTE WS-AVERAGE126 = WS-TOTAL126 / 10.

       CLASSIFY-CODE36.
           EVALUATE WS-CODE36
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS36
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS36
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS36
           END-EVALUATE.

       EXTRACT-FIELD-SAFE30.
           ACCEPT WS-POS30.
           IF WS-POS30 IS NUMERIC AND WS-POS30 > 0 AND WS-POS30 < 76
               MOVE WS-RECORD30(WS-POS30:5) TO WS-PART30
           END-IF.

       ECHO-NAME-SAFE13.
           MOVE '<p>Thank you</p>' TO WS-PAGE13.
           EXEC CICS WEB SEND FROM(WS-PAGE13) END-EXEC.

       CONVERT-FILE-SAFE67.
           MOVE "convert /srv/in/report.txt" TO WS-CMD67.
           CALL 'SYSTEM' USING WS-CMD67.

       FORMAT-HEADER140.
           MOVE 'MONTHLY REPORT' TO WS-TITLE140.
           STRING WS-TITLE140 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER140.
           DISPLAY WS-HEADER140.

       ECHO-NAME-SAFE101.
           MOVE '<p>Thank you</p>' TO WS-PAGE101.
           EXEC CICS WEB SEND FROM(WS-PAGE101) END-EXEC.

       ECHO-NAME-SAFE44.
           MOVE '<p>Thank you</p>' TO WS-PAGE44.
           EXEC CICS WEB SEND FROM(WS-PAGE44) END-EXEC.

       FORMAT-HEADER14.
           MOVE 'MONTHLY REPORT' TO WS-TITLE14.
           STRING WS-TITLE14 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER14.
           DISPLAY WS-HEADER14.

       WRITE-EXPORT25.
           MOVE LK-PATH25 TO WS-EXPORT-PATH25.
           OPEN OUTPUT EXPORT-FILE25.
           CLOSE EXPORT-FILE25.

       FORMAT-HEADER65.
           MOVE 'MONTHLY REPORT' TO WS-TITLE65.
           STRING WS-TITLE65 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER65.
           DISPLAY WS-HEADER65.

       WRITE-EXPORT42.
           MOVE LK-PATH42 TO WS-EXPORT-PATH42.
           OPEN OUTPUT EXPORT-FILE42.
           CLOSE EXPORT-FILE42.

       FORMAT-HEADER145.
           MOVE 'MONTHLY REPORT' TO WS-TITLE145.
           STRING WS-TITLE145 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER145.
           DISPLAY WS-HEADER145.

       WRITE-EXPORT-SAFE135.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH135.
           OPEN OUTPUT EXPORT-FILE135.
           CLOSE EXPORT-FILE135.

       WRITE-EXPORT-SAFE66.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH66.
           OPEN OUTPUT EXPORT-FILE66.
           CLOSE EXPORT-FILE66.

       FORMAT-HEADER108.
           MOVE 'MONTHLY REPORT' TO WS-TITLE108.
           STRING WS-TITLE108 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER108.
           DISPLAY WS-HEADER108.

       ECHO-NAME10.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM10) END-EXEC.
           STRING '<p>' WS-FORM10 '</p>' DELIMITED BY SIZE INTO WS-PAGE10.
           EXEC CICS WEB SEND FROM(WS-PAGE10) END-EXEC.

       COMPUTE-TOTALS50.
           MOVE 0 TO WS-TOTAL50.
           PERFORM VARYING WS-K50 FROM 1 BY 1 UNTIL WS-K50 > 10
               ADD WS-K50 TO WS-TOTAL50
           END-PERFORM.
           COMPUTE WS-AVERAGE50 = WS-TOTAL50 / 10.

       CHECK-LIMIT121.
           IF WS-AMOUNT121 > 1000
               MOVE 'Y' TO WS-FLAG121
           ELSE
               MOVE 'N' TO WS-FLAG121
           END-IF.

       EXTRACT-FIELD38.
           ACCEPT WS-POS38.
           MOVE WS-RECORD38(WS-POS38:5) TO WS-PART38.

       CHECK-LIMIT90.
           IF WS-AMOUNT90 > 1000
               MOVE 'Y' TO WS-FLAG90
           ELSE
               MOVE 'N' TO WS-FLAG90
           END-IF.

       CONNECT-DB-SAFE130.
           ACCEPT WS-CONN-PW130 FROM ENVIRONMENT 'DB_PASSWORD'.

       FORMAT-HEADER27.
           MOVE 'MONTHLY REPORT' TO WS-TITLE27.
           STRING WS-TITLE27 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER27.
           DISPLAY WS-HEADER27.

       FORMAT-HEADER24.
           MOVE 'MONTHLY REPORT' TO WS-TITLE24.
           STRING WS-TITLE24 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER24.
           DISPLAY WS-HEADER24.

       CONNECT-DB-SAFE6.
           ACCEPT WS-CONN-PW6 FROM ENVIRONMENT 'DB_PASSWORD'.

       FORMAT-HEADER73.
           MOVE 'MONTHLY REPORT' TO WS-TITLE73.
           STRING WS-TITLE73 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER73.
           DISPLAY WS-HEADER73.

       EXTRACT-FIELD59.
           ACCEPT WS-POS59.
           MOVE WS-RECORD59(WS-POS59:5) TO WS-PART59.

       LOG-LOGIN-SAFE107.
           DISPLAY 'LOGIN ' WS-USER107.

       CLASSIFY-CODE20.
           EVALUATE WS-CODE20
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS20
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS20
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS20
           END-EVALUATE.

       FORMAT-HEADER56.
           MOVE 'MONTHLY REPORT' TO WS-TITLE56.
           STRING WS-TITLE56 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER56.
           DISPLAY WS-HEADER56.

       COMPUTE-TOTALS120.
           MOVE 0 TO WS-TOTAL120.
           PERFORM VARYING WS-K120 FROM 1 BY 1 UNTIL WS-K120 > 10
               ADD WS-K120 TO WS-TOTAL120
           END-PERFORM.
           COMPUTE WS-AVERAGE120 = WS-TOTAL120 / 10.

       CONVERT-FILE-SAFE32.
           MOVE "convert /srv/in/report.txt" TO WS-CMD32.
           CALL 'SYSTEM' USING WS-CMD32.

       FORMAT-HEADER60.
           MOVE 'MONTHLY REPORT' TO WS-TITLE60.
           STRING WS-TITLE60 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER60.
           DISPLAY WS-HEADER60.

       ECHO-NAME144.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM144) END-EXEC.
           STRING '<p>' WS-FORM144 '</p>' DELIMITED BY SIZE INTO WS-PAGE144.
           EXEC CICS WEB SEND FROM(WS-PAGE144) END-EXEC.

       CONVERT-FILE-SAFE35.
           MOVE "convert /srv/in/report.txt" TO WS-CMD35.
           CALL 'SYSTEM' USING WS-CMD35.

       CHECK-LIMIT103.
           IF WS-AMOUNT103 > 1000
               MOVE 'Y' TO WS-FLAG103
           ELSE
               MOVE 'N' TO WS-FLAG103
           END-IF.

       COMPUTE-TOTALS122.
           MOVE 0 TO WS-TOTAL122.
           PERFORM VARYING WS-K122 FROM 1 BY 1 UNTIL WS-K122 > 10
               ADD WS-K122 TO WS-TOTAL122
           END-PERFORM.
           COMPUTE WS-AVERAGE122 = WS-TOTAL122 / 10.

       LOG-LOGIN85.
           DISPLAY 'LOGIN ' WS-USER85 ' ' WS-PASSWORD-IN85.

       FORMAT-HEADER105.
           MOVE 'MONTHLY REPORT' TO WS-TITLE105.
           STRING WS-TITLE105 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER105.
           DISPLAY WS-HEADER105.

       CLASSIFY-CODE64.
           EVALUATE WS-CODE64
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS64
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS64
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS64
           END-EVALUATE.

       LOG-LOGIN82.
           DISPLAY 'LOGIN ' WS-USER82 ' ' WS-PASSWORD-IN82.

       COMPUTE-TOTALS111.
           MOVE 0 TO WS-TOTAL111.
           PERFORM VARYING WS-K111 FROM 1 BY 1 UNTIL WS-K111 > 10
               ADD WS-K111 TO WS-TOTAL111
           END-PERFORM.
           COMPUTE WS-AVERAGE111 = WS-TOTAL111 / 10.

       CLASSIFY-CODE100.
           EVALUATE WS-CODE100
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS100
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS100
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS100
           END-EVALUATE.

       LOG-LOGIN-SAFE138.
           DISPLAY 'LOGIN ' WS-USER138.

       COMPUTE-TOTALS147.
           MOVE 0 TO WS-TOTAL147.
           PERFORM VARYING WS-K147 FROM 1 BY 1 UNTIL WS-K147 > 10
               ADD WS-K147 TO WS-TOTAL147
           END-PERFORM.
           COMPUTE WS-AVERAGE147 = WS-TOTAL147 / 10.

       CHECK-LIMIT12.
           IF WS-AMOUNT12 > 1000
               MOVE 'Y' TO WS-FLAG12
           ELSE
               MOVE 'N' TO WS-FLAG12
           END-IF.

       CLASSIFY-CODE87.
           EVALUATE WS-CODE87
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS87
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS87
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS87
           END-EVALUATE.

       CLASSIFY-CODE95.
           EVALUATE WS-CODE95
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS95
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS95
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS95
           END-EVALUATE.

       CLASSIFY-CODE119.
           EVALUATE WS-CODE119
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS119
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS119
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS119
           END-EVALUATE.

       LOG-LOGIN-SAFE89.
           DISPLAY 'LOGIN ' WS-USER89.

       FORMAT-HEADER76.
           MOVE 'MONTHLY REPORT' TO WS-TITLE76.
           STRING WS-TITLE76 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER76.
           DISPLAY WS-HEADER76.

       CONNECT-DB134.
           MOVE WS-DB-PASSWORD134 TO WS-CONN-PW134.

       PREPARE-QUERY-SAFE26.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT26.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT26 END-EXEC.

       CONNECT-DB78.
           MOVE WS-DB-PASSWORD78 TO WS-CONN-PW78.

       FORMAT-HEADER75.
           MOVE 'MONTHLY REPORT' TO WS-TITLE75.
           STRING WS-TITLE75 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER75.
           DISPLAY WS-HEADER75.

       FORMAT-HEADER125.
           MOVE 'MONTHLY REPORT' TO WS-TITLE125.
           STRING WS-TITLE125 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER125.
           DISPLAY WS-HEADER125.

       CLASSIFY-CODE116.
           EVALUATE WS-CODE116
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS116
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS116
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS116
           END-EVALUATE.

       COMPUTE-TOTALS115.
           MOVE 0 TO WS-TOTAL115.
           PERFORM VARYING WS-K115 FROM 1 BY 1 UNTIL WS-K115 > 10
               ADD WS-K115 TO WS-TOTAL115
           END-PERFORM.
           COMPUTE WS-AVERAGE115 = WS-TOTAL115 / 10.

       CONVERT-FILE133.
           STRING "convert " LK-NAME133 DELIMITED BY SIZE INTO WS-CMD133.
           CALL 'SYSTEM' USING WS-CMD133.

       CLASSIFY-CODE104.
           EVALUATE WS-CODE104
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS104
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS104
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS104
           END-EVALUATE.

       COMPUTE-TOTALS3.
           MOVE 0 TO WS-TOTAL3.
           PERFORM VARYING WS-K3 FROM 1 BY 1 UNTIL WS-K3 > 10
               ADD WS-K3 TO WS-TOTAL3
           END-PERFORM.
           COMPUTE WS-AVERAGE3 = WS-TOTAL3 / 10.

       FORMAT-HEADER88.
           MOVE 'MONTHLY REPORT' TO WS-TITLE88.
           STRING WS-TITLE88 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER88.
           DISPLAY WS-HEADER88.

       COMPUTE-TOTALS49.
           MOVE 0 TO WS-TOTAL49.
           PERFORM VARYING WS-K49 FROM 1 BY 1 UNTIL WS-K49 > 10
               ADD WS-K49 TO WS-TOTAL49
           END-PERFORM.
           COMPUTE WS-AVERAGE49 = WS-TOTAL49 / 10.

       EXTRACT-FIELD-SAFE48.
           ACCEPT WS-POS48.
           IF WS-POS48 IS NUMERIC AND WS-POS48 > 0 AND WS-POS48 < 76
               MOVE WS-RECORD48(WS-POS48:5) TO WS-PART48
           END-IF.

       WRITE-EXPORT-SAFE131.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH131.
           OPEN OUTPUT EXPORT-FILE131.
           CLOSE EXPORT-FILE131.

       LOG-LOGIN-SAFE47.
           DISPLAY 'LOGIN ' WS-USER47.

       CLASSIFY-CODE51.
           EVALUATE WS-CODE51
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS51
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS51
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS51
           END-EVALUATE.

       CONNECT-DB-SAFE97.
           ACCEPT WS-CONN-PW97 FROM ENVIRONMENT 'DB_PASSWORD'.

       CHECK-LIMIT29.
           IF WS-AMOUNT29 > 1000
               MOVE 'Y' TO WS-FLAG29
           ELSE
               MOVE 'N' TO WS-FLAG29
           END-IF.

       CHECK-LIMIT5.
           IF WS-AMOUNT5 > 1000
               MOVE 'Y' TO WS-FLAG5
           ELSE
               MOVE 'N' TO WS-FLAG5
           END-IF.

       WRITE-EXPORT98.
           MOVE LK-PATH98 TO WS-EXPORT-PATH98.
           OPEN OUTPUT EXPORT-FILE98.
           CLOSE EXPORT-FILE98.

       CONNECT-DB19.
           MOVE WS-DB-PASSWORD19 TO WS-CONN-PW19.

       LOG-LOGIN137.
           DISPLAY 'LOGIN ' WS-USER137 ' ' WS-PASSWORD-IN137.

       CONNECT-DB-SAFE83.
           ACCEPT WS-CONN-PW83 FROM ENVIRONMENT 'DB_PASSWORD'.

       WRITE-EXPORT117.
           MOVE LK-PATH117 TO WS-EXPORT-PATH117.
           OPEN OUTPUT EXPORT-FILE117.
           CLOSE EXPORT-FILE117.

       FORMAT-HEADER132.
           MOVE 'MONTHLY REPORT' TO WS-TITLE132.
           STRING WS-TITLE132 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER132.
           DISPLAY WS-HEADER132.

       COMPUTE-TOTALS142.
           MOVE 0 TO WS-TOTAL142.
           PERFORM VARYING WS-K142 FROM 1 BY 1 UNTIL WS-K142 > 10
               ADD WS-K142 TO WS-TOTAL142
           END-PERFORM.
           COMPUTE WS-AVERAGE142 = WS-TOTAL142 / 10.

       COMPUTE-TOTALS84.
           MOVE 0 TO WS-TOTAL84.
           PERFORM VARYING WS-K84 FROM 1 BY 1 UNTIL WS-K84 > 10
               ADD WS-K84 TO WS-TOTAL84
           END-PERFORM.
           COMPUTE WS-AVERAGE84 = WS-TOTAL84 / 10.

       CLASSIFY-CODE129.
           EVALUATE WS-CODE129
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS129
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS129
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS129
           END-EVALUATE.

       CONVERT-FILE77.
           STRING "convert " LK-NAME77 DELIMITED BY SIZE INTO WS-CMD77.
           CALL 'SYSTEM' USING WS-CMD77.

       LOG-LOGIN40.
           DISPLAY 'LOGIN ' WS-USER40 ' ' WS-PASSWORD-IN40.

       CONVERT-FILE96.
           STRING "convert " LK-NAME96 DELIMITED BY SIZE INTO WS-CMD96.
           CALL 'SYSTEM' USING WS-CMD96.

       WRITE-EXPORT-SAFE94.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH94.
           OPEN OUTPUT EXPORT-FILE94.
           CLOSE EXPORT-FILE94.

       CONNECT-DB-SAFE18.
           ACCEPT WS-CONN-PW18 FROM ENVIRONMENT 'DB_PASSWORD'.

       PREPARE-QUERY33.
           MOVE LK-FILTER33 TO WS-STMT33.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT33 END-EXEC.

       FORMAT-HEADER34.
           MOVE 'MONTHLY REPORT' TO WS-TITLE34.
           STRING WS-TITLE34 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER34.
           DISPLAY WS-HEADER34.

       CONNECT-DB112.
           MOVE WS-DB-PASSWORD112 TO WS-CONN-PW112.

       ECHO-NAME57.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM57) END-EXEC.
           STRING '<p>' WS-FORM57 '</p>' DELIMITED BY SIZE INTO WS-PAGE57.
           EXEC CICS WEB SEND FROM(WS-PAGE57) END-EXEC.

       PREPARE-QUERY68.
           MOVE LK-FILTER68 TO WS-STMT68.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT68 END-EXEC.

       CLASSIFY-CODE118.
           EVALUATE WS-CODE118
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS118
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS118
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS118
           END-EVALUATE.

       CLASSIFY-CODE152.
           EVALUATE WS-CODE152
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS152
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS152
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS152
           END-EVALUATE.

       ECHO-NAME41.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM41) END-EXEC.
           STRING '<p>' WS-FORM41 '</p>' DELIMITED BY SIZE INTO WS-PAGE41.
           EXEC CICS WEB SEND FROM(WS-PAGE41) END-EXEC.

       ECHO-NAME113.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM113) END-EXEC.
           STRING '<p>' WS-FORM113 '</p>' DELIMITED BY SIZE INTO WS-PAGE113.
           EXEC CICS WEB SEND FROM(WS-PAGE113) END-EXEC.

       PREPARE-QUERY-SAFE80.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT80.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT80 END-EXEC.

       CHECK-LIMIT146.
           IF WS-AMOUNT146 > 1000
               MOVE 'Y' TO WS-FLAG146
           ELSE
               MOVE 'N' TO WS-FLAG146
           END-IF.

       ECHO-NAME123.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM123) END-EXEC.
           STRING '<p>' WS-FORM123 '</p>' DELIMITED BY SIZE INTO WS-PAGE123.
           EXEC CICS WEB SEND FROM(WS-PAGE123) END-EXEC.

       ECHO-NAME92.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM92) END-EXEC.
           STRING '<p>' WS-FORM92 '</p>' DELIMITED BY SIZE INTO WS-PAGE92.
           EXEC CICS WEB SEND FROM(WS-PAGE92) END-EXEC.

       CONVERT-FILE-SAFE15.
           MOVE "convert /srv/in/report.txt" TO WS-CMD15.
           CALL 'SYSTEM' USING WS-CMD15.

       FORMAT-HEADER127.
           MOVE 'MONTHLY REPORT' TO WS-TITLE127.
           STRING WS-TITLE127 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER127.
           DISPLAY WS-HEADER127.

       LOG-LOGIN-SAFE91.
           DISPLAY 'LOGIN ' WS-USER91.

       FORMAT-HEADER102.
           MOVE 'MONTHLY REPORT' TO WS-TITLE102.
           STRING WS-TITLE102 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER102.
           DISPLAY WS-HEADER102.

       LOG-LOGIN141.
           DISPLAY 'LOGIN ' WS-USER141 ' ' WS-PASSWORD-IN141.

       LOG-LOGIN-SAFE22.
           DISPLAY 'LOGIN ' WS-USER22.

       COMPUTE-TOTALS63.
           MOVE 0 TO WS-TOTAL63.
           PERFORM VARYING WS-K63 FROM 1 BY 1 UNTIL WS-K63 > 10
               ADD WS-K63 TO WS-TOTAL63
           END-PERFORM.
           COMPUTE WS-AVERAGE63 = WS-TOTAL63 / 10.

       CONNECT-DB106.
           MOVE WS-DB-PASSWORD106 TO WS-CONN-PW106.

       CLASSIFY-CODE114.
           EVALUATE WS-CODE114
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS114
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS114
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS114
           END-EVALUATE.

       CONNECT-DB-SAFE39.
           ACCEPT WS-CONN-PW39 FROM ENVIRONMENT 'DB_PASSWORD'.

       LOG-LOGIN-SAFE74.
           DISPLAY 'LOGIN ' WS-USER74.

       COMPUTE-TOTALS139.
           MOVE 0 TO WS-TOTAL139.
           PERFORM VARYING WS-K139 FROM 1 BY 1 UNTIL WS-K139 > 10
               ADD WS-K139 TO WS-TOTAL139
           END-PERFORM.
           COMPUTE WS-AVERAGE139 = WS-TOTAL139 / 10.

       LOG-LOGIN1.
           DISPLAY 'LOGIN ' WS-USER1 ' ' WS-PASSWORD-IN1.

       COMPUTE-TOTALS58.
           MOVE 0 TO WS-TOTAL58.
           PERFORM VARYING WS-K58 FROM 1 BY 1 UNTIL WS-K58 > 10
               ADD WS-K58 TO WS-TOTAL58
           END-PERFORM.
           COMPUTE WS-AVERAGE58 = WS-TOTAL58 / 10.

       PREPARE-QUERY-SAFE17.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT17.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT17 END-EXEC.

       ECHO-NAME46.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM46) END-EXEC.
           STRING '<p>' WS-FORM46 '</p>' DELIMITED BY SIZE INTO WS-PAGE46.
           EXEC CICS WEB SEND FROM(WS-PAGE46) END-EXEC.

       ECHO-NAME110.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM110) END-EXEC.
           STRING '<p>' WS-FORM110 '</p>' DELIMITED BY SIZE INTO WS-PAGE110.
           EXEC CICS WEB SEND FROM(WS-PAGE110) END-EXEC.

       CHECK-LIMIT4.
           IF WS-AMOUNT4 > 1000
               MOVE 'Y' TO WS-FLAG4
           ELSE
               MOVE 'N' TO WS-FLAG4
           END-IF.

       COMPUTE-TOTALS9.
           MOVE 0 TO WS-TOTAL9.
           PERFORM VARYING WS-K9 FROM 1 BY 1 UNTIL WS-K9 > 10
               ADD WS-K9 TO WS-TOTAL9
           END-PERFORM.
           COMPUTE WS-AVERAGE9 = WS-TOTAL9 / 10.

       COMPUTE-TOTALS37.
           MOVE 0 TO WS-TOTAL37.
           PERFORM VARYING WS-K37 FROM 1 BY 1 UNTIL WS-K37 > 10
               ADD WS-K37 TO WS-TOTAL37
           END-PERFORM.
           COMPUTE WS-AVERAGE37 = WS-TOTAL37 / 10.

       CHECK-LIMIT16.
           IF WS-AMOUNT16 > 1000
               MOVE 'Y' TO WS-FLAG16
           ELSE
               MOVE 'N' TO WS-FLAG16
           END-IF.

       ECHO-NAME-SAFE148.
           MOVE '<p>Thank you</p>' TO WS-PAGE148.
           EXEC CICS WEB SEND FROM(WS-PAGE148) END-EXEC.

       CHECK-LIMIT143.
           IF WS-AMOUNT143 > 1000
               MOVE 'Y' TO WS-FLAG143
           ELSE
               MOVE 'N' TO WS-FLAG143
           END-IF.

       WRITE-EXPORT99.
           MOVE LK-PATH99 TO WS-EXPORT-PATH99.
           OPEN OUTPUT EXPORT-FILE99.
           CLOSE EXPORT-FILE99.

       EXTRACT-FIELD-SAFE11.
           ACCEPT WS-POS11.
           IF WS-POS11 IS NUMERIC AND WS-POS11 > 0 AND WS-POS11 < 76
               MOVE WS-RECORD11(WS-POS11:5) TO WS-PART11
           END-IF.

       WRITE-EXPORT-SAFE54.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH54.
           OPEN OUTPUT EXPORT-FILE54.
           CLOSE EXPORT-FILE54.

       CHECK-LIMIT7.
           IF WS-AMOUNT7 > 1000
               MOVE 'Y' TO WS-FLAG7
           ELSE
               MOVE 'N' TO WS-FLAG7
           END-IF.

       FORMAT-HEADER72.
           MOVE 'MONTHLY REPORT' TO WS-TITLE72.
           STRING WS-TITLE72 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER72.
           DISPLAY WS-HEADER72.

       CLASSIFY-CODE62.
           EVALUATE WS-CODE62
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS62
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS62
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS62
           END-EVALUATE.

       CHECK-LIMIT128.
           IF WS-AMOUNT128 > 1000
               MOVE 'Y' TO WS-FLAG128
           ELSE
               MOVE 'N' TO WS-FLAG128
           END-IF.

       CLASSIFY-CODE28.
           EVALUATE WS-CODE28
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS28
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS28
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS28
           END-EVALUATE.

       WRITE-EXPORT-SAFE124.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH124.
           OPEN OUTPUT EXPORT-FILE124.
           CLOSE EXPORT-FILE124.

       COMPUTE-TOTALS70.
           MOVE 0 TO WS-TOTAL70.
           PERFORM VARYING WS-K70 FROM 1 BY 1 UNTIL WS-K70 > 10
               ADD WS-K70 TO WS-TOTAL70
           END-PERFORM.
           COMPUTE WS-AVERAGE70 = WS-TOTAL70 / 10.

       CONNECT-DB-SAFE61.
           ACCEPT WS-CONN-PW61 FROM ENVIRONMENT 'DB_PASSWORD'.

       CONVERT-FILE-SAFE31.
           MOVE "convert /srv/in/report.txt" TO WS-CMD31.
           CALL 'SYSTEM' USING WS-CMD31.

       LOG-LOGIN2.
           DISPLAY 'LOGIN ' WS-USER2 ' ' WS-PASSWORD-IN2.

       CHECK-LIMIT8.
           IF WS-AMOUNT8 > 1000
               MOVE 'Y' TO WS-FLAG8
           ELSE
               MOVE 'N' TO WS-FLAG8
           END-IF.

       LOG-LOGIN23.
           DISPLAY 'LOGIN ' WS-USER23 ' ' WS-PASSWORD-IN23.

       COMPUTE-TOTALS136.
           MOVE 0 TO WS-TOTAL136.
           PERFORM VARYING WS-K136 FROM 1 BY 1 UNTIL WS-K136 > 10
               ADD WS-K136 TO WS-TOTAL136
           END-PERFORM.
           COMPUTE WS-AVERAGE136 = WS-TOTAL136 / 10.

       CONVERT-FILE-SAFE43.
           MOVE "convert /srv/in/report.txt" TO WS-CMD43.
           CALL 'SYSTEM' USING WS-CMD43.

       PREPARE-QUERY109.
           MOVE LK-FILTER109 TO WS-STMT109.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT109 END-EXEC.

