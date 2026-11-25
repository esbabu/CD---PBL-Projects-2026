       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTR04.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EXPORT-FILE20 ASSIGN TO DYNAMIC WS-EXPORT-PATH20
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE23 ASSIGN TO DYNAMIC WS-EXPORT-PATH23
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE35 ASSIGN TO DYNAMIC WS-EXPORT-PATH35
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE43 ASSIGN TO DYNAMIC WS-EXPORT-PATH43
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE48 ASSIGN TO DYNAMIC WS-EXPORT-PATH48
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE72 ASSIGN TO DYNAMIC WS-EXPORT-PATH72
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE75 ASSIGN TO DYNAMIC WS-EXPORT-PATH75
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE77 ASSIGN TO DYNAMIC WS-EXPORT-PATH77
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE95 ASSIGN TO DYNAMIC WS-EXPORT-PATH95
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE100 ASSIGN TO DYNAMIC WS-EXPORT-PATH100
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE101 ASSIGN TO DYNAMIC WS-EXPORT-PATH101
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE107 ASSIGN TO DYNAMIC WS-EXPORT-PATH107
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE111 ASSIGN TO DYNAMIC WS-EXPORT-PATH111
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE114 ASSIGN TO DYNAMIC WS-EXPORT-PATH114
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE139 ASSIGN TO DYNAMIC WS-EXPORT-PATH139
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE141 ASSIGN TO DYNAMIC WS-EXPORT-PATH141
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE155 ASSIGN TO DYNAMIC WS-EXPORT-PATH155
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE157 ASSIGN TO DYNAMIC WS-EXPORT-PATH157
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE168 ASSIGN TO DYNAMIC WS-EXPORT-PATH168
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE176 ASSIGN TO DYNAMIC WS-EXPORT-PATH176
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  EXPORT-FILE20.
       01  EXPORT-LINE20         PIC X(80).
       FD  EXPORT-FILE23.
       01  EXPORT-LINE23         PIC X(80).
       FD  EXPORT-FILE35.
       01  EXPORT-LINE35         PIC X(80).
       FD  EXPORT-FILE43.
       01  EXPORT-LINE43         PIC X(80).
       FD  EXPORT-FILE48.
       01  EXPORT-LINE48         PIC X(80).
       FD  EXPORT-FILE72.
       01  EXPORT-LINE72         PIC X(80).
       FD  EXPORT-FILE75.
       01  EXPORT-LINE75         PIC X(80).
       FD  EXPORT-FILE77.
       01  EXPORT-LINE77         PIC X(80).
       FD  EXPORT-FILE95.
       01  EXPORT-LINE95         PIC X(80).
       FD  EXPORT-FILE100.
       01  EXPORT-LINE100         PIC X(80).
       FD  EXPORT-FILE101.
       01  EXPORT-LINE101         PIC X(80).
       FD  EXPORT-FILE107.
       01  EXPORT-LINE107         PIC X(80).
       FD  EXPORT-FILE111.
       01  EXPORT-LINE111         PIC X(80).
       FD  EXPORT-FILE114.
       01  EXPORT-LINE114         PIC X(80).
       FD  EXPORT-FILE139.
       01  EXPORT-LINE139         PIC X(80).
       FD  EXPORT-FILE141.
       01  EXPORT-LINE141         PIC X(80).
       FD  EXPORT-FILE155.
       01  EXPORT-LINE155         PIC X(80).
       FD  EXPORT-FILE157.
       01  EXPORT-LINE157         PIC X(80).
       FD  EXPORT-FILE168.
       01  EXPORT-LINE168         PIC X(80).
       FD  EXPORT-FILE176.
       01  EXPORT-LINE176         PIC X(80).
       WORKING-STORAGE SECTION.
       01  WS-CMD1            PIC X(100).
       01  WS-STMT2           PIC X(200).
       01  WS-POS5            PIC 99.
       01  WS-RECORD5         PIC X(80).
       01  WS-PART5           PIC X(5).
       01  WS-STMT7           PIC X(200).
       01  WS-CMD10            PIC X(100).
       01  WS-DB-PASSWORD14    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW14        PIC X(12).
       01  WS-CMD15            PIC X(100).
       01  WS-CMD16            PIC X(100).
       01  WS-EXPORT-PATH20    PIC X(60).
       01  WS-EXPORT-PATH23    PIC X(60).
       01  WS-POS25            PIC 99.
       01  WS-RECORD25         PIC X(80).
       01  WS-PART25           PIC X(5).
       01  WS-POS28            PIC 99.
       01  WS-RECORD28         PIC X(80).
       01  WS-PART28           PIC X(5).
       01  WS-DB-PASSWORD29    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW29        PIC X(12).
       01  WS-STMT34           PIC X(200).
       01  WS-EXPORT-PATH35    PIC X(60).
       01  WS-STMT36           PIC X(200).
       01  WS-POS38            PIC 99.
       01  WS-RECORD38         PIC X(80).
       01  WS-PART38           PIC X(5).
       01  WS-POS40            PIC 99.
       01  WS-RECORD40         PIC X(80).
       01  WS-PART40           PIC X(5).
       01  WS-EXPORT-PATH43    PIC X(60).
       01  WS-DB-PASSWORD47    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW47        PIC X(12).
       01  WS-EXPORT-PATH48    PIC X(60).
       01  WS-USER49           PIC X(10).
       01  WS-PASSWORD-IN49    PIC X(12).
       01  WS-POS50            PIC 99.
       01  WS-RECORD50         PIC X(80).
       01  WS-PART50           PIC X(5).
       01  WS-FORM53           PIC X(40).
       01  WS-PAGE53           PIC X(80).
       01  WS-CMD55            PIC X(100).
       01  WS-POS56            PIC 99.
       01  WS-RECORD56         PIC X(80).
       01  WS-PART56           PIC X(5).
       01  WS-CMD63            PIC X(100).
       01  WS-USER70           PIC X(10).
       01  WS-PASSWORD-IN70    PIC X(12).
       01  WS-POS71            PIC 99.
       01  WS-RECORD71         PIC X(80).
       01  WS-PART71           PIC X(5).
       01  WS-EXPORT-PATH72    PIC X(60).
       01  WS-EXPORT-PATH75    PIC X(60).
       01  WS-DB-PASSWORD76    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW76        PIC X(12).
       01  WS-EXPORT-PATH77    PIC X(60).
       01  WS-USER79           PIC X(10).
       01  WS-PASSWORD-IN79    PIC X(12).
       01  WS-USER80           PIC X(10).
       01  WS-PASSWORD-IN80    PIC X(12).
       01  WS-STMT81           PIC X(200).
       01  WS-POS84            PIC 99.
       01  WS-RECORD84         PIC X(80).
       01  WS-PART84           PIC X(5).
       01  WS-CMD85            PIC X(100).
       01  WS-STMT86           PIC X(200).
       01  WS-CMD87            PIC X(100).
       01  WS-USER90           PIC X(10).
       01  WS-PASSWORD-IN90    PIC X(12).
       01  WS-STMT91           PIC X(200).
       01  WS-DB-PASSWORD92    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW92        PIC X(12).
       01  WS-DB-PASSWORD93    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW93        PIC X(12).
       01  WS-EXPORT-PATH95    PIC X(60).
       01  WS-FORM96           PIC X(40).
       01  WS-PAGE96           PIC X(80).
       01  WS-USER97           PIC X(10).
       01  WS-PASSWORD-IN97    PIC X(12).
       01  WS-STMT99           PIC X(200).
       01  WS-EXPORT-PATH100    PIC X(60).
       01  WS-EXPORT-PATH101    PIC X(60).
       01  WS-USER102           PIC X(10).
       01  WS-PASSWORD-IN102    PIC X(12).
       01  WS-STMT103           PIC X(200).
       01  WS-EXPORT-PATH107    PIC X(60).
       01  WS-USER109           PIC X(10).
       01  WS-PASSWORD-IN109    PIC X(12).
       01  WS-FORM110           PIC X(40).
       01  WS-PAGE110           PIC X(80).
       01  WS-EXPORT-PATH111    PIC X(60).
       01  WS-EXPORT-PATH114    PIC X(60).
       01  WS-FORM115           PIC X(40).
       01  WS-PAGE115           PIC X(80).
       01  WS-USER116           PIC X(10).
       01  WS-PASSWORD-IN116    PIC X(12).
       01  WS-FORM125           PIC X(40).
       01  WS-PAGE125           PIC X(80).
       01  WS-CMD128            PIC X(100).
       01  WS-POS130            PIC 99.
       01  WS-RECORD130         PIC X(80).
       01  WS-PART130           PIC X(5).
       01  WS-STMT131           PIC X(200).
       01  WS-DB-PASSWORD133    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW133        PIC X(12).
       01  WS-STMT134           PIC X(200).
       01  WS-DB-PASSWORD135    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW135        PIC X(12).
       01  WS-DB-PASSWORD136    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW136        PIC X(12).
       01  WS-FORM138           PIC X(40).
       01  WS-PAGE138           PIC X(80).
       01  WS-EXPORT-PATH139    PIC X(60).
       01  WS-EXPORT-PATH141    PIC X(60).
       01  WS-FORM143           PIC X(40).
       01  WS-PAGE143           PIC X(80).
       01  WS-POS145            PIC 99.
       01  WS-RECORD145         PIC X(80).
       01  WS-PART145           PIC X(5).
       01  WS-CMD148            PIC X(100).
       01  WS-STMT150           PIC X(200).
       01  WS-DB-PASSWORD151    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW151        PIC X(12).
       01  WS-DB-PASSWORD152    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW152        PIC X(12).
       01  WS-USER154           PIC X(10).
       01  WS-PASSWORD-IN154    PIC X(12).
       01  WS-EXPORT-PATH155    PIC X(60).
       01  WS-EXPORT-PATH157    PIC X(60).
       01  WS-USER160           PIC X(10).
       01  WS-PASSWORD-IN160    PIC X(12).
       01  WS-DB-PASSWORD162    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW162        PIC X(12).
       01  WS-DB-PASSWORD163    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW163        PIC X(12).
       01  WS-DB-PASSWORD164    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW164        PIC X(12).
       01  WS-STMT165           PIC X(200).
       01  WS-EXPORT-PATH168    PIC X(60).
       01  WS-FORM169           PIC X(40).
       01  WS-PAGE169           PIC X(80).
       01  WS-STMT170           PIC X(200).
       01  WS-USER171           PIC X(10).
       01  WS-PASSWORD-IN171    PIC X(12).
       01  WS-USER172           PIC X(10).
       01  WS-PASSWORD-IN172    PIC X(12).
       01  WS-DB-PASSWORD174    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW174        PIC X(12).
       01  WS-FORM175           PIC X(40).
       01  WS-PAGE175           PIC X(80).
       01  WS-EXPORT-PATH176    PIC X(60).
       01  WS-POS177            PIC 99.
       01  WS-RECORD177         PIC X(80).
       01  WS-PART177           PIC X(5).
       01  WS-DB-PASSWORD178    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW178        PIC X(12).
       01  WS-CMD180            PIC X(100).
       01  WS-TOTAL3          PIC 9(6) VALUE 0.
       01  WS-K3              PIC 99 VALUE 0.
       01  WS-AVERAGE3        PIC 9(6)V99 VALUE 0.
       01  WS-CODE4           PIC 9 VALUE 1.
       01  WS-STATUS4         PIC X(6) VALUE SPACES.
       01  WS-TITLE6          PIC X(20) VALUE SPACES.
       01  WS-HEADER6         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT8         PIC 9(6) VALUE 500.
       01  WS-FLAG8           PIC X VALUE 'N'.
       01  WS-AMOUNT9         PIC 9(6) VALUE 500.
       01  WS-FLAG9           PIC X VALUE 'N'.
       01  WS-CODE11           PIC 9 VALUE 1.
       01  WS-STATUS11         PIC X(6) VALUE SPACES.
       01  WS-TOTAL12          PIC 9(6) VALUE 0.
       01  WS-K12              PIC 99 VALUE 0.
       01  WS-AVERAGE12        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT13         PIC 9(6) VALUE 500.
       01  WS-FLAG13           PIC X VALUE 'N'.
       01  WS-TOTAL17          PIC 9(6) VALUE 0.
       01  WS-K17              PIC 99 VALUE 0.
       01  WS-AVERAGE17        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT18         PIC 9(6) VALUE 500.
       01  WS-FLAG18           PIC X VALUE 'N'.
       01  WS-CODE19           PIC 9 VALUE 1.
       01  WS-STATUS19         PIC X(6) VALUE SPACES.
       01  WS-TOTAL21          PIC 9(6) VALUE 0.
       01  WS-K21              PIC 99 VALUE 0.
       01  WS-AVERAGE21        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT22         PIC 9(6) VALUE 500.
       01  WS-FLAG22           PIC X VALUE 'N'.
       01  WS-CODE24           PIC 9 VALUE 1.
       01  WS-STATUS24         PIC X(6) VALUE SPACES.
       01  WS-TITLE26          PIC X(20) VALUE SPACES.
       01  WS-HEADER26         PIC X(40) VALUE SPACES.
       01  WS-TITLE27          PIC X(20) VALUE SPACES.
       01  WS-HEADER27         PIC X(40) VALUE SPACES.
       01  WS-TOTAL30          PIC 9(6) VALUE 0.
       01  WS-K30              PIC 99 VALUE 0.
       01  WS-AVERAGE30        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE31          PIC X(20) VALUE SPACES.
       01  WS-HEADER31         PIC X(40) VALUE SPACES.
       01  WS-CODE32           PIC 9 VALUE 1.
       01  WS-STATUS32         PIC X(6) VALUE SPACES.
       01  WS-CODE33           PIC 9 VALUE 1.
       01  WS-STATUS33         PIC X(6) VALUE SPACES.
       01  WS-TITLE37          PIC X(20) VALUE SPACES.
       01  WS-HEADER37         PIC X(40) VALUE SPACES.
       01  WS-TOTAL39          PIC 9(6) VALUE 0.
       01  WS-K39              PIC 99 VALUE 0.
       01  WS-AVERAGE39        PIC 9(6)V99 VALUE 0.
       01  WS-CODE41           PIC 9 VALUE 1.
       01  WS-STATUS41         PIC X(6) VALUE SPACES.
       01  WS-CODE42           PIC 9 VALUE 1.
       01  WS-STATUS42         PIC X(6) VALUE SPACES.
       01  WS-TOTAL44          PIC 9(6) VALUE 0.
       01  WS-K44              PIC 99 VALUE 0.
       01  WS-AVERAGE44        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT45         PIC 9(6) VALUE 500.
       01  WS-FLAG45           PIC X VALUE 'N'.
       01  WS-TITLE46          PIC X(20) VALUE SPACES.
       01  WS-HEADER46         PIC X(40) VALUE SPACES.
       01  WS-TOTAL51          PIC 9(6) VALUE 0.
       01  WS-K51              PIC 99 VALUE 0.
       01  WS-AVERAGE51        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL52          PIC 9(6) VALUE 0.
       01  WS-K52              PIC 99 VALUE 0.
       01  WS-AVERAGE52        PIC 9(6)V99 VALUE 0.
       01  WS-CODE54           PIC 9 VALUE 1.
       01  WS-STATUS54         PIC X(6) VALUE SPACES.
       01  WS-TITLE57          PIC X(20) VALUE SPACES.
       01  WS-HEADER57         PIC X(40) VALUE SPACES.
       01  WS-CODE58           PIC 9 VALUE 1.
       01  WS-STATUS58         PIC X(6) VALUE SPACES.
       01  WS-TITLE59          PIC X(20) VALUE SPACES.
       01  WS-HEADER59         PIC X(40) VALUE SPACES.
       01  WS-TOTAL60          PIC 9(6) VALUE 0.
       01  WS-K60              PIC 99 VALUE 0.
       01  WS-AVERAGE60        PIC 9(6)V99 VALUE 0.
       01  WS-CODE61           PIC 9 VALUE 1.
       01  WS-STATUS61         PIC X(6) VALUE SPACES.
       01  WS-TOTAL62          PIC 9(6) VALUE 0.
       01  WS-K62              PIC 99 VALUE 0.
       01  WS-AVERAGE62        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL64          PIC 9(6) VALUE 0.
       01  WS-K64              PIC 99 VALUE 0.
       01  WS-AVERAGE64        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE65          PIC X(20) VALUE SPACES.
       01  WS-HEADER65         PIC X(40) VALUE SPACES.
       01  WS-CODE66           PIC 9 VALUE 1.
       01  WS-STATUS66         PIC X(6) VALUE SPACES.
       01  WS-TOTAL67          PIC 9(6) VALUE 0.
       01  WS-K67              PIC 99 VALUE 0.
       01  WS-AVERAGE67        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE68          PIC X(20) VALUE SPACES.
       01  WS-HEADER68         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT69         PIC 9(6) VALUE 500.
       01  WS-FLAG69           PIC X VALUE 'N'.
       01  WS-CODE73           PIC 9 VALUE 1.
       01  WS-STATUS73         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT74         PIC 9(6) VALUE 500.
       01  WS-FLAG74           PIC X VALUE 'N'.
       01  WS-TOTAL78          PIC 9(6) VALUE 0.
       01  WS-K78              PIC 99 VALUE 0.
       01  WS-AVERAGE78        PIC 9(6)V99 VALUE 0.
       01  WS-CODE82           PIC 9 VALUE 1.
       01  WS-STATUS82         PIC X(6) VALUE SPACES.
       01  WS-TITLE83          PIC X(20) VALUE SPACES.
       01  WS-HEADER83         PIC X(40) VALUE SPACES.
       01  WS-CODE88           PIC 9 VALUE 1.
       01  WS-STATUS88         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT89         PIC 9(6) VALUE 500.
       01  WS-FLAG89           PIC X VALUE 'N'.
       01  WS-AMOUNT94         PIC 9(6) VALUE 500.
       01  WS-FLAG94           PIC X VALUE 'N'.
       01  WS-TOTAL98          PIC 9(6) VALUE 0.
       01  WS-K98              PIC 99 VALUE 0.
       01  WS-AVERAGE98        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE104          PIC X(20) VALUE SPACES.
       01  WS-HEADER104         PIC X(40) VALUE SPACES.
       01  WS-TOTAL105          PIC 9(6) VALUE 0.
       01  WS-K105              PIC 99 VALUE 0.
       01  WS-AVERAGE105        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE106          PIC X(20) VALUE SPACES.
       01  WS-HEADER106         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT108         PIC 9(6) VALUE 500.
       01  WS-FLAG108           PIC X VALUE 'N'.
       01  WS-AMOUNT112         PIC 9(6) VALUE 500.
       01  WS-FLAG112           PIC X VALUE 'N'.
       01  WS-TITLE113          PIC X(20) VALUE SPACES.
       01  WS-HEADER113         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT117         PIC 9(6) VALUE 500.
       01  WS-FLAG117           PIC X VALUE 'N'.
       01  WS-CODE118           PIC 9 VALUE 1.
       01  WS-STATUS118         PIC X(6) VALUE SPACES.
       01  WS-CODE119           PIC 9 VALUE 1.
       01  WS-STATUS119         PIC X(6) VALUE SPACES.
       01  WS-TITLE120          PIC X(20) VALUE SPACES.
       01  WS-HEADER120         PIC X(40) VALUE SPACES.
       01  WS-CODE121           PIC 9 VALUE 1.
       01  WS-STATUS121         PIC X(6) VALUE SPACES.
       01  WS-CODE122           PIC 9 VALUE 1.
       01  WS-STATUS122         PIC X(6) VALUE SPACES.
       01  WS-TITLE123          PIC X(20) VALUE SPACES.
       01  WS-HEADER123         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT124         PIC 9(6) VALUE 500.
       01  WS-FLAG124           PIC X VALUE 'N'.
       01  WS-AMOUNT126         PIC 9(6) VALUE 500.
       01  WS-FLAG126           PIC X VALUE 'N'.
       01  WS-CODE127           PIC 9 VALUE 1.
       01  WS-STATUS127         PIC X(6) VALUE SPACES.
       01  WS-TITLE129          PIC X(20) VALUE SPACES.
       01  WS-HEADER129         PIC X(40) VALUE SPACES.
       01  WS-TOTAL132          PIC 9(6) VALUE 0.
       01  WS-K132              PIC 99 VALUE 0.
       01  WS-AVERAGE132        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL137          PIC 9(6) VALUE 0.
       01  WS-K137              PIC 99 VALUE 0.
       01  WS-AVERAGE137        PIC 9(6)V99 VALUE 0.
       01  WS-CODE140           PIC 9 VALUE 1.
       01  WS-STATUS140         PIC X(6) VALUE SPACES.
       01  WS-TITLE142          PIC X(20) VALUE SPACES.
       01  WS-HEADER142         PIC X(40) VALUE SPACES.
       01  WS-CODE144           PIC 9 VALUE 1.
       01  WS-STATUS144         PIC X(6) VALUE SPACES.
       01  WS-TITLE146          PIC X(20) VALUE SPACES.
       01  WS-HEADER146         PIC X(40) VALUE SPACES.
       01  WS-CODE147           PIC 9 VALUE 1.
       01  WS-STATUS147         PIC X(6) VALUE SPACES.
       01  WS-CODE149           PIC 9 VALUE 1.
       01  WS-STATUS149         PIC X(6) VALUE SPACES.
       01  WS-TOTAL153          PIC 9(6) VALUE 0.
       01  WS-K153              PIC 99 VALUE 0.
       01  WS-AVERAGE153        PIC 9(6)V99 VALUE 0.
       01  WS-CODE156           PIC 9 VALUE 1.
       01  WS-STATUS156         PIC X(6) VALUE SPACES.
       01  WS-CODE158           PIC 9 VALUE 1.
       01  WS-STATUS158         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT159         PIC 9(6) VALUE 500.
       01  WS-FLAG159           PIC X VALUE 'N'.
       01  WS-AMOUNT161         PIC 9(6) VALUE 500.
       01  WS-FLAG161           PIC X VALUE 'N'.
       01  WS-AMOUNT166         PIC 9(6) VALUE 500.
       01  WS-FLAG166           PIC X VALUE 'N'.
       01  WS-TOTAL167          PIC 9(6) VALUE 0.
       01  WS-K167              PIC 99 VALUE 0.
       01  WS-AVERAGE167        PIC 9(6)V99 VALUE 0.
       01  WS-CODE173           PIC 9 VALUE 1.
       01  WS-STATUS173         PIC X(6) VALUE SPACES.
       01  WS-TOTAL179          PIC 9(6) VALUE 0.
       01  WS-K179              PIC 99 VALUE 0.
       01  WS-AVERAGE179        PIC 9(6)V99 VALUE 0.
       LINKAGE SECTION.
       01  LK-NAME1           PIC X(40).
       01  LK-FILTER2         PIC X(100).
       01  LK-FILTER7         PIC X(100).
       01  LK-NAME10           PIC X(40).
       01  LK-NAME15           PIC X(40).
       01  LK-NAME16           PIC X(40).
       01  LK-PATH20           PIC X(60).
       01  LK-PATH23           PIC X(60).
       01  LK-FILTER34         PIC X(100).
       01  LK-PATH35           PIC X(60).
       01  LK-FILTER36         PIC X(100).
       01  LK-PATH43           PIC X(60).
       01  LK-PATH48           PIC X(60).
       01  LK-NAME55           PIC X(40).
       01  LK-NAME63           PIC X(40).
       01  LK-PATH72           PIC X(60).
       01  LK-PATH75           PIC X(60).
       01  LK-PATH77           PIC X(60).
       01  LK-FILTER81         PIC X(100).
       01  LK-NAME85           PIC X(40).
       01  LK-FILTER86         PIC X(100).
       01  LK-NAME87           PIC X(40).
       01  LK-FILTER91         PIC X(100).
       01  LK-PATH95           PIC X(60).
       01  LK-FILTER99         PIC X(100).
       01  LK-PATH100           PIC X(60).
       01  LK-PATH101           PIC X(60).
       01  LK-FILTER103         PIC X(100).
       01  LK-PATH107           PIC X(60).
       01  LK-PATH111           PIC X(60).
       01  LK-PATH114           PIC X(60).
       01  LK-NAME128           PIC X(40).
       01  LK-FILTER131         PIC X(100).
       01  LK-FILTER134         PIC X(100).
       01  LK-PATH139           PIC X(60).
       01  LK-PATH141           PIC X(60).
       01  LK-NAME148           PIC X(40).
       01  LK-FILTER150         PIC X(100).
       01  LK-PATH155           PIC X(60).
       01  LK-PATH157           PIC X(60).
       01  LK-FILTER165         PIC X(100).
       01  LK-PATH168           PIC X(60).
       01  LK-FILTER170         PIC X(100).
       01  LK-PATH176           PIC X(60).
       01  LK-NAME180           PIC X(40).
       PROCEDURE DIVISION USING LK-NAME1 LK-FILTER2 LK-FILTER7 LK-NAME10 LK-NAME15 LK-NAME16 LK-PATH20 LK-PATH23 LK-FILTER34 LK-PATH35 LK-FILTER36 LK-PATH43 LK-PATH48 LK-NAME55 LK-NAME63 LK-PATH72 LK-PATH75 LK-PATH77 LK-FILTER81 LK-NAME85 LK-FILTER86 LK-NAME87 LK-FILTER91 LK-PATH95 LK-FILTER99 LK-PATH100 LK-PATH101 LK-FILTER103 LK-PATH107 LK-PATH111 LK-PATH114 LK-NAME128 LK-FILTER131 LK-FILTER134 LK-PATH139 LK-PATH141 LK-NAME148 LK-FILTER150 LK-PATH155 LK-PATH157 LK-FILTER165 LK-PATH168 LK-FILTER170 LK-PATH176 LK-NAME180.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       CLASSIFY-CODE41.
           EVALUATE WS-CODE41
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS41
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS41
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS41
           END-EVALUATE.

       COMPUTE-TOTALS167.
           MOVE 0 TO WS-TOTAL167.
           PERFORM VARYING WS-K167 FROM 1 BY 1 UNTIL WS-K167 > 10
               ADD WS-K167 TO WS-TOTAL167
           END-PERFORM.
           COMPUTE WS-AVERAGE167 = WS-TOTAL167 / 10.

       LOG-LOGIN49.
           DISPLAY 'LOGIN ' WS-USER49 ' ' WS-PASSWORD-IN49.

       FORMAT-HEADER37.
           MOVE 'MONTHLY REPORT' TO WS-TITLE37.
           STRING WS-TITLE37 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER37.
           DISPLAY WS-HEADER37.

       PREPARE-QUERY-SAFE103.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT103.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT103 END-EXEC.

       CHECK-LIMIT13.
           IF WS-AMOUNT13 > 1000
               MOVE 'Y' TO WS-FLAG13
           ELSE
               MOVE 'N' TO WS-FLAG13
           END-IF.

       WRITE-EXPORT-SAFE75.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH75.
           OPEN OUTPUT EXPORT-FILE75.
           CLOSE EXPORT-FILE75.

       WRITE-EXPORT43.
           MOVE LK-PATH43 TO WS-EXPORT-PATH43.
           OPEN OUTPUT EXPORT-FILE43.
           CLOSE EXPORT-FILE43.

       COMPUTE-TOTALS39.
           MOVE 0 TO WS-TOTAL39.
           PERFORM VARYING WS-K39 FROM 1 BY 1 UNTIL WS-K39 > 10
               ADD WS-K39 TO WS-TOTAL39
           END-PERFORM.
           COMPUTE WS-AVERAGE39 = WS-TOTAL39 / 10.

       WRITE-EXPORT157.
           MOVE LK-PATH157 TO WS-EXPORT-PATH157.
           OPEN OUTPUT EXPORT-FILE157.
           CLOSE EXPORT-FILE157.

       CONVERT-FILE180.
           STRING "convert " LK-NAME180 DELIMITED BY SIZE INTO WS-CMD180.
           CALL 'SYSTEM' USING WS-CMD180.

       ECHO-NAME-SAFE169.
           MOVE '<p>Thank you</p>' TO WS-PAGE169.
           EXEC CICS WEB SEND FROM(WS-PAGE169) END-EXEC.

       CLASSIFY-CODE122.
           EVALUATE WS-CODE122
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS122
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS122
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS122
           END-EVALUATE.

       ECHO-NAME-SAFE125.
           MOVE '<p>Thank you</p>' TO WS-PAGE125.
           EXEC CICS WEB SEND FROM(WS-PAGE125) END-EXEC.

       WRITE-EXPORT107.
           MOVE LK-PATH107 TO WS-EXPORT-PATH107.
           OPEN OUTPUT EXPORT-FILE107.
           CLOSE EXPORT-FILE107.

       COMPUTE-TOTALS30.
           MOVE 0 TO WS-TOTAL30.
           PERFORM VARYING WS-K30 FROM 1 BY 1 UNTIL WS-K30 > 10
               ADD WS-K30 TO WS-TOTAL30
           END-PERFORM.
           COMPUTE WS-AVERAGE30 = WS-TOTAL30 / 10.

       CLASSIFY-CODE147.
           EVALUATE WS-CODE147
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS147
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS147
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS147
           END-EVALUATE.

       CONNECT-DB152.
           MOVE WS-DB-PASSWORD152 TO WS-CONN-PW152.

       EXTRACT-FIELD130.
           ACCEPT WS-POS130.
           MOVE WS-RECORD130(WS-POS130:5) TO WS-PART130.

       CHECK-LIMIT108.
           IF WS-AMOUNT108 > 1000
               MOVE 'Y' TO WS-FLAG108
           ELSE
               MOVE 'N' TO WS-FLAG108
           END-IF.

       FORMAT-HEADER120.
           MOVE 'MONTHLY REPORT' TO WS-TITLE120.
           STRING WS-TITLE120 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER120.
           DISPLAY WS-HEADER120.

       PREPARE-QUERY-SAFE91.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT91.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT91 END-EXEC.

       ECHO-NAME175.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM175) END-EXEC.
           STRING '<p>' WS-FORM175 '</p>' DELIMITED BY SIZE INTO WS-PAGE175.
           EXEC CICS WEB SEND FROM(WS-PAGE175) END-EXEC.

       CLASSIFY-CODE33.
           EVALUATE WS-CODE33
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS33
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS33
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS33
           END-EVALUATE.

       COMPUTE-TOTALS179.
           MOVE 0 TO WS-TOTAL179.
           PERFORM VARYING WS-K179 FROM 1 BY 1 UNTIL WS-K179 > 10
               ADD WS-K179 TO WS-TOTAL179
           END-PERFORM.
           COMPUTE WS-AVERAGE179 = WS-TOTAL179 / 10.

       CONVERT-FILE55.
           STRING "convert " LK-NAME55 DELIMITED BY SIZE INTO WS-CMD55.
           CALL 'SYSTEM' USING WS-CMD55.

       WRITE-EXPORT-SAFE114.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH114.
           OPEN OUTPUT EXPORT-FILE114.
           CLOSE EXPORT-FILE114.

       COMPUTE-TOTALS12.
           MOVE 0 TO WS-TOTAL12.
           PERFORM VARYING WS-K12 FROM 1 BY 1 UNTIL WS-K12 > 10
               ADD WS-K12 TO WS-TOTAL12
           END-PERFORM.
           COMPUTE WS-AVERAGE12 = WS-TOTAL12 / 10.

       CONNECT-DB135.
           MOVE WS-DB-PASSWORD135 TO WS-CONN-PW135.

       EXTRACT-FIELD-SAFE56.
           ACCEPT WS-POS56.
           IF WS-POS56 IS NUMERIC AND WS-POS56 > 0 AND WS-POS56 < 76
               MOVE WS-RECORD56(WS-POS56:5) TO WS-PART56
           END-IF.

       FORMAT-HEADER65.
           MOVE 'MONTHLY REPORT' TO WS-TITLE65.
           STRING WS-TITLE65 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER65.
           DISPLAY WS-HEADER65.

       ECHO-NAME115.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM115) END-EXEC.
           STRING '<p>' WS-FORM115 '</p>' DELIMITED BY SIZE INTO WS-PAGE115.
           EXEC CICS WEB SEND FROM(WS-PAGE115) END-EXEC.

       WRITE-EXPORT20.
           MOVE LK-PATH20 TO WS-EXPORT-PATH20.
           OPEN OUTPUT EXPORT-FILE20.
           CLOSE EXPORT-FILE20.

       CONVERT-FILE-SAFE1.
           MOVE "convert /srv/in/report.txt" TO WS-CMD1.
           CALL 'SYSTEM' USING WS-CMD1.

       CHECK-LIMIT124.
           IF WS-AMOUNT124 > 1000
               MOVE 'Y' TO WS-FLAG124
           ELSE
               MOVE 'N' TO WS-FLAG124
           END-IF.

       CLASSIFY-CODE42.
           EVALUATE WS-CODE42
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS42
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS42
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS42
           END-EVALUATE.

       LOG-LOGIN-SAFE109.
           DISPLAY 'LOGIN ' WS-USER109.

       CONNECT-DB-SAFE14.
           ACCEPT WS-CONN-PW14 FROM ENVIRONMENT 'DB_PASSWORD'.

       CHECK-LIMIT18.
           IF WS-AMOUNT18 > 1000
               MOVE 'Y' TO WS-FLAG18
           ELSE
               MOVE 'N' TO WS-FLAG18
           END-IF.

       COMPUTE-TOTALS153.
           MOVE 0 TO WS-TOTAL153.
           PERFORM VARYING WS-K153 FROM 1 BY 1 UNTIL WS-K153 > 10
               ADD WS-K153 TO WS-TOTAL153
           END-PERFORM.
           COMPUTE WS-AVERAGE153 = WS-TOTAL153 / 10.

       PREPARE-QUERY-SAFE81.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT81.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT81 END-EXEC.

       PREPARE-QUERY-SAFE170.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT170.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT170 END-EXEC.

       CONNECT-DB162.
           MOVE WS-DB-PASSWORD162 TO WS-CONN-PW162.

       WRITE-EXPORT-SAFE176.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH176.
           OPEN OUTPUT EXPORT-FILE176.
           CLOSE EXPORT-FILE176.

       LOG-LOGIN70.
           DISPLAY 'LOGIN ' WS-USER70 ' ' WS-PASSWORD-IN70.

       CONNECT-DB-SAFE93.
           ACCEPT WS-CONN-PW93 FROM ENVIRONMENT 'DB_PASSWORD'.

       COMPUTE-TOTALS17.
           MOVE 0 TO WS-TOTAL17.
           PERFORM VARYING WS-K17 FROM 1 BY 1 UNTIL WS-K17 > 10
               ADD WS-K17 TO WS-TOTAL17
           END-PERFORM.
           COMPUTE WS-AVERAGE17 = WS-TOTAL17 / 10.

       CONVERT-FILE16.
           STRING "convert " LK-NAME16 DELIMITED BY SIZE INTO WS-CMD16.
           CALL 'SYSTEM' USING WS-CMD16.

       COMPUTE-TOTALS105.
           MOVE 0 TO WS-TOTAL105.
           PERFORM VARYING WS-K105 FROM 1 BY 1 UNTIL WS-K105 > 10
               ADD WS-K105 TO WS-TOTAL105
           END-PERFORM.
           COMPUTE WS-AVERAGE105 = WS-TOTAL105 / 10.

       WRITE-EXPORT-SAFE111.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH111.
           OPEN OUTPUT EXPORT-FILE111.
           CLOSE EXPORT-FILE111.

       CONVERT-FILE-SAFE85.
           MOVE "convert /srv/in/report.txt" TO WS-CMD85.
           CALL 'SYSTEM' USING WS-CMD85.

       PREPARE-QUERY-SAFE36.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT36.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT36 END-EXEC.

       CHECK-LIMIT94.
           IF WS-AMOUNT94 > 1000
               MOVE 'Y' TO WS-FLAG94
           ELSE
               MOVE 'N' TO WS-FLAG94
           END-IF.

       EXTRACT-FIELD-SAFE38.
           ACCEPT WS-POS38.
           IF WS-POS38 IS NUMERIC AND WS-POS38 > 0 AND WS-POS38 < 76
               MOVE WS-RECORD38(WS-POS38:5) TO WS-PART38
           END-IF.

       ECHO-NAME110.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM110) END-EXEC.
           STRING '<p>' WS-FORM110 '</p>' DELIMITED BY SIZE INTO WS-PAGE110.
           EXEC CICS WEB SEND FROM(WS-PAGE110) END-EXEC.

       CLASSIFY-CODE140.
           EVALUATE WS-CODE140
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS140
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS140
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS140
           END-EVALUATE.

       FORMAT-HEADER123.
           MOVE 'MONTHLY REPORT' TO WS-TITLE123.
           STRING WS-TITLE123 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER123.
           DISPLAY WS-HEADER123.

       CLASSIFY-CODE58.
           EVALUATE WS-CODE58
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS58
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS58
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS58
           END-EVALUATE.

       PREPARE-QUERY134.
           MOVE LK-FILTER134 TO WS-STMT134.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT134 END-EXEC.

       EXTRACT-FIELD-SAFE28.
           ACCEPT WS-POS28.
           IF WS-POS28 IS NUMERIC AND WS-POS28 > 0 AND WS-POS28 < 76
               MOVE WS-RECORD28(WS-POS28:5) TO WS-PART28
           END-IF.

       WRITE-EXPORT-SAFE155.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH155.
           OPEN OUTPUT EXPORT-FILE155.
           CLOSE EXPORT-FILE155.

       CONNECT-DB92.
           MOVE WS-DB-PASSWORD92 TO WS-CONN-PW92.

       FORMAT-HEADER106.
           MOVE 'MONTHLY REPORT' TO WS-TITLE106.
           STRING WS-TITLE106 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER106.
           DISPLAY WS-HEADER106.

       CHECK-LIMIT22.
           IF WS-AMOUNT22 > 1000
               MOVE 'Y' TO WS-FLAG22
           ELSE
               MOVE 'N' TO WS-FLAG22
           END-IF.

       CHECK-LIMIT166.
           IF WS-AMOUNT166 > 1000
               MOVE 'Y' TO WS-FLAG166
           ELSE
               MOVE 'N' TO WS-FLAG166
           END-IF.

       FORMAT-HEADER26.
           MOVE 'MONTHLY REPORT' TO WS-TITLE26.
           STRING WS-TITLE26 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER26.
           DISPLAY WS-HEADER26.

       CONNECT-DB164.
           MOVE WS-DB-PASSWORD164 TO WS-CONN-PW164.

       FORMAT-HEADER27.
           MOVE 'MONTHLY REPORT' TO WS-TITLE27.
           STRING WS-TITLE27 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER27.
           DISPLAY WS-HEADER27.

       LOG-LOGIN116.
           DISPLAY 'LOGIN ' WS-USER116 ' ' WS-PASSWORD-IN116.

       WRITE-EXPORT-SAFE72.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH72.
           OPEN OUTPUT EXPORT-FILE72.
           CLOSE EXPORT-FILE72.

       EXTRACT-FIELD-SAFE84.
           ACCEPT WS-POS84.
           IF WS-POS84 IS NUMERIC AND WS-POS84 > 0 AND WS-POS84 < 76
               MOVE WS-RECORD84(WS-POS84:5) TO WS-PART84
           END-IF.

       LOG-LOGIN-SAFE102.
           DISPLAY 'LOGIN ' WS-USER102.

       FORMAT-HEADER46.
           MOVE 'MONTHLY REPORT' TO WS-TITLE46.
           STRING WS-TITLE46 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER46.
           DISPLAY WS-HEADER46.

       CLASSIFY-CODE158.
           EVALUATE WS-CODE158
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS158
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS158
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS158
           END-EVALUATE.

       FORMAT-HEADER113.
           MOVE 'MONTHLY REPORT' TO WS-TITLE113.
           STRING WS-TITLE113 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER113.
           DISPLAY WS-HEADER113.

       CHECK-LIMIT45.
           IF WS-AMOUNT45 > 1000
               MOVE 'Y' TO WS-FLAG45
           ELSE
               MOVE 'N' TO WS-FLAG45
           END-IF.

       LOG-LOGIN160.
           DISPLAY 'LOGIN ' WS-USER160 ' ' WS-PASSWORD-IN160.

       EXTRACT-FIELD71.
           ACCEPT WS-POS71.
           MOVE WS-RECORD71(WS-POS71:5) TO WS-PART71.

       CHECK-LIMIT161.
           IF WS-AMOUNT161 > 1000
               MOVE 'Y' TO WS-FLAG161
           ELSE
               MOVE 'N' TO WS-FLAG161
           END-IF.

       EXTRACT-FIELD5.
           ACCEPT WS-POS5.
           MOVE WS-RECORD5(WS-POS5:5) TO WS-PART5.

       WRITE-EXPORT141.
           MOVE LK-PATH141 TO WS-EXPORT-PATH141.
           OPEN OUTPUT EXPORT-FILE141.
           CLOSE EXPORT-FILE141.

       CHECK-LIMIT126.
           IF WS-AMOUNT126 > 1000
               MOVE 'Y' TO WS-FLAG126
           ELSE
               MOVE 'N' TO WS-FLAG126
           END-IF.

       CLASSIFY-CODE121.
           EVALUATE WS-CODE121
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS121
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS121
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS121
           END-EVALUATE.

       COMPUTE-TOTALS62.
           MOVE 0 TO WS-TOTAL62.
           PERFORM VARYING WS-K62 FROM 1 BY 1 UNTIL WS-K62 > 10
               ADD WS-K62 TO WS-TOTAL62
           END-PERFORM.
           COMPUTE WS-AVERAGE62 = WS-TOTAL62 / 10.

       PREPARE-QUERY-SAFE2.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT2.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT2 END-EXEC.

       PREPARE-QUERY-SAFE34.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT34.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT34 END-EXEC.

       COMPUTE-TOTALS132.
           MOVE 0 TO WS-TOTAL132.
           PERFORM VARYING WS-K132 FROM 1 BY 1 UNTIL WS-K132 > 10
               ADD WS-K132 TO WS-TOTAL132
           END-PERFORM.
           COMPUTE WS-AVERAGE132 = WS-TOTAL132 / 10.

       LOG-LOGIN-SAFE97.
           DISPLAY 'LOGIN ' WS-USER97.

       PREPARE-QUERY7.
           MOVE LK-FILTER7 TO WS-STMT7.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT7 END-EXEC.

       ECHO-NAME-SAFE53.
           MOVE '<p>Thank you</p>' TO WS-PAGE53.
           EXEC CICS WEB SEND FROM(WS-PAGE53) END-EXEC.

       ECHO-NAME-SAFE96.
           MOVE '<p>Thank you</p>' TO WS-PAGE96.
           EXEC CICS WEB SEND FROM(WS-PAGE96) END-EXEC.

       COMPUTE-TOTALS64.
           MOVE 0 TO WS-TOTAL64.
           PERFORM VARYING WS-K64 FROM 1 BY 1 UNTIL WS-K64 > 10
               ADD WS-K64 TO WS-TOTAL64
           END-PERFORM.
           COMPUTE WS-AVERAGE64 = WS-TOTAL64 / 10.

       PREPARE-QUERY150.
           MOVE LK-FILTER150 TO WS-STMT150.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT150 END-EXEC.

       LOG-LOGIN-SAFE171.
           DISPLAY 'LOGIN ' WS-USER171.

       CLASSIFY-CODE173.
           EVALUATE WS-CODE173
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS173
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS173
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS173
           END-EVALUATE.

       PREPARE-QUERY-SAFE165.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT165.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT165 END-EXEC.

       PREPARE-QUERY-SAFE131.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT131.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT131 END-EXEC.

       FORMAT-HEADER146.
           MOVE 'MONTHLY REPORT' TO WS-TITLE146.
           STRING WS-TITLE146 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER146.
           DISPLAY WS-HEADER146.

       WRITE-EXPORT-SAFE168.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH168.
           OPEN OUTPUT EXPORT-FILE168.
           CLOSE EXPORT-FILE168.

       CLASSIFY-CODE156.
           EVALUATE WS-CODE156
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS156
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS156
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS156
           END-EVALUATE.

       WRITE-EXPORT95.
           MOVE LK-PATH95 TO WS-EXPORT-PATH95.
           OPEN OUTPUT EXPORT-FILE95.
           CLOSE EXPORT-FILE95.

       LOG-LOGIN-SAFE154.
           DISPLAY 'LOGIN ' WS-USER154.

       CHECK-LIMIT69.
           IF WS-AMOUNT69 > 1000
               MOVE 'Y' TO WS-FLAG69
           ELSE
               MOVE 'N' TO WS-FLAG69
           END-IF.

       CLASSIFY-CODE24.
           EVALUATE WS-CODE24
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS24
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS24
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS24
           END-EVALUATE.

       COMPUTE-TOTALS3.
           MOVE 0 TO WS-TOTAL3.
           PERFORM VARYING WS-K3 FROM 1 BY 1 UNTIL WS-K3 > 10
               ADD WS-K3 TO WS-TOTAL3
           END-PERFORM.
           COMPUTE WS-AVERAGE3 = WS-TOTAL3 / 10.

       COMPUTE-TOTALS52.
           MOVE 0 TO WS-TOTAL52.
           PERFORM VARYING WS-K52 FROM 1 BY 1 UNTIL WS-K52 > 10
               ADD WS-K52 TO WS-TOTAL52
           END-PERFORM.
           COMPUTE WS-AVERAGE52 = WS-TOTAL52 / 10.

       EXTRACT-FIELD50.
           ACCEPT WS-POS50.
           MOVE WS-RECORD50(WS-POS50:5) TO WS-PART50.

       CONVERT-FILE128.
           STRING "convert " LK-NAME128 DELIMITED BY SIZE INTO WS-CMD128.
           CALL 'SYSTEM' USING WS-CMD128.

       CLASSIFY-CODE4.
           EVALUATE WS-CODE4
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS4
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS4
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS4
           END-EVALUATE.

       CONVERT-FILE10.
           STRING "convert " LK-NAME10 DELIMITED BY SIZE INTO WS-CMD10.
           CALL 'SYSTEM' USING WS-CMD10.

       CLASSIFY-CODE127.
           EVALUATE WS-CODE127
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS127
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS127
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS127
           END-EVALUATE.

       EXTRACT-FIELD-SAFE177.
           ACCEPT WS-POS177.
           IF WS-POS177 IS NUMERIC AND WS-POS177 > 0 AND WS-POS177 < 76
               MOVE WS-RECORD177(WS-POS177:5) TO WS-PART177
           END-IF.

       CLASSIFY-CODE19.
           EVALUATE WS-CODE19
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS19
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS19
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS19
           END-EVALUATE.

       LOG-LOGIN-SAFE90.
           DISPLAY 'LOGIN ' WS-USER90.

       CONNECT-DB163.
           MOVE WS-DB-PASSWORD163 TO WS-CONN-PW163.

       CHECK-LIMIT89.
           IF WS-AMOUNT89 > 1000
               MOVE 'Y' TO WS-FLAG89
           ELSE
               MOVE 'N' TO WS-FLAG89
           END-IF.

       FORMAT-HEADER142.
           MOVE 'MONTHLY REPORT' TO WS-TITLE142.
           STRING WS-TITLE142 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER142.
           DISPLAY WS-HEADER142.

       CHECK-LIMIT9.
           IF WS-AMOUNT9 > 1000
               MOVE 'Y' TO WS-FLAG9
           ELSE
               MOVE 'N' TO WS-FLAG9
           END-IF.

       CLASSIFY-CODE54.
           EVALUATE WS-CODE54
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS54
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS54
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS54
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

       CONNECT-DB76.
           MOVE WS-DB-PASSWORD76 TO WS-CONN-PW76.

       ECHO-NAME-SAFE143.
           MOVE '<p>Thank you</p>' TO WS-PAGE143.
           EXEC CICS WEB SEND FROM(WS-PAGE143) END-EXEC.

       PREPARE-QUERY-SAFE86.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT86.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT86 END-EXEC.

       CLASSIFY-CODE88.
           EVALUATE WS-CODE88
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS88
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS88
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS88
           END-EVALUATE.

       COMPUTE-TOTALS78.
           MOVE 0 TO WS-TOTAL78.
           PERFORM VARYING WS-K78 FROM 1 BY 1 UNTIL WS-K78 > 10
               ADD WS-K78 TO WS-TOTAL78
           END-PERFORM.
           COMPUTE WS-AVERAGE78 = WS-TOTAL78 / 10.

       CLASSIFY-CODE82.
           EVALUATE WS-CODE82
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS82
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS82
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS82
           END-EVALUATE.

       CONNECT-DB-SAFE29.
           ACCEPT WS-CONN-PW29 FROM ENVIRONMENT 'DB_PASSWORD'.

       PREPARE-QUERY-SAFE99.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT99.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT99 END-EXEC.

       ECHO-NAME-SAFE138.
           MOVE '<p>Thank you</p>' TO WS-PAGE138.
           EXEC CICS WEB SEND FROM(WS-PAGE138) END-EXEC.

       WRITE-EXPORT-SAFE101.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH101.
           OPEN OUTPUT EXPORT-FILE101.
           CLOSE EXPORT-FILE101.

       FORMAT-HEADER57.
           MOVE 'MONTHLY REPORT' TO WS-TITLE57.
           STRING WS-TITLE57 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER57.
           DISPLAY WS-HEADER57.

       LOG-LOGIN80.
           DISPLAY 'LOGIN ' WS-USER80 ' ' WS-PASSWORD-IN80.

       WRITE-EXPORT-SAFE48.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH48.
           OPEN OUTPUT EXPORT-FILE48.
           CLOSE EXPORT-FILE48.

       FORMAT-HEADER6.
           MOVE 'MONTHLY REPORT' TO WS-TITLE6.
           STRING WS-TITLE6 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER6.
           DISPLAY WS-HEADER6.

       CLASSIFY-CODE149.
           EVALUATE WS-CODE149
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS149
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS149
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS149
           END-EVALUATE.

       COMPUTE-TOTALS98.
           MOVE 0 TO WS-TOTAL98.
           PERFORM VARYING WS-K98 FROM 1 BY 1 UNTIL WS-K98 > 10
               ADD WS-K98 TO WS-TOTAL98
           END-PERFORM.
           COMPUTE WS-AVERAGE98 = WS-TOTAL98 / 10.

       CHECK-LIMIT112.
           IF WS-AMOUNT112 > 1000
               MOVE 'Y' TO WS-FLAG112
           ELSE
               MOVE 'N' TO WS-FLAG112
           END-IF.

       CONNECT-DB151.
           MOVE WS-DB-PASSWORD151 TO WS-CONN-PW151.

       CONVERT-FILE148.
           STRING "convert " LK-NAME148 DELIMITED BY SIZE INTO WS-CMD148.
           CALL 'SYSTEM' USING WS-CMD148.

       FORMAT-HEADER129.
           MOVE 'MONTHLY REPORT' TO WS-TITLE129.
           STRING WS-TITLE129 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER129.
           DISPLAY WS-HEADER129.

       CLASSIFY-CODE32.
           EVALUATE WS-CODE32
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS32
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS32
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS32
           END-EVALUATE.

       WRITE-EXPORT23.
           MOVE LK-PATH23 TO WS-EXPORT-PATH23.
           OPEN OUTPUT EXPORT-FILE23.
           CLOSE EXPORT-FILE23.

       CLASSIFY-CODE66.
           EVALUATE WS-CODE66
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS66
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS66
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS66
           END-EVALUATE.

       CHECK-LIMIT8.
           IF WS-AMOUNT8 > 1000
               MOVE 'Y' TO WS-FLAG8
           ELSE
               MOVE 'N' TO WS-FLAG8
           END-IF.

       CHECK-LIMIT74.
           IF WS-AMOUNT74 > 1000
               MOVE 'Y' TO WS-FLAG74
           ELSE
               MOVE 'N' TO WS-FLAG74
           END-IF.

       EXTRACT-FIELD40.
           ACCEPT WS-POS40.
           MOVE WS-RECORD40(WS-POS40:5) TO WS-PART40.

       FORMAT-HEADER68.
           MOVE 'MONTHLY REPORT' TO WS-TITLE68.
           STRING WS-TITLE68 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER68.
           DISPLAY WS-HEADER68.

       COMPUTE-TOTALS51.
           MOVE 0 TO WS-TOTAL51.
           PERFORM VARYING WS-K51 FROM 1 BY 1 UNTIL WS-K51 > 10
               ADD WS-K51 TO WS-TOTAL51
           END-PERFORM.
           COMPUTE WS-AVERAGE51 = WS-TOTAL51 / 10.

       COMPUTE-TOTALS21.
           MOVE 0 TO WS-TOTAL21.
           PERFORM VARYING WS-K21 FROM 1 BY 1 UNTIL WS-K21 > 10
               ADD WS-K21 TO WS-TOTAL21
           END-PERFORM.
           COMPUTE WS-AVERAGE21 = WS-TOTAL21 / 10.

       CONVERT-FILE87.
           STRING "convert " LK-NAME87 DELIMITED BY SIZE INTO WS-CMD87.
           CALL 'SYSTEM' USING WS-CMD87.

       WRITE-EXPORT-SAFE139.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH139.
           OPEN OUTPUT EXPORT-FILE139.
           CLOSE EXPORT-FILE139.

       CHECK-LIMIT159.
           IF WS-AMOUNT159 > 1000
               MOVE 'Y' TO WS-FLAG159
           ELSE
               MOVE 'N' TO WS-FLAG159
           END-IF.

       FORMAT-HEADER83.
           MOVE 'MONTHLY REPORT' TO WS-TITLE83.
           STRING WS-TITLE83 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER83.
           DISPLAY WS-HEADER83.

       CONNECT-DB174.
           MOVE WS-DB-PASSWORD174 TO WS-CONN-PW174.

       CONNECT-DB-SAFE47.
           ACCEPT WS-CONN-PW47 FROM ENVIRONMENT 'DB_PASSWORD'.

       CLASSIFY-CODE73.
           EVALUATE WS-CODE73
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS73
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS73
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS73
           END-EVALUATE.

       WRITE-EXPORT-SAFE100.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH100.
           OPEN OUTPUT EXPORT-FILE100.
           CLOSE EXPORT-FILE100.

       CONNECT-DB-SAFE136.
           ACCEPT WS-CONN-PW136 FROM ENVIRONMENT 'DB_PASSWORD'.

       CONNECT-DB178.
           MOVE WS-DB-PASSWORD178 TO WS-CONN-PW178.

       LOG-LOGIN172.
           DISPLAY 'LOGIN ' WS-USER172 ' ' WS-PASSWORD-IN172.

       WRITE-EXPORT77.
           MOVE LK-PATH77 TO WS-EXPORT-PATH77.
           OPEN OUTPUT EXPORT-FILE77.
           CLOSE EXPORT-FILE77.

       WRITE-EXPORT-SAFE35.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH35.
           OPEN OUTPUT EXPORT-FILE35.
           CLOSE EXPORT-FILE35.

       CLASSIFY-CODE61.
           EVALUATE WS-CODE61
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS61
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS61
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS61
           END-EVALUATE.

       EXTRACT-FIELD-SAFE25.
           ACCEPT WS-POS25.
           IF WS-POS25 IS NUMERIC AND WS-POS25 > 0 AND WS-POS25 < 76
               MOVE WS-RECORD25(WS-POS25:5) TO WS-PART25
           END-IF.

       COMPUTE-TOTALS44.
           MOVE 0 TO WS-TOTAL44.
           PERFORM VARYING WS-K44 FROM 1 BY 1 UNTIL WS-K44 > 10
               ADD WS-K44 TO WS-TOTAL44
           END-PERFORM.
           COMPUTE WS-AVERAGE44 = WS-TOTAL44 / 10.

       FORMAT-HEADER104.
           MOVE 'MONTHLY REPORT' TO WS-TITLE104.
           STRING WS-TITLE104 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER104.
           DISPLAY WS-HEADER104.

       FORMAT-HEADER31.
           MOVE 'MONTHLY REPORT' TO WS-TITLE31.
           STRING WS-TITLE31 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER31.
           DISPLAY WS-HEADER31.

       LOG-LOGIN-SAFE79.
           DISPLAY 'LOGIN ' WS-USER79.

       CLASSIFY-CODE11.
           EVALUATE WS-CODE11
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS11
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS11
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS11
           END-EVALUATE.

       CONVERT-FILE-SAFE15.
           MOVE "convert /srv/in/report.txt" TO WS-CMD15.
           CALL 'SYSTEM' USING WS-CMD15.

       COMPUTE-TOTALS67.
           MOVE 0 TO WS-TOTAL67.
           PERFORM VARYING WS-K67 FROM 1 BY 1 UNTIL WS-K67 > 10
               ADD WS-K67 TO WS-TOTAL67
           END-PERFORM.
           COMPUTE WS-AVERAGE67 = WS-TOTAL67 / 10.

       FORMAT-HEADER59.
           MOVE 'MONTHLY REPORT' TO WS-TITLE59.
           STRING WS-TITLE59 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER59.
           DISPLAY WS-HEADER59.

       CLASSIFY-CODE118.
           EVALUATE WS-CODE118
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS118
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS118
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS118
           END-EVALUATE.

       CONNECT-DB133.
           MOVE WS-DB-PASSWORD133 TO WS-CONN-PW133.

       COMPUTE-TOTALS60.
           MOVE 0 TO WS-TOTAL60.
           PERFORM VARYING WS-K60 FROM 1 BY 1 UNTIL WS-K60 > 10
               ADD WS-K60 TO WS-TOTAL60
           END-PERFORM.
           COMPUTE WS-AVERAGE60 = WS-TOTAL60 / 10.

       CHECK-LIMIT117.
           IF WS-AMOUNT117 > 1000
               MOVE 'Y' TO WS-FLAG117
           ELSE
               MOVE 'N' TO WS-FLAG117
           END-IF.

       CONVERT-FILE-SAFE63.
           MOVE "convert /srv/in/report.txt" TO WS-CMD63.
           CALL 'SYSTEM' USING WS-CMD63.

       CLASSIFY-CODE144.
           EVALUATE WS-CODE144
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS144
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS144
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS144
           END-EVALUATE.

       EXTRACT-FIELD145.
           ACCEPT WS-POS145.
           MOVE WS-RECORD145(WS-POS145:5) TO WS-PART145.

       COMPUTE-TOTALS137.
           MOVE 0 TO WS-TOTAL137.
           PERFORM VARYING WS-K137 FROM 1 BY 1 UNTIL WS-K137 > 10
               ADD WS-K137 TO WS-TOTAL137
           END-PERFORM.
           COMPUTE WS-AVERAGE137 = WS-TOTAL137 / 10.

