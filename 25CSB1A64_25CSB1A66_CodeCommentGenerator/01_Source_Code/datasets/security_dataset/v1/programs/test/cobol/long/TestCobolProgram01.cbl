       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTE01.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-TARGET1         PIC X(8).
       01  WS-TARGET3         PIC X(8).
       01  WS-IDX5            PIC 99.
       01  WS-TAB5.
           05  WS-ENTRY5      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT5            PIC X(10).
       01  WS-TARGET6         PIC X(8).
       01  WS-TARGET12         PIC X(8).
       01  WS-IDX13            PIC 99.
       01  WS-TAB13.
           05  WS-ENTRY13      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT13            PIC X(10).
       01  WS-IDX14            PIC 99.
       01  WS-TAB14.
           05  WS-ENTRY14      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT14            PIC X(10).
       01  WS-IDX16            PIC 99.
       01  WS-TAB16.
           05  WS-ENTRY16      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT16            PIC X(10).
       01  WS-IDX17            PIC 99.
       01  WS-TAB17.
           05  WS-ENTRY17      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT17            PIC X(10).
       01  WS-TARGET18         PIC X(8).
       01  WS-TARGET19         PIC X(8).
       01  WS-TARGET20         PIC X(8).
       01  WS-TARGET21         PIC X(8).
       01  WS-IDX24            PIC 99.
       01  WS-TAB24.
           05  WS-ENTRY24      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT24            PIC X(10).
       01  WS-TARGET27         PIC X(8).
       01  WS-IDX29            PIC 99.
       01  WS-TAB29.
           05  WS-ENTRY29      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT29            PIC X(10).
       01  WS-IDX30            PIC 99.
       01  WS-TAB30.
           05  WS-ENTRY30      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT30            PIC X(10).
       01  WS-IDX33            PIC 99.
       01  WS-TAB33.
           05  WS-ENTRY33      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT33            PIC X(10).
       01  WS-TARGET35         PIC X(8).
       01  WS-TARGET42         PIC X(8).
       01  WS-TARGET43         PIC X(8).
       01  WS-TARGET44         PIC X(8).
       01  WS-TARGET45         PIC X(8).
       01  WS-TARGET47         PIC X(8).
       01  WS-IDX48            PIC 99.
       01  WS-TAB48.
           05  WS-ENTRY48      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT48            PIC X(10).
       01  WS-TARGET49         PIC X(8).
       01  WS-IDX51            PIC 99.
       01  WS-TAB51.
           05  WS-ENTRY51      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT51            PIC X(10).
       01  WS-TARGET60         PIC X(8).
       01  WS-IDX62            PIC 99.
       01  WS-TAB62.
           05  WS-ENTRY62      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT62            PIC X(10).
       01  WS-IDX63            PIC 99.
       01  WS-TAB63.
           05  WS-ENTRY63      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT63            PIC X(10).
       01  WS-TARGET65         PIC X(8).
       01  WS-TARGET67         PIC X(8).
       01  WS-IDX70            PIC 99.
       01  WS-TAB70.
           05  WS-ENTRY70      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT70            PIC X(10).
       01  WS-TARGET72         PIC X(8).
       01  WS-IDX73            PIC 99.
       01  WS-TAB73.
           05  WS-ENTRY73      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT73            PIC X(10).
       01  WS-TARGET75         PIC X(8).
       01  WS-TARGET80         PIC X(8).
       01  WS-TARGET81         PIC X(8).
       01  WS-TARGET83         PIC X(8).
       01  WS-TARGET84         PIC X(8).
       01  WS-TARGET87         PIC X(8).
       01  WS-TARGET89         PIC X(8).
       01  WS-TARGET90         PIC X(8).
       01  WS-IDX91            PIC 99.
       01  WS-TAB91.
           05  WS-ENTRY91      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT91            PIC X(10).
       01  WS-TARGET96         PIC X(8).
       01  WS-TARGET97         PIC X(8).
       01  WS-IDX99            PIC 99.
       01  WS-TAB99.
           05  WS-ENTRY99      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT99            PIC X(10).
       01  WS-IDX102            PIC 99.
       01  WS-TAB102.
           05  WS-ENTRY102      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT102            PIC X(10).
       01  WS-TARGET103         PIC X(8).
       01  WS-TARGET104         PIC X(8).
       01  WS-TARGET106         PIC X(8).
       01  WS-TARGET107         PIC X(8).
       01  WS-IDX108            PIC 99.
       01  WS-TAB108.
           05  WS-ENTRY108      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT108            PIC X(10).
       01  WS-TARGET110         PIC X(8).
       01  WS-TARGET112         PIC X(8).
       01  WS-TARGET114         PIC X(8).
       01  WS-TARGET115         PIC X(8).
       01  WS-IDX117            PIC 99.
       01  WS-TAB117.
           05  WS-ENTRY117      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT117            PIC X(10).
       01  WS-TARGET118         PIC X(8).
       01  WS-IDX119            PIC 99.
       01  WS-TAB119.
           05  WS-ENTRY119      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT119            PIC X(10).
       01  WS-IDX123            PIC 99.
       01  WS-TAB123.
           05  WS-ENTRY123      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT123            PIC X(10).
       01  WS-TARGET124         PIC X(8).
       01  WS-TARGET125         PIC X(8).
       01  WS-IDX128            PIC 99.
       01  WS-TAB128.
           05  WS-ENTRY128      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT128            PIC X(10).
       01  WS-TARGET130         PIC X(8).
       01  WS-TARGET132         PIC X(8).
       01  WS-TARGET137         PIC X(8).
       01  WS-IDX144            PIC 99.
       01  WS-TAB144.
           05  WS-ENTRY144      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT144            PIC X(10).
       01  WS-TARGET145         PIC X(8).
       01  WS-IDX146            PIC 99.
       01  WS-TAB146.
           05  WS-ENTRY146      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT146            PIC X(10).
       01  WS-TARGET148         PIC X(8).
       01  WS-IDX149            PIC 99.
       01  WS-TAB149.
           05  WS-ENTRY149      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT149            PIC X(10).
       01  WS-IDX151            PIC 99.
       01  WS-TAB151.
           05  WS-ENTRY151      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT151            PIC X(10).
       01  WS-IDX153            PIC 99.
       01  WS-TAB153.
           05  WS-ENTRY153      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT153            PIC X(10).
       01  WS-TARGET158         PIC X(8).
       01  WS-TARGET160         PIC X(8).
       01  WS-IDX161            PIC 99.
       01  WS-TAB161.
           05  WS-ENTRY161      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT161            PIC X(10).
       01  WS-TARGET162         PIC X(8).
       01  WS-TARGET163         PIC X(8).
       01  WS-IDX164            PIC 99.
       01  WS-TAB164.
           05  WS-ENTRY164      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT164            PIC X(10).
       01  WS-IDX165            PIC 99.
       01  WS-TAB165.
           05  WS-ENTRY165      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT165            PIC X(10).
       01  WS-TARGET166         PIC X(8).
       01  WS-TARGET168         PIC X(8).
       01  WS-TARGET171         PIC X(8).
       01  WS-IDX172            PIC 99.
       01  WS-TAB172.
           05  WS-ENTRY172      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT172            PIC X(10).
       01  WS-IDX173            PIC 99.
       01  WS-TAB173.
           05  WS-ENTRY173      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT173            PIC X(10).
       01  WS-TARGET175         PIC X(8).
       01  WS-IDX176            PIC 99.
       01  WS-TAB176.
           05  WS-ENTRY176      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT176            PIC X(10).
       01  WS-TARGET181         PIC X(8).
       01  WS-IDX182            PIC 99.
       01  WS-TAB182.
           05  WS-ENTRY182      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT182            PIC X(10).
       01  WS-IDX183            PIC 99.
       01  WS-TAB183.
           05  WS-ENTRY183      PIC X(10) OCCURS 10 TIMES.
       01  WS-OUT183            PIC X(10).
       01  WS-TARGET184         PIC X(8).
       01  WS-TITLE2          PIC X(20) VALUE SPACES.
       01  WS-HEADER2         PIC X(40) VALUE SPACES.
       01  WS-TOTAL4          PIC 9(6) VALUE 0.
       01  WS-K4              PIC 99 VALUE 0.
       01  WS-AVERAGE4        PIC 9(6)V99 VALUE 0.
       01  WS-CODE7           PIC 9 VALUE 1.
       01  WS-STATUS7         PIC X(6) VALUE SPACES.
       01  WS-TOTAL8          PIC 9(6) VALUE 0.
       01  WS-K8              PIC 99 VALUE 0.
       01  WS-AVERAGE8        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL9          PIC 9(6) VALUE 0.
       01  WS-K9              PIC 99 VALUE 0.
       01  WS-AVERAGE9        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL10          PIC 9(6) VALUE 0.
       01  WS-K10              PIC 99 VALUE 0.
       01  WS-AVERAGE10        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE11          PIC X(20) VALUE SPACES.
       01  WS-HEADER11         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT15         PIC 9(6) VALUE 500.
       01  WS-FLAG15           PIC X VALUE 'N'.
       01  WS-TITLE22          PIC X(20) VALUE SPACES.
       01  WS-HEADER22         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT23         PIC 9(6) VALUE 500.
       01  WS-FLAG23           PIC X VALUE 'N'.
       01  WS-TITLE25          PIC X(20) VALUE SPACES.
       01  WS-HEADER25         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT26         PIC 9(6) VALUE 500.
       01  WS-FLAG26           PIC X VALUE 'N'.
       01  WS-CODE28           PIC 9 VALUE 1.
       01  WS-STATUS28         PIC X(6) VALUE SPACES.
       01  WS-TOTAL31          PIC 9(6) VALUE 0.
       01  WS-K31              PIC 99 VALUE 0.
       01  WS-AVERAGE31        PIC 9(6)V99 VALUE 0.
       01  WS-CODE32           PIC 9 VALUE 1.
       01  WS-STATUS32         PIC X(6) VALUE SPACES.
       01  WS-TOTAL34          PIC 9(6) VALUE 0.
       01  WS-K34              PIC 99 VALUE 0.
       01  WS-AVERAGE34        PIC 9(6)V99 VALUE 0.
       01  WS-CODE36           PIC 9 VALUE 1.
       01  WS-STATUS36         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT37         PIC 9(6) VALUE 500.
       01  WS-FLAG37           PIC X VALUE 'N'.
       01  WS-TOTAL38          PIC 9(6) VALUE 0.
       01  WS-K38              PIC 99 VALUE 0.
       01  WS-AVERAGE38        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE39          PIC X(20) VALUE SPACES.
       01  WS-HEADER39         PIC X(40) VALUE SPACES.
       01  WS-TITLE40          PIC X(20) VALUE SPACES.
       01  WS-HEADER40         PIC X(40) VALUE SPACES.
       01  WS-CODE41           PIC 9 VALUE 1.
       01  WS-STATUS41         PIC X(6) VALUE SPACES.
       01  WS-CODE46           PIC 9 VALUE 1.
       01  WS-STATUS46         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT50         PIC 9(6) VALUE 500.
       01  WS-FLAG50           PIC X VALUE 'N'.
       01  WS-TITLE52          PIC X(20) VALUE SPACES.
       01  WS-HEADER52         PIC X(40) VALUE SPACES.
       01  WS-TITLE53          PIC X(20) VALUE SPACES.
       01  WS-HEADER53         PIC X(40) VALUE SPACES.
       01  WS-TOTAL54          PIC 9(6) VALUE 0.
       01  WS-K54              PIC 99 VALUE 0.
       01  WS-AVERAGE54        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL55          PIC 9(6) VALUE 0.
       01  WS-K55              PIC 99 VALUE 0.
       01  WS-AVERAGE55        PIC 9(6)V99 VALUE 0.
       01  WS-CODE56           PIC 9 VALUE 1.
       01  WS-STATUS56         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT57         PIC 9(6) VALUE 500.
       01  WS-FLAG57           PIC X VALUE 'N'.
       01  WS-AMOUNT58         PIC 9(6) VALUE 500.
       01  WS-FLAG58           PIC X VALUE 'N'.
       01  WS-TOTAL59          PIC 9(6) VALUE 0.
       01  WS-K59              PIC 99 VALUE 0.
       01  WS-AVERAGE59        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE61          PIC X(20) VALUE SPACES.
       01  WS-HEADER61         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT64         PIC 9(6) VALUE 500.
       01  WS-FLAG64           PIC X VALUE 'N'.
       01  WS-CODE66           PIC 9 VALUE 1.
       01  WS-STATUS66         PIC X(6) VALUE SPACES.
       01  WS-TITLE68          PIC X(20) VALUE SPACES.
       01  WS-HEADER68         PIC X(40) VALUE SPACES.
       01  WS-TITLE69          PIC X(20) VALUE SPACES.
       01  WS-HEADER69         PIC X(40) VALUE SPACES.
       01  WS-TITLE71          PIC X(20) VALUE SPACES.
       01  WS-HEADER71         PIC X(40) VALUE SPACES.
       01  WS-TITLE74          PIC X(20) VALUE SPACES.
       01  WS-HEADER74         PIC X(40) VALUE SPACES.
       01  WS-TITLE76          PIC X(20) VALUE SPACES.
       01  WS-HEADER76         PIC X(40) VALUE SPACES.
       01  WS-TITLE77          PIC X(20) VALUE SPACES.
       01  WS-HEADER77         PIC X(40) VALUE SPACES.
       01  WS-TOTAL78          PIC 9(6) VALUE 0.
       01  WS-K78              PIC 99 VALUE 0.
       01  WS-AVERAGE78        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT79         PIC 9(6) VALUE 500.
       01  WS-FLAG79           PIC X VALUE 'N'.
       01  WS-CODE82           PIC 9 VALUE 1.
       01  WS-STATUS82         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT85         PIC 9(6) VALUE 500.
       01  WS-FLAG85           PIC X VALUE 'N'.
       01  WS-TOTAL86          PIC 9(6) VALUE 0.
       01  WS-K86              PIC 99 VALUE 0.
       01  WS-AVERAGE86        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT88         PIC 9(6) VALUE 500.
       01  WS-FLAG88           PIC X VALUE 'N'.
       01  WS-CODE92           PIC 9 VALUE 1.
       01  WS-STATUS92         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT93         PIC 9(6) VALUE 500.
       01  WS-FLAG93           PIC X VALUE 'N'.
       01  WS-TOTAL94          PIC 9(6) VALUE 0.
       01  WS-K94              PIC 99 VALUE 0.
       01  WS-AVERAGE94        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT95         PIC 9(6) VALUE 500.
       01  WS-FLAG95           PIC X VALUE 'N'.
       01  WS-TITLE98          PIC X(20) VALUE SPACES.
       01  WS-HEADER98         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT100         PIC 9(6) VALUE 500.
       01  WS-FLAG100           PIC X VALUE 'N'.
       01  WS-TOTAL101          PIC 9(6) VALUE 0.
       01  WS-K101              PIC 99 VALUE 0.
       01  WS-AVERAGE101        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE105          PIC X(20) VALUE SPACES.
       01  WS-HEADER105         PIC X(40) VALUE SPACES.
       01  WS-TOTAL109          PIC 9(6) VALUE 0.
       01  WS-K109              PIC 99 VALUE 0.
       01  WS-AVERAGE109        PIC 9(6)V99 VALUE 0.
       01  WS-CODE111           PIC 9 VALUE 1.
       01  WS-STATUS111         PIC X(6) VALUE SPACES.
       01  WS-TITLE113          PIC X(20) VALUE SPACES.
       01  WS-HEADER113         PIC X(40) VALUE SPACES.
       01  WS-TOTAL116          PIC 9(6) VALUE 0.
       01  WS-K116              PIC 99 VALUE 0.
       01  WS-AVERAGE116        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE120          PIC X(20) VALUE SPACES.
       01  WS-HEADER120         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT121         PIC 9(6) VALUE 500.
       01  WS-FLAG121           PIC X VALUE 'N'.
       01  WS-CODE122           PIC 9 VALUE 1.
       01  WS-STATUS122         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT126         PIC 9(6) VALUE 500.
       01  WS-FLAG126           PIC X VALUE 'N'.
       01  WS-CODE127           PIC 9 VALUE 1.
       01  WS-STATUS127         PIC X(6) VALUE SPACES.
       01  WS-CODE129           PIC 9 VALUE 1.
       01  WS-STATUS129         PIC X(6) VALUE SPACES.
       01  WS-TOTAL131          PIC 9(6) VALUE 0.
       01  WS-K131              PIC 99 VALUE 0.
       01  WS-AVERAGE131        PIC 9(6)V99 VALUE 0.
       01  WS-CODE133           PIC 9 VALUE 1.
       01  WS-STATUS133         PIC X(6) VALUE SPACES.
       01  WS-TOTAL134          PIC 9(6) VALUE 0.
       01  WS-K134              PIC 99 VALUE 0.
       01  WS-AVERAGE134        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL135          PIC 9(6) VALUE 0.
       01  WS-K135              PIC 99 VALUE 0.
       01  WS-AVERAGE135        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL136          PIC 9(6) VALUE 0.
       01  WS-K136              PIC 99 VALUE 0.
       01  WS-AVERAGE136        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE138          PIC X(20) VALUE SPACES.
       01  WS-HEADER138         PIC X(40) VALUE SPACES.
       01  WS-TOTAL139          PIC 9(6) VALUE 0.
       01  WS-K139              PIC 99 VALUE 0.
       01  WS-AVERAGE139        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE140          PIC X(20) VALUE SPACES.
       01  WS-HEADER140         PIC X(40) VALUE SPACES.
       01  WS-TOTAL141          PIC 9(6) VALUE 0.
       01  WS-K141              PIC 99 VALUE 0.
       01  WS-AVERAGE141        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL142          PIC 9(6) VALUE 0.
       01  WS-K142              PIC 99 VALUE 0.
       01  WS-AVERAGE142        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT143         PIC 9(6) VALUE 500.
       01  WS-FLAG143           PIC X VALUE 'N'.
       01  WS-CODE147           PIC 9 VALUE 1.
       01  WS-STATUS147         PIC X(6) VALUE SPACES.
       01  WS-TOTAL150          PIC 9(6) VALUE 0.
       01  WS-K150              PIC 99 VALUE 0.
       01  WS-AVERAGE150        PIC 9(6)V99 VALUE 0.
       01  WS-CODE152           PIC 9 VALUE 1.
       01  WS-STATUS152         PIC X(6) VALUE SPACES.
       01  WS-TITLE154          PIC X(20) VALUE SPACES.
       01  WS-HEADER154         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT155         PIC 9(6) VALUE 500.
       01  WS-FLAG155           PIC X VALUE 'N'.
       01  WS-TOTAL156          PIC 9(6) VALUE 0.
       01  WS-K156              PIC 99 VALUE 0.
       01  WS-AVERAGE156        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT157         PIC 9(6) VALUE 500.
       01  WS-FLAG157           PIC X VALUE 'N'.
       01  WS-AMOUNT159         PIC 9(6) VALUE 500.
       01  WS-FLAG159           PIC X VALUE 'N'.
       01  WS-CODE167           PIC 9 VALUE 1.
       01  WS-STATUS167         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT169         PIC 9(6) VALUE 500.
       01  WS-FLAG169           PIC X VALUE 'N'.
       01  WS-CODE170           PIC 9 VALUE 1.
       01  WS-STATUS170         PIC X(6) VALUE SPACES.
       01  WS-CODE174           PIC 9 VALUE 1.
       01  WS-STATUS174         PIC X(6) VALUE SPACES.
       01  WS-TOTAL177          PIC 9(6) VALUE 0.
       01  WS-K177              PIC 99 VALUE 0.
       01  WS-AVERAGE177        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT178         PIC 9(6) VALUE 500.
       01  WS-FLAG178           PIC X VALUE 'N'.
       01  WS-TITLE179          PIC X(20) VALUE SPACES.
       01  WS-HEADER179         PIC X(40) VALUE SPACES.
       01  WS-TOTAL180          PIC 9(6) VALUE 0.
       01  WS-K180              PIC 99 VALUE 0.
       01  WS-AVERAGE180        PIC 9(6)V99 VALUE 0.
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       LOOKUP-ENTRY-SAFE144.
           ACCEPT WS-IDX144.
           IF WS-IDX144 > 0 AND WS-IDX144 NOT > 10
               MOVE WS-ENTRY144(WS-IDX144) TO WS-OUT144
           END-IF.

       TRANSFER1.
           EXEC CICS RECEIVE INTO(WS-TARGET1) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET1) END-EXEC.

       LOOKUP-ENTRY165.
           ACCEPT WS-IDX165.
           MOVE WS-ENTRY165(WS-IDX165) TO WS-OUT165.

       FORMAT-HEADER2.
           MOVE 'MONTHLY REPORT' TO WS-TITLE2.
           STRING WS-TITLE2 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER2.
           DISPLAY WS-HEADER2.

       CLASSIFY-CODE133.
           EVALUATE WS-CODE133
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS133
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS133
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS133
           END-EVALUATE.

       LOOKUP-ENTRY-SAFE128.
           ACCEPT WS-IDX128.
           IF WS-IDX128 > 0 AND WS-IDX128 NOT > 10
               MOVE WS-ENTRY128(WS-IDX128) TO WS-OUT128
           END-IF.

       LOOKUP-ENTRY-SAFE102.
           ACCEPT WS-IDX102.
           IF WS-IDX102 > 0 AND WS-IDX102 NOT > 10
               MOVE WS-ENTRY102(WS-IDX102) TO WS-OUT102
           END-IF.

       LOOKUP-ENTRY-SAFE33.
           ACCEPT WS-IDX33.
           IF WS-IDX33 > 0 AND WS-IDX33 NOT > 10
               MOVE WS-ENTRY33(WS-IDX33) TO WS-OUT33
           END-IF.

       TRANSFER-SAFE175.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       FORMAT-HEADER39.
           MOVE 'MONTHLY REPORT' TO WS-TITLE39.
           STRING WS-TITLE39 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER39.
           DISPLAY WS-HEADER39.

       TRANSFER-SAFE106.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE35.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER83.
           EXEC CICS RECEIVE INTO(WS-TARGET83) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET83) END-EXEC.

       COMPUTE-TOTALS55.
           MOVE 0 TO WS-TOTAL55.
           PERFORM VARYING WS-K55 FROM 1 BY 1 UNTIL WS-K55 > 10
               ADD WS-K55 TO WS-TOTAL55
           END-PERFORM.
           COMPUTE WS-AVERAGE55 = WS-TOTAL55 / 10.

       TRANSFER18.
           EXEC CICS RECEIVE INTO(WS-TARGET18) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET18) END-EXEC.

       TRANSFER163.
           EXEC CICS RECEIVE INTO(WS-TARGET163) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET163) END-EXEC.

       FORMAT-HEADER74.
           MOVE 'MONTHLY REPORT' TO WS-TITLE74.
           STRING WS-TITLE74 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER74.
           DISPLAY WS-HEADER74.

       CHECK-LIMIT143.
           IF WS-AMOUNT143 > 1000
               MOVE 'Y' TO WS-FLAG143
           ELSE
               MOVE 'N' TO WS-FLAG143
           END-IF.

       TRANSFER-SAFE6.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE84.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER43.
           EXEC CICS RECEIVE INTO(WS-TARGET43) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET43) END-EXEC.

       FORMAT-HEADER179.
           MOVE 'MONTHLY REPORT' TO WS-TITLE179.
           STRING WS-TITLE179 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER179.
           DISPLAY WS-HEADER179.

       COMPUTE-TOTALS141.
           MOVE 0 TO WS-TOTAL141.
           PERFORM VARYING WS-K141 FROM 1 BY 1 UNTIL WS-K141 > 10
               ADD WS-K141 TO WS-TOTAL141
           END-PERFORM.
           COMPUTE WS-AVERAGE141 = WS-TOTAL141 / 10.

       CLASSIFY-CODE82.
           EVALUATE WS-CODE82
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS82
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS82
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS82
           END-EVALUATE.

       CHECK-LIMIT157.
           IF WS-AMOUNT157 > 1000
               MOVE 'Y' TO WS-FLAG157
           ELSE
               MOVE 'N' TO WS-FLAG157
           END-IF.

       CHECK-LIMIT159.
           IF WS-AMOUNT159 > 1000
               MOVE 'Y' TO WS-FLAG159
           ELSE
               MOVE 'N' TO WS-FLAG159
           END-IF.

       COMPUTE-TOTALS34.
           MOVE 0 TO WS-TOTAL34.
           PERFORM VARYING WS-K34 FROM 1 BY 1 UNTIL WS-K34 > 10
               ADD WS-K34 TO WS-TOTAL34
           END-PERFORM.
           COMPUTE WS-AVERAGE34 = WS-TOTAL34 / 10.

       COMPUTE-TOTALS94.
           MOVE 0 TO WS-TOTAL94.
           PERFORM VARYING WS-K94 FROM 1 BY 1 UNTIL WS-K94 > 10
               ADD WS-K94 TO WS-TOTAL94
           END-PERFORM.
           COMPUTE WS-AVERAGE94 = WS-TOTAL94 / 10.

       TRANSFER-SAFE47.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CLASSIFY-CODE36.
           EVALUATE WS-CODE36
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS36
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS36
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS36
           END-EVALUATE.

       COMPUTE-TOTALS109.
           MOVE 0 TO WS-TOTAL109.
           PERFORM VARYING WS-K109 FROM 1 BY 1 UNTIL WS-K109 > 10
               ADD WS-K109 TO WS-TOTAL109
           END-PERFORM.
           COMPUTE WS-AVERAGE109 = WS-TOTAL109 / 10.

       LOOKUP-ENTRY73.
           ACCEPT WS-IDX73.
           MOVE WS-ENTRY73(WS-IDX73) TO WS-OUT73.

       FORMAT-HEADER40.
           MOVE 'MONTHLY REPORT' TO WS-TITLE40.
           STRING WS-TITLE40 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER40.
           DISPLAY WS-HEADER40.

       CHECK-LIMIT85.
           IF WS-AMOUNT85 > 1000
               MOVE 'Y' TO WS-FLAG85
           ELSE
               MOVE 'N' TO WS-FLAG85
           END-IF.

       LOOKUP-ENTRY16.
           ACCEPT WS-IDX16.
           MOVE WS-ENTRY16(WS-IDX16) TO WS-OUT16.

       COMPUTE-TOTALS54.
           MOVE 0 TO WS-TOTAL54.
           PERFORM VARYING WS-K54 FROM 1 BY 1 UNTIL WS-K54 > 10
               ADD WS-K54 TO WS-TOTAL54
           END-PERFORM.
           COMPUTE WS-AVERAGE54 = WS-TOTAL54 / 10.

       TRANSFER80.
           EXEC CICS RECEIVE INTO(WS-TARGET80) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET80) END-EXEC.

       TRANSFER137.
           EXEC CICS RECEIVE INTO(WS-TARGET137) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET137) END-EXEC.

       CLASSIFY-CODE46.
           EVALUATE WS-CODE46
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS46
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS46
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS46
           END-EVALUATE.

       TRANSFER-SAFE107.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE118.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       FORMAT-HEADER105.
           MOVE 'MONTHLY REPORT' TO WS-TITLE105.
           STRING WS-TITLE105 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER105.
           DISPLAY WS-HEADER105.

       LOOKUP-ENTRY24.
           ACCEPT WS-IDX24.
           MOVE WS-ENTRY24(WS-IDX24) TO WS-OUT24.

       COMPUTE-TOTALS86.
           MOVE 0 TO WS-TOTAL86.
           PERFORM VARYING WS-K86 FROM 1 BY 1 UNTIL WS-K86 > 10
               ADD WS-K86 TO WS-TOTAL86
           END-PERFORM.
           COMPUTE WS-AVERAGE86 = WS-TOTAL86 / 10.

       TRANSFER27.
           EXEC CICS RECEIVE INTO(WS-TARGET27) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET27) END-EXEC.

       TRANSFER-SAFE115.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER75.
           EXEC CICS RECEIVE INTO(WS-TARGET75) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET75) END-EXEC.

       TRANSFER158.
           EXEC CICS RECEIVE INTO(WS-TARGET158) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET158) END-EXEC.

       LOOKUP-ENTRY30.
           ACCEPT WS-IDX30.
           MOVE WS-ENTRY30(WS-IDX30) TO WS-OUT30.

       FORMAT-HEADER71.
           MOVE 'MONTHLY REPORT' TO WS-TITLE71.
           STRING WS-TITLE71 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER71.
           DISPLAY WS-HEADER71.

       LOOKUP-ENTRY-SAFE117.
           ACCEPT WS-IDX117.
           IF WS-IDX117 > 0 AND WS-IDX117 NOT > 10
               MOVE WS-ENTRY117(WS-IDX117) TO WS-OUT117
           END-IF.

       TRANSFER162.
           EXEC CICS RECEIVE INTO(WS-TARGET162) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET162) END-EXEC.

       COMPUTE-TOTALS134.
           MOVE 0 TO WS-TOTAL134.
           PERFORM VARYING WS-K134 FROM 1 BY 1 UNTIL WS-K134 > 10
               ADD WS-K134 TO WS-TOTAL134
           END-PERFORM.
           COMPUTE WS-AVERAGE134 = WS-TOTAL134 / 10.

       COMPUTE-TOTALS142.
           MOVE 0 TO WS-TOTAL142.
           PERFORM VARYING WS-K142 FROM 1 BY 1 UNTIL WS-K142 > 10
               ADD WS-K142 TO WS-TOTAL142
           END-PERFORM.
           COMPUTE WS-AVERAGE142 = WS-TOTAL142 / 10.

       LOOKUP-ENTRY-SAFE146.
           ACCEPT WS-IDX146.
           IF WS-IDX146 > 0 AND WS-IDX146 NOT > 10
               MOVE WS-ENTRY146(WS-IDX146) TO WS-OUT146
           END-IF.

       TRANSFER-SAFE148.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       FORMAT-HEADER25.
           MOVE 'MONTHLY REPORT' TO WS-TITLE25.
           STRING WS-TITLE25 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER25.
           DISPLAY WS-HEADER25.

       CLASSIFY-CODE28.
           EVALUATE WS-CODE28
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS28
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS28
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS28
           END-EVALUATE.

       CLASSIFY-CODE147.
           EVALUATE WS-CODE147
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS147
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS147
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS147
           END-EVALUATE.

       TRANSFER130.
           EXEC CICS RECEIVE INTO(WS-TARGET130) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET130) END-EXEC.

       CLASSIFY-CODE32.
           EVALUATE WS-CODE32
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS32
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS32
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS32
           END-EVALUATE.

       FORMAT-HEADER77.
           MOVE 'MONTHLY REPORT' TO WS-TITLE77.
           STRING WS-TITLE77 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER77.
           DISPLAY WS-HEADER77.

       CLASSIFY-CODE129.
           EVALUATE WS-CODE129
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS129
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS129
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS129
           END-EVALUATE.

       FORMAT-HEADER140.
           MOVE 'MONTHLY REPORT' TO WS-TITLE140.
           STRING WS-TITLE140 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER140.
           DISPLAY WS-HEADER140.

       LOOKUP-ENTRY-SAFE182.
           ACCEPT WS-IDX182.
           IF WS-IDX182 > 0 AND WS-IDX182 NOT > 10
               MOVE WS-ENTRY182(WS-IDX182) TO WS-OUT182
           END-IF.

       TRANSFER-SAFE160.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY-SAFE91.
           ACCEPT WS-IDX91.
           IF WS-IDX91 > 0 AND WS-IDX91 NOT > 10
               MOVE WS-ENTRY91(WS-IDX91) TO WS-OUT91
           END-IF.

       COMPUTE-TOTALS38.
           MOVE 0 TO WS-TOTAL38.
           PERFORM VARYING WS-K38 FROM 1 BY 1 UNTIL WS-K38 > 10
               ADD WS-K38 TO WS-TOTAL38
           END-PERFORM.
           COMPUTE WS-AVERAGE38 = WS-TOTAL38 / 10.

       COMPUTE-TOTALS9.
           MOVE 0 TO WS-TOTAL9.
           PERFORM VARYING WS-K9 FROM 1 BY 1 UNTIL WS-K9 > 10
               ADD WS-K9 TO WS-TOTAL9
           END-PERFORM.
           COMPUTE WS-AVERAGE9 = WS-TOTAL9 / 10.

       TRANSFER-SAFE44.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER81.
           EXEC CICS RECEIVE INTO(WS-TARGET81) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET81) END-EXEC.

       FORMAT-HEADER113.
           MOVE 'MONTHLY REPORT' TO WS-TITLE113.
           STRING WS-TITLE113 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER113.
           DISPLAY WS-HEADER113.

       CHECK-LIMIT100.
           IF WS-AMOUNT100 > 1000
               MOVE 'Y' TO WS-FLAG100
           ELSE
               MOVE 'N' TO WS-FLAG100
           END-IF.

       TRANSFER-SAFE90.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CHECK-LIMIT93.
           IF WS-AMOUNT93 > 1000
               MOVE 'Y' TO WS-FLAG93
           ELSE
               MOVE 'N' TO WS-FLAG93
           END-IF.

       COMPUTE-TOTALS139.
           MOVE 0 TO WS-TOTAL139.
           PERFORM VARYING WS-K139 FROM 1 BY 1 UNTIL WS-K139 > 10
               ADD WS-K139 TO WS-TOTAL139
           END-PERFORM.
           COMPUTE WS-AVERAGE139 = WS-TOTAL139 / 10.

       TRANSFER-SAFE145.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE19.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER125.
           EXEC CICS RECEIVE INTO(WS-TARGET125) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET125) END-EXEC.

       LOOKUP-ENTRY-SAFE108.
           ACCEPT WS-IDX108.
           IF WS-IDX108 > 0 AND WS-IDX108 NOT > 10
               MOVE WS-ENTRY108(WS-IDX108) TO WS-OUT108
           END-IF.

       TRANSFER-SAFE65.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CLASSIFY-CODE167.
           EVALUATE WS-CODE167
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS167
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS167
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS167
           END-EVALUATE.

       COMPUTE-TOTALS177.
           MOVE 0 TO WS-TOTAL177.
           PERFORM VARYING WS-K177 FROM 1 BY 1 UNTIL WS-K177 > 10
               ADD WS-K177 TO WS-TOTAL177
           END-PERFORM.
           COMPUTE WS-AVERAGE177 = WS-TOTAL177 / 10.

       COMPUTE-TOTALS8.
           MOVE 0 TO WS-TOTAL8.
           PERFORM VARYING WS-K8 FROM 1 BY 1 UNTIL WS-K8 > 10
               ADD WS-K8 TO WS-TOTAL8
           END-PERFORM.
           COMPUTE WS-AVERAGE8 = WS-TOTAL8 / 10.

       CLASSIFY-CODE174.
           EVALUATE WS-CODE174
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS174
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS174
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS174
           END-EVALUATE.

       FORMAT-HEADER11.
           MOVE 'MONTHLY REPORT' TO WS-TITLE11.
           STRING WS-TITLE11 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER11.
           DISPLAY WS-HEADER11.

       CHECK-LIMIT95.
           IF WS-AMOUNT95 > 1000
               MOVE 'Y' TO WS-FLAG95
           ELSE
               MOVE 'N' TO WS-FLAG95
           END-IF.

       TRANSFER-SAFE103.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER89.
           EXEC CICS RECEIVE INTO(WS-TARGET89) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET89) END-EXEC.

       COMPUTE-TOTALS4.
           MOVE 0 TO WS-TOTAL4.
           PERFORM VARYING WS-K4 FROM 1 BY 1 UNTIL WS-K4 > 10
               ADD WS-K4 TO WS-TOTAL4
           END-PERFORM.
           COMPUTE WS-AVERAGE4 = WS-TOTAL4 / 10.

       FORMAT-HEADER69.
           MOVE 'MONTHLY REPORT' TO WS-TITLE69.
           STRING WS-TITLE69 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER69.
           DISPLAY WS-HEADER69.

       CHECK-LIMIT169.
           IF WS-AMOUNT169 > 1000
               MOVE 'Y' TO WS-FLAG169
           ELSE
               MOVE 'N' TO WS-FLAG169
           END-IF.

       COMPUTE-TOTALS156.
           MOVE 0 TO WS-TOTAL156.
           PERFORM VARYING WS-K156 FROM 1 BY 1 UNTIL WS-K156 > 10
               ADD WS-K156 TO WS-TOTAL156
           END-PERFORM.
           COMPUTE WS-AVERAGE156 = WS-TOTAL156 / 10.

       LOOKUP-ENTRY-SAFE149.
           ACCEPT WS-IDX149.
           IF WS-IDX149 > 0 AND WS-IDX149 NOT > 10
               MOVE WS-ENTRY149(WS-IDX149) TO WS-OUT149
           END-IF.

       FORMAT-HEADER53.
           MOVE 'MONTHLY REPORT' TO WS-TITLE53.
           STRING WS-TITLE53 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER53.
           DISPLAY WS-HEADER53.

       COMPUTE-TOTALS135.
           MOVE 0 TO WS-TOTAL135.
           PERFORM VARYING WS-K135 FROM 1 BY 1 UNTIL WS-K135 > 10
               ADD WS-K135 TO WS-TOTAL135
           END-PERFORM.
           COMPUTE WS-AVERAGE135 = WS-TOTAL135 / 10.

       TRANSFER171.
           EXEC CICS RECEIVE INTO(WS-TARGET171) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET171) END-EXEC.

       TRANSFER-SAFE12.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER181.
           EXEC CICS RECEIVE INTO(WS-TARGET181) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET181) END-EXEC.

       FORMAT-HEADER154.
           MOVE 'MONTHLY REPORT' TO WS-TITLE154.
           STRING WS-TITLE154 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER154.
           DISPLAY WS-HEADER154.

       FORMAT-HEADER120.
           MOVE 'MONTHLY REPORT' TO WS-TITLE120.
           STRING WS-TITLE120 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER120.
           DISPLAY WS-HEADER120.

       CHECK-LIMIT57.
           IF WS-AMOUNT57 > 1000
               MOVE 'Y' TO WS-FLAG57
           ELSE
               MOVE 'N' TO WS-FLAG57
           END-IF.

       CHECK-LIMIT50.
           IF WS-AMOUNT50 > 1000
               MOVE 'Y' TO WS-FLAG50
           ELSE
               MOVE 'N' TO WS-FLAG50
           END-IF.

       TRANSFER-SAFE21.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CLASSIFY-CODE41.
           EVALUATE WS-CODE41
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS41
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS41
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS41
           END-EVALUATE.

       CLASSIFY-CODE56.
           EVALUATE WS-CODE56
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS56
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS56
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS56
           END-EVALUATE.

       TRANSFER97.
           EXEC CICS RECEIVE INTO(WS-TARGET97) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET97) END-EXEC.

       CLASSIFY-CODE111.
           EVALUATE WS-CODE111
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS111
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS111
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS111
           END-EVALUATE.

       FORMAT-HEADER68.
           MOVE 'MONTHLY REPORT' TO WS-TITLE68.
           STRING WS-TITLE68 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER68.
           DISPLAY WS-HEADER68.

       CLASSIFY-CODE127.
           EVALUATE WS-CODE127
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS127
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS127
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS127
           END-EVALUATE.

       CHECK-LIMIT79.
           IF WS-AMOUNT79 > 1000
               MOVE 'Y' TO WS-FLAG79
           ELSE
               MOVE 'N' TO WS-FLAG79
           END-IF.

       COMPUTE-TOTALS131.
           MOVE 0 TO WS-TOTAL131.
           PERFORM VARYING WS-K131 FROM 1 BY 1 UNTIL WS-K131 > 10
               ADD WS-K131 TO WS-TOTAL131
           END-PERFORM.
           COMPUTE WS-AVERAGE131 = WS-TOTAL131 / 10.

       LOOKUP-ENTRY161.
           ACCEPT WS-IDX161.
           MOVE WS-ENTRY161(WS-IDX161) TO WS-OUT161.

       LOOKUP-ENTRY70.
           ACCEPT WS-IDX70.
           MOVE WS-ENTRY70(WS-IDX70) TO WS-OUT70.

       TRANSFER20.
           EXEC CICS RECEIVE INTO(WS-TARGET20) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET20) END-EXEC.

       FORMAT-HEADER61.
           MOVE 'MONTHLY REPORT' TO WS-TITLE61.
           STRING WS-TITLE61 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER61.
           DISPLAY WS-HEADER61.

       LOOKUP-ENTRY-SAFE13.
           ACCEPT WS-IDX13.
           IF WS-IDX13 > 0 AND WS-IDX13 NOT > 10
               MOVE WS-ENTRY13(WS-IDX13) TO WS-OUT13
           END-IF.

       LOOKUP-ENTRY-SAFE99.
           ACCEPT WS-IDX99.
           IF WS-IDX99 > 0 AND WS-IDX99 NOT > 10
               MOVE WS-ENTRY99(WS-IDX99) TO WS-OUT99
           END-IF.

       FORMAT-HEADER98.
           MOVE 'MONTHLY REPORT' TO WS-TITLE98.
           STRING WS-TITLE98 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER98.
           DISPLAY WS-HEADER98.

       LOOKUP-ENTRY17.
           ACCEPT WS-IDX17.
           MOVE WS-ENTRY17(WS-IDX17) TO WS-OUT17.

       LOOKUP-ENTRY29.
           ACCEPT WS-IDX29.
           MOVE WS-ENTRY29(WS-IDX29) TO WS-OUT29.

       CHECK-LIMIT178.
           IF WS-AMOUNT178 > 1000
               MOVE 'Y' TO WS-FLAG178
           ELSE
               MOVE 'N' TO WS-FLAG178
           END-IF.

       COMPUTE-TOTALS10.
           MOVE 0 TO WS-TOTAL10.
           PERFORM VARYING WS-K10 FROM 1 BY 1 UNTIL WS-K10 > 10
               ADD WS-K10 TO WS-TOTAL10
           END-PERFORM.
           COMPUTE WS-AVERAGE10 = WS-TOTAL10 / 10.

       TRANSFER168.
           EXEC CICS RECEIVE INTO(WS-TARGET168) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET168) END-EXEC.

       CHECK-LIMIT155.
           IF WS-AMOUNT155 > 1000
               MOVE 'Y' TO WS-FLAG155
           ELSE
               MOVE 'N' TO WS-FLAG155
           END-IF.

       FORMAT-HEADER76.
           MOVE 'MONTHLY REPORT' TO WS-TITLE76.
           STRING WS-TITLE76 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER76.
           DISPLAY WS-HEADER76.

       FORMAT-HEADER138.
           MOVE 'MONTHLY REPORT' TO WS-TITLE138.
           STRING WS-TITLE138 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER138.
           DISPLAY WS-HEADER138.

       TRANSFER-SAFE184.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       FORMAT-HEADER52.
           MOVE 'MONTHLY REPORT' TO WS-TITLE52.
           STRING WS-TITLE52 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER52.
           DISPLAY WS-HEADER52.

       COMPUTE-TOTALS116.
           MOVE 0 TO WS-TOTAL116.
           PERFORM VARYING WS-K116 FROM 1 BY 1 UNTIL WS-K116 > 10
               ADD WS-K116 TO WS-TOTAL116
           END-PERFORM.
           COMPUTE WS-AVERAGE116 = WS-TOTAL116 / 10.

       CLASSIFY-CODE7.
           EVALUATE WS-CODE7
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS7
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS7
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS7
           END-EVALUATE.

       TRANSFER-SAFE114.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY-SAFE51.
           ACCEPT WS-IDX51.
           IF WS-IDX51 > 0 AND WS-IDX51 NOT > 10
               MOVE WS-ENTRY51(WS-IDX51) TO WS-OUT51
           END-IF.

       CLASSIFY-CODE92.
           EVALUATE WS-CODE92
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS92
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS92
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS92
           END-EVALUATE.

       LOOKUP-ENTRY-SAFE48.
           ACCEPT WS-IDX48.
           IF WS-IDX48 > 0 AND WS-IDX48 NOT > 10
               MOVE WS-ENTRY48(WS-IDX48) TO WS-OUT48
           END-IF.

       CLASSIFY-CODE66.
           EVALUATE WS-CODE66
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS66
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS66
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS66
           END-EVALUATE.

       TRANSFER-SAFE67.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY123.
           ACCEPT WS-IDX123.
           MOVE WS-ENTRY123(WS-IDX123) TO WS-OUT123.

       LOOKUP-ENTRY5.
           ACCEPT WS-IDX5.
           MOVE WS-ENTRY5(WS-IDX5) TO WS-OUT5.

       COMPUTE-TOTALS150.
           MOVE 0 TO WS-TOTAL150.
           PERFORM VARYING WS-K150 FROM 1 BY 1 UNTIL WS-K150 > 10
               ADD WS-K150 TO WS-TOTAL150
           END-PERFORM.
           COMPUTE WS-AVERAGE150 = WS-TOTAL150 / 10.

       CHECK-LIMIT15.
           IF WS-AMOUNT15 > 1000
               MOVE 'Y' TO WS-FLAG15
           ELSE
               MOVE 'N' TO WS-FLAG15
           END-IF.

       FORMAT-HEADER22.
           MOVE 'MONTHLY REPORT' TO WS-TITLE22.
           STRING WS-TITLE22 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER22.
           DISPLAY WS-HEADER22.

       COMPUTE-TOTALS78.
           MOVE 0 TO WS-TOTAL78.
           PERFORM VARYING WS-K78 FROM 1 BY 1 UNTIL WS-K78 > 10
               ADD WS-K78 TO WS-TOTAL78
           END-PERFORM.
           COMPUTE WS-AVERAGE78 = WS-TOTAL78 / 10.

       CLASSIFY-CODE122.
           EVALUATE WS-CODE122
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS122
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS122
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS122
           END-EVALUATE.

       CHECK-LIMIT121.
           IF WS-AMOUNT121 > 1000
               MOVE 'Y' TO WS-FLAG121
           ELSE
               MOVE 'N' TO WS-FLAG121
           END-IF.

       LOOKUP-ENTRY-SAFE62.
           ACCEPT WS-IDX62.
           IF WS-IDX62 > 0 AND WS-IDX62 NOT > 10
               MOVE WS-ENTRY62(WS-IDX62) TO WS-OUT62
           END-IF.

       CHECK-LIMIT88.
           IF WS-AMOUNT88 > 1000
               MOVE 'Y' TO WS-FLAG88
           ELSE
               MOVE 'N' TO WS-FLAG88
           END-IF.

       TRANSFER-SAFE72.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY63.
           ACCEPT WS-IDX63.
           MOVE WS-ENTRY63(WS-IDX63) TO WS-OUT63.

       TRANSFER-SAFE60.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER166.
           EXEC CICS RECEIVE INTO(WS-TARGET166) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET166) END-EXEC.

       TRANSFER3.
           EXEC CICS RECEIVE INTO(WS-TARGET3) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET3) END-EXEC.

       LOOKUP-ENTRY172.
           ACCEPT WS-IDX172.
           MOVE WS-ENTRY172(WS-IDX172) TO WS-OUT172.

       TRANSFER-SAFE124.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       COMPUTE-TOTALS31.
           MOVE 0 TO WS-TOTAL31.
           PERFORM VARYING WS-K31 FROM 1 BY 1 UNTIL WS-K31 > 10
               ADD WS-K31 TO WS-TOTAL31
           END-PERFORM.
           COMPUTE WS-AVERAGE31 = WS-TOTAL31 / 10.

       TRANSFER112.
           EXEC CICS RECEIVE INTO(WS-TARGET112) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET112) END-EXEC.

       CLASSIFY-CODE170.
           EVALUATE WS-CODE170
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS170
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS170
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS170
           END-EVALUATE.

       CHECK-LIMIT23.
           IF WS-AMOUNT23 > 1000
               MOVE 'Y' TO WS-FLAG23
           ELSE
               MOVE 'N' TO WS-FLAG23
           END-IF.

       LOOKUP-ENTRY176.
           ACCEPT WS-IDX176.
           MOVE WS-ENTRY176(WS-IDX176) TO WS-OUT176.

       COMPUTE-TOTALS136.
           MOVE 0 TO WS-TOTAL136.
           PERFORM VARYING WS-K136 FROM 1 BY 1 UNTIL WS-K136 > 10
               ADD WS-K136 TO WS-TOTAL136
           END-PERFORM.
           COMPUTE WS-AVERAGE136 = WS-TOTAL136 / 10.

       CLASSIFY-CODE152.
           EVALUATE WS-CODE152
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS152
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS152
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS152
           END-EVALUATE.

       CHECK-LIMIT64.
           IF WS-AMOUNT64 > 1000
               MOVE 'Y' TO WS-FLAG64
           ELSE
               MOVE 'N' TO WS-FLAG64
           END-IF.

       CHECK-LIMIT58.
           IF WS-AMOUNT58 > 1000
               MOVE 'Y' TO WS-FLAG58
           ELSE
               MOVE 'N' TO WS-FLAG58
           END-IF.

       TRANSFER-SAFE45.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER42.
           EXEC CICS RECEIVE INTO(WS-TARGET42) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET42) END-EXEC.

       COMPUTE-TOTALS180.
           MOVE 0 TO WS-TOTAL180.
           PERFORM VARYING WS-K180 FROM 1 BY 1 UNTIL WS-K180 > 10
               ADD WS-K180 TO WS-TOTAL180
           END-PERFORM.
           COMPUTE WS-AVERAGE180 = WS-TOTAL180 / 10.

       TRANSFER132.
           EXEC CICS RECEIVE INTO(WS-TARGET132) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET132) END-EXEC.

       CHECK-LIMIT26.
           IF WS-AMOUNT26 > 1000
               MOVE 'Y' TO WS-FLAG26
           ELSE
               MOVE 'N' TO WS-FLAG26
           END-IF.

       COMPUTE-TOTALS59.
           MOVE 0 TO WS-TOTAL59.
           PERFORM VARYING WS-K59 FROM 1 BY 1 UNTIL WS-K59 > 10
               ADD WS-K59 TO WS-TOTAL59
           END-PERFORM.
           COMPUTE WS-AVERAGE59 = WS-TOTAL59 / 10.

       CHECK-LIMIT37.
           IF WS-AMOUNT37 > 1000
               MOVE 'Y' TO WS-FLAG37
           ELSE
               MOVE 'N' TO WS-FLAG37
           END-IF.

       COMPUTE-TOTALS101.
           MOVE 0 TO WS-TOTAL101.
           PERFORM VARYING WS-K101 FROM 1 BY 1 UNTIL WS-K101 > 10
               ADD WS-K101 TO WS-TOTAL101
           END-PERFORM.
           COMPUTE WS-AVERAGE101 = WS-TOTAL101 / 10.

       TRANSFER-SAFE110.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       LOOKUP-ENTRY-SAFE173.
           ACCEPT WS-IDX173.
           IF WS-IDX173 > 0 AND WS-IDX173 NOT > 10
               MOVE WS-ENTRY173(WS-IDX173) TO WS-OUT173
           END-IF.

       TRANSFER-SAFE96.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER-SAFE87.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       TRANSFER49.
           EXEC CICS RECEIVE INTO(WS-TARGET49) END-EXEC.
           EXEC CICS XCTL PROGRAM(WS-TARGET49) END-EXEC.

       LOOKUP-ENTRY-SAFE164.
           ACCEPT WS-IDX164.
           IF WS-IDX164 > 0 AND WS-IDX164 NOT > 10
               MOVE WS-ENTRY164(WS-IDX164) TO WS-OUT164
           END-IF.

       LOOKUP-ENTRY-SAFE14.
           ACCEPT WS-IDX14.
           IF WS-IDX14 > 0 AND WS-IDX14 NOT > 10
               MOVE WS-ENTRY14(WS-IDX14) TO WS-OUT14
           END-IF.

       LOOKUP-ENTRY119.
           ACCEPT WS-IDX119.
           MOVE WS-ENTRY119(WS-IDX119) TO WS-OUT119.

       LOOKUP-ENTRY183.
           ACCEPT WS-IDX183.
           MOVE WS-ENTRY183(WS-IDX183) TO WS-OUT183.

       LOOKUP-ENTRY-SAFE153.
           ACCEPT WS-IDX153.
           IF WS-IDX153 > 0 AND WS-IDX153 NOT > 10
               MOVE WS-ENTRY153(WS-IDX153) TO WS-OUT153
           END-IF.

       TRANSFER-SAFE104.
           EXEC CICS XCTL PROGRAM('MENU01') END-EXEC.

       CHECK-LIMIT126.
           IF WS-AMOUNT126 > 1000
               MOVE 'Y' TO WS-FLAG126
           ELSE
               MOVE 'N' TO WS-FLAG126
           END-IF.

       LOOKUP-ENTRY-SAFE151.
           ACCEPT WS-IDX151.
           IF WS-IDX151 > 0 AND WS-IDX151 NOT > 10
               MOVE WS-ENTRY151(WS-IDX151) TO WS-OUT151
           END-IF.

