       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTR03.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EXPORT-FILE26 ASSIGN TO DYNAMIC WS-EXPORT-PATH26
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE37 ASSIGN TO DYNAMIC WS-EXPORT-PATH37
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE43 ASSIGN TO DYNAMIC WS-EXPORT-PATH43
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE44 ASSIGN TO DYNAMIC WS-EXPORT-PATH44
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE45 ASSIGN TO DYNAMIC WS-EXPORT-PATH45
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE53 ASSIGN TO DYNAMIC WS-EXPORT-PATH53
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE82 ASSIGN TO DYNAMIC WS-EXPORT-PATH82
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE90 ASSIGN TO DYNAMIC WS-EXPORT-PATH90
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE93 ASSIGN TO DYNAMIC WS-EXPORT-PATH93
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE114 ASSIGN TO DYNAMIC WS-EXPORT-PATH114
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE122 ASSIGN TO DYNAMIC WS-EXPORT-PATH122
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE137 ASSIGN TO DYNAMIC WS-EXPORT-PATH137
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE147 ASSIGN TO DYNAMIC WS-EXPORT-PATH147
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE150 ASSIGN TO DYNAMIC WS-EXPORT-PATH150
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE160 ASSIGN TO DYNAMIC WS-EXPORT-PATH160
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE164 ASSIGN TO DYNAMIC WS-EXPORT-PATH164
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE171 ASSIGN TO DYNAMIC WS-EXPORT-PATH171
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE183 ASSIGN TO DYNAMIC WS-EXPORT-PATH183
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  EXPORT-FILE26.
       01  EXPORT-LINE26         PIC X(80).
       FD  EXPORT-FILE37.
       01  EXPORT-LINE37         PIC X(80).
       FD  EXPORT-FILE43.
       01  EXPORT-LINE43         PIC X(80).
       FD  EXPORT-FILE44.
       01  EXPORT-LINE44         PIC X(80).
       FD  EXPORT-FILE45.
       01  EXPORT-LINE45         PIC X(80).
       FD  EXPORT-FILE53.
       01  EXPORT-LINE53         PIC X(80).
       FD  EXPORT-FILE82.
       01  EXPORT-LINE82         PIC X(80).
       FD  EXPORT-FILE90.
       01  EXPORT-LINE90         PIC X(80).
       FD  EXPORT-FILE93.
       01  EXPORT-LINE93         PIC X(80).
       FD  EXPORT-FILE114.
       01  EXPORT-LINE114         PIC X(80).
       FD  EXPORT-FILE122.
       01  EXPORT-LINE122         PIC X(80).
       FD  EXPORT-FILE137.
       01  EXPORT-LINE137         PIC X(80).
       FD  EXPORT-FILE147.
       01  EXPORT-LINE147         PIC X(80).
       FD  EXPORT-FILE150.
       01  EXPORT-LINE150         PIC X(80).
       FD  EXPORT-FILE160.
       01  EXPORT-LINE160         PIC X(80).
       FD  EXPORT-FILE164.
       01  EXPORT-LINE164         PIC X(80).
       FD  EXPORT-FILE171.
       01  EXPORT-LINE171         PIC X(80).
       FD  EXPORT-FILE183.
       01  EXPORT-LINE183         PIC X(80).
       WORKING-STORAGE SECTION.
       01  WS-DB-PASSWORD1    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW1        PIC X(12).
       01  WS-USER3           PIC X(10).
       01  WS-PASSWORD-IN3    PIC X(12).
       01  WS-FORM4           PIC X(40).
       01  WS-PAGE4           PIC X(80).
       01  WS-USER8           PIC X(10).
       01  WS-PASSWORD-IN8    PIC X(12).
       01  WS-STMT10           PIC X(200).
       01  WS-USER12           PIC X(10).
       01  WS-PASSWORD-IN12    PIC X(12).
       01  WS-POS13            PIC 99.
       01  WS-RECORD13         PIC X(80).
       01  WS-PART13           PIC X(5).
       01  WS-DB-PASSWORD14    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW14        PIC X(12).
       01  WS-POS16            PIC 99.
       01  WS-RECORD16         PIC X(80).
       01  WS-PART16           PIC X(5).
       01  WS-DB-PASSWORD17    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW17        PIC X(12).
       01  WS-POS18            PIC 99.
       01  WS-RECORD18         PIC X(80).
       01  WS-PART18           PIC X(5).
       01  WS-DB-PASSWORD20    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW20        PIC X(12).
       01  WS-FORM21           PIC X(40).
       01  WS-PAGE21           PIC X(80).
       01  WS-STMT22           PIC X(200).
       01  WS-POS23            PIC 99.
       01  WS-RECORD23         PIC X(80).
       01  WS-PART23           PIC X(5).
       01  WS-POS24            PIC 99.
       01  WS-RECORD24         PIC X(80).
       01  WS-PART24           PIC X(5).
       01  WS-USER25           PIC X(10).
       01  WS-PASSWORD-IN25    PIC X(12).
       01  WS-EXPORT-PATH26    PIC X(60).
       01  WS-FORM27           PIC X(40).
       01  WS-PAGE27           PIC X(80).
       01  WS-FORM31           PIC X(40).
       01  WS-PAGE31           PIC X(80).
       01  WS-USER32           PIC X(10).
       01  WS-PASSWORD-IN32    PIC X(12).
       01  WS-STMT35           PIC X(200).
       01  WS-EXPORT-PATH37    PIC X(60).
       01  WS-USER39           PIC X(10).
       01  WS-PASSWORD-IN39    PIC X(12).
       01  WS-DB-PASSWORD41    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW41        PIC X(12).
       01  WS-EXPORT-PATH43    PIC X(60).
       01  WS-EXPORT-PATH44    PIC X(60).
       01  WS-EXPORT-PATH45    PIC X(60).
       01  WS-DB-PASSWORD47    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW47        PIC X(12).
       01  WS-FORM52           PIC X(40).
       01  WS-PAGE52           PIC X(80).
       01  WS-EXPORT-PATH53    PIC X(60).
       01  WS-POS55            PIC 99.
       01  WS-RECORD55         PIC X(80).
       01  WS-PART55           PIC X(5).
       01  WS-DB-PASSWORD56    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW56        PIC X(12).
       01  WS-POS57            PIC 99.
       01  WS-RECORD57         PIC X(80).
       01  WS-PART57           PIC X(5).
       01  WS-CMD58            PIC X(100).
       01  WS-FORM59           PIC X(40).
       01  WS-PAGE59           PIC X(80).
       01  WS-POS60            PIC 99.
       01  WS-RECORD60         PIC X(80).
       01  WS-PART60           PIC X(5).
       01  WS-USER61           PIC X(10).
       01  WS-PASSWORD-IN61    PIC X(12).
       01  WS-FORM62           PIC X(40).
       01  WS-PAGE62           PIC X(80).
       01  WS-STMT65           PIC X(200).
       01  WS-DB-PASSWORD68    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW68        PIC X(12).
       01  WS-POS72            PIC 99.
       01  WS-RECORD72         PIC X(80).
       01  WS-PART72           PIC X(5).
       01  WS-USER73           PIC X(10).
       01  WS-PASSWORD-IN73    PIC X(12).
       01  WS-POS74            PIC 99.
       01  WS-RECORD74         PIC X(80).
       01  WS-PART74           PIC X(5).
       01  WS-CMD75            PIC X(100).
       01  WS-DB-PASSWORD76    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW76        PIC X(12).
       01  WS-DB-PASSWORD78    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW78        PIC X(12).
       01  WS-CMD79            PIC X(100).
       01  WS-FORM81           PIC X(40).
       01  WS-PAGE81           PIC X(80).
       01  WS-EXPORT-PATH82    PIC X(60).
       01  WS-POS84            PIC 99.
       01  WS-RECORD84         PIC X(80).
       01  WS-PART84           PIC X(5).
       01  WS-FORM86           PIC X(40).
       01  WS-PAGE86           PIC X(80).
       01  WS-STMT87           PIC X(200).
       01  WS-DB-PASSWORD88    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW88        PIC X(12).
       01  WS-DB-PASSWORD89    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW89        PIC X(12).
       01  WS-EXPORT-PATH90    PIC X(60).
       01  WS-STMT92           PIC X(200).
       01  WS-EXPORT-PATH93    PIC X(60).
       01  WS-USER95           PIC X(10).
       01  WS-PASSWORD-IN95    PIC X(12).
       01  WS-POS96            PIC 99.
       01  WS-RECORD96         PIC X(80).
       01  WS-PART96           PIC X(5).
       01  WS-DB-PASSWORD98    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW98        PIC X(12).
       01  WS-CMD101            PIC X(100).
       01  WS-POS102            PIC 99.
       01  WS-RECORD102         PIC X(80).
       01  WS-PART102           PIC X(5).
       01  WS-FORM105           PIC X(40).
       01  WS-PAGE105           PIC X(80).
       01  WS-DB-PASSWORD106    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW106        PIC X(12).
       01  WS-USER107           PIC X(10).
       01  WS-PASSWORD-IN107    PIC X(12).
       01  WS-STMT108           PIC X(200).
       01  WS-FORM111           PIC X(40).
       01  WS-PAGE111           PIC X(80).
       01  WS-FORM112           PIC X(40).
       01  WS-PAGE112           PIC X(80).
       01  WS-USER113           PIC X(10).
       01  WS-PASSWORD-IN113    PIC X(12).
       01  WS-EXPORT-PATH114    PIC X(60).
       01  WS-USER116           PIC X(10).
       01  WS-PASSWORD-IN116    PIC X(12).
       01  WS-USER117           PIC X(10).
       01  WS-PASSWORD-IN117    PIC X(12).
       01  WS-DB-PASSWORD118    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW118        PIC X(12).
       01  WS-POS119            PIC 99.
       01  WS-RECORD119         PIC X(80).
       01  WS-PART119           PIC X(5).
       01  WS-STMT120           PIC X(200).
       01  WS-STMT121           PIC X(200).
       01  WS-EXPORT-PATH122    PIC X(60).
       01  WS-DB-PASSWORD123    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW123        PIC X(12).
       01  WS-CMD124            PIC X(100).
       01  WS-POS127            PIC 99.
       01  WS-RECORD127         PIC X(80).
       01  WS-PART127           PIC X(5).
       01  WS-DB-PASSWORD128    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW128        PIC X(12).
       01  WS-DB-PASSWORD129    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW129        PIC X(12).
       01  WS-CMD130            PIC X(100).
       01  WS-USER131           PIC X(10).
       01  WS-PASSWORD-IN131    PIC X(12).
       01  WS-DB-PASSWORD134    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW134        PIC X(12).
       01  WS-POS135            PIC 99.
       01  WS-RECORD135         PIC X(80).
       01  WS-PART135           PIC X(5).
       01  WS-POS136            PIC 99.
       01  WS-RECORD136         PIC X(80).
       01  WS-PART136           PIC X(5).
       01  WS-EXPORT-PATH137    PIC X(60).
       01  WS-STMT142           PIC X(200).
       01  WS-POS144            PIC 99.
       01  WS-RECORD144         PIC X(80).
       01  WS-PART144           PIC X(5).
       01  WS-CMD145            PIC X(100).
       01  WS-EXPORT-PATH147    PIC X(60).
       01  WS-FORM148           PIC X(40).
       01  WS-PAGE148           PIC X(80).
       01  WS-CMD149            PIC X(100).
       01  WS-EXPORT-PATH150    PIC X(60).
       01  WS-POS152            PIC 99.
       01  WS-RECORD152         PIC X(80).
       01  WS-PART152           PIC X(5).
       01  WS-CMD153            PIC X(100).
       01  WS-DB-PASSWORD154    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW154        PIC X(12).
       01  WS-USER156           PIC X(10).
       01  WS-PASSWORD-IN156    PIC X(12).
       01  WS-CMD157            PIC X(100).
       01  WS-POS158            PIC 99.
       01  WS-RECORD158         PIC X(80).
       01  WS-PART158           PIC X(5).
       01  WS-FORM159           PIC X(40).
       01  WS-PAGE159           PIC X(80).
       01  WS-EXPORT-PATH160    PIC X(60).
       01  WS-USER161           PIC X(10).
       01  WS-PASSWORD-IN161    PIC X(12).
       01  WS-FORM163           PIC X(40).
       01  WS-PAGE163           PIC X(80).
       01  WS-EXPORT-PATH164    PIC X(60).
       01  WS-DB-PASSWORD167    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW167        PIC X(12).
       01  WS-POS168            PIC 99.
       01  WS-RECORD168         PIC X(80).
       01  WS-PART168           PIC X(5).
       01  WS-EXPORT-PATH171    PIC X(60).
       01  WS-STMT173           PIC X(200).
       01  WS-STMT174           PIC X(200).
       01  WS-FORM177           PIC X(40).
       01  WS-PAGE177           PIC X(80).
       01  WS-CMD178            PIC X(100).
       01  WS-STMT179           PIC X(200).
       01  WS-USER180           PIC X(10).
       01  WS-PASSWORD-IN180    PIC X(12).
       01  WS-USER181           PIC X(10).
       01  WS-PASSWORD-IN181    PIC X(12).
       01  WS-EXPORT-PATH183    PIC X(60).
       01  WS-POS184            PIC 99.
       01  WS-RECORD184         PIC X(80).
       01  WS-PART184           PIC X(5).
       01  WS-STMT188           PIC X(200).
       01  WS-TITLE2          PIC X(20) VALUE SPACES.
       01  WS-HEADER2         PIC X(40) VALUE SPACES.
       01  WS-TOTAL5          PIC 9(6) VALUE 0.
       01  WS-K5              PIC 99 VALUE 0.
       01  WS-AVERAGE5        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE6          PIC X(20) VALUE SPACES.
       01  WS-HEADER6         PIC X(40) VALUE SPACES.
       01  WS-TOTAL7          PIC 9(6) VALUE 0.
       01  WS-K7              PIC 99 VALUE 0.
       01  WS-AVERAGE7        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE9          PIC X(20) VALUE SPACES.
       01  WS-HEADER9         PIC X(40) VALUE SPACES.
       01  WS-CODE11           PIC 9 VALUE 1.
       01  WS-STATUS11         PIC X(6) VALUE SPACES.
       01  WS-TITLE15          PIC X(20) VALUE SPACES.
       01  WS-HEADER15         PIC X(40) VALUE SPACES.
       01  WS-TITLE19          PIC X(20) VALUE SPACES.
       01  WS-HEADER19         PIC X(40) VALUE SPACES.
       01  WS-TITLE28          PIC X(20) VALUE SPACES.
       01  WS-HEADER28         PIC X(40) VALUE SPACES.
       01  WS-TOTAL29          PIC 9(6) VALUE 0.
       01  WS-K29              PIC 99 VALUE 0.
       01  WS-AVERAGE29        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL30          PIC 9(6) VALUE 0.
       01  WS-K30              PIC 99 VALUE 0.
       01  WS-AVERAGE30        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE33          PIC X(20) VALUE SPACES.
       01  WS-HEADER33         PIC X(40) VALUE SPACES.
       01  WS-TITLE34          PIC X(20) VALUE SPACES.
       01  WS-HEADER34         PIC X(40) VALUE SPACES.
       01  WS-TITLE36          PIC X(20) VALUE SPACES.
       01  WS-HEADER36         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT38         PIC 9(6) VALUE 500.
       01  WS-FLAG38           PIC X VALUE 'N'.
       01  WS-AMOUNT40         PIC 9(6) VALUE 500.
       01  WS-FLAG40           PIC X VALUE 'N'.
       01  WS-CODE42           PIC 9 VALUE 1.
       01  WS-STATUS42         PIC X(6) VALUE SPACES.
       01  WS-TITLE46          PIC X(20) VALUE SPACES.
       01  WS-HEADER46         PIC X(40) VALUE SPACES.
       01  WS-TOTAL48          PIC 9(6) VALUE 0.
       01  WS-K48              PIC 99 VALUE 0.
       01  WS-AVERAGE48        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL49          PIC 9(6) VALUE 0.
       01  WS-K49              PIC 99 VALUE 0.
       01  WS-AVERAGE49        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT50         PIC 9(6) VALUE 500.
       01  WS-FLAG50           PIC X VALUE 'N'.
       01  WS-CODE51           PIC 9 VALUE 1.
       01  WS-STATUS51         PIC X(6) VALUE SPACES.
       01  WS-CODE54           PIC 9 VALUE 1.
       01  WS-STATUS54         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT63         PIC 9(6) VALUE 500.
       01  WS-FLAG63           PIC X VALUE 'N'.
       01  WS-TITLE64          PIC X(20) VALUE SPACES.
       01  WS-HEADER64         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT66         PIC 9(6) VALUE 500.
       01  WS-FLAG66           PIC X VALUE 'N'.
       01  WS-TOTAL67          PIC 9(6) VALUE 0.
       01  WS-K67              PIC 99 VALUE 0.
       01  WS-AVERAGE67        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL69          PIC 9(6) VALUE 0.
       01  WS-K69              PIC 99 VALUE 0.
       01  WS-AVERAGE69        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT70         PIC 9(6) VALUE 500.
       01  WS-FLAG70           PIC X VALUE 'N'.
       01  WS-TOTAL71          PIC 9(6) VALUE 0.
       01  WS-K71              PIC 99 VALUE 0.
       01  WS-AVERAGE71        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT77         PIC 9(6) VALUE 500.
       01  WS-FLAG77           PIC X VALUE 'N'.
       01  WS-AMOUNT80         PIC 9(6) VALUE 500.
       01  WS-FLAG80           PIC X VALUE 'N'.
       01  WS-AMOUNT83         PIC 9(6) VALUE 500.
       01  WS-FLAG83           PIC X VALUE 'N'.
       01  WS-TITLE85          PIC X(20) VALUE SPACES.
       01  WS-HEADER85         PIC X(40) VALUE SPACES.
       01  WS-TITLE91          PIC X(20) VALUE SPACES.
       01  WS-HEADER91         PIC X(40) VALUE SPACES.
       01  WS-TOTAL94          PIC 9(6) VALUE 0.
       01  WS-K94              PIC 99 VALUE 0.
       01  WS-AVERAGE94        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE97          PIC X(20) VALUE SPACES.
       01  WS-HEADER97         PIC X(40) VALUE SPACES.
       01  WS-TITLE99          PIC X(20) VALUE SPACES.
       01  WS-HEADER99         PIC X(40) VALUE SPACES.
       01  WS-TOTAL100          PIC 9(6) VALUE 0.
       01  WS-K100              PIC 99 VALUE 0.
       01  WS-AVERAGE100        PIC 9(6)V99 VALUE 0.
       01  WS-CODE103           PIC 9 VALUE 1.
       01  WS-STATUS103         PIC X(6) VALUE SPACES.
       01  WS-TITLE104          PIC X(20) VALUE SPACES.
       01  WS-HEADER104         PIC X(40) VALUE SPACES.
       01  WS-TITLE109          PIC X(20) VALUE SPACES.
       01  WS-HEADER109         PIC X(40) VALUE SPACES.
       01  WS-CODE110           PIC 9 VALUE 1.
       01  WS-STATUS110         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT115         PIC 9(6) VALUE 500.
       01  WS-FLAG115           PIC X VALUE 'N'.
       01  WS-AMOUNT125         PIC 9(6) VALUE 500.
       01  WS-FLAG125           PIC X VALUE 'N'.
       01  WS-TOTAL126          PIC 9(6) VALUE 0.
       01  WS-K126              PIC 99 VALUE 0.
       01  WS-AVERAGE126        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL132          PIC 9(6) VALUE 0.
       01  WS-K132              PIC 99 VALUE 0.
       01  WS-AVERAGE132        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT133         PIC 9(6) VALUE 500.
       01  WS-FLAG133           PIC X VALUE 'N'.
       01  WS-TOTAL138          PIC 9(6) VALUE 0.
       01  WS-K138              PIC 99 VALUE 0.
       01  WS-AVERAGE138        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT139         PIC 9(6) VALUE 500.
       01  WS-FLAG139           PIC X VALUE 'N'.
       01  WS-AMOUNT140         PIC 9(6) VALUE 500.
       01  WS-FLAG140           PIC X VALUE 'N'.
       01  WS-TITLE141          PIC X(20) VALUE SPACES.
       01  WS-HEADER141         PIC X(40) VALUE SPACES.
       01  WS-TITLE143          PIC X(20) VALUE SPACES.
       01  WS-HEADER143         PIC X(40) VALUE SPACES.
       01  WS-TITLE146          PIC X(20) VALUE SPACES.
       01  WS-HEADER146         PIC X(40) VALUE SPACES.
       01  WS-TOTAL151          PIC 9(6) VALUE 0.
       01  WS-K151              PIC 99 VALUE 0.
       01  WS-AVERAGE151        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE155          PIC X(20) VALUE SPACES.
       01  WS-HEADER155         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT162         PIC 9(6) VALUE 500.
       01  WS-FLAG162           PIC X VALUE 'N'.
       01  WS-CODE165           PIC 9 VALUE 1.
       01  WS-STATUS165         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT166         PIC 9(6) VALUE 500.
       01  WS-FLAG166           PIC X VALUE 'N'.
       01  WS-TITLE169          PIC X(20) VALUE SPACES.
       01  WS-HEADER169         PIC X(40) VALUE SPACES.
       01  WS-CODE170           PIC 9 VALUE 1.
       01  WS-STATUS170         PIC X(6) VALUE SPACES.
       01  WS-CODE172           PIC 9 VALUE 1.
       01  WS-STATUS172         PIC X(6) VALUE SPACES.
       01  WS-TITLE175          PIC X(20) VALUE SPACES.
       01  WS-HEADER175         PIC X(40) VALUE SPACES.
       01  WS-TITLE176          PIC X(20) VALUE SPACES.
       01  WS-HEADER176         PIC X(40) VALUE SPACES.
       01  WS-CODE182           PIC 9 VALUE 1.
       01  WS-STATUS182         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT185         PIC 9(6) VALUE 500.
       01  WS-FLAG185           PIC X VALUE 'N'.
       01  WS-CODE186           PIC 9 VALUE 1.
       01  WS-STATUS186         PIC X(6) VALUE SPACES.
       01  WS-TOTAL187          PIC 9(6) VALUE 0.
       01  WS-K187              PIC 99 VALUE 0.
       01  WS-AVERAGE187        PIC 9(6)V99 VALUE 0.
       01  WS-CODE189           PIC 9 VALUE 1.
       01  WS-STATUS189         PIC X(6) VALUE SPACES.
       LINKAGE SECTION.
       01  LK-FILTER10         PIC X(100).
       01  LK-FILTER22         PIC X(100).
       01  LK-PATH26           PIC X(60).
       01  LK-FILTER35         PIC X(100).
       01  LK-PATH37           PIC X(60).
       01  LK-PATH43           PIC X(60).
       01  LK-PATH44           PIC X(60).
       01  LK-PATH45           PIC X(60).
       01  LK-PATH53           PIC X(60).
       01  LK-NAME58           PIC X(40).
       01  LK-FILTER65         PIC X(100).
       01  LK-NAME75           PIC X(40).
       01  LK-NAME79           PIC X(40).
       01  LK-PATH82           PIC X(60).
       01  LK-FILTER87         PIC X(100).
       01  LK-PATH90           PIC X(60).
       01  LK-FILTER92         PIC X(100).
       01  LK-PATH93           PIC X(60).
       01  LK-NAME101           PIC X(40).
       01  LK-FILTER108         PIC X(100).
       01  LK-PATH114           PIC X(60).
       01  LK-FILTER120         PIC X(100).
       01  LK-FILTER121         PIC X(100).
       01  LK-PATH122           PIC X(60).
       01  LK-NAME124           PIC X(40).
       01  LK-NAME130           PIC X(40).
       01  LK-PATH137           PIC X(60).
       01  LK-FILTER142         PIC X(100).
       01  LK-NAME145           PIC X(40).
       01  LK-PATH147           PIC X(60).
       01  LK-NAME149           PIC X(40).
       01  LK-PATH150           PIC X(60).
       01  LK-NAME153           PIC X(40).
       01  LK-NAME157           PIC X(40).
       01  LK-PATH160           PIC X(60).
       01  LK-PATH164           PIC X(60).
       01  LK-PATH171           PIC X(60).
       01  LK-FILTER173         PIC X(100).
       01  LK-FILTER174         PIC X(100).
       01  LK-NAME178           PIC X(40).
       01  LK-FILTER179         PIC X(100).
       01  LK-PATH183           PIC X(60).
       01  LK-FILTER188         PIC X(100).
       PROCEDURE DIVISION USING LK-FILTER10 LK-FILTER22 LK-PATH26 LK-FILTER35 LK-PATH37 LK-PATH43 LK-PATH44 LK-PATH45 LK-PATH53 LK-NAME58 LK-FILTER65 LK-NAME75 LK-NAME79 LK-PATH82 LK-FILTER87 LK-PATH90 LK-FILTER92 LK-PATH93 LK-NAME101 LK-FILTER108 LK-PATH114 LK-FILTER120 LK-FILTER121 LK-PATH122 LK-NAME124 LK-NAME130 LK-PATH137 LK-FILTER142 LK-NAME145 LK-PATH147 LK-NAME149 LK-PATH150 LK-NAME153 LK-NAME157 LK-PATH160 LK-PATH164 LK-PATH171 LK-FILTER173 LK-FILTER174 LK-NAME178 LK-FILTER179 LK-PATH183 LK-FILTER188.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       PREPARE-QUERY173.
           MOVE LK-FILTER173 TO WS-STMT173.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT173 END-EXEC.

       PREPARE-QUERY-SAFE22.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT22.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT22 END-EXEC.

       CLASSIFY-CODE182.
           EVALUATE WS-CODE182
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS182
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS182
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS182
           END-EVALUATE.

       CLASSIFY-CODE172.
           EVALUATE WS-CODE172
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS172
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS172
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS172
           END-EVALUATE.

       LOG-LOGIN-SAFE25.
           DISPLAY 'LOGIN ' WS-USER25.

       CHECK-LIMIT40.
           IF WS-AMOUNT40 > 1000
               MOVE 'Y' TO WS-FLAG40
           ELSE
               MOVE 'N' TO WS-FLAG40
           END-IF.

       PREPARE-QUERY92.
           MOVE LK-FILTER92 TO WS-STMT92.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT92 END-EXEC.

       CONNECT-DB-SAFE167.
           ACCEPT WS-CONN-PW167 FROM ENVIRONMENT 'DB_PASSWORD'.

       COMPUTE-TOTALS29.
           MOVE 0 TO WS-TOTAL29.
           PERFORM VARYING WS-K29 FROM 1 BY 1 UNTIL WS-K29 > 10
               ADD WS-K29 TO WS-TOTAL29
           END-PERFORM.
           COMPUTE WS-AVERAGE29 = WS-TOTAL29 / 10.

       CHECK-LIMIT50.
           IF WS-AMOUNT50 > 1000
               MOVE 'Y' TO WS-FLAG50
           ELSE
               MOVE 'N' TO WS-FLAG50
           END-IF.

       EXTRACT-FIELD-SAFE72.
           ACCEPT WS-POS72.
           IF WS-POS72 IS NUMERIC AND WS-POS72 > 0 AND WS-POS72 < 76
               MOVE WS-RECORD72(WS-POS72:5) TO WS-PART72
           END-IF.

       CHECK-LIMIT162.
           IF WS-AMOUNT162 > 1000
               MOVE 'Y' TO WS-FLAG162
           ELSE
               MOVE 'N' TO WS-FLAG162
           END-IF.

       EXTRACT-FIELD-SAFE24.
           ACCEPT WS-POS24.
           IF WS-POS24 IS NUMERIC AND WS-POS24 > 0 AND WS-POS24 < 76
               MOVE WS-RECORD24(WS-POS24:5) TO WS-PART24
           END-IF.

       CLASSIFY-CODE103.
           EVALUATE WS-CODE103
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS103
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS103
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS103
           END-EVALUATE.

       EXTRACT-FIELD84.
           ACCEPT WS-POS84.
           MOVE WS-RECORD84(WS-POS84:5) TO WS-PART84.

       EXTRACT-FIELD-SAFE127.
           ACCEPT WS-POS127.
           IF WS-POS127 IS NUMERIC AND WS-POS127 > 0 AND WS-POS127 < 76
               MOVE WS-RECORD127(WS-POS127:5) TO WS-PART127
           END-IF.

       CLASSIFY-CODE11.
           EVALUATE WS-CODE11
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS11
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS11
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS11
           END-EVALUATE.

       LOG-LOGIN-SAFE107.
           DISPLAY 'LOGIN ' WS-USER107.

       CLASSIFY-CODE51.
           EVALUATE WS-CODE51
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS51
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS51
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS51
           END-EVALUATE.

       CONVERT-FILE-SAFE75.
           MOVE "convert /srv/in/report.txt" TO WS-CMD75.
           CALL 'SYSTEM' USING WS-CMD75.

       COMPUTE-TOTALS126.
           MOVE 0 TO WS-TOTAL126.
           PERFORM VARYING WS-K126 FROM 1 BY 1 UNTIL WS-K126 > 10
               ADD WS-K126 TO WS-TOTAL126
           END-PERFORM.
           COMPUTE WS-AVERAGE126 = WS-TOTAL126 / 10.

       FORMAT-HEADER6.
           MOVE 'MONTHLY REPORT' TO WS-TITLE6.
           STRING WS-TITLE6 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER6.
           DISPLAY WS-HEADER6.

       CONVERT-FILE-SAFE79.
           MOVE "convert /srv/in/report.txt" TO WS-CMD79.
           CALL 'SYSTEM' USING WS-CMD79.

       EXTRACT-FIELD136.
           ACCEPT WS-POS136.
           MOVE WS-RECORD136(WS-POS136:5) TO WS-PART136.

       CHECK-LIMIT139.
           IF WS-AMOUNT139 > 1000
               MOVE 'Y' TO WS-FLAG139
           ELSE
               MOVE 'N' TO WS-FLAG139
           END-IF.

       FORMAT-HEADER64.
           MOVE 'MONTHLY REPORT' TO WS-TITLE64.
           STRING WS-TITLE64 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER64.
           DISPLAY WS-HEADER64.

       CLASSIFY-CODE170.
           EVALUATE WS-CODE170
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS170
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS170
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS170
           END-EVALUATE.

       WRITE-EXPORT-SAFE45.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH45.
           OPEN OUTPUT EXPORT-FILE45.
           CLOSE EXPORT-FILE45.

       FORMAT-HEADER155.
           MOVE 'MONTHLY REPORT' TO WS-TITLE155.
           STRING WS-TITLE155 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER155.
           DISPLAY WS-HEADER155.

       WRITE-EXPORT-SAFE26.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH26.
           OPEN OUTPUT EXPORT-FILE26.
           CLOSE EXPORT-FILE26.

       CONNECT-DB134.
           MOVE WS-DB-PASSWORD134 TO WS-CONN-PW134.

       COMPUTE-TOTALS30.
           MOVE 0 TO WS-TOTAL30.
           PERFORM VARYING WS-K30 FROM 1 BY 1 UNTIL WS-K30 > 10
               ADD WS-K30 TO WS-TOTAL30
           END-PERFORM.
           COMPUTE WS-AVERAGE30 = WS-TOTAL30 / 10.

       CONNECT-DB-SAFE68.
           ACCEPT WS-CONN-PW68 FROM ENVIRONMENT 'DB_PASSWORD'.

       CLASSIFY-CODE186.
           EVALUATE WS-CODE186
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS186
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS186
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS186
           END-EVALUATE.

       FORMAT-HEADER176.
           MOVE 'MONTHLY REPORT' TO WS-TITLE176.
           STRING WS-TITLE176 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER176.
           DISPLAY WS-HEADER176.

       WRITE-EXPORT-SAFE90.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH90.
           OPEN OUTPUT EXPORT-FILE90.
           CLOSE EXPORT-FILE90.

       CONVERT-FILE130.
           STRING "convert " LK-NAME130 DELIMITED BY SIZE INTO WS-CMD130.
           CALL 'SYSTEM' USING WS-CMD130.

       PREPARE-QUERY120.
           MOVE LK-FILTER120 TO WS-STMT120.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT120 END-EXEC.

       CONVERT-FILE124.
           STRING "convert " LK-NAME124 DELIMITED BY SIZE INTO WS-CMD124.
           CALL 'SYSTEM' USING WS-CMD124.

       PREPARE-QUERY-SAFE65.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT65.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT65 END-EXEC.

       WRITE-EXPORT-SAFE44.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH44.
           OPEN OUTPUT EXPORT-FILE44.
           CLOSE EXPORT-FILE44.

       FORMAT-HEADER109.
           MOVE 'MONTHLY REPORT' TO WS-TITLE109.
           STRING WS-TITLE109 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER109.
           DISPLAY WS-HEADER109.

       ECHO-NAME-SAFE31.
           MOVE '<p>Thank you</p>' TO WS-PAGE31.
           EXEC CICS WEB SEND FROM(WS-PAGE31) END-EXEC.

       EXTRACT-FIELD135.
           ACCEPT WS-POS135.
           MOVE WS-RECORD135(WS-POS135:5) TO WS-PART135.

       ECHO-NAME86.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM86) END-EXEC.
           STRING '<p>' WS-FORM86 '</p>' DELIMITED BY SIZE INTO WS-PAGE86.
           EXEC CICS WEB SEND FROM(WS-PAGE86) END-EXEC.

       WRITE-EXPORT-SAFE164.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH164.
           OPEN OUTPUT EXPORT-FILE164.
           CLOSE EXPORT-FILE164.

       LOG-LOGIN-SAFE131.
           DISPLAY 'LOGIN ' WS-USER131.

       FORMAT-HEADER9.
           MOVE 'MONTHLY REPORT' TO WS-TITLE9.
           STRING WS-TITLE9 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER9.
           DISPLAY WS-HEADER9.

       ECHO-NAME-SAFE148.
           MOVE '<p>Thank you</p>' TO WS-PAGE148.
           EXEC CICS WEB SEND FROM(WS-PAGE148) END-EXEC.

       EXTRACT-FIELD-SAFE16.
           ACCEPT WS-POS16.
           IF WS-POS16 IS NUMERIC AND WS-POS16 > 0 AND WS-POS16 < 76
               MOVE WS-RECORD16(WS-POS16:5) TO WS-PART16
           END-IF.

       CONVERT-FILE-SAFE178.
           MOVE "convert /srv/in/report.txt" TO WS-CMD178.
           CALL 'SYSTEM' USING WS-CMD178.

       FORMAT-HEADER91.
           MOVE 'MONTHLY REPORT' TO WS-TITLE91.
           STRING WS-TITLE91 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER91.
           DISPLAY WS-HEADER91.

       COMPUTE-TOTALS151.
           MOVE 0 TO WS-TOTAL151.
           PERFORM VARYING WS-K151 FROM 1 BY 1 UNTIL WS-K151 > 10
               ADD WS-K151 TO WS-TOTAL151
           END-PERFORM.
           COMPUTE WS-AVERAGE151 = WS-TOTAL151 / 10.

       CHECK-LIMIT83.
           IF WS-AMOUNT83 > 1000
               MOVE 'Y' TO WS-FLAG83
           ELSE
               MOVE 'N' TO WS-FLAG83
           END-IF.

       COMPUTE-TOTALS100.
           MOVE 0 TO WS-TOTAL100.
           PERFORM VARYING WS-K100 FROM 1 BY 1 UNTIL WS-K100 > 10
               ADD WS-K100 TO WS-TOTAL100
           END-PERFORM.
           COMPUTE WS-AVERAGE100 = WS-TOTAL100 / 10.

       FORMAT-HEADER46.
           MOVE 'MONTHLY REPORT' TO WS-TITLE46.
           STRING WS-TITLE46 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER46.
           DISPLAY WS-HEADER46.

       ECHO-NAME21.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM21) END-EXEC.
           STRING '<p>' WS-FORM21 '</p>' DELIMITED BY SIZE INTO WS-PAGE21.
           EXEC CICS WEB SEND FROM(WS-PAGE21) END-EXEC.

       WRITE-EXPORT-SAFE171.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH171.
           OPEN OUTPUT EXPORT-FILE171.
           CLOSE EXPORT-FILE171.

       PREPARE-QUERY188.
           MOVE LK-FILTER188 TO WS-STMT188.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT188 END-EXEC.

       WRITE-EXPORT160.
           MOVE LK-PATH160 TO WS-EXPORT-PATH160.
           OPEN OUTPUT EXPORT-FILE160.
           CLOSE EXPORT-FILE160.

       WRITE-EXPORT-SAFE122.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH122.
           OPEN OUTPUT EXPORT-FILE122.
           CLOSE EXPORT-FILE122.

       LOG-LOGIN3.
           DISPLAY 'LOGIN ' WS-USER3 ' ' WS-PASSWORD-IN3.

       CONNECT-DB14.
           MOVE WS-DB-PASSWORD14 TO WS-CONN-PW14.

       CHECK-LIMIT70.
           IF WS-AMOUNT70 > 1000
               MOVE 'Y' TO WS-FLAG70
           ELSE
               MOVE 'N' TO WS-FLAG70
           END-IF.

       EXTRACT-FIELD-SAFE13.
           ACCEPT WS-POS13.
           IF WS-POS13 IS NUMERIC AND WS-POS13 > 0 AND WS-POS13 < 76
               MOVE WS-RECORD13(WS-POS13:5) TO WS-PART13
           END-IF.

       CHECK-LIMIT38.
           IF WS-AMOUNT38 > 1000
               MOVE 'Y' TO WS-FLAG38
           ELSE
               MOVE 'N' TO WS-FLAG38
           END-IF.

       CHECK-LIMIT77.
           IF WS-AMOUNT77 > 1000
               MOVE 'Y' TO WS-FLAG77
           ELSE
               MOVE 'N' TO WS-FLAG77
           END-IF.

       EXTRACT-FIELD-SAFE168.
           ACCEPT WS-POS168.
           IF WS-POS168 IS NUMERIC AND WS-POS168 > 0 AND WS-POS168 < 76
               MOVE WS-RECORD168(WS-POS168:5) TO WS-PART168
           END-IF.

       LOG-LOGIN8.
           DISPLAY 'LOGIN ' WS-USER8 ' ' WS-PASSWORD-IN8.

       PREPARE-QUERY121.
           MOVE LK-FILTER121 TO WS-STMT121.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT121 END-EXEC.

       EXTRACT-FIELD-SAFE102.
           ACCEPT WS-POS102.
           IF WS-POS102 IS NUMERIC AND WS-POS102 > 0 AND WS-POS102 < 76
               MOVE WS-RECORD102(WS-POS102:5) TO WS-PART102
           END-IF.

       ECHO-NAME111.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM111) END-EXEC.
           STRING '<p>' WS-FORM111 '</p>' DELIMITED BY SIZE INTO WS-PAGE111.
           EXEC CICS WEB SEND FROM(WS-PAGE111) END-EXEC.

       COMPUTE-TOTALS5.
           MOVE 0 TO WS-TOTAL5.
           PERFORM VARYING WS-K5 FROM 1 BY 1 UNTIL WS-K5 > 10
               ADD WS-K5 TO WS-TOTAL5
           END-PERFORM.
           COMPUTE WS-AVERAGE5 = WS-TOTAL5 / 10.

       COMPUTE-TOTALS132.
           MOVE 0 TO WS-TOTAL132.
           PERFORM VARYING WS-K132 FROM 1 BY 1 UNTIL WS-K132 > 10
               ADD WS-K132 TO WS-TOTAL132
           END-PERFORM.
           COMPUTE WS-AVERAGE132 = WS-TOTAL132 / 10.

       FORMAT-HEADER15.
           MOVE 'MONTHLY REPORT' TO WS-TITLE15.
           STRING WS-TITLE15 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER15.
           DISPLAY WS-HEADER15.

       EXTRACT-FIELD55.
           ACCEPT WS-POS55.
           MOVE WS-RECORD55(WS-POS55:5) TO WS-PART55.

       LOG-LOGIN61.
           DISPLAY 'LOGIN ' WS-USER61 ' ' WS-PASSWORD-IN61.

       CONNECT-DB154.
           MOVE WS-DB-PASSWORD154 TO WS-CONN-PW154.

       CONVERT-FILE-SAFE153.
           MOVE "convert /srv/in/report.txt" TO WS-CMD153.
           CALL 'SYSTEM' USING WS-CMD153.

       CONNECT-DB-SAFE20.
           ACCEPT WS-CONN-PW20 FROM ENVIRONMENT 'DB_PASSWORD'.

       ECHO-NAME-SAFE4.
           MOVE '<p>Thank you</p>' TO WS-PAGE4.
           EXEC CICS WEB SEND FROM(WS-PAGE4) END-EXEC.

       FORMAT-HEADER85.
           MOVE 'MONTHLY REPORT' TO WS-TITLE85.
           STRING WS-TITLE85 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER85.
           DISPLAY WS-HEADER85.

       WRITE-EXPORT-SAFE114.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH114.
           OPEN OUTPUT EXPORT-FILE114.
           CLOSE EXPORT-FILE114.

       COMPUTE-TOTALS138.
           MOVE 0 TO WS-TOTAL138.
           PERFORM VARYING WS-K138 FROM 1 BY 1 UNTIL WS-K138 > 10
               ADD WS-K138 TO WS-TOTAL138
           END-PERFORM.
           COMPUTE WS-AVERAGE138 = WS-TOTAL138 / 10.

       WRITE-EXPORT-SAFE147.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH147.
           OPEN OUTPUT EXPORT-FILE147.
           CLOSE EXPORT-FILE147.

       CONVERT-FILE101.
           STRING "convert " LK-NAME101 DELIMITED BY SIZE INTO WS-CMD101.
           CALL 'SYSTEM' USING WS-CMD101.

       PREPARE-QUERY142.
           MOVE LK-FILTER142 TO WS-STMT142.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT142 END-EXEC.

       FORMAT-HEADER141.
           MOVE 'MONTHLY REPORT' TO WS-TITLE141.
           STRING WS-TITLE141 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER141.
           DISPLAY WS-HEADER141.

       WRITE-EXPORT137.
           MOVE LK-PATH137 TO WS-EXPORT-PATH137.
           OPEN OUTPUT EXPORT-FILE137.
           CLOSE EXPORT-FILE137.

       COMPUTE-TOTALS71.
           MOVE 0 TO WS-TOTAL71.
           PERFORM VARYING WS-K71 FROM 1 BY 1 UNTIL WS-K71 > 10
               ADD WS-K71 TO WS-TOTAL71
           END-PERFORM.
           COMPUTE WS-AVERAGE71 = WS-TOTAL71 / 10.

       EXTRACT-FIELD144.
           ACCEPT WS-POS144.
           MOVE WS-RECORD144(WS-POS144:5) TO WS-PART144.

       FORMAT-HEADER99.
           MOVE 'MONTHLY REPORT' TO WS-TITLE99.
           STRING WS-TITLE99 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER99.
           DISPLAY WS-HEADER99.

       CLASSIFY-CODE54.
           EVALUATE WS-CODE54
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS54
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS54
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS54
           END-EVALUATE.

       CONNECT-DB-SAFE88.
           ACCEPT WS-CONN-PW88 FROM ENVIRONMENT 'DB_PASSWORD'.

       CHECK-LIMIT66.
           IF WS-AMOUNT66 > 1000
               MOVE 'Y' TO WS-FLAG66
           ELSE
               MOVE 'N' TO WS-FLAG66
           END-IF.

       COMPUTE-TOTALS49.
           MOVE 0 TO WS-TOTAL49.
           PERFORM VARYING WS-K49 FROM 1 BY 1 UNTIL WS-K49 > 10
               ADD WS-K49 TO WS-TOTAL49
           END-PERFORM.
           COMPUTE WS-AVERAGE49 = WS-TOTAL49 / 10.

       CLASSIFY-CODE42.
           EVALUATE WS-CODE42
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS42
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS42
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS42
           END-EVALUATE.

       COMPUTE-TOTALS69.
           MOVE 0 TO WS-TOTAL69.
           PERFORM VARYING WS-K69 FROM 1 BY 1 UNTIL WS-K69 > 10
               ADD WS-K69 TO WS-TOTAL69
           END-PERFORM.
           COMPUTE WS-AVERAGE69 = WS-TOTAL69 / 10.

       FORMAT-HEADER104.
           MOVE 'MONTHLY REPORT' TO WS-TITLE104.
           STRING WS-TITLE104 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER104.
           DISPLAY WS-HEADER104.

       ECHO-NAME163.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM163) END-EXEC.
           STRING '<p>' WS-FORM163 '</p>' DELIMITED BY SIZE INTO WS-PAGE163.
           EXEC CICS WEB SEND FROM(WS-PAGE163) END-EXEC.

       LOG-LOGIN-SAFE12.
           DISPLAY 'LOGIN ' WS-USER12.

       EXTRACT-FIELD23.
           ACCEPT WS-POS23.
           MOVE WS-RECORD23(WS-POS23:5) TO WS-PART23.

       PREPARE-QUERY87.
           MOVE LK-FILTER87 TO WS-STMT87.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT87 END-EXEC.

       EXTRACT-FIELD-SAFE158.
           ACCEPT WS-POS158.
           IF WS-POS158 IS NUMERIC AND WS-POS158 > 0 AND WS-POS158 < 76
               MOVE WS-RECORD158(WS-POS158:5) TO WS-PART158
           END-IF.

       CHECK-LIMIT63.
           IF WS-AMOUNT63 > 1000
               MOVE 'Y' TO WS-FLAG63
           ELSE
               MOVE 'N' TO WS-FLAG63
           END-IF.

       COMPUTE-TOTALS94.
           MOVE 0 TO WS-TOTAL94.
           PERFORM VARYING WS-K94 FROM 1 BY 1 UNTIL WS-K94 > 10
               ADD WS-K94 TO WS-TOTAL94
           END-PERFORM.
           COMPUTE WS-AVERAGE94 = WS-TOTAL94 / 10.

       LOG-LOGIN117.
           DISPLAY 'LOGIN ' WS-USER117 ' ' WS-PASSWORD-IN117.

       COMPUTE-TOTALS67.
           MOVE 0 TO WS-TOTAL67.
           PERFORM VARYING WS-K67 FROM 1 BY 1 UNTIL WS-K67 > 10
               ADD WS-K67 TO WS-TOTAL67
           END-PERFORM.
           COMPUTE WS-AVERAGE67 = WS-TOTAL67 / 10.

       WRITE-EXPORT93.
           MOVE LK-PATH93 TO WS-EXPORT-PATH93.
           OPEN OUTPUT EXPORT-FILE93.
           CLOSE EXPORT-FILE93.

       CONNECT-DB78.
           MOVE WS-DB-PASSWORD78 TO WS-CONN-PW78.

       LOG-LOGIN-SAFE39.
           DISPLAY 'LOGIN ' WS-USER39.

       LOG-LOGIN73.
           DISPLAY 'LOGIN ' WS-USER73 ' ' WS-PASSWORD-IN73.

       PREPARE-QUERY-SAFE174.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT174.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT174 END-EXEC.

       CONNECT-DB-SAFE128.
           ACCEPT WS-CONN-PW128 FROM ENVIRONMENT 'DB_PASSWORD'.

       FORMAT-HEADER175.
           MOVE 'MONTHLY REPORT' TO WS-TITLE175.
           STRING WS-TITLE175 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER175.
           DISPLAY WS-HEADER175.

       LOG-LOGIN181.
           DISPLAY 'LOGIN ' WS-USER181 ' ' WS-PASSWORD-IN181.

       CONVERT-FILE-SAFE157.
           MOVE "convert /srv/in/report.txt" TO WS-CMD157.
           CALL 'SYSTEM' USING WS-CMD157.

       FORMAT-HEADER169.
           MOVE 'MONTHLY REPORT' TO WS-TITLE169.
           STRING WS-TITLE169 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER169.
           DISPLAY WS-HEADER169.

       PREPARE-QUERY-SAFE10.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT10.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT10 END-EXEC.

       CHECK-LIMIT166.
           IF WS-AMOUNT166 > 1000
               MOVE 'Y' TO WS-FLAG166
           ELSE
               MOVE 'N' TO WS-FLAG166
           END-IF.

       EXTRACT-FIELD119.
           ACCEPT WS-POS119.
           MOVE WS-RECORD119(WS-POS119:5) TO WS-PART119.

       ECHO-NAME62.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM62) END-EXEC.
           STRING '<p>' WS-FORM62 '</p>' DELIMITED BY SIZE INTO WS-PAGE62.
           EXEC CICS WEB SEND FROM(WS-PAGE62) END-EXEC.

       EXTRACT-FIELD-SAFE184.
           ACCEPT WS-POS184.
           IF WS-POS184 IS NUMERIC AND WS-POS184 > 0 AND WS-POS184 < 76
               MOVE WS-RECORD184(WS-POS184:5) TO WS-PART184
           END-IF.

       FORMAT-HEADER2.
           MOVE 'MONTHLY REPORT' TO WS-TITLE2.
           STRING WS-TITLE2 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER2.
           DISPLAY WS-HEADER2.

       ECHO-NAME-SAFE59.
           MOVE '<p>Thank you</p>' TO WS-PAGE59.
           EXEC CICS WEB SEND FROM(WS-PAGE59) END-EXEC.

       ECHO-NAME-SAFE112.
           MOVE '<p>Thank you</p>' TO WS-PAGE112.
           EXEC CICS WEB SEND FROM(WS-PAGE112) END-EXEC.

       CLASSIFY-CODE165.
           EVALUATE WS-CODE165
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS165
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS165
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS165
           END-EVALUATE.

       CONNECT-DB-SAFE106.
           ACCEPT WS-CONN-PW106 FROM ENVIRONMENT 'DB_PASSWORD'.

       COMPUTE-TOTALS7.
           MOVE 0 TO WS-TOTAL7.
           PERFORM VARYING WS-K7 FROM 1 BY 1 UNTIL WS-K7 > 10
               ADD WS-K7 TO WS-TOTAL7
           END-PERFORM.
           COMPUTE WS-AVERAGE7 = WS-TOTAL7 / 10.

       FORMAT-HEADER36.
           MOVE 'MONTHLY REPORT' TO WS-TITLE36.
           STRING WS-TITLE36 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER36.
           DISPLAY WS-HEADER36.

       CONNECT-DB-SAFE17.
           ACCEPT WS-CONN-PW17 FROM ENVIRONMENT 'DB_PASSWORD'.

       ECHO-NAME-SAFE52.
           MOVE '<p>Thank you</p>' TO WS-PAGE52.
           EXEC CICS WEB SEND FROM(WS-PAGE52) END-EXEC.

       CLASSIFY-CODE189.
           EVALUATE WS-CODE189
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS189
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS189
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS189
           END-EVALUATE.

       CHECK-LIMIT115.
           IF WS-AMOUNT115 > 1000
               MOVE 'Y' TO WS-FLAG115
           ELSE
               MOVE 'N' TO WS-FLAG115
           END-IF.

       CHECK-LIMIT80.
           IF WS-AMOUNT80 > 1000
               MOVE 'Y' TO WS-FLAG80
           ELSE
               MOVE 'N' TO WS-FLAG80
           END-IF.

       WRITE-EXPORT150.
           MOVE LK-PATH150 TO WS-EXPORT-PATH150.
           OPEN OUTPUT EXPORT-FILE150.
           CLOSE EXPORT-FILE150.

       EXTRACT-FIELD152.
           ACCEPT WS-POS152.
           MOVE WS-RECORD152(WS-POS152:5) TO WS-PART152.

       FORMAT-HEADER28.
           MOVE 'MONTHLY REPORT' TO WS-TITLE28.
           STRING WS-TITLE28 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER28.
           DISPLAY WS-HEADER28.

       FORMAT-HEADER143.
           MOVE 'MONTHLY REPORT' TO WS-TITLE143.
           STRING WS-TITLE143 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER143.
           DISPLAY WS-HEADER143.

       CHECK-LIMIT125.
           IF WS-AMOUNT125 > 1000
               MOVE 'Y' TO WS-FLAG125
           ELSE
               MOVE 'N' TO WS-FLAG125
           END-IF.

       WRITE-EXPORT82.
           MOVE LK-PATH82 TO WS-EXPORT-PATH82.
           OPEN OUTPUT EXPORT-FILE82.
           CLOSE EXPORT-FILE82.

       FORMAT-HEADER33.
           MOVE 'MONTHLY REPORT' TO WS-TITLE33.
           STRING WS-TITLE33 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER33.
           DISPLAY WS-HEADER33.

       FORMAT-HEADER19.
           MOVE 'MONTHLY REPORT' TO WS-TITLE19.
           STRING WS-TITLE19 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER19.
           DISPLAY WS-HEADER19.

       EXTRACT-FIELD96.
           ACCEPT WS-POS96.
           MOVE WS-RECORD96(WS-POS96:5) TO WS-PART96.

       CONNECT-DB129.
           MOVE WS-DB-PASSWORD129 TO WS-CONN-PW129.

       EXTRACT-FIELD-SAFE74.
           ACCEPT WS-POS74.
           IF WS-POS74 IS NUMERIC AND WS-POS74 > 0 AND WS-POS74 < 76
               MOVE WS-RECORD74(WS-POS74:5) TO WS-PART74
           END-IF.

       CONVERT-FILE58.
           STRING "convert " LK-NAME58 DELIMITED BY SIZE INTO WS-CMD58.
           CALL 'SYSTEM' USING WS-CMD58.

       CONNECT-DB-SAFE56.
           ACCEPT WS-CONN-PW56 FROM ENVIRONMENT 'DB_PASSWORD'.

       LOG-LOGIN-SAFE116.
           DISPLAY 'LOGIN ' WS-USER116.

       LOG-LOGIN32.
           DISPLAY 'LOGIN ' WS-USER32 ' ' WS-PASSWORD-IN32.

       LOG-LOGIN-SAFE161.
           DISPLAY 'LOGIN ' WS-USER161.

       WRITE-EXPORT-SAFE183.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH183.
           OPEN OUTPUT EXPORT-FILE183.
           CLOSE EXPORT-FILE183.

       CONNECT-DB-SAFE89.
           ACCEPT WS-CONN-PW89 FROM ENVIRONMENT 'DB_PASSWORD'.

       FORMAT-HEADER97.
           MOVE 'MONTHLY REPORT' TO WS-TITLE97.
           STRING WS-TITLE97 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER97.
           DISPLAY WS-HEADER97.

       CONNECT-DB41.
           MOVE WS-DB-PASSWORD41 TO WS-CONN-PW41.

       ECHO-NAME-SAFE159.
           MOVE '<p>Thank you</p>' TO WS-PAGE159.
           EXEC CICS WEB SEND FROM(WS-PAGE159) END-EXEC.

       WRITE-EXPORT-SAFE43.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH43.
           OPEN OUTPUT EXPORT-FILE43.
           CLOSE EXPORT-FILE43.

       CONNECT-DB118.
           MOVE WS-DB-PASSWORD118 TO WS-CONN-PW118.

       EXTRACT-FIELD-SAFE57.
           ACCEPT WS-POS57.
           IF WS-POS57 IS NUMERIC AND WS-POS57 > 0 AND WS-POS57 < 76
               MOVE WS-RECORD57(WS-POS57:5) TO WS-PART57
           END-IF.

       EXTRACT-FIELD-SAFE60.
           ACCEPT WS-POS60.
           IF WS-POS60 IS NUMERIC AND WS-POS60 > 0 AND WS-POS60 < 76
               MOVE WS-RECORD60(WS-POS60:5) TO WS-PART60
           END-IF.

       WRITE-EXPORT53.
           MOVE LK-PATH53 TO WS-EXPORT-PATH53.
           OPEN OUTPUT EXPORT-FILE53.
           CLOSE EXPORT-FILE53.

       PREPARE-QUERY108.
           MOVE LK-FILTER108 TO WS-STMT108.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT108 END-EXEC.

       FORMAT-HEADER34.
           MOVE 'MONTHLY REPORT' TO WS-TITLE34.
           STRING WS-TITLE34 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER34.
           DISPLAY WS-HEADER34.

       CONNECT-DB1.
           MOVE WS-DB-PASSWORD1 TO WS-CONN-PW1.

       CONVERT-FILE-SAFE145.
           MOVE "convert /srv/in/report.txt" TO WS-CMD145.
           CALL 'SYSTEM' USING WS-CMD145.

       PREPARE-QUERY-SAFE35.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT35.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT35 END-EXEC.

       CONNECT-DB76.
           MOVE WS-DB-PASSWORD76 TO WS-CONN-PW76.

       PREPARE-QUERY179.
           MOVE LK-FILTER179 TO WS-STMT179.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT179 END-EXEC.

       FORMAT-HEADER146.
           MOVE 'MONTHLY REPORT' TO WS-TITLE146.
           STRING WS-TITLE146 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER146.
           DISPLAY WS-HEADER146.

       WRITE-EXPORT-SAFE37.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH37.
           OPEN OUTPUT EXPORT-FILE37.
           CLOSE EXPORT-FILE37.

       ECHO-NAME105.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM105) END-EXEC.
           STRING '<p>' WS-FORM105 '</p>' DELIMITED BY SIZE INTO WS-PAGE105.
           EXEC CICS WEB SEND FROM(WS-PAGE105) END-EXEC.

       CONNECT-DB-SAFE47.
           ACCEPT WS-CONN-PW47 FROM ENVIRONMENT 'DB_PASSWORD'.

       COMPUTE-TOTALS187.
           MOVE 0 TO WS-TOTAL187.
           PERFORM VARYING WS-K187 FROM 1 BY 1 UNTIL WS-K187 > 10
               ADD WS-K187 TO WS-TOTAL187
           END-PERFORM.
           COMPUTE WS-AVERAGE187 = WS-TOTAL187 / 10.

       LOG-LOGIN113.
           DISPLAY 'LOGIN ' WS-USER113 ' ' WS-PASSWORD-IN113.

       LOG-LOGIN95.
           DISPLAY 'LOGIN ' WS-USER95 ' ' WS-PASSWORD-IN95.

       ECHO-NAME177.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM177) END-EXEC.
           STRING '<p>' WS-FORM177 '</p>' DELIMITED BY SIZE INTO WS-PAGE177.
           EXEC CICS WEB SEND FROM(WS-PAGE177) END-EXEC.

       CONNECT-DB98.
           MOVE WS-DB-PASSWORD98 TO WS-CONN-PW98.

       COMPUTE-TOTALS48.
           MOVE 0 TO WS-TOTAL48.
           PERFORM VARYING WS-K48 FROM 1 BY 1 UNTIL WS-K48 > 10
               ADD WS-K48 TO WS-TOTAL48
           END-PERFORM.
           COMPUTE WS-AVERAGE48 = WS-TOTAL48 / 10.

       ECHO-NAME81.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM81) END-EXEC.
           STRING '<p>' WS-FORM81 '</p>' DELIMITED BY SIZE INTO WS-PAGE81.
           EXEC CICS WEB SEND FROM(WS-PAGE81) END-EXEC.

       CHECK-LIMIT185.
           IF WS-AMOUNT185 > 1000
               MOVE 'Y' TO WS-FLAG185
           ELSE
               MOVE 'N' TO WS-FLAG185
           END-IF.

       CHECK-LIMIT140.
           IF WS-AMOUNT140 > 1000
               MOVE 'Y' TO WS-FLAG140
           ELSE
               MOVE 'N' TO WS-FLAG140
           END-IF.

       ECHO-NAME27.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM27) END-EXEC.
           STRING '<p>' WS-FORM27 '</p>' DELIMITED BY SIZE INTO WS-PAGE27.
           EXEC CICS WEB SEND FROM(WS-PAGE27) END-EXEC.

       LOG-LOGIN156.
           DISPLAY 'LOGIN ' WS-USER156 ' ' WS-PASSWORD-IN156.

       LOG-LOGIN-SAFE180.
           DISPLAY 'LOGIN ' WS-USER180.

       CONVERT-FILE-SAFE149.
           MOVE "convert /srv/in/report.txt" TO WS-CMD149.
           CALL 'SYSTEM' USING WS-CMD149.

       CLASSIFY-CODE110.
           EVALUATE WS-CODE110
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS110
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS110
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS110
           END-EVALUATE.

       CONNECT-DB-SAFE123.
           ACCEPT WS-CONN-PW123 FROM ENVIRONMENT 'DB_PASSWORD'.

       CHECK-LIMIT133.
           IF WS-AMOUNT133 > 1000
               MOVE 'Y' TO WS-FLAG133
           ELSE
               MOVE 'N' TO WS-FLAG133
           END-IF.

       EXTRACT-FIELD18.
           ACCEPT WS-POS18.
           MOVE WS-RECORD18(WS-POS18:5) TO WS-PART18.

