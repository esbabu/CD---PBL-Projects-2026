       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTR07.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EXPORT-FILE3 ASSIGN TO DYNAMIC WS-EXPORT-PATH3
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE11 ASSIGN TO DYNAMIC WS-EXPORT-PATH11
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE48 ASSIGN TO DYNAMIC WS-EXPORT-PATH48
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE70 ASSIGN TO DYNAMIC WS-EXPORT-PATH70
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE85 ASSIGN TO DYNAMIC WS-EXPORT-PATH85
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE104 ASSIGN TO DYNAMIC WS-EXPORT-PATH104
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE110 ASSIGN TO DYNAMIC WS-EXPORT-PATH110
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE115 ASSIGN TO DYNAMIC WS-EXPORT-PATH115
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE135 ASSIGN TO DYNAMIC WS-EXPORT-PATH135
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE139 ASSIGN TO DYNAMIC WS-EXPORT-PATH139
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE155 ASSIGN TO DYNAMIC WS-EXPORT-PATH155
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE157 ASSIGN TO DYNAMIC WS-EXPORT-PATH157
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE158 ASSIGN TO DYNAMIC WS-EXPORT-PATH158
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE169 ASSIGN TO DYNAMIC WS-EXPORT-PATH169
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE174 ASSIGN TO DYNAMIC WS-EXPORT-PATH174
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  EXPORT-FILE3.
       01  EXPORT-LINE3         PIC X(80).
       FD  EXPORT-FILE11.
       01  EXPORT-LINE11         PIC X(80).
       FD  EXPORT-FILE48.
       01  EXPORT-LINE48         PIC X(80).
       FD  EXPORT-FILE70.
       01  EXPORT-LINE70         PIC X(80).
       FD  EXPORT-FILE85.
       01  EXPORT-LINE85         PIC X(80).
       FD  EXPORT-FILE104.
       01  EXPORT-LINE104         PIC X(80).
       FD  EXPORT-FILE110.
       01  EXPORT-LINE110         PIC X(80).
       FD  EXPORT-FILE115.
       01  EXPORT-LINE115         PIC X(80).
       FD  EXPORT-FILE135.
       01  EXPORT-LINE135         PIC X(80).
       FD  EXPORT-FILE139.
       01  EXPORT-LINE139         PIC X(80).
       FD  EXPORT-FILE155.
       01  EXPORT-LINE155         PIC X(80).
       FD  EXPORT-FILE157.
       01  EXPORT-LINE157         PIC X(80).
       FD  EXPORT-FILE158.
       01  EXPORT-LINE158         PIC X(80).
       FD  EXPORT-FILE169.
       01  EXPORT-LINE169         PIC X(80).
       FD  EXPORT-FILE174.
       01  EXPORT-LINE174         PIC X(80).
       WORKING-STORAGE SECTION.
       01  WS-POS2            PIC 99.
       01  WS-RECORD2         PIC X(80).
       01  WS-PART2           PIC X(5).
       01  WS-EXPORT-PATH3    PIC X(60).
       01  WS-USER10           PIC X(10).
       01  WS-PASSWORD-IN10    PIC X(12).
       01  WS-EXPORT-PATH11    PIC X(60).
       01  WS-STMT12           PIC X(200).
       01  WS-FORM14           PIC X(40).
       01  WS-PAGE14           PIC X(80).
       01  WS-CMD15            PIC X(100).
       01  WS-POS16            PIC 99.
       01  WS-RECORD16         PIC X(80).
       01  WS-PART16           PIC X(5).
       01  WS-USER17           PIC X(10).
       01  WS-PASSWORD-IN17    PIC X(12).
       01  WS-CMD18            PIC X(100).
       01  WS-FORM20           PIC X(40).
       01  WS-PAGE20           PIC X(80).
       01  WS-DB-PASSWORD21    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW21        PIC X(12).
       01  WS-STMT22           PIC X(200).
       01  WS-CMD28            PIC X(100).
       01  WS-DB-PASSWORD29    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW29        PIC X(12).
       01  WS-POS30            PIC 99.
       01  WS-RECORD30         PIC X(80).
       01  WS-PART30           PIC X(5).
       01  WS-CMD31            PIC X(100).
       01  WS-POS32            PIC 99.
       01  WS-RECORD32         PIC X(80).
       01  WS-PART32           PIC X(5).
       01  WS-POS34            PIC 99.
       01  WS-RECORD34         PIC X(80).
       01  WS-PART34           PIC X(5).
       01  WS-CMD35            PIC X(100).
       01  WS-CMD36            PIC X(100).
       01  WS-FORM38           PIC X(40).
       01  WS-PAGE38           PIC X(80).
       01  WS-FORM43           PIC X(40).
       01  WS-PAGE43           PIC X(80).
       01  WS-STMT44           PIC X(200).
       01  WS-USER45           PIC X(10).
       01  WS-PASSWORD-IN45    PIC X(12).
       01  WS-STMT47           PIC X(200).
       01  WS-EXPORT-PATH48    PIC X(60).
       01  WS-FORM49           PIC X(40).
       01  WS-PAGE49           PIC X(80).
       01  WS-STMT50           PIC X(200).
       01  WS-CMD51            PIC X(100).
       01  WS-DB-PASSWORD54    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW54        PIC X(12).
       01  WS-USER56           PIC X(10).
       01  WS-PASSWORD-IN56    PIC X(12).
       01  WS-DB-PASSWORD57    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW57        PIC X(12).
       01  WS-USER58           PIC X(10).
       01  WS-PASSWORD-IN58    PIC X(12).
       01  WS-USER59           PIC X(10).
       01  WS-PASSWORD-IN59    PIC X(12).
       01  WS-STMT60           PIC X(200).
       01  WS-POS63            PIC 99.
       01  WS-RECORD63         PIC X(80).
       01  WS-PART63           PIC X(5).
       01  WS-USER64           PIC X(10).
       01  WS-PASSWORD-IN64    PIC X(12).
       01  WS-FORM65           PIC X(40).
       01  WS-PAGE65           PIC X(80).
       01  WS-CMD66            PIC X(100).
       01  WS-STMT68           PIC X(200).
       01  WS-CMD69            PIC X(100).
       01  WS-EXPORT-PATH70    PIC X(60).
       01  WS-CMD71            PIC X(100).
       01  WS-DB-PASSWORD72    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW72        PIC X(12).
       01  WS-DB-PASSWORD74    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW74        PIC X(12).
       01  WS-DB-PASSWORD76    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW76        PIC X(12).
       01  WS-USER77           PIC X(10).
       01  WS-PASSWORD-IN77    PIC X(12).
       01  WS-CMD80            PIC X(100).
       01  WS-STMT82           PIC X(200).
       01  WS-EXPORT-PATH85    PIC X(60).
       01  WS-STMT86           PIC X(200).
       01  WS-CMD87            PIC X(100).
       01  WS-CMD88            PIC X(100).
       01  WS-STMT89           PIC X(200).
       01  WS-STMT90           PIC X(200).
       01  WS-STMT92           PIC X(200).
       01  WS-USER93           PIC X(10).
       01  WS-PASSWORD-IN93    PIC X(12).
       01  WS-STMT94           PIC X(200).
       01  WS-STMT95           PIC X(200).
       01  WS-CMD99            PIC X(100).
       01  WS-POS103            PIC 99.
       01  WS-RECORD103         PIC X(80).
       01  WS-PART103           PIC X(5).
       01  WS-EXPORT-PATH104    PIC X(60).
       01  WS-FORM106           PIC X(40).
       01  WS-PAGE106           PIC X(80).
       01  WS-DB-PASSWORD108    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW108        PIC X(12).
       01  WS-EXPORT-PATH110    PIC X(60).
       01  WS-CMD111            PIC X(100).
       01  WS-EXPORT-PATH115    PIC X(60).
       01  WS-DB-PASSWORD123    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW123        PIC X(12).
       01  WS-STMT124           PIC X(200).
       01  WS-DB-PASSWORD125    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW125        PIC X(12).
       01  WS-STMT128           PIC X(200).
       01  WS-CMD129            PIC X(100).
       01  WS-STMT133           PIC X(200).
       01  WS-EXPORT-PATH135    PIC X(60).
       01  WS-POS136            PIC 99.
       01  WS-RECORD136         PIC X(80).
       01  WS-PART136           PIC X(5).
       01  WS-FORM138           PIC X(40).
       01  WS-PAGE138           PIC X(80).
       01  WS-EXPORT-PATH139    PIC X(60).
       01  WS-FORM140           PIC X(40).
       01  WS-PAGE140           PIC X(80).
       01  WS-USER141           PIC X(10).
       01  WS-PASSWORD-IN141    PIC X(12).
       01  WS-DB-PASSWORD142    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW142        PIC X(12).
       01  WS-USER146           PIC X(10).
       01  WS-PASSWORD-IN146    PIC X(12).
       01  WS-DB-PASSWORD147    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW147        PIC X(12).
       01  WS-CMD148            PIC X(100).
       01  WS-POS151            PIC 99.
       01  WS-RECORD151         PIC X(80).
       01  WS-PART151           PIC X(5).
       01  WS-EXPORT-PATH155    PIC X(60).
       01  WS-FORM156           PIC X(40).
       01  WS-PAGE156           PIC X(80).
       01  WS-EXPORT-PATH157    PIC X(60).
       01  WS-EXPORT-PATH158    PIC X(60).
       01  WS-POS160            PIC 99.
       01  WS-RECORD160         PIC X(80).
       01  WS-PART160           PIC X(5).
       01  WS-USER163           PIC X(10).
       01  WS-PASSWORD-IN163    PIC X(12).
       01  WS-DB-PASSWORD167    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW167        PIC X(12).
       01  WS-USER168           PIC X(10).
       01  WS-PASSWORD-IN168    PIC X(12).
       01  WS-EXPORT-PATH169    PIC X(60).
       01  WS-FORM171           PIC X(40).
       01  WS-PAGE171           PIC X(80).
       01  WS-STMT173           PIC X(200).
       01  WS-EXPORT-PATH174    PIC X(60).
       01  WS-USER175           PIC X(10).
       01  WS-PASSWORD-IN175    PIC X(12).
       01  WS-CODE1           PIC 9 VALUE 1.
       01  WS-STATUS1         PIC X(6) VALUE SPACES.
       01  WS-CODE4           PIC 9 VALUE 1.
       01  WS-STATUS4         PIC X(6) VALUE SPACES.
       01  WS-TITLE5          PIC X(20) VALUE SPACES.
       01  WS-HEADER5         PIC X(40) VALUE SPACES.
       01  WS-CODE6           PIC 9 VALUE 1.
       01  WS-STATUS6         PIC X(6) VALUE SPACES.
       01  WS-TOTAL7          PIC 9(6) VALUE 0.
       01  WS-K7              PIC 99 VALUE 0.
       01  WS-AVERAGE7        PIC 9(6)V99 VALUE 0.
       01  WS-CODE8           PIC 9 VALUE 1.
       01  WS-STATUS8         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT9         PIC 9(6) VALUE 500.
       01  WS-FLAG9           PIC X VALUE 'N'.
       01  WS-TOTAL13          PIC 9(6) VALUE 0.
       01  WS-K13              PIC 99 VALUE 0.
       01  WS-AVERAGE13        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE19          PIC X(20) VALUE SPACES.
       01  WS-HEADER19         PIC X(40) VALUE SPACES.
       01  WS-TITLE23          PIC X(20) VALUE SPACES.
       01  WS-HEADER23         PIC X(40) VALUE SPACES.
       01  WS-CODE24           PIC 9 VALUE 1.
       01  WS-STATUS24         PIC X(6) VALUE SPACES.
       01  WS-TOTAL25          PIC 9(6) VALUE 0.
       01  WS-K25              PIC 99 VALUE 0.
       01  WS-AVERAGE25        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT26         PIC 9(6) VALUE 500.
       01  WS-FLAG26           PIC X VALUE 'N'.
       01  WS-TOTAL27          PIC 9(6) VALUE 0.
       01  WS-K27              PIC 99 VALUE 0.
       01  WS-AVERAGE27        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT33         PIC 9(6) VALUE 500.
       01  WS-FLAG33           PIC X VALUE 'N'.
       01  WS-AMOUNT37         PIC 9(6) VALUE 500.
       01  WS-FLAG37           PIC X VALUE 'N'.
       01  WS-CODE39           PIC 9 VALUE 1.
       01  WS-STATUS39         PIC X(6) VALUE SPACES.
       01  WS-TITLE40          PIC X(20) VALUE SPACES.
       01  WS-HEADER40         PIC X(40) VALUE SPACES.
       01  WS-CODE41           PIC 9 VALUE 1.
       01  WS-STATUS41         PIC X(6) VALUE SPACES.
       01  WS-TOTAL42          PIC 9(6) VALUE 0.
       01  WS-K42              PIC 99 VALUE 0.
       01  WS-AVERAGE42        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT46         PIC 9(6) VALUE 500.
       01  WS-FLAG46           PIC X VALUE 'N'.
       01  WS-AMOUNT52         PIC 9(6) VALUE 500.
       01  WS-FLAG52           PIC X VALUE 'N'.
       01  WS-AMOUNT53         PIC 9(6) VALUE 500.
       01  WS-FLAG53           PIC X VALUE 'N'.
       01  WS-TOTAL55          PIC 9(6) VALUE 0.
       01  WS-K55              PIC 99 VALUE 0.
       01  WS-AVERAGE55        PIC 9(6)V99 VALUE 0.
       01  WS-CODE61           PIC 9 VALUE 1.
       01  WS-STATUS61         PIC X(6) VALUE SPACES.
       01  WS-CODE62           PIC 9 VALUE 1.
       01  WS-STATUS62         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT67         PIC 9(6) VALUE 500.
       01  WS-FLAG67           PIC X VALUE 'N'.
       01  WS-AMOUNT73         PIC 9(6) VALUE 500.
       01  WS-FLAG73           PIC X VALUE 'N'.
       01  WS-AMOUNT75         PIC 9(6) VALUE 500.
       01  WS-FLAG75           PIC X VALUE 'N'.
       01  WS-AMOUNT78         PIC 9(6) VALUE 500.
       01  WS-FLAG78           PIC X VALUE 'N'.
       01  WS-CODE79           PIC 9 VALUE 1.
       01  WS-STATUS79         PIC X(6) VALUE SPACES.
       01  WS-TOTAL81          PIC 9(6) VALUE 0.
       01  WS-K81              PIC 99 VALUE 0.
       01  WS-AVERAGE81        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE83          PIC X(20) VALUE SPACES.
       01  WS-HEADER83         PIC X(40) VALUE SPACES.
       01  WS-TOTAL84          PIC 9(6) VALUE 0.
       01  WS-K84              PIC 99 VALUE 0.
       01  WS-AVERAGE84        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT91         PIC 9(6) VALUE 500.
       01  WS-FLAG91           PIC X VALUE 'N'.
       01  WS-TOTAL96          PIC 9(6) VALUE 0.
       01  WS-K96              PIC 99 VALUE 0.
       01  WS-AVERAGE96        PIC 9(6)V99 VALUE 0.
       01  WS-CODE97           PIC 9 VALUE 1.
       01  WS-STATUS97         PIC X(6) VALUE SPACES.
       01  WS-TITLE98          PIC X(20) VALUE SPACES.
       01  WS-HEADER98         PIC X(40) VALUE SPACES.
       01  WS-TITLE100          PIC X(20) VALUE SPACES.
       01  WS-HEADER100         PIC X(40) VALUE SPACES.
       01  WS-CODE101           PIC 9 VALUE 1.
       01  WS-STATUS101         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT102         PIC 9(6) VALUE 500.
       01  WS-FLAG102           PIC X VALUE 'N'.
       01  WS-AMOUNT105         PIC 9(6) VALUE 500.
       01  WS-FLAG105           PIC X VALUE 'N'.
       01  WS-TOTAL107          PIC 9(6) VALUE 0.
       01  WS-K107              PIC 99 VALUE 0.
       01  WS-AVERAGE107        PIC 9(6)V99 VALUE 0.
       01  WS-CODE109           PIC 9 VALUE 1.
       01  WS-STATUS109         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT112         PIC 9(6) VALUE 500.
       01  WS-FLAG112           PIC X VALUE 'N'.
       01  WS-CODE113           PIC 9 VALUE 1.
       01  WS-STATUS113         PIC X(6) VALUE SPACES.
       01  WS-CODE114           PIC 9 VALUE 1.
       01  WS-STATUS114         PIC X(6) VALUE SPACES.
       01  WS-CODE116           PIC 9 VALUE 1.
       01  WS-STATUS116         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT117         PIC 9(6) VALUE 500.
       01  WS-FLAG117           PIC X VALUE 'N'.
       01  WS-AMOUNT118         PIC 9(6) VALUE 500.
       01  WS-FLAG118           PIC X VALUE 'N'.
       01  WS-TITLE119          PIC X(20) VALUE SPACES.
       01  WS-HEADER119         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT120         PIC 9(6) VALUE 500.
       01  WS-FLAG120           PIC X VALUE 'N'.
       01  WS-TITLE121          PIC X(20) VALUE SPACES.
       01  WS-HEADER121         PIC X(40) VALUE SPACES.
       01  WS-CODE122           PIC 9 VALUE 1.
       01  WS-STATUS122         PIC X(6) VALUE SPACES.
       01  WS-TOTAL126          PIC 9(6) VALUE 0.
       01  WS-K126              PIC 99 VALUE 0.
       01  WS-AVERAGE126        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE127          PIC X(20) VALUE SPACES.
       01  WS-HEADER127         PIC X(40) VALUE SPACES.
       01  WS-TOTAL130          PIC 9(6) VALUE 0.
       01  WS-K130              PIC 99 VALUE 0.
       01  WS-AVERAGE130        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL131          PIC 9(6) VALUE 0.
       01  WS-K131              PIC 99 VALUE 0.
       01  WS-AVERAGE131        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL132          PIC 9(6) VALUE 0.
       01  WS-K132              PIC 99 VALUE 0.
       01  WS-AVERAGE132        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL134          PIC 9(6) VALUE 0.
       01  WS-K134              PIC 99 VALUE 0.
       01  WS-AVERAGE134        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT137         PIC 9(6) VALUE 500.
       01  WS-FLAG137           PIC X VALUE 'N'.
       01  WS-TITLE143          PIC X(20) VALUE SPACES.
       01  WS-HEADER143         PIC X(40) VALUE SPACES.
       01  WS-CODE144           PIC 9 VALUE 1.
       01  WS-STATUS144         PIC X(6) VALUE SPACES.
       01  WS-TOTAL145          PIC 9(6) VALUE 0.
       01  WS-K145              PIC 99 VALUE 0.
       01  WS-AVERAGE145        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE149          PIC X(20) VALUE SPACES.
       01  WS-HEADER149         PIC X(40) VALUE SPACES.
       01  WS-TOTAL150          PIC 9(6) VALUE 0.
       01  WS-K150              PIC 99 VALUE 0.
       01  WS-AVERAGE150        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT152         PIC 9(6) VALUE 500.
       01  WS-FLAG152           PIC X VALUE 'N'.
       01  WS-TITLE153          PIC X(20) VALUE SPACES.
       01  WS-HEADER153         PIC X(40) VALUE SPACES.
       01  WS-TOTAL154          PIC 9(6) VALUE 0.
       01  WS-K154              PIC 99 VALUE 0.
       01  WS-AVERAGE154        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL159          PIC 9(6) VALUE 0.
       01  WS-K159              PIC 99 VALUE 0.
       01  WS-AVERAGE159        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL161          PIC 9(6) VALUE 0.
       01  WS-K161              PIC 99 VALUE 0.
       01  WS-AVERAGE161        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT162         PIC 9(6) VALUE 500.
       01  WS-FLAG162           PIC X VALUE 'N'.
       01  WS-TITLE164          PIC X(20) VALUE SPACES.
       01  WS-HEADER164         PIC X(40) VALUE SPACES.
       01  WS-TOTAL165          PIC 9(6) VALUE 0.
       01  WS-K165              PIC 99 VALUE 0.
       01  WS-AVERAGE165        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT166         PIC 9(6) VALUE 500.
       01  WS-FLAG166           PIC X VALUE 'N'.
       01  WS-AMOUNT170         PIC 9(6) VALUE 500.
       01  WS-FLAG170           PIC X VALUE 'N'.
       01  WS-TOTAL172          PIC 9(6) VALUE 0.
       01  WS-K172              PIC 99 VALUE 0.
       01  WS-AVERAGE172        PIC 9(6)V99 VALUE 0.
       LINKAGE SECTION.
       01  LK-PATH3           PIC X(60).
       01  LK-PATH11           PIC X(60).
       01  LK-FILTER12         PIC X(100).
       01  LK-NAME15           PIC X(40).
       01  LK-NAME18           PIC X(40).
       01  LK-FILTER22         PIC X(100).
       01  LK-NAME28           PIC X(40).
       01  LK-NAME31           PIC X(40).
       01  LK-NAME35           PIC X(40).
       01  LK-NAME36           PIC X(40).
       01  LK-FILTER44         PIC X(100).
       01  LK-FILTER47         PIC X(100).
       01  LK-PATH48           PIC X(60).
       01  LK-FILTER50         PIC X(100).
       01  LK-NAME51           PIC X(40).
       01  LK-FILTER60         PIC X(100).
       01  LK-NAME66           PIC X(40).
       01  LK-FILTER68         PIC X(100).
       01  LK-NAME69           PIC X(40).
       01  LK-PATH70           PIC X(60).
       01  LK-NAME71           PIC X(40).
       01  LK-NAME80           PIC X(40).
       01  LK-FILTER82         PIC X(100).
       01  LK-PATH85           PIC X(60).
       01  LK-FILTER86         PIC X(100).
       01  LK-NAME87           PIC X(40).
       01  LK-NAME88           PIC X(40).
       01  LK-FILTER89         PIC X(100).
       01  LK-FILTER90         PIC X(100).
       01  LK-FILTER92         PIC X(100).
       01  LK-FILTER94         PIC X(100).
       01  LK-FILTER95         PIC X(100).
       01  LK-NAME99           PIC X(40).
       01  LK-PATH104           PIC X(60).
       01  LK-PATH110           PIC X(60).
       01  LK-NAME111           PIC X(40).
       01  LK-PATH115           PIC X(60).
       01  LK-FILTER124         PIC X(100).
       01  LK-FILTER128         PIC X(100).
       01  LK-NAME129           PIC X(40).
       01  LK-FILTER133         PIC X(100).
       01  LK-PATH135           PIC X(60).
       01  LK-PATH139           PIC X(60).
       01  LK-NAME148           PIC X(40).
       01  LK-PATH155           PIC X(60).
       01  LK-PATH157           PIC X(60).
       01  LK-PATH158           PIC X(60).
       01  LK-PATH169           PIC X(60).
       01  LK-FILTER173         PIC X(100).
       01  LK-PATH174           PIC X(60).
       PROCEDURE DIVISION USING LK-PATH3 LK-PATH11 LK-FILTER12 LK-NAME15 LK-NAME18 LK-FILTER22 LK-NAME28 LK-NAME31 LK-NAME35 LK-NAME36 LK-FILTER44 LK-FILTER47 LK-PATH48 LK-FILTER50 LK-NAME51 LK-FILTER60 LK-NAME66 LK-FILTER68 LK-NAME69 LK-PATH70 LK-NAME71 LK-NAME80 LK-FILTER82 LK-PATH85 LK-FILTER86 LK-NAME87 LK-NAME88 LK-FILTER89 LK-FILTER90 LK-FILTER92 LK-FILTER94 LK-FILTER95 LK-NAME99 LK-PATH104 LK-PATH110 LK-NAME111 LK-PATH115 LK-FILTER124 LK-FILTER128 LK-NAME129 LK-FILTER133 LK-PATH135 LK-PATH139 LK-NAME148 LK-PATH155 LK-PATH157 LK-PATH158 LK-PATH169 LK-FILTER173 LK-PATH174.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       PREPARE-QUERY-SAFE124.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT124.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT124 END-EXEC.

       CLASSIFY-CODE101.
           EVALUATE WS-CODE101
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS101
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS101
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS101
           END-EVALUATE.

       CHECK-LIMIT117.
           IF WS-AMOUNT117 > 1000
               MOVE 'Y' TO WS-FLAG117
           ELSE
               MOVE 'N' TO WS-FLAG117
           END-IF.

       CONVERT-FILE-SAFE28.
           MOVE "convert /srv/in/report.txt" TO WS-CMD28.
           CALL 'SYSTEM' USING WS-CMD28.

       LOG-LOGIN146.
           DISPLAY 'LOGIN ' WS-USER146 ' ' WS-PASSWORD-IN146.

       ECHO-NAME-SAFE43.
           MOVE '<p>Thank you</p>' TO WS-PAGE43.
           EXEC CICS WEB SEND FROM(WS-PAGE43) END-EXEC.

       COMPUTE-TOTALS172.
           MOVE 0 TO WS-TOTAL172.
           PERFORM VARYING WS-K172 FROM 1 BY 1 UNTIL WS-K172 > 10
               ADD WS-K172 TO WS-TOTAL172
           END-PERFORM.
           COMPUTE WS-AVERAGE172 = WS-TOTAL172 / 10.

       EXTRACT-FIELD16.
           ACCEPT WS-POS16.
           MOVE WS-RECORD16(WS-POS16:5) TO WS-PART16.

       LOG-LOGIN56.
           DISPLAY 'LOGIN ' WS-USER56 ' ' WS-PASSWORD-IN56.

       COMPUTE-TOTALS150.
           MOVE 0 TO WS-TOTAL150.
           PERFORM VARYING WS-K150 FROM 1 BY 1 UNTIL WS-K150 > 10
               ADD WS-K150 TO WS-TOTAL150
           END-PERFORM.
           COMPUTE WS-AVERAGE150 = WS-TOTAL150 / 10.

       ECHO-NAME65.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM65) END-EXEC.
           STRING '<p>' WS-FORM65 '</p>' DELIMITED BY SIZE INTO WS-PAGE65.
           EXEC CICS WEB SEND FROM(WS-PAGE65) END-EXEC.

       PREPARE-QUERY-SAFE89.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT89.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT89 END-EXEC.

       WRITE-EXPORT139.
           MOVE LK-PATH139 TO WS-EXPORT-PATH139.
           OPEN OUTPUT EXPORT-FILE139.
           CLOSE EXPORT-FILE139.

       FORMAT-HEADER127.
           MOVE 'MONTHLY REPORT' TO WS-TITLE127.
           STRING WS-TITLE127 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER127.
           DISPLAY WS-HEADER127.

       CHECK-LIMIT91.
           IF WS-AMOUNT91 > 1000
               MOVE 'Y' TO WS-FLAG91
           ELSE
               MOVE 'N' TO WS-FLAG91
           END-IF.

       CONVERT-FILE-SAFE69.
           MOVE "convert /srv/in/report.txt" TO WS-CMD69.
           CALL 'SYSTEM' USING WS-CMD69.

       CHECK-LIMIT105.
           IF WS-AMOUNT105 > 1000
               MOVE 'Y' TO WS-FLAG105
           ELSE
               MOVE 'N' TO WS-FLAG105
           END-IF.

       COMPUTE-TOTALS55.
           MOVE 0 TO WS-TOTAL55.
           PERFORM VARYING WS-K55 FROM 1 BY 1 UNTIL WS-K55 > 10
               ADD WS-K55 TO WS-TOTAL55
           END-PERFORM.
           COMPUTE WS-AVERAGE55 = WS-TOTAL55 / 10.

       CHECK-LIMIT112.
           IF WS-AMOUNT112 > 1000
               MOVE 'Y' TO WS-FLAG112
           ELSE
               MOVE 'N' TO WS-FLAG112
           END-IF.

       EXTRACT-FIELD-SAFE160.
           ACCEPT WS-POS160.
           IF WS-POS160 IS NUMERIC AND WS-POS160 > 0 AND WS-POS160 < 76
               MOVE WS-RECORD160(WS-POS160:5) TO WS-PART160
           END-IF.

       LOG-LOGIN93.
           DISPLAY 'LOGIN ' WS-USER93 ' ' WS-PASSWORD-IN93.

       CHECK-LIMIT67.
           IF WS-AMOUNT67 > 1000
               MOVE 'Y' TO WS-FLAG67
           ELSE
               MOVE 'N' TO WS-FLAG67
           END-IF.

       COMPUTE-TOTALS96.
           MOVE 0 TO WS-TOTAL96.
           PERFORM VARYING WS-K96 FROM 1 BY 1 UNTIL WS-K96 > 10
               ADD WS-K96 TO WS-TOTAL96
           END-PERFORM.
           COMPUTE WS-AVERAGE96 = WS-TOTAL96 / 10.

       PREPARE-QUERY-SAFE50.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT50.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT50 END-EXEC.

       CHECK-LIMIT137.
           IF WS-AMOUNT137 > 1000
               MOVE 'Y' TO WS-FLAG137
           ELSE
               MOVE 'N' TO WS-FLAG137
           END-IF.

       FORMAT-HEADER83.
           MOVE 'MONTHLY REPORT' TO WS-TITLE83.
           STRING WS-TITLE83 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER83.
           DISPLAY WS-HEADER83.

       CHECK-LIMIT152.
           IF WS-AMOUNT152 > 1000
               MOVE 'Y' TO WS-FLAG152
           ELSE
               MOVE 'N' TO WS-FLAG152
           END-IF.

       PREPARE-QUERY22.
           MOVE LK-FILTER22 TO WS-STMT22.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT22 END-EXEC.

       CHECK-LIMIT120.
           IF WS-AMOUNT120 > 1000
               MOVE 'Y' TO WS-FLAG120
           ELSE
               MOVE 'N' TO WS-FLAG120
           END-IF.

       CLASSIFY-CODE79.
           EVALUATE WS-CODE79
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS79
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS79
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS79
           END-EVALUATE.

       LOG-LOGIN17.
           DISPLAY 'LOGIN ' WS-USER17 ' ' WS-PASSWORD-IN17.

       WRITE-EXPORT169.
           MOVE LK-PATH169 TO WS-EXPORT-PATH169.
           OPEN OUTPUT EXPORT-FILE169.
           CLOSE EXPORT-FILE169.

       LOG-LOGIN-SAFE163.
           DISPLAY 'LOGIN ' WS-USER163.

       CHECK-LIMIT75.
           IF WS-AMOUNT75 > 1000
               MOVE 'Y' TO WS-FLAG75
           ELSE
               MOVE 'N' TO WS-FLAG75
           END-IF.

       WRITE-EXPORT-SAFE155.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH155.
           OPEN OUTPUT EXPORT-FILE155.
           CLOSE EXPORT-FILE155.

       WRITE-EXPORT174.
           MOVE LK-PATH174 TO WS-EXPORT-PATH174.
           OPEN OUTPUT EXPORT-FILE174.
           CLOSE EXPORT-FILE174.

       FORMAT-HEADER19.
           MOVE 'MONTHLY REPORT' TO WS-TITLE19.
           STRING WS-TITLE19 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER19.
           DISPLAY WS-HEADER19.

       CONNECT-DB-SAFE123.
           ACCEPT WS-CONN-PW123 FROM ENVIRONMENT 'DB_PASSWORD'.

       ECHO-NAME49.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM49) END-EXEC.
           STRING '<p>' WS-FORM49 '</p>' DELIMITED BY SIZE INTO WS-PAGE49.
           EXEC CICS WEB SEND FROM(WS-PAGE49) END-EXEC.

       ECHO-NAME106.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM106) END-EXEC.
           STRING '<p>' WS-FORM106 '</p>' DELIMITED BY SIZE INTO WS-PAGE106.
           EXEC CICS WEB SEND FROM(WS-PAGE106) END-EXEC.

       COMPUTE-TOTALS42.
           MOVE 0 TO WS-TOTAL42.
           PERFORM VARYING WS-K42 FROM 1 BY 1 UNTIL WS-K42 > 10
               ADD WS-K42 TO WS-TOTAL42
           END-PERFORM.
           COMPUTE WS-AVERAGE42 = WS-TOTAL42 / 10.

       CONVERT-FILE129.
           STRING "convert " LK-NAME129 DELIMITED BY SIZE INTO WS-CMD129.
           CALL 'SYSTEM' USING WS-CMD129.

       LOG-LOGIN-SAFE141.
           DISPLAY 'LOGIN ' WS-USER141.

       CHECK-LIMIT162.
           IF WS-AMOUNT162 > 1000
               MOVE 'Y' TO WS-FLAG162
           ELSE
               MOVE 'N' TO WS-FLAG162
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

       LOG-LOGIN59.
           DISPLAY 'LOGIN ' WS-USER59 ' ' WS-PASSWORD-IN59.

       PREPARE-QUERY-SAFE95.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT95.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT95 END-EXEC.

       CHECK-LIMIT26.
           IF WS-AMOUNT26 > 1000
               MOVE 'Y' TO WS-FLAG26
           ELSE
               MOVE 'N' TO WS-FLAG26
           END-IF.

       PREPARE-QUERY-SAFE94.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT94.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT94 END-EXEC.

       CONNECT-DB-SAFE57.
           ACCEPT WS-CONN-PW57 FROM ENVIRONMENT 'DB_PASSWORD'.

       CONNECT-DB-SAFE147.
           ACCEPT WS-CONN-PW147 FROM ENVIRONMENT 'DB_PASSWORD'.

       FORMAT-HEADER100.
           MOVE 'MONTHLY REPORT' TO WS-TITLE100.
           STRING WS-TITLE100 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER100.
           DISPLAY WS-HEADER100.

       ECHO-NAME38.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM38) END-EXEC.
           STRING '<p>' WS-FORM38 '</p>' DELIMITED BY SIZE INTO WS-PAGE38.
           EXEC CICS WEB SEND FROM(WS-PAGE38) END-EXEC.

       PREPARE-QUERY86.
           MOVE LK-FILTER86 TO WS-STMT86.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT86 END-EXEC.

       CONVERT-FILE-SAFE87.
           MOVE "convert /srv/in/report.txt" TO WS-CMD87.
           CALL 'SYSTEM' USING WS-CMD87.

       CLASSIFY-CODE41.
           EVALUATE WS-CODE41
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS41
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS41
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS41
           END-EVALUATE.

       CLASSIFY-CODE1.
           EVALUATE WS-CODE1
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS1
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS1
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS1
           END-EVALUATE.

       ECHO-NAME-SAFE171.
           MOVE '<p>Thank you</p>' TO WS-PAGE171.
           EXEC CICS WEB SEND FROM(WS-PAGE171) END-EXEC.

       COMPUTE-TOTALS159.
           MOVE 0 TO WS-TOTAL159.
           PERFORM VARYING WS-K159 FROM 1 BY 1 UNTIL WS-K159 > 10
               ADD WS-K159 TO WS-TOTAL159
           END-PERFORM.
           COMPUTE WS-AVERAGE159 = WS-TOTAL159 / 10.

       COMPUTE-TOTALS25.
           MOVE 0 TO WS-TOTAL25.
           PERFORM VARYING WS-K25 FROM 1 BY 1 UNTIL WS-K25 > 10
               ADD WS-K25 TO WS-TOTAL25
           END-PERFORM.
           COMPUTE WS-AVERAGE25 = WS-TOTAL25 / 10.

       FORMAT-HEADER23.
           MOVE 'MONTHLY REPORT' TO WS-TITLE23.
           STRING WS-TITLE23 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER23.
           DISPLAY WS-HEADER23.

       PREPARE-QUERY-SAFE90.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT90.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT90 END-EXEC.

       COMPUTE-TOTALS165.
           MOVE 0 TO WS-TOTAL165.
           PERFORM VARYING WS-K165 FROM 1 BY 1 UNTIL WS-K165 > 10
               ADD WS-K165 TO WS-TOTAL165
           END-PERFORM.
           COMPUTE WS-AVERAGE165 = WS-TOTAL165 / 10.

       FORMAT-HEADER143.
           MOVE 'MONTHLY REPORT' TO WS-TITLE143.
           STRING WS-TITLE143 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER143.
           DISPLAY WS-HEADER143.

       PREPARE-QUERY-SAFE12.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT12.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT12 END-EXEC.

       CHECK-LIMIT73.
           IF WS-AMOUNT73 > 1000
               MOVE 'Y' TO WS-FLAG73
           ELSE
               MOVE 'N' TO WS-FLAG73
           END-IF.

       COMPUTE-TOTALS13.
           MOVE 0 TO WS-TOTAL13.
           PERFORM VARYING WS-K13 FROM 1 BY 1 UNTIL WS-K13 > 10
               ADD WS-K13 TO WS-TOTAL13
           END-PERFORM.
           COMPUTE WS-AVERAGE13 = WS-TOTAL13 / 10.

       CLASSIFY-CODE39.
           EVALUATE WS-CODE39
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS39
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS39
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS39
           END-EVALUATE.

       PREPARE-QUERY-SAFE133.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT133.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT133 END-EXEC.

       CLASSIFY-CODE144.
           EVALUATE WS-CODE144
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS144
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS144
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS144
           END-EVALUATE.

       LOG-LOGIN10.
           DISPLAY 'LOGIN ' WS-USER10 ' ' WS-PASSWORD-IN10.

       FORMAT-HEADER98.
           MOVE 'MONTHLY REPORT' TO WS-TITLE98.
           STRING WS-TITLE98 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER98.
           DISPLAY WS-HEADER98.

       ECHO-NAME138.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM138) END-EXEC.
           STRING '<p>' WS-FORM138 '</p>' DELIMITED BY SIZE INTO WS-PAGE138.
           EXEC CICS WEB SEND FROM(WS-PAGE138) END-EXEC.

       EXTRACT-FIELD151.
           ACCEPT WS-POS151.
           MOVE WS-RECORD151(WS-POS151:5) TO WS-PART151.

       CONVERT-FILE-SAFE35.
           MOVE "convert /srv/in/report.txt" TO WS-CMD35.
           CALL 'SYSTEM' USING WS-CMD35.

       CHECK-LIMIT118.
           IF WS-AMOUNT118 > 1000
               MOVE 'Y' TO WS-FLAG118
           ELSE
               MOVE 'N' TO WS-FLAG118
           END-IF.

       EXTRACT-FIELD2.
           ACCEPT WS-POS2.
           MOVE WS-RECORD2(WS-POS2:5) TO WS-PART2.

       CLASSIFY-CODE109.
           EVALUATE WS-CODE109
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS109
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS109
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS109
           END-EVALUATE.

       CLASSIFY-CODE6.
           EVALUATE WS-CODE6
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS6
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS6
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS6
           END-EVALUATE.

       LOG-LOGIN175.
           DISPLAY 'LOGIN ' WS-USER175 ' ' WS-PASSWORD-IN175.

       CONVERT-FILE36.
           STRING "convert " LK-NAME36 DELIMITED BY SIZE INTO WS-CMD36.
           CALL 'SYSTEM' USING WS-CMD36.

       LOG-LOGIN-SAFE58.
           DISPLAY 'LOGIN ' WS-USER58.

       COMPUTE-TOTALS132.
           MOVE 0 TO WS-TOTAL132.
           PERFORM VARYING WS-K132 FROM 1 BY 1 UNTIL WS-K132 > 10
               ADD WS-K132 TO WS-TOTAL132
           END-PERFORM.
           COMPUTE WS-AVERAGE132 = WS-TOTAL132 / 10.

       WRITE-EXPORT-SAFE48.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH48.
           OPEN OUTPUT EXPORT-FILE48.
           CLOSE EXPORT-FILE48.

       WRITE-EXPORT135.
           MOVE LK-PATH135 TO WS-EXPORT-PATH135.
           OPEN OUTPUT EXPORT-FILE135.
           CLOSE EXPORT-FILE135.

       WRITE-EXPORT-SAFE115.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH115.
           OPEN OUTPUT EXPORT-FILE115.
           CLOSE EXPORT-FILE115.

       PREPARE-QUERY44.
           MOVE LK-FILTER44 TO WS-STMT44.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT44 END-EXEC.

       COMPUTE-TOTALS161.
           MOVE 0 TO WS-TOTAL161.
           PERFORM VARYING WS-K161 FROM 1 BY 1 UNTIL WS-K161 > 10
               ADD WS-K161 TO WS-TOTAL161
           END-PERFORM.
           COMPUTE WS-AVERAGE161 = WS-TOTAL161 / 10.

       PREPARE-QUERY-SAFE47.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT47.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT47 END-EXEC.

       CONNECT-DB-SAFE74.
           ACCEPT WS-CONN-PW74 FROM ENVIRONMENT 'DB_PASSWORD'.

       ECHO-NAME14.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM14) END-EXEC.
           STRING '<p>' WS-FORM14 '</p>' DELIMITED BY SIZE INTO WS-PAGE14.
           EXEC CICS WEB SEND FROM(WS-PAGE14) END-EXEC.

       CONVERT-FILE111.
           STRING "convert " LK-NAME111 DELIMITED BY SIZE INTO WS-CMD111.
           CALL 'SYSTEM' USING WS-CMD111.

       CLASSIFY-CODE61.
           EVALUATE WS-CODE61
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS61
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS61
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS61
           END-EVALUATE.

       WRITE-EXPORT-SAFE11.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH11.
           OPEN OUTPUT EXPORT-FILE11.
           CLOSE EXPORT-FILE11.

       CONNECT-DB-SAFE29.
           ACCEPT WS-CONN-PW29 FROM ENVIRONMENT 'DB_PASSWORD'.

       COMPUTE-TOTALS134.
           MOVE 0 TO WS-TOTAL134.
           PERFORM VARYING WS-K134 FROM 1 BY 1 UNTIL WS-K134 > 10
               ADD WS-K134 TO WS-TOTAL134
           END-PERFORM.
           COMPUTE WS-AVERAGE134 = WS-TOTAL134 / 10.

       CHECK-LIMIT78.
           IF WS-AMOUNT78 > 1000
               MOVE 'Y' TO WS-FLAG78
           ELSE
               MOVE 'N' TO WS-FLAG78
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

       PREPARE-QUERY82.
           MOVE LK-FILTER82 TO WS-STMT82.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT82 END-EXEC.

       CONNECT-DB167.
           MOVE WS-DB-PASSWORD167 TO WS-CONN-PW167.

       CONVERT-FILE66.
           STRING "convert " LK-NAME66 DELIMITED BY SIZE INTO WS-CMD66.
           CALL 'SYSTEM' USING WS-CMD66.

       CONVERT-FILE80.
           STRING "convert " LK-NAME80 DELIMITED BY SIZE INTO WS-CMD80.
           CALL 'SYSTEM' USING WS-CMD80.

       WRITE-EXPORT-SAFE157.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH157.
           OPEN OUTPUT EXPORT-FILE157.
           CLOSE EXPORT-FILE157.

       COMPUTE-TOTALS130.
           MOVE 0 TO WS-TOTAL130.
           PERFORM VARYING WS-K130 FROM 1 BY 1 UNTIL WS-K130 > 10
               ADD WS-K130 TO WS-TOTAL130
           END-PERFORM.
           COMPUTE WS-AVERAGE130 = WS-TOTAL130 / 10.

       COMPUTE-TOTALS81.
           MOVE 0 TO WS-TOTAL81.
           PERFORM VARYING WS-K81 FROM 1 BY 1 UNTIL WS-K81 > 10
               ADD WS-K81 TO WS-TOTAL81
           END-PERFORM.
           COMPUTE WS-AVERAGE81 = WS-TOTAL81 / 10.

       FORMAT-HEADER40.
           MOVE 'MONTHLY REPORT' TO WS-TITLE40.
           STRING WS-TITLE40 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER40.
           DISPLAY WS-HEADER40.

       CONVERT-FILE88.
           STRING "convert " LK-NAME88 DELIMITED BY SIZE INTO WS-CMD88.
           CALL 'SYSTEM' USING WS-CMD88.

       COMPUTE-TOTALS126.
           MOVE 0 TO WS-TOTAL126.
           PERFORM VARYING WS-K126 FROM 1 BY 1 UNTIL WS-K126 > 10
               ADD WS-K126 TO WS-TOTAL126
           END-PERFORM.
           COMPUTE WS-AVERAGE126 = WS-TOTAL126 / 10.

       COMPUTE-TOTALS154.
           MOVE 0 TO WS-TOTAL154.
           PERFORM VARYING WS-K154 FROM 1 BY 1 UNTIL WS-K154 > 10
               ADD WS-K154 TO WS-TOTAL154
           END-PERFORM.
           COMPUTE WS-AVERAGE154 = WS-TOTAL154 / 10.

       WRITE-EXPORT104.
           MOVE LK-PATH104 TO WS-EXPORT-PATH104.
           OPEN OUTPUT EXPORT-FILE104.
           CLOSE EXPORT-FILE104.

       CLASSIFY-CODE116.
           EVALUATE WS-CODE116
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS116
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS116
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS116
           END-EVALUATE.

       EXTRACT-FIELD30.
           ACCEPT WS-POS30.
           MOVE WS-RECORD30(WS-POS30:5) TO WS-PART30.

       ECHO-NAME-SAFE140.
           MOVE '<p>Thank you</p>' TO WS-PAGE140.
           EXEC CICS WEB SEND FROM(WS-PAGE140) END-EXEC.

       CONNECT-DB142.
           MOVE WS-DB-PASSWORD142 TO WS-CONN-PW142.

       CHECK-LIMIT46.
           IF WS-AMOUNT46 > 1000
               MOVE 'Y' TO WS-FLAG46
           ELSE
               MOVE 'N' TO WS-FLAG46
           END-IF.

       CONVERT-FILE-SAFE51.
           MOVE "convert /srv/in/report.txt" TO WS-CMD51.
           CALL 'SYSTEM' USING WS-CMD51.

       CLASSIFY-CODE4.
           EVALUATE WS-CODE4
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS4
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS4
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS4
           END-EVALUATE.

       CONNECT-DB108.
           MOVE WS-DB-PASSWORD108 TO WS-CONN-PW108.

       CONNECT-DB-SAFE72.
           ACCEPT WS-CONN-PW72 FROM ENVIRONMENT 'DB_PASSWORD'.

       COMPUTE-TOTALS84.
           MOVE 0 TO WS-TOTAL84.
           PERFORM VARYING WS-K84 FROM 1 BY 1 UNTIL WS-K84 > 10
               ADD WS-K84 TO WS-TOTAL84
           END-PERFORM.
           COMPUTE WS-AVERAGE84 = WS-TOTAL84 / 10.

       CLASSIFY-CODE122.
           EVALUATE WS-CODE122
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS122
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS122
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS122
           END-EVALUATE.

       COMPUTE-TOTALS107.
           MOVE 0 TO WS-TOTAL107.
           PERFORM VARYING WS-K107 FROM 1 BY 1 UNTIL WS-K107 > 10
               ADD WS-K107 TO WS-TOTAL107
           END-PERFORM.
           COMPUTE WS-AVERAGE107 = WS-TOTAL107 / 10.

       PREPARE-QUERY128.
           MOVE LK-FILTER128 TO WS-STMT128.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT128 END-EXEC.

       FORMAT-HEADER153.
           MOVE 'MONTHLY REPORT' TO WS-TITLE153.
           STRING WS-TITLE153 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER153.
           DISPLAY WS-HEADER153.

       WRITE-EXPORT-SAFE85.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH85.
           OPEN OUTPUT EXPORT-FILE85.
           CLOSE EXPORT-FILE85.

       CLASSIFY-CODE97.
           EVALUATE WS-CODE97
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS97
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS97
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS97
           END-EVALUATE.

       WRITE-EXPORT-SAFE158.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH158.
           OPEN OUTPUT EXPORT-FILE158.
           CLOSE EXPORT-FILE158.

       EXTRACT-FIELD103.
           ACCEPT WS-POS103.
           MOVE WS-RECORD103(WS-POS103:5) TO WS-PART103.

       WRITE-EXPORT70.
           MOVE LK-PATH70 TO WS-EXPORT-PATH70.
           OPEN OUTPUT EXPORT-FILE70.
           CLOSE EXPORT-FILE70.

       CHECK-LIMIT33.
           IF WS-AMOUNT33 > 1000
               MOVE 'Y' TO WS-FLAG33
           ELSE
               MOVE 'N' TO WS-FLAG33
           END-IF.

       FORMAT-HEADER119.
           MOVE 'MONTHLY REPORT' TO WS-TITLE119.
           STRING WS-TITLE119 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER119.
           DISPLAY WS-HEADER119.

       LOG-LOGIN77.
           DISPLAY 'LOGIN ' WS-USER77 ' ' WS-PASSWORD-IN77.

       EXTRACT-FIELD136.
           ACCEPT WS-POS136.
           MOVE WS-RECORD136(WS-POS136:5) TO WS-PART136.

       CHECK-LIMIT9.
           IF WS-AMOUNT9 > 1000
               MOVE 'Y' TO WS-FLAG9
           ELSE
               MOVE 'N' TO WS-FLAG9
           END-IF.

       PREPARE-QUERY92.
           MOVE LK-FILTER92 TO WS-STMT92.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT92 END-EXEC.

       ECHO-NAME20.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM20) END-EXEC.
           STRING '<p>' WS-FORM20 '</p>' DELIMITED BY SIZE INTO WS-PAGE20.
           EXEC CICS WEB SEND FROM(WS-PAGE20) END-EXEC.

       FORMAT-HEADER5.
           MOVE 'MONTHLY REPORT' TO WS-TITLE5.
           STRING WS-TITLE5 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER5.
           DISPLAY WS-HEADER5.

       CLASSIFY-CODE114.
           EVALUATE WS-CODE114
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS114
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS114
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS114
           END-EVALUATE.

       CONVERT-FILE-SAFE31.
           MOVE "convert /srv/in/report.txt" TO WS-CMD31.
           CALL 'SYSTEM' USING WS-CMD31.

       CONNECT-DB-SAFE21.
           ACCEPT WS-CONN-PW21 FROM ENVIRONMENT 'DB_PASSWORD'.

       FORMAT-HEADER164.
           MOVE 'MONTHLY REPORT' TO WS-TITLE164.
           STRING WS-TITLE164 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER164.
           DISPLAY WS-HEADER164.

       CONVERT-FILE-SAFE15.
           MOVE "convert /srv/in/report.txt" TO WS-CMD15.
           CALL 'SYSTEM' USING WS-CMD15.

       PREPARE-QUERY-SAFE60.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT60.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT60 END-EXEC.

       CLASSIFY-CODE8.
           EVALUATE WS-CODE8
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS8
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS8
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS8
           END-EVALUATE.

       EXTRACT-FIELD-SAFE34.
           ACCEPT WS-POS34.
           IF WS-POS34 IS NUMERIC AND WS-POS34 > 0 AND WS-POS34 < 76
               MOVE WS-RECORD34(WS-POS34:5) TO WS-PART34
           END-IF.

       CONVERT-FILE18.
           STRING "convert " LK-NAME18 DELIMITED BY SIZE INTO WS-CMD18.
           CALL 'SYSTEM' USING WS-CMD18.

       EXTRACT-FIELD32.
           ACCEPT WS-POS32.
           MOVE WS-RECORD32(WS-POS32:5) TO WS-PART32.

       LOG-LOGIN168.
           DISPLAY 'LOGIN ' WS-USER168 ' ' WS-PASSWORD-IN168.

       CHECK-LIMIT37.
           IF WS-AMOUNT37 > 1000
               MOVE 'Y' TO WS-FLAG37
           ELSE
               MOVE 'N' TO WS-FLAG37
           END-IF.

       LOG-LOGIN64.
           DISPLAY 'LOGIN ' WS-USER64 ' ' WS-PASSWORD-IN64.

       ECHO-NAME-SAFE156.
           MOVE '<p>Thank you</p>' TO WS-PAGE156.
           EXEC CICS WEB SEND FROM(WS-PAGE156) END-EXEC.

       CONVERT-FILE148.
           STRING "convert " LK-NAME148 DELIMITED BY SIZE INTO WS-CMD148.
           CALL 'SYSTEM' USING WS-CMD148.

       CLASSIFY-CODE62.
           EVALUATE WS-CODE62
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS62
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS62
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS62
           END-EVALUATE.

       CONVERT-FILE99.
           STRING "convert " LK-NAME99 DELIMITED BY SIZE INTO WS-CMD99.
           CALL 'SYSTEM' USING WS-CMD99.

       WRITE-EXPORT-SAFE3.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH3.
           OPEN OUTPUT EXPORT-FILE3.
           CLOSE EXPORT-FILE3.

       EXTRACT-FIELD-SAFE63.
           ACCEPT WS-POS63.
           IF WS-POS63 IS NUMERIC AND WS-POS63 > 0 AND WS-POS63 < 76
               MOVE WS-RECORD63(WS-POS63:5) TO WS-PART63
           END-IF.

       CONVERT-FILE-SAFE71.
           MOVE "convert /srv/in/report.txt" TO WS-CMD71.
           CALL 'SYSTEM' USING WS-CMD71.

       COMPUTE-TOTALS27.
           MOVE 0 TO WS-TOTAL27.
           PERFORM VARYING WS-K27 FROM 1 BY 1 UNTIL WS-K27 > 10
               ADD WS-K27 TO WS-TOTAL27
           END-PERFORM.
           COMPUTE WS-AVERAGE27 = WS-TOTAL27 / 10.

       PREPARE-QUERY68.
           MOVE LK-FILTER68 TO WS-STMT68.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT68 END-EXEC.

       CHECK-LIMIT52.
           IF WS-AMOUNT52 > 1000
               MOVE 'Y' TO WS-FLAG52
           ELSE
               MOVE 'N' TO WS-FLAG52
           END-IF.

       FORMAT-HEADER121.
           MOVE 'MONTHLY REPORT' TO WS-TITLE121.
           STRING WS-TITLE121 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER121.
           DISPLAY WS-HEADER121.

       CHECK-LIMIT170.
           IF WS-AMOUNT170 > 1000
               MOVE 'Y' TO WS-FLAG170
           ELSE
               MOVE 'N' TO WS-FLAG170
           END-IF.

       CHECK-LIMIT166.
           IF WS-AMOUNT166 > 1000
               MOVE 'Y' TO WS-FLAG166
           ELSE
               MOVE 'N' TO WS-FLAG166
           END-IF.

       CONNECT-DB125.
           MOVE WS-DB-PASSWORD125 TO WS-CONN-PW125.

       PREPARE-QUERY-SAFE173.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT173.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT173 END-EXEC.

       COMPUTE-TOTALS131.
           MOVE 0 TO WS-TOTAL131.
           PERFORM VARYING WS-K131 FROM 1 BY 1 UNTIL WS-K131 > 10
               ADD WS-K131 TO WS-TOTAL131
           END-PERFORM.
           COMPUTE WS-AVERAGE131 = WS-TOTAL131 / 10.

       COMPUTE-TOTALS145.
           MOVE 0 TO WS-TOTAL145.
           PERFORM VARYING WS-K145 FROM 1 BY 1 UNTIL WS-K145 > 10
               ADD WS-K145 TO WS-TOTAL145
           END-PERFORM.
           COMPUTE WS-AVERAGE145 = WS-TOTAL145 / 10.

       CONNECT-DB76.
           MOVE WS-DB-PASSWORD76 TO WS-CONN-PW76.

       LOG-LOGIN-SAFE45.
           DISPLAY 'LOGIN ' WS-USER45.

       CONNECT-DB-SAFE54.
           ACCEPT WS-CONN-PW54 FROM ENVIRONMENT 'DB_PASSWORD'.

       WRITE-EXPORT-SAFE110.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH110.
           OPEN OUTPUT EXPORT-FILE110.
           CLOSE EXPORT-FILE110.

       CHECK-LIMIT53.
           IF WS-AMOUNT53 > 1000
               MOVE 'Y' TO WS-FLAG53
           ELSE
               MOVE 'N' TO WS-FLAG53
           END-IF.

       FORMAT-HEADER149.
           MOVE 'MONTHLY REPORT' TO WS-TITLE149.
           STRING WS-TITLE149 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER149.
           DISPLAY WS-HEADER149.

       COMPUTE-TOTALS7.
           MOVE 0 TO WS-TOTAL7.
           PERFORM VARYING WS-K7 FROM 1 BY 1 UNTIL WS-K7 > 10
               ADD WS-K7 TO WS-TOTAL7
           END-PERFORM.
           COMPUTE WS-AVERAGE7 = WS-TOTAL7 / 10.

       CHECK-LIMIT102.
           IF WS-AMOUNT102 > 1000
               MOVE 'Y' TO WS-FLAG102
           ELSE
               MOVE 'N' TO WS-FLAG102
           END-IF.

