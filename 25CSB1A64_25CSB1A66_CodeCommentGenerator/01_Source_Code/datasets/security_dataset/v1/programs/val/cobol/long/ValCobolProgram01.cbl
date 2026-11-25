       IDENTIFICATION DIVISION.
       PROGRAM-ID. LVA01.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-CUST4           PIC X(10).
       01  WS-SQL4            PIC X(200).
       01  WS-NAME4           PIC X(30).
       01  WS-CUST5           PIC X(10).
       01  WS-SQL5            PIC X(200).
       01  WS-NAME5           PIC X(30).
       01  WS-CUST7           PIC X(10).
       01  WS-SQL7            PIC X(200).
       01  WS-NAME7           PIC X(30).
       01  WS-CUST11           PIC X(10).
       01  WS-SQL11            PIC X(200).
       01  WS-NAME11           PIC X(30).
       01  WS-PROG12           PIC X(8).
       01  WS-DATA12           PIC X(50).
       01  WS-CHOICE12         PIC X.
       01  WS-CUST13           PIC X(10).
       01  WS-SQL13            PIC X(200).
       01  WS-NAME13           PIC X(30).
       01  WS-PROG14           PIC X(8).
       01  WS-DATA14           PIC X(50).
       01  WS-CHOICE14         PIC X.
       01  WS-CUST15           PIC X(10).
       01  WS-SQL15            PIC X(200).
       01  WS-NAME15           PIC X(30).
       01  WS-PROG21           PIC X(8).
       01  WS-DATA21           PIC X(50).
       01  WS-CHOICE21         PIC X.
       01  WS-PROG22           PIC X(8).
       01  WS-DATA22           PIC X(50).
       01  WS-CHOICE22         PIC X.
       01  WS-CUST23           PIC X(10).
       01  WS-SQL23            PIC X(200).
       01  WS-NAME23           PIC X(30).
       01  WS-CUST24           PIC X(10).
       01  WS-SQL24            PIC X(200).
       01  WS-NAME24           PIC X(30).
       01  WS-PROG25           PIC X(8).
       01  WS-DATA25           PIC X(50).
       01  WS-CHOICE25         PIC X.
       01  WS-PROG27           PIC X(8).
       01  WS-DATA27           PIC X(50).
       01  WS-CHOICE27         PIC X.
       01  WS-PROG28           PIC X(8).
       01  WS-DATA28           PIC X(50).
       01  WS-CHOICE28         PIC X.
       01  WS-PROG29           PIC X(8).
       01  WS-DATA29           PIC X(50).
       01  WS-CHOICE29         PIC X.
       01  WS-PROG30           PIC X(8).
       01  WS-DATA30           PIC X(50).
       01  WS-CHOICE30         PIC X.
       01  WS-PROG31           PIC X(8).
       01  WS-DATA31           PIC X(50).
       01  WS-CHOICE31         PIC X.
       01  WS-CUST33           PIC X(10).
       01  WS-SQL33            PIC X(200).
       01  WS-NAME33           PIC X(30).
       01  WS-CUST34           PIC X(10).
       01  WS-SQL34            PIC X(200).
       01  WS-NAME34           PIC X(30).
       01  WS-PROG36           PIC X(8).
       01  WS-DATA36           PIC X(50).
       01  WS-CHOICE36         PIC X.
       01  WS-PROG37           PIC X(8).
       01  WS-DATA37           PIC X(50).
       01  WS-CHOICE37         PIC X.
       01  WS-PROG38           PIC X(8).
       01  WS-DATA38           PIC X(50).
       01  WS-CHOICE38         PIC X.
       01  WS-CUST39           PIC X(10).
       01  WS-SQL39            PIC X(200).
       01  WS-NAME39           PIC X(30).
       01  WS-CUST41           PIC X(10).
       01  WS-SQL41            PIC X(200).
       01  WS-NAME41           PIC X(30).
       01  WS-CUST48           PIC X(10).
       01  WS-SQL48            PIC X(200).
       01  WS-NAME48           PIC X(30).
       01  WS-PROG49           PIC X(8).
       01  WS-DATA49           PIC X(50).
       01  WS-CHOICE49         PIC X.
       01  WS-CUST50           PIC X(10).
       01  WS-SQL50            PIC X(200).
       01  WS-NAME50           PIC X(30).
       01  WS-CUST51           PIC X(10).
       01  WS-SQL51            PIC X(200).
       01  WS-NAME51           PIC X(30).
       01  WS-PROG54           PIC X(8).
       01  WS-DATA54           PIC X(50).
       01  WS-CHOICE54         PIC X.
       01  WS-PROG55           PIC X(8).
       01  WS-DATA55           PIC X(50).
       01  WS-CHOICE55         PIC X.
       01  WS-PROG57           PIC X(8).
       01  WS-DATA57           PIC X(50).
       01  WS-CHOICE57         PIC X.
       01  WS-CUST58           PIC X(10).
       01  WS-SQL58            PIC X(200).
       01  WS-NAME58           PIC X(30).
       01  WS-CUST61           PIC X(10).
       01  WS-SQL61            PIC X(200).
       01  WS-NAME61           PIC X(30).
       01  WS-PROG62           PIC X(8).
       01  WS-DATA62           PIC X(50).
       01  WS-CHOICE62         PIC X.
       01  WS-CUST63           PIC X(10).
       01  WS-SQL63            PIC X(200).
       01  WS-NAME63           PIC X(30).
       01  WS-PROG66           PIC X(8).
       01  WS-DATA66           PIC X(50).
       01  WS-CHOICE66         PIC X.
       01  WS-PROG67           PIC X(8).
       01  WS-DATA67           PIC X(50).
       01  WS-CHOICE67         PIC X.
       01  WS-CUST68           PIC X(10).
       01  WS-SQL68            PIC X(200).
       01  WS-NAME68           PIC X(30).
       01  WS-PROG71           PIC X(8).
       01  WS-DATA71           PIC X(50).
       01  WS-CHOICE71         PIC X.
       01  WS-CUST72           PIC X(10).
       01  WS-SQL72            PIC X(200).
       01  WS-NAME72           PIC X(30).
       01  WS-CUST74           PIC X(10).
       01  WS-SQL74            PIC X(200).
       01  WS-NAME74           PIC X(30).
       01  WS-CUST76           PIC X(10).
       01  WS-SQL76            PIC X(200).
       01  WS-NAME76           PIC X(30).
       01  WS-PROG79           PIC X(8).
       01  WS-DATA79           PIC X(50).
       01  WS-CHOICE79         PIC X.
       01  WS-CUST80           PIC X(10).
       01  WS-SQL80            PIC X(200).
       01  WS-NAME80           PIC X(30).
       01  WS-CUST82           PIC X(10).
       01  WS-SQL82            PIC X(200).
       01  WS-NAME82           PIC X(30).
       01  WS-CUST83           PIC X(10).
       01  WS-SQL83            PIC X(200).
       01  WS-NAME83           PIC X(30).
       01  WS-CUST84           PIC X(10).
       01  WS-SQL84            PIC X(200).
       01  WS-NAME84           PIC X(30).
       01  WS-PROG85           PIC X(8).
       01  WS-DATA85           PIC X(50).
       01  WS-CHOICE85         PIC X.
       01  WS-CUST88           PIC X(10).
       01  WS-SQL88            PIC X(200).
       01  WS-NAME88           PIC X(30).
       01  WS-PROG89           PIC X(8).
       01  WS-DATA89           PIC X(50).
       01  WS-CHOICE89         PIC X.
       01  WS-PROG91           PIC X(8).
       01  WS-DATA91           PIC X(50).
       01  WS-CHOICE91         PIC X.
       01  WS-CUST92           PIC X(10).
       01  WS-SQL92            PIC X(200).
       01  WS-NAME92           PIC X(30).
       01  WS-PROG93           PIC X(8).
       01  WS-DATA93           PIC X(50).
       01  WS-CHOICE93         PIC X.
       01  WS-PROG97           PIC X(8).
       01  WS-DATA97           PIC X(50).
       01  WS-CHOICE97         PIC X.
       01  WS-PROG100           PIC X(8).
       01  WS-DATA100           PIC X(50).
       01  WS-CHOICE100         PIC X.
       01  WS-CUST101           PIC X(10).
       01  WS-SQL101            PIC X(200).
       01  WS-NAME101           PIC X(30).
       01  WS-PROG102           PIC X(8).
       01  WS-DATA102           PIC X(50).
       01  WS-CHOICE102         PIC X.
       01  WS-CUST104           PIC X(10).
       01  WS-SQL104            PIC X(200).
       01  WS-NAME104           PIC X(30).
       01  WS-PROG105           PIC X(8).
       01  WS-DATA105           PIC X(50).
       01  WS-CHOICE105         PIC X.
       01  WS-CUST106           PIC X(10).
       01  WS-SQL106            PIC X(200).
       01  WS-NAME106           PIC X(30).
       01  WS-CUST107           PIC X(10).
       01  WS-SQL107            PIC X(200).
       01  WS-NAME107           PIC X(30).
       01  WS-PROG108           PIC X(8).
       01  WS-DATA108           PIC X(50).
       01  WS-CHOICE108         PIC X.
       01  WS-PROG110           PIC X(8).
       01  WS-DATA110           PIC X(50).
       01  WS-CHOICE110         PIC X.
       01  WS-CUST112           PIC X(10).
       01  WS-SQL112            PIC X(200).
       01  WS-NAME112           PIC X(30).
       01  WS-PROG114           PIC X(8).
       01  WS-DATA114           PIC X(50).
       01  WS-CHOICE114         PIC X.
       01  WS-CUST116           PIC X(10).
       01  WS-SQL116            PIC X(200).
       01  WS-NAME116           PIC X(30).
       01  WS-CUST117           PIC X(10).
       01  WS-SQL117            PIC X(200).
       01  WS-NAME117           PIC X(30).
       01  WS-CUST120           PIC X(10).
       01  WS-SQL120            PIC X(200).
       01  WS-NAME120           PIC X(30).
       01  WS-PROG121           PIC X(8).
       01  WS-DATA121           PIC X(50).
       01  WS-CHOICE121         PIC X.
       01  WS-PROG122           PIC X(8).
       01  WS-DATA122           PIC X(50).
       01  WS-CHOICE122         PIC X.
       01  WS-PROG123           PIC X(8).
       01  WS-DATA123           PIC X(50).
       01  WS-CHOICE123         PIC X.
       01  WS-CUST124           PIC X(10).
       01  WS-SQL124            PIC X(200).
       01  WS-NAME124           PIC X(30).
       01  WS-PROG125           PIC X(8).
       01  WS-DATA125           PIC X(50).
       01  WS-CHOICE125         PIC X.
       01  WS-CUST126           PIC X(10).
       01  WS-SQL126            PIC X(200).
       01  WS-NAME126           PIC X(30).
       01  WS-CUST128           PIC X(10).
       01  WS-SQL128            PIC X(200).
       01  WS-NAME128           PIC X(30).
       01  WS-CUST129           PIC X(10).
       01  WS-SQL129            PIC X(200).
       01  WS-NAME129           PIC X(30).
       01  WS-PROG130           PIC X(8).
       01  WS-DATA130           PIC X(50).
       01  WS-CHOICE130         PIC X.
       01  WS-PROG131           PIC X(8).
       01  WS-DATA131           PIC X(50).
       01  WS-CHOICE131         PIC X.
       01  WS-CUST134           PIC X(10).
       01  WS-SQL134            PIC X(200).
       01  WS-NAME134           PIC X(30).
       01  WS-CUST138           PIC X(10).
       01  WS-SQL138            PIC X(200).
       01  WS-NAME138           PIC X(30).
       01  WS-CUST139           PIC X(10).
       01  WS-SQL139            PIC X(200).
       01  WS-NAME139           PIC X(30).
       01  WS-PROG141           PIC X(8).
       01  WS-DATA141           PIC X(50).
       01  WS-CHOICE141         PIC X.
       01  WS-PROG143           PIC X(8).
       01  WS-DATA143           PIC X(50).
       01  WS-CHOICE143         PIC X.
       01  WS-PROG147           PIC X(8).
       01  WS-DATA147           PIC X(50).
       01  WS-CHOICE147         PIC X.
       01  WS-CUST151           PIC X(10).
       01  WS-SQL151            PIC X(200).
       01  WS-NAME151           PIC X(30).
       01  WS-PROG152           PIC X(8).
       01  WS-DATA152           PIC X(50).
       01  WS-CHOICE152         PIC X.
       01  WS-CUST154           PIC X(10).
       01  WS-SQL154            PIC X(200).
       01  WS-NAME154           PIC X(30).
       01  WS-CUST155           PIC X(10).
       01  WS-SQL155            PIC X(200).
       01  WS-NAME155           PIC X(30).
       01  WS-CUST157           PIC X(10).
       01  WS-SQL157            PIC X(200).
       01  WS-NAME157           PIC X(30).
       01  WS-CUST158           PIC X(10).
       01  WS-SQL158            PIC X(200).
       01  WS-NAME158           PIC X(30).
       01  WS-PROG162           PIC X(8).
       01  WS-DATA162           PIC X(50).
       01  WS-CHOICE162         PIC X.
       01  WS-CODE1           PIC 9 VALUE 1.
       01  WS-STATUS1         PIC X(6) VALUE SPACES.
       01  WS-TITLE2          PIC X(20) VALUE SPACES.
       01  WS-HEADER2         PIC X(40) VALUE SPACES.
       01  WS-TOTAL3          PIC 9(6) VALUE 0.
       01  WS-K3              PIC 99 VALUE 0.
       01  WS-AVERAGE3        PIC 9(6)V99 VALUE 0.
       01  WS-CODE6           PIC 9 VALUE 1.
       01  WS-STATUS6         PIC X(6) VALUE SPACES.
       01  WS-TITLE8          PIC X(20) VALUE SPACES.
       01  WS-HEADER8         PIC X(40) VALUE SPACES.
       01  WS-TOTAL9          PIC 9(6) VALUE 0.
       01  WS-K9              PIC 99 VALUE 0.
       01  WS-AVERAGE9        PIC 9(6)V99 VALUE 0.
       01  WS-CODE10           PIC 9 VALUE 1.
       01  WS-STATUS10         PIC X(6) VALUE SPACES.
       01  WS-TITLE16          PIC X(20) VALUE SPACES.
       01  WS-HEADER16         PIC X(40) VALUE SPACES.
       01  WS-CODE17           PIC 9 VALUE 1.
       01  WS-STATUS17         PIC X(6) VALUE SPACES.
       01  WS-TITLE18          PIC X(20) VALUE SPACES.
       01  WS-HEADER18         PIC X(40) VALUE SPACES.
       01  WS-TITLE19          PIC X(20) VALUE SPACES.
       01  WS-HEADER19         PIC X(40) VALUE SPACES.
       01  WS-TITLE20          PIC X(20) VALUE SPACES.
       01  WS-HEADER20         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT26         PIC 9(6) VALUE 500.
       01  WS-FLAG26           PIC X VALUE 'N'.
       01  WS-CODE32           PIC 9 VALUE 1.
       01  WS-STATUS32         PIC X(6) VALUE SPACES.
       01  WS-TITLE35          PIC X(20) VALUE SPACES.
       01  WS-HEADER35         PIC X(40) VALUE SPACES.
       01  WS-CODE40           PIC 9 VALUE 1.
       01  WS-STATUS40         PIC X(6) VALUE SPACES.
       01  WS-TOTAL42          PIC 9(6) VALUE 0.
       01  WS-K42              PIC 99 VALUE 0.
       01  WS-AVERAGE42        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL43          PIC 9(6) VALUE 0.
       01  WS-K43              PIC 99 VALUE 0.
       01  WS-AVERAGE43        PIC 9(6)V99 VALUE 0.
       01  WS-CODE44           PIC 9 VALUE 1.
       01  WS-STATUS44         PIC X(6) VALUE SPACES.
       01  WS-TOTAL45          PIC 9(6) VALUE 0.
       01  WS-K45              PIC 99 VALUE 0.
       01  WS-AVERAGE45        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT46         PIC 9(6) VALUE 500.
       01  WS-FLAG46           PIC X VALUE 'N'.
       01  WS-AMOUNT47         PIC 9(6) VALUE 500.
       01  WS-FLAG47           PIC X VALUE 'N'.
       01  WS-TOTAL52          PIC 9(6) VALUE 0.
       01  WS-K52              PIC 99 VALUE 0.
       01  WS-AVERAGE52        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT53         PIC 9(6) VALUE 500.
       01  WS-FLAG53           PIC X VALUE 'N'.
       01  WS-CODE56           PIC 9 VALUE 1.
       01  WS-STATUS56         PIC X(6) VALUE SPACES.
       01  WS-TOTAL59          PIC 9(6) VALUE 0.
       01  WS-K59              PIC 99 VALUE 0.
       01  WS-AVERAGE59        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE60          PIC X(20) VALUE SPACES.
       01  WS-HEADER60         PIC X(40) VALUE SPACES.
       01  WS-TOTAL64          PIC 9(6) VALUE 0.
       01  WS-K64              PIC 99 VALUE 0.
       01  WS-AVERAGE64        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT65         PIC 9(6) VALUE 500.
       01  WS-FLAG65           PIC X VALUE 'N'.
       01  WS-TOTAL69          PIC 9(6) VALUE 0.
       01  WS-K69              PIC 99 VALUE 0.
       01  WS-AVERAGE69        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT70         PIC 9(6) VALUE 500.
       01  WS-FLAG70           PIC X VALUE 'N'.
       01  WS-CODE73           PIC 9 VALUE 1.
       01  WS-STATUS73         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT75         PIC 9(6) VALUE 500.
       01  WS-FLAG75           PIC X VALUE 'N'.
       01  WS-CODE77           PIC 9 VALUE 1.
       01  WS-STATUS77         PIC X(6) VALUE SPACES.
       01  WS-CODE78           PIC 9 VALUE 1.
       01  WS-STATUS78         PIC X(6) VALUE SPACES.
       01  WS-CODE81           PIC 9 VALUE 1.
       01  WS-STATUS81         PIC X(6) VALUE SPACES.
       01  WS-TOTAL86          PIC 9(6) VALUE 0.
       01  WS-K86              PIC 99 VALUE 0.
       01  WS-AVERAGE86        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT87         PIC 9(6) VALUE 500.
       01  WS-FLAG87           PIC X VALUE 'N'.
       01  WS-TITLE90          PIC X(20) VALUE SPACES.
       01  WS-HEADER90         PIC X(40) VALUE SPACES.
       01  WS-CODE94           PIC 9 VALUE 1.
       01  WS-STATUS94         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT95         PIC 9(6) VALUE 500.
       01  WS-FLAG95           PIC X VALUE 'N'.
       01  WS-TITLE96          PIC X(20) VALUE SPACES.
       01  WS-HEADER96         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT98         PIC 9(6) VALUE 500.
       01  WS-FLAG98           PIC X VALUE 'N'.
       01  WS-AMOUNT99         PIC 9(6) VALUE 500.
       01  WS-FLAG99           PIC X VALUE 'N'.
       01  WS-AMOUNT103         PIC 9(6) VALUE 500.
       01  WS-FLAG103           PIC X VALUE 'N'.
       01  WS-TITLE109          PIC X(20) VALUE SPACES.
       01  WS-HEADER109         PIC X(40) VALUE SPACES.
       01  WS-TITLE111          PIC X(20) VALUE SPACES.
       01  WS-HEADER111         PIC X(40) VALUE SPACES.
       01  WS-CODE113           PIC 9 VALUE 1.
       01  WS-STATUS113         PIC X(6) VALUE SPACES.
       01  WS-CODE115           PIC 9 VALUE 1.
       01  WS-STATUS115         PIC X(6) VALUE SPACES.
       01  WS-CODE118           PIC 9 VALUE 1.
       01  WS-STATUS118         PIC X(6) VALUE SPACES.
       01  WS-TOTAL119          PIC 9(6) VALUE 0.
       01  WS-K119              PIC 99 VALUE 0.
       01  WS-AVERAGE119        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE127          PIC X(20) VALUE SPACES.
       01  WS-HEADER127         PIC X(40) VALUE SPACES.
       01  WS-CODE132           PIC 9 VALUE 1.
       01  WS-STATUS132         PIC X(6) VALUE SPACES.
       01  WS-TITLE133          PIC X(20) VALUE SPACES.
       01  WS-HEADER133         PIC X(40) VALUE SPACES.
       01  WS-TOTAL135          PIC 9(6) VALUE 0.
       01  WS-K135              PIC 99 VALUE 0.
       01  WS-AVERAGE135        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE136          PIC X(20) VALUE SPACES.
       01  WS-HEADER136         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT137         PIC 9(6) VALUE 500.
       01  WS-FLAG137           PIC X VALUE 'N'.
       01  WS-TITLE140          PIC X(20) VALUE SPACES.
       01  WS-HEADER140         PIC X(40) VALUE SPACES.
       01  WS-CODE142           PIC 9 VALUE 1.
       01  WS-STATUS142         PIC X(6) VALUE SPACES.
       01  WS-TITLE144          PIC X(20) VALUE SPACES.
       01  WS-HEADER144         PIC X(40) VALUE SPACES.
       01  WS-TITLE145          PIC X(20) VALUE SPACES.
       01  WS-HEADER145         PIC X(40) VALUE SPACES.
       01  WS-TITLE146          PIC X(20) VALUE SPACES.
       01  WS-HEADER146         PIC X(40) VALUE SPACES.
       01  WS-CODE148           PIC 9 VALUE 1.
       01  WS-STATUS148         PIC X(6) VALUE SPACES.
       01  WS-CODE149           PIC 9 VALUE 1.
       01  WS-STATUS149         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT150         PIC 9(6) VALUE 500.
       01  WS-FLAG150           PIC X VALUE 'N'.
       01  WS-TITLE153          PIC X(20) VALUE SPACES.
       01  WS-HEADER153         PIC X(40) VALUE SPACES.
       01  WS-TOTAL156          PIC 9(6) VALUE 0.
       01  WS-K156              PIC 99 VALUE 0.
       01  WS-AVERAGE156        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT159         PIC 9(6) VALUE 500.
       01  WS-FLAG159           PIC X VALUE 'N'.
       01  WS-TOTAL160          PIC 9(6) VALUE 0.
       01  WS-K160              PIC 99 VALUE 0.
       01  WS-AVERAGE160        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE161          PIC X(20) VALUE SPACES.
       01  WS-HEADER161         PIC X(40) VALUE SPACES.
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       FORMAT-HEADER144.
           MOVE 'MONTHLY REPORT' TO WS-TITLE144.
           STRING WS-TITLE144 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER144.
           DISPLAY WS-HEADER144.

       QUERY-CUSTOMER154.
           ACCEPT WS-CUST154.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST154 "'"
               DELIMITED BY SIZE INTO WS-SQL154.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL154 END-EXEC.

       RUN-HANDLER85.
           ACCEPT WS-PROG85.
           CALL WS-PROG85 USING WS-DATA85.

       FORMAT-HEADER140.
           MOVE 'MONTHLY REPORT' TO WS-TITLE140.
           STRING WS-TITLE140 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER140.
           DISPLAY WS-HEADER140.

       RUN-HANDLER21.
           ACCEPT WS-PROG21.
           CALL WS-PROG21 USING WS-DATA21.

       RUN-HANDLER67.
           ACCEPT WS-PROG67.
           CALL WS-PROG67 USING WS-DATA67.

       CLASSIFY-CODE115.
           EVALUATE WS-CODE115
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS115
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS115
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS115
           END-EVALUATE.

       COMPUTE-TOTALS69.
           MOVE 0 TO WS-TOTAL69.
           PERFORM VARYING WS-K69 FROM 1 BY 1 UNTIL WS-K69 > 10
               ADD WS-K69 TO WS-TOTAL69
           END-PERFORM.
           COMPUTE WS-AVERAGE69 = WS-TOTAL69 / 10.

       FORMAT-HEADER20.
           MOVE 'MONTHLY REPORT' TO WS-TITLE20.
           STRING WS-TITLE20 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER20.
           DISPLAY WS-HEADER20.

       QUERY-CUSTOMER41.
           ACCEPT WS-CUST41.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST41 "'"
               DELIMITED BY SIZE INTO WS-SQL41.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL41 END-EXEC.

       COMPUTE-TOTALS43.
           MOVE 0 TO WS-TOTAL43.
           PERFORM VARYING WS-K43 FROM 1 BY 1 UNTIL WS-K43 > 10
               ADD WS-K43 TO WS-TOTAL43
           END-PERFORM.
           COMPUTE WS-AVERAGE43 = WS-TOTAL43 / 10.

       RUN-HANDLER-SAFE79.
           ACCEPT WS-CHOICE79.
           IF WS-CHOICE79 = 'A'
               CALL 'HANDLERA' USING WS-DATA79
           ELSE
               CALL 'HANDLERB' USING WS-DATA79
           END-IF.

       CLASSIFY-CODE77.
           EVALUATE WS-CODE77
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS77
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS77
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS77
           END-EVALUATE.

       FORMAT-HEADER19.
           MOVE 'MONTHLY REPORT' TO WS-TITLE19.
           STRING WS-TITLE19 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER19.
           DISPLAY WS-HEADER19.

       CHECK-LIMIT98.
           IF WS-AMOUNT98 > 1000
               MOVE 'Y' TO WS-FLAG98
           ELSE
               MOVE 'N' TO WS-FLAG98
           END-IF.

       RUN-HANDLER-SAFE121.
           ACCEPT WS-CHOICE121.
           IF WS-CHOICE121 = 'A'
               CALL 'HANDLERA' USING WS-DATA121
           ELSE
               CALL 'HANDLERB' USING WS-DATA121
           END-IF.

       FORMAT-HEADER90.
           MOVE 'MONTHLY REPORT' TO WS-TITLE90.
           STRING WS-TITLE90 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER90.
           DISPLAY WS-HEADER90.

       CLASSIFY-CODE78.
           EVALUATE WS-CODE78
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS78
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS78
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS78
           END-EVALUATE.

       CHECK-LIMIT95.
           IF WS-AMOUNT95 > 1000
               MOVE 'Y' TO WS-FLAG95
           ELSE
               MOVE 'N' TO WS-FLAG95
           END-IF.

       FORMAT-HEADER35.
           MOVE 'MONTHLY REPORT' TO WS-TITLE35.
           STRING WS-TITLE35 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER35.
           DISPLAY WS-HEADER35.

       RUN-HANDLER141.
           ACCEPT WS-PROG141.
           CALL WS-PROG141 USING WS-DATA141.

       FORMAT-HEADER145.
           MOVE 'MONTHLY REPORT' TO WS-TITLE145.
           STRING WS-TITLE145 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER145.
           DISPLAY WS-HEADER145.

       QUERY-CUSTOMER117.
           ACCEPT WS-CUST117.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST117 "'"
               DELIMITED BY SIZE INTO WS-SQL117.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL117 END-EXEC.

       QUERY-CUSTOMER-SAFE82.
           ACCEPT WS-CUST82.
           EXEC SQL
               SELECT NAME INTO :WS-NAME82 FROM CUST WHERE ID = :WS-CUST82
           END-EXEC.

       FORMAT-HEADER136.
           MOVE 'MONTHLY REPORT' TO WS-TITLE136.
           STRING WS-TITLE136 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER136.
           DISPLAY WS-HEADER136.

       CLASSIFY-CODE17.
           EVALUATE WS-CODE17
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS17
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS17
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS17
           END-EVALUATE.

       QUERY-CUSTOMER34.
           ACCEPT WS-CUST34.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST34 "'"
               DELIMITED BY SIZE INTO WS-SQL34.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL34 END-EXEC.

       QUERY-CUSTOMER112.
           ACCEPT WS-CUST112.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST112 "'"
               DELIMITED BY SIZE INTO WS-SQL112.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL112 END-EXEC.

       RUN-HANDLER-SAFE49.
           ACCEPT WS-CHOICE49.
           IF WS-CHOICE49 = 'A'
               CALL 'HANDLERA' USING WS-DATA49
           ELSE
               CALL 'HANDLERB' USING WS-DATA49
           END-IF.

       FORMAT-HEADER60.
           MOVE 'MONTHLY REPORT' TO WS-TITLE60.
           STRING WS-TITLE60 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER60.
           DISPLAY WS-HEADER60.

       RUN-HANDLER147.
           ACCEPT WS-PROG147.
           CALL WS-PROG147 USING WS-DATA147.

       CLASSIFY-CODE1.
           EVALUATE WS-CODE1
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS1
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS1
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS1
           END-EVALUATE.

       RUN-HANDLER-SAFE25.
           ACCEPT WS-CHOICE25.
           IF WS-CHOICE25 = 'A'
               CALL 'HANDLERA' USING WS-DATA25
           ELSE
               CALL 'HANDLERB' USING WS-DATA25
           END-IF.

       COMPUTE-TOTALS119.
           MOVE 0 TO WS-TOTAL119.
           PERFORM VARYING WS-K119 FROM 1 BY 1 UNTIL WS-K119 > 10
               ADD WS-K119 TO WS-TOTAL119
           END-PERFORM.
           COMPUTE WS-AVERAGE119 = WS-TOTAL119 / 10.

       RUN-HANDLER66.
           ACCEPT WS-PROG66.
           CALL WS-PROG66 USING WS-DATA66.

       QUERY-CUSTOMER-SAFE126.
           ACCEPT WS-CUST126.
           EXEC SQL
               SELECT NAME INTO :WS-NAME126 FROM CUST WHERE ID = :WS-CUST126
           END-EXEC.

       RUN-HANDLER22.
           ACCEPT WS-PROG22.
           CALL WS-PROG22 USING WS-DATA22.

       QUERY-CUSTOMER-SAFE139.
           ACCEPT WS-CUST139.
           EXEC SQL
               SELECT NAME INTO :WS-NAME139 FROM CUST WHERE ID = :WS-CUST139
           END-EXEC.

       CHECK-LIMIT46.
           IF WS-AMOUNT46 > 1000
               MOVE 'Y' TO WS-FLAG46
           ELSE
               MOVE 'N' TO WS-FLAG46
           END-IF.

       RUN-HANDLER38.
           ACCEPT WS-PROG38.
           CALL WS-PROG38 USING WS-DATA38.

       CLASSIFY-CODE94.
           EVALUATE WS-CODE94
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS94
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS94
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS94
           END-EVALUATE.

       FORMAT-HEADER18.
           MOVE 'MONTHLY REPORT' TO WS-TITLE18.
           STRING WS-TITLE18 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER18.
           DISPLAY WS-HEADER18.

       CHECK-LIMIT87.
           IF WS-AMOUNT87 > 1000
               MOVE 'Y' TO WS-FLAG87
           ELSE
               MOVE 'N' TO WS-FLAG87
           END-IF.

       QUERY-CUSTOMER-SAFE134.
           ACCEPT WS-CUST134.
           EXEC SQL
               SELECT NAME INTO :WS-NAME134 FROM CUST WHERE ID = :WS-CUST134
           END-EXEC.

       QUERY-CUSTOMER23.
           ACCEPT WS-CUST23.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST23 "'"
               DELIMITED BY SIZE INTO WS-SQL23.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL23 END-EXEC.

       CLASSIFY-CODE56.
           EVALUATE WS-CODE56
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS56
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS56
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS56
           END-EVALUATE.

       COMPUTE-TOTALS64.
           MOVE 0 TO WS-TOTAL64.
           PERFORM VARYING WS-K64 FROM 1 BY 1 UNTIL WS-K64 > 10
               ADD WS-K64 TO WS-TOTAL64
           END-PERFORM.
           COMPUTE WS-AVERAGE64 = WS-TOTAL64 / 10.

       QUERY-CUSTOMER-SAFE39.
           ACCEPT WS-CUST39.
           EXEC SQL
               SELECT NAME INTO :WS-NAME39 FROM CUST WHERE ID = :WS-CUST39
           END-EXEC.

       QUERY-CUSTOMER-SAFE4.
           ACCEPT WS-CUST4.
           EXEC SQL
               SELECT NAME INTO :WS-NAME4 FROM CUST WHERE ID = :WS-CUST4
           END-EXEC.

       CLASSIFY-CODE118.
           EVALUATE WS-CODE118
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS118
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS118
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS118
           END-EVALUATE.

       RUN-HANDLER-SAFE108.
           ACCEPT WS-CHOICE108.
           IF WS-CHOICE108 = 'A'
               CALL 'HANDLERA' USING WS-DATA108
           ELSE
               CALL 'HANDLERB' USING WS-DATA108
           END-IF.

       CLASSIFY-CODE32.
           EVALUATE WS-CODE32
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS32
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS32
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS32
           END-EVALUATE.

       RUN-HANDLER12.
           ACCEPT WS-PROG12.
           CALL WS-PROG12 USING WS-DATA12.

       COMPUTE-TOTALS160.
           MOVE 0 TO WS-TOTAL160.
           PERFORM VARYING WS-K160 FROM 1 BY 1 UNTIL WS-K160 > 10
               ADD WS-K160 TO WS-TOTAL160
           END-PERFORM.
           COMPUTE WS-AVERAGE160 = WS-TOTAL160 / 10.

       QUERY-CUSTOMER-SAFE76.
           ACCEPT WS-CUST76.
           EXEC SQL
               SELECT NAME INTO :WS-NAME76 FROM CUST WHERE ID = :WS-CUST76
           END-EXEC.

       RUN-HANDLER97.
           ACCEPT WS-PROG97.
           CALL WS-PROG97 USING WS-DATA97.

       RUN-HANDLER-SAFE54.
           ACCEPT WS-CHOICE54.
           IF WS-CHOICE54 = 'A'
               CALL 'HANDLERA' USING WS-DATA54
           ELSE
               CALL 'HANDLERB' USING WS-DATA54
           END-IF.

       FORMAT-HEADER16.
           MOVE 'MONTHLY REPORT' TO WS-TITLE16.
           STRING WS-TITLE16 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER16.
           DISPLAY WS-HEADER16.

       QUERY-CUSTOMER-SAFE104.
           ACCEPT WS-CUST104.
           EXEC SQL
               SELECT NAME INTO :WS-NAME104 FROM CUST WHERE ID = :WS-CUST104
           END-EXEC.

       COMPUTE-TOTALS86.
           MOVE 0 TO WS-TOTAL86.
           PERFORM VARYING WS-K86 FROM 1 BY 1 UNTIL WS-K86 > 10
               ADD WS-K86 TO WS-TOTAL86
           END-PERFORM.
           COMPUTE WS-AVERAGE86 = WS-TOTAL86 / 10.

       RUN-HANDLER-SAFE110.
           ACCEPT WS-CHOICE110.
           IF WS-CHOICE110 = 'A'
               CALL 'HANDLERA' USING WS-DATA110
           ELSE
               CALL 'HANDLERB' USING WS-DATA110
           END-IF.

       CHECK-LIMIT99.
           IF WS-AMOUNT99 > 1000
               MOVE 'Y' TO WS-FLAG99
           ELSE
               MOVE 'N' TO WS-FLAG99
           END-IF.

       RUN-HANDLER-SAFE100.
           ACCEPT WS-CHOICE100.
           IF WS-CHOICE100 = 'A'
               CALL 'HANDLERA' USING WS-DATA100
           ELSE
               CALL 'HANDLERB' USING WS-DATA100
           END-IF.

       QUERY-CUSTOMER106.
           ACCEPT WS-CUST106.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST106 "'"
               DELIMITED BY SIZE INTO WS-SQL106.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL106 END-EXEC.

       COMPUTE-TOTALS3.
           MOVE 0 TO WS-TOTAL3.
           PERFORM VARYING WS-K3 FROM 1 BY 1 UNTIL WS-K3 > 10
               ADD WS-K3 TO WS-TOTAL3
           END-PERFORM.
           COMPUTE WS-AVERAGE3 = WS-TOTAL3 / 10.

       QUERY-CUSTOMER-SAFE63.
           ACCEPT WS-CUST63.
           EXEC SQL
               SELECT NAME INTO :WS-NAME63 FROM CUST WHERE ID = :WS-CUST63
           END-EXEC.

       QUERY-CUSTOMER120.
           ACCEPT WS-CUST120.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST120 "'"
               DELIMITED BY SIZE INTO WS-SQL120.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL120 END-EXEC.

       FORMAT-HEADER161.
           MOVE 'MONTHLY REPORT' TO WS-TITLE161.
           STRING WS-TITLE161 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER161.
           DISPLAY WS-HEADER161.

       COMPUTE-TOTALS156.
           MOVE 0 TO WS-TOTAL156.
           PERFORM VARYING WS-K156 FROM 1 BY 1 UNTIL WS-K156 > 10
               ADD WS-K156 TO WS-TOTAL156
           END-PERFORM.
           COMPUTE WS-AVERAGE156 = WS-TOTAL156 / 10.

       QUERY-CUSTOMER83.
           ACCEPT WS-CUST83.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST83 "'"
               DELIMITED BY SIZE INTO WS-SQL83.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL83 END-EXEC.

       CLASSIFY-CODE132.
           EVALUATE WS-CODE132
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS132
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS132
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS132
           END-EVALUATE.

       FORMAT-HEADER133.
           MOVE 'MONTHLY REPORT' TO WS-TITLE133.
           STRING WS-TITLE133 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER133.
           DISPLAY WS-HEADER133.

       RUN-HANDLER-SAFE130.
           ACCEPT WS-CHOICE130.
           IF WS-CHOICE130 = 'A'
               CALL 'HANDLERA' USING WS-DATA130
           ELSE
               CALL 'HANDLERB' USING WS-DATA130
           END-IF.

       QUERY-CUSTOMER11.
           ACCEPT WS-CUST11.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST11 "'"
               DELIMITED BY SIZE INTO WS-SQL11.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL11 END-EXEC.

       QUERY-CUSTOMER-SAFE48.
           ACCEPT WS-CUST48.
           EXEC SQL
               SELECT NAME INTO :WS-NAME48 FROM CUST WHERE ID = :WS-CUST48
           END-EXEC.

       QUERY-CUSTOMER58.
           ACCEPT WS-CUST58.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST58 "'"
               DELIMITED BY SIZE INTO WS-SQL58.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL58 END-EXEC.

       RUN-HANDLER-SAFE125.
           ACCEPT WS-CHOICE125.
           IF WS-CHOICE125 = 'A'
               CALL 'HANDLERA' USING WS-DATA125
           ELSE
               CALL 'HANDLERB' USING WS-DATA125
           END-IF.

       QUERY-CUSTOMER-SAFE24.
           ACCEPT WS-CUST24.
           EXEC SQL
               SELECT NAME INTO :WS-NAME24 FROM CUST WHERE ID = :WS-CUST24
           END-EXEC.

       COMPUTE-TOTALS9.
           MOVE 0 TO WS-TOTAL9.
           PERFORM VARYING WS-K9 FROM 1 BY 1 UNTIL WS-K9 > 10
               ADD WS-K9 TO WS-TOTAL9
           END-PERFORM.
           COMPUTE WS-AVERAGE9 = WS-TOTAL9 / 10.

       QUERY-CUSTOMER15.
           ACCEPT WS-CUST15.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST15 "'"
               DELIMITED BY SIZE INTO WS-SQL15.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL15 END-EXEC.

       RUN-HANDLER152.
           ACCEPT WS-PROG152.
           CALL WS-PROG152 USING WS-DATA152.

       QUERY-CUSTOMER13.
           ACCEPT WS-CUST13.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST13 "'"
               DELIMITED BY SIZE INTO WS-SQL13.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL13 END-EXEC.

       RUN-HANDLER114.
           ACCEPT WS-PROG114.
           CALL WS-PROG114 USING WS-DATA114.

       FORMAT-HEADER111.
           MOVE 'MONTHLY REPORT' TO WS-TITLE111.
           STRING WS-TITLE111 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER111.
           DISPLAY WS-HEADER111.

       QUERY-CUSTOMER138.
           ACCEPT WS-CUST138.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST138 "'"
               DELIMITED BY SIZE INTO WS-SQL138.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL138 END-EXEC.

       CHECK-LIMIT75.
           IF WS-AMOUNT75 > 1000
               MOVE 'Y' TO WS-FLAG75
           ELSE
               MOVE 'N' TO WS-FLAG75
           END-IF.

       RUN-HANDLER30.
           ACCEPT WS-PROG30.
           CALL WS-PROG30 USING WS-DATA30.

       QUERY-CUSTOMER-SAFE51.
           ACCEPT WS-CUST51.
           EXEC SQL
               SELECT NAME INTO :WS-NAME51 FROM CUST WHERE ID = :WS-CUST51
           END-EXEC.

       QUERY-CUSTOMER155.
           ACCEPT WS-CUST155.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST155 "'"
               DELIMITED BY SIZE INTO WS-SQL155.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL155 END-EXEC.

       QUERY-CUSTOMER157.
           ACCEPT WS-CUST157.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST157 "'"
               DELIMITED BY SIZE INTO WS-SQL157.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL157 END-EXEC.

       CHECK-LIMIT53.
           IF WS-AMOUNT53 > 1000
               MOVE 'Y' TO WS-FLAG53
           ELSE
               MOVE 'N' TO WS-FLAG53
           END-IF.

       CLASSIFY-CODE113.
           EVALUATE WS-CODE113
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS113
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS113
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS113
           END-EVALUATE.

       QUERY-CUSTOMER61.
           ACCEPT WS-CUST61.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST61 "'"
               DELIMITED BY SIZE INTO WS-SQL61.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL61 END-EXEC.

       RUN-HANDLER89.
           ACCEPT WS-PROG89.
           CALL WS-PROG89 USING WS-DATA89.

       CLASSIFY-CODE40.
           EVALUATE WS-CODE40
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS40
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS40
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS40
           END-EVALUATE.

       RUN-HANDLER143.
           ACCEPT WS-PROG143.
           CALL WS-PROG143 USING WS-DATA143.

       COMPUTE-TOTALS59.
           MOVE 0 TO WS-TOTAL59.
           PERFORM VARYING WS-K59 FROM 1 BY 1 UNTIL WS-K59 > 10
               ADD WS-K59 TO WS-TOTAL59
           END-PERFORM.
           COMPUTE WS-AVERAGE59 = WS-TOTAL59 / 10.

       CLASSIFY-CODE10.
           EVALUATE WS-CODE10
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS10
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS10
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS10
           END-EVALUATE.

       RUN-HANDLER31.
           ACCEPT WS-PROG31.
           CALL WS-PROG31 USING WS-DATA31.

       QUERY-CUSTOMER72.
           ACCEPT WS-CUST72.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST72 "'"
               DELIMITED BY SIZE INTO WS-SQL72.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL72 END-EXEC.

       RUN-HANDLER-SAFE62.
           ACCEPT WS-CHOICE62.
           IF WS-CHOICE62 = 'A'
               CALL 'HANDLERA' USING WS-DATA62
           ELSE
               CALL 'HANDLERB' USING WS-DATA62
           END-IF.

       QUERY-CUSTOMER-SAFE129.
           ACCEPT WS-CUST129.
           EXEC SQL
               SELECT NAME INTO :WS-NAME129 FROM CUST WHERE ID = :WS-CUST129
           END-EXEC.

       COMPUTE-TOTALS135.
           MOVE 0 TO WS-TOTAL135.
           PERFORM VARYING WS-K135 FROM 1 BY 1 UNTIL WS-K135 > 10
               ADD WS-K135 TO WS-TOTAL135
           END-PERFORM.
           COMPUTE WS-AVERAGE135 = WS-TOTAL135 / 10.

       CHECK-LIMIT103.
           IF WS-AMOUNT103 > 1000
               MOVE 'Y' TO WS-FLAG103
           ELSE
               MOVE 'N' TO WS-FLAG103
           END-IF.

       QUERY-CUSTOMER-SAFE92.
           ACCEPT WS-CUST92.
           EXEC SQL
               SELECT NAME INTO :WS-NAME92 FROM CUST WHERE ID = :WS-CUST92
           END-EXEC.

       COMPUTE-TOTALS52.
           MOVE 0 TO WS-TOTAL52.
           PERFORM VARYING WS-K52 FROM 1 BY 1 UNTIL WS-K52 > 10
               ADD WS-K52 TO WS-TOTAL52
           END-PERFORM.
           COMPUTE WS-AVERAGE52 = WS-TOTAL52 / 10.

       CLASSIFY-CODE6.
           EVALUATE WS-CODE6
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS6
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS6
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS6
           END-EVALUATE.

       QUERY-CUSTOMER80.
           ACCEPT WS-CUST80.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST80 "'"
               DELIMITED BY SIZE INTO WS-SQL80.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL80 END-EXEC.

       QUERY-CUSTOMER-SAFE158.
           ACCEPT WS-CUST158.
           EXEC SQL
               SELECT NAME INTO :WS-NAME158 FROM CUST WHERE ID = :WS-CUST158
           END-EXEC.

       QUERY-CUSTOMER50.
           ACCEPT WS-CUST50.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST50 "'"
               DELIMITED BY SIZE INTO WS-SQL50.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL50 END-EXEC.

       RUN-HANDLER-SAFE93.
           ACCEPT WS-CHOICE93.
           IF WS-CHOICE93 = 'A'
               CALL 'HANDLERA' USING WS-DATA93
           ELSE
               CALL 'HANDLERB' USING WS-DATA93
           END-IF.

       FORMAT-HEADER109.
           MOVE 'MONTHLY REPORT' TO WS-TITLE109.
           STRING WS-TITLE109 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER109.
           DISPLAY WS-HEADER109.

       QUERY-CUSTOMER151.
           ACCEPT WS-CUST151.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST151 "'"
               DELIMITED BY SIZE INTO WS-SQL151.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL151 END-EXEC.

       QUERY-CUSTOMER7.
           ACCEPT WS-CUST7.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST7 "'"
               DELIMITED BY SIZE INTO WS-SQL7.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL7 END-EXEC.

       CLASSIFY-CODE142.
           EVALUATE WS-CODE142
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS142
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS142
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS142
           END-EVALUATE.

       FORMAT-HEADER146.
           MOVE 'MONTHLY REPORT' TO WS-TITLE146.
           STRING WS-TITLE146 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER146.
           DISPLAY WS-HEADER146.

       RUN-HANDLER-SAFE28.
           ACCEPT WS-CHOICE28.
           IF WS-CHOICE28 = 'A'
               CALL 'HANDLERA' USING WS-DATA28
           ELSE
               CALL 'HANDLERB' USING WS-DATA28
           END-IF.

       RUN-HANDLER122.
           ACCEPT WS-PROG122.
           CALL WS-PROG122 USING WS-DATA122.

       QUERY-CUSTOMER33.
           ACCEPT WS-CUST33.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST33 "'"
               DELIMITED BY SIZE INTO WS-SQL33.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL33 END-EXEC.

       RUN-HANDLER-SAFE55.
           ACCEPT WS-CHOICE55.
           IF WS-CHOICE55 = 'A'
               CALL 'HANDLERA' USING WS-DATA55
           ELSE
               CALL 'HANDLERB' USING WS-DATA55
           END-IF.

       RUN-HANDLER131.
           ACCEPT WS-PROG131.
           CALL WS-PROG131 USING WS-DATA131.

       RUN-HANDLER-SAFE102.
           ACCEPT WS-CHOICE102.
           IF WS-CHOICE102 = 'A'
               CALL 'HANDLERA' USING WS-DATA102
           ELSE
               CALL 'HANDLERB' USING WS-DATA102
           END-IF.

       RUN-HANDLER14.
           ACCEPT WS-PROG14.
           CALL WS-PROG14 USING WS-DATA14.

       RUN-HANDLER-SAFE27.
           ACCEPT WS-CHOICE27.
           IF WS-CHOICE27 = 'A'
               CALL 'HANDLERA' USING WS-DATA27
           ELSE
               CALL 'HANDLERB' USING WS-DATA27
           END-IF.

       RUN-HANDLER29.
           ACCEPT WS-PROG29.
           CALL WS-PROG29 USING WS-DATA29.

       QUERY-CUSTOMER68.
           ACCEPT WS-CUST68.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST68 "'"
               DELIMITED BY SIZE INTO WS-SQL68.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL68 END-EXEC.

       CHECK-LIMIT26.
           IF WS-AMOUNT26 > 1000
               MOVE 'Y' TO WS-FLAG26
           ELSE
               MOVE 'N' TO WS-FLAG26
           END-IF.

       QUERY-CUSTOMER-SAFE74.
           ACCEPT WS-CUST74.
           EXEC SQL
               SELECT NAME INTO :WS-NAME74 FROM CUST WHERE ID = :WS-CUST74
           END-EXEC.

       QUERY-CUSTOMER84.
           ACCEPT WS-CUST84.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST84 "'"
               DELIMITED BY SIZE INTO WS-SQL84.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL84 END-EXEC.

       QUERY-CUSTOMER-SAFE107.
           ACCEPT WS-CUST107.
           EXEC SQL
               SELECT NAME INTO :WS-NAME107 FROM CUST WHERE ID = :WS-CUST107
           END-EXEC.

       FORMAT-HEADER127.
           MOVE 'MONTHLY REPORT' TO WS-TITLE127.
           STRING WS-TITLE127 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER127.
           DISPLAY WS-HEADER127.

       QUERY-CUSTOMER88.
           ACCEPT WS-CUST88.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST88 "'"
               DELIMITED BY SIZE INTO WS-SQL88.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL88 END-EXEC.

       CLASSIFY-CODE148.
           EVALUATE WS-CODE148
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS148
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS148
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS148
           END-EVALUATE.

       RUN-HANDLER123.
           ACCEPT WS-PROG123.
           CALL WS-PROG123 USING WS-DATA123.

       RUN-HANDLER-SAFE37.
           ACCEPT WS-CHOICE37.
           IF WS-CHOICE37 = 'A'
               CALL 'HANDLERA' USING WS-DATA37
           ELSE
               CALL 'HANDLERB' USING WS-DATA37
           END-IF.

       CHECK-LIMIT65.
           IF WS-AMOUNT65 > 1000
               MOVE 'Y' TO WS-FLAG65
           ELSE
               MOVE 'N' TO WS-FLAG65
           END-IF.

       QUERY-CUSTOMER-SAFE124.
           ACCEPT WS-CUST124.
           EXEC SQL
               SELECT NAME INTO :WS-NAME124 FROM CUST WHERE ID = :WS-CUST124
           END-EXEC.

       FORMAT-HEADER96.
           MOVE 'MONTHLY REPORT' TO WS-TITLE96.
           STRING WS-TITLE96 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER96.
           DISPLAY WS-HEADER96.

       RUN-HANDLER-SAFE162.
           ACCEPT WS-CHOICE162.
           IF WS-CHOICE162 = 'A'
               CALL 'HANDLERA' USING WS-DATA162
           ELSE
               CALL 'HANDLERB' USING WS-DATA162
           END-IF.

       RUN-HANDLER-SAFE71.
           ACCEPT WS-CHOICE71.
           IF WS-CHOICE71 = 'A'
               CALL 'HANDLERA' USING WS-DATA71
           ELSE
               CALL 'HANDLERB' USING WS-DATA71
           END-IF.

       FORMAT-HEADER153.
           MOVE 'MONTHLY REPORT' TO WS-TITLE153.
           STRING WS-TITLE153 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER153.
           DISPLAY WS-HEADER153.

       CHECK-LIMIT150.
           IF WS-AMOUNT150 > 1000
               MOVE 'Y' TO WS-FLAG150
           ELSE
               MOVE 'N' TO WS-FLAG150
           END-IF.

       FORMAT-HEADER2.
           MOVE 'MONTHLY REPORT' TO WS-TITLE2.
           STRING WS-TITLE2 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER2.
           DISPLAY WS-HEADER2.

       CLASSIFY-CODE149.
           EVALUATE WS-CODE149
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS149
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS149
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS149
           END-EVALUATE.

       RUN-HANDLER57.
           ACCEPT WS-PROG57.
           CALL WS-PROG57 USING WS-DATA57.

       CHECK-LIMIT70.
           IF WS-AMOUNT70 > 1000
               MOVE 'Y' TO WS-FLAG70
           ELSE
               MOVE 'N' TO WS-FLAG70
           END-IF.

       QUERY-CUSTOMER-SAFE101.
           ACCEPT WS-CUST101.
           EXEC SQL
               SELECT NAME INTO :WS-NAME101 FROM CUST WHERE ID = :WS-CUST101
           END-EXEC.

       COMPUTE-TOTALS45.
           MOVE 0 TO WS-TOTAL45.
           PERFORM VARYING WS-K45 FROM 1 BY 1 UNTIL WS-K45 > 10
               ADD WS-K45 TO WS-TOTAL45
           END-PERFORM.
           COMPUTE WS-AVERAGE45 = WS-TOTAL45 / 10.

       CHECK-LIMIT137.
           IF WS-AMOUNT137 > 1000
               MOVE 'Y' TO WS-FLAG137
           ELSE
               MOVE 'N' TO WS-FLAG137
           END-IF.

       CLASSIFY-CODE44.
           EVALUATE WS-CODE44
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS44
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS44
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS44
           END-EVALUATE.

       QUERY-CUSTOMER128.
           ACCEPT WS-CUST128.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST128 "'"
               DELIMITED BY SIZE INTO WS-SQL128.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL128 END-EXEC.

       QUERY-CUSTOMER-SAFE116.
           ACCEPT WS-CUST116.
           EXEC SQL
               SELECT NAME INTO :WS-NAME116 FROM CUST WHERE ID = :WS-CUST116
           END-EXEC.

       RUN-HANDLER91.
           ACCEPT WS-PROG91.
           CALL WS-PROG91 USING WS-DATA91.

       COMPUTE-TOTALS42.
           MOVE 0 TO WS-TOTAL42.
           PERFORM VARYING WS-K42 FROM 1 BY 1 UNTIL WS-K42 > 10
               ADD WS-K42 TO WS-TOTAL42
           END-PERFORM.
           COMPUTE WS-AVERAGE42 = WS-TOTAL42 / 10.

       CHECK-LIMIT159.
           IF WS-AMOUNT159 > 1000
               MOVE 'Y' TO WS-FLAG159
           ELSE
               MOVE 'N' TO WS-FLAG159
           END-IF.

       QUERY-CUSTOMER5.
           ACCEPT WS-CUST5.
           STRING "SELECT NAME FROM CUST WHERE ID = '" WS-CUST5 "'"
               DELIMITED BY SIZE INTO WS-SQL5.
           EXEC SQL EXECUTE IMMEDIATE :WS-SQL5 END-EXEC.

       CHECK-LIMIT47.
           IF WS-AMOUNT47 > 1000
               MOVE 'Y' TO WS-FLAG47
           ELSE
               MOVE 'N' TO WS-FLAG47
           END-IF.

       RUN-HANDLER36.
           ACCEPT WS-PROG36.
           CALL WS-PROG36 USING WS-DATA36.

       CLASSIFY-CODE81.
           EVALUATE WS-CODE81
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS81
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS81
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS81
           END-EVALUATE.

       FORMAT-HEADER8.
           MOVE 'MONTHLY REPORT' TO WS-TITLE8.
           STRING WS-TITLE8 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER8.
           DISPLAY WS-HEADER8.

       RUN-HANDLER-SAFE105.
           ACCEPT WS-CHOICE105.
           IF WS-CHOICE105 = 'A'
               CALL 'HANDLERA' USING WS-DATA105
           ELSE
               CALL 'HANDLERB' USING WS-DATA105
           END-IF.

       CLASSIFY-CODE73.
           EVALUATE WS-CODE73
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS73
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS73
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS73
           END-EVALUATE.

