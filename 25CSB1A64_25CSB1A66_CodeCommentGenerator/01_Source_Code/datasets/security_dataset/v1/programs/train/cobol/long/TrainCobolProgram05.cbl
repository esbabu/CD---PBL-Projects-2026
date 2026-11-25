       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTR05.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EXPORT-FILE21 ASSIGN TO DYNAMIC WS-EXPORT-PATH21
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE28 ASSIGN TO DYNAMIC WS-EXPORT-PATH28
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE41 ASSIGN TO DYNAMIC WS-EXPORT-PATH41
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE62 ASSIGN TO DYNAMIC WS-EXPORT-PATH62
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE69 ASSIGN TO DYNAMIC WS-EXPORT-PATH69
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE71 ASSIGN TO DYNAMIC WS-EXPORT-PATH71
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE74 ASSIGN TO DYNAMIC WS-EXPORT-PATH74
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE75 ASSIGN TO DYNAMIC WS-EXPORT-PATH75
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE76 ASSIGN TO DYNAMIC WS-EXPORT-PATH76
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE80 ASSIGN TO DYNAMIC WS-EXPORT-PATH80
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE84 ASSIGN TO DYNAMIC WS-EXPORT-PATH84
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE85 ASSIGN TO DYNAMIC WS-EXPORT-PATH85
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE91 ASSIGN TO DYNAMIC WS-EXPORT-PATH91
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE94 ASSIGN TO DYNAMIC WS-EXPORT-PATH94
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE107 ASSIGN TO DYNAMIC WS-EXPORT-PATH107
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE129 ASSIGN TO DYNAMIC WS-EXPORT-PATH129
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE140 ASSIGN TO DYNAMIC WS-EXPORT-PATH140
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE157 ASSIGN TO DYNAMIC WS-EXPORT-PATH157
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE162 ASSIGN TO DYNAMIC WS-EXPORT-PATH162
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE165 ASSIGN TO DYNAMIC WS-EXPORT-PATH165
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE173 ASSIGN TO DYNAMIC WS-EXPORT-PATH173
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE182 ASSIGN TO DYNAMIC WS-EXPORT-PATH182
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE184 ASSIGN TO DYNAMIC WS-EXPORT-PATH184
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE201 ASSIGN TO DYNAMIC WS-EXPORT-PATH201
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  EXPORT-FILE21.
       01  EXPORT-LINE21         PIC X(80).
       FD  EXPORT-FILE28.
       01  EXPORT-LINE28         PIC X(80).
       FD  EXPORT-FILE41.
       01  EXPORT-LINE41         PIC X(80).
       FD  EXPORT-FILE62.
       01  EXPORT-LINE62         PIC X(80).
       FD  EXPORT-FILE69.
       01  EXPORT-LINE69         PIC X(80).
       FD  EXPORT-FILE71.
       01  EXPORT-LINE71         PIC X(80).
       FD  EXPORT-FILE74.
       01  EXPORT-LINE74         PIC X(80).
       FD  EXPORT-FILE75.
       01  EXPORT-LINE75         PIC X(80).
       FD  EXPORT-FILE76.
       01  EXPORT-LINE76         PIC X(80).
       FD  EXPORT-FILE80.
       01  EXPORT-LINE80         PIC X(80).
       FD  EXPORT-FILE84.
       01  EXPORT-LINE84         PIC X(80).
       FD  EXPORT-FILE85.
       01  EXPORT-LINE85         PIC X(80).
       FD  EXPORT-FILE91.
       01  EXPORT-LINE91         PIC X(80).
       FD  EXPORT-FILE94.
       01  EXPORT-LINE94         PIC X(80).
       FD  EXPORT-FILE107.
       01  EXPORT-LINE107         PIC X(80).
       FD  EXPORT-FILE129.
       01  EXPORT-LINE129         PIC X(80).
       FD  EXPORT-FILE140.
       01  EXPORT-LINE140         PIC X(80).
       FD  EXPORT-FILE157.
       01  EXPORT-LINE157         PIC X(80).
       FD  EXPORT-FILE162.
       01  EXPORT-LINE162         PIC X(80).
       FD  EXPORT-FILE165.
       01  EXPORT-LINE165         PIC X(80).
       FD  EXPORT-FILE173.
       01  EXPORT-LINE173         PIC X(80).
       FD  EXPORT-FILE182.
       01  EXPORT-LINE182         PIC X(80).
       FD  EXPORT-FILE184.
       01  EXPORT-LINE184         PIC X(80).
       FD  EXPORT-FILE201.
       01  EXPORT-LINE201         PIC X(80).
       WORKING-STORAGE SECTION.
       01  WS-FORM1           PIC X(40).
       01  WS-PAGE1           PIC X(80).
       01  WS-USER2           PIC X(10).
       01  WS-PASSWORD-IN2    PIC X(12).
       01  WS-POS4            PIC 99.
       01  WS-RECORD4         PIC X(80).
       01  WS-PART4           PIC X(5).
       01  WS-FORM5           PIC X(40).
       01  WS-PAGE5           PIC X(80).
       01  WS-USER6           PIC X(10).
       01  WS-PASSWORD-IN6    PIC X(12).
       01  WS-DB-PASSWORD8    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW8        PIC X(12).
       01  WS-POS9            PIC 99.
       01  WS-RECORD9         PIC X(80).
       01  WS-PART9           PIC X(5).
       01  WS-POS11            PIC 99.
       01  WS-RECORD11         PIC X(80).
       01  WS-PART11           PIC X(5).
       01  WS-DB-PASSWORD13    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW13        PIC X(12).
       01  WS-USER14           PIC X(10).
       01  WS-PASSWORD-IN14    PIC X(12).
       01  WS-USER15           PIC X(10).
       01  WS-PASSWORD-IN15    PIC X(12).
       01  WS-STMT17           PIC X(200).
       01  WS-POS18            PIC 99.
       01  WS-RECORD18         PIC X(80).
       01  WS-PART18           PIC X(5).
       01  WS-POS20            PIC 99.
       01  WS-RECORD20         PIC X(80).
       01  WS-PART20           PIC X(5).
       01  WS-EXPORT-PATH21    PIC X(60).
       01  WS-FORM22           PIC X(40).
       01  WS-PAGE22           PIC X(80).
       01  WS-FORM23           PIC X(40).
       01  WS-PAGE23           PIC X(80).
       01  WS-DB-PASSWORD27    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW27        PIC X(12).
       01  WS-EXPORT-PATH28    PIC X(60).
       01  WS-POS31            PIC 99.
       01  WS-RECORD31         PIC X(80).
       01  WS-PART31           PIC X(5).
       01  WS-FORM33           PIC X(40).
       01  WS-PAGE33           PIC X(80).
       01  WS-CMD34            PIC X(100).
       01  WS-FORM35           PIC X(40).
       01  WS-PAGE35           PIC X(80).
       01  WS-FORM36           PIC X(40).
       01  WS-PAGE36           PIC X(80).
       01  WS-DB-PASSWORD37    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW37        PIC X(12).
       01  WS-STMT38           PIC X(200).
       01  WS-FORM40           PIC X(40).
       01  WS-PAGE40           PIC X(80).
       01  WS-EXPORT-PATH41    PIC X(60).
       01  WS-FORM43           PIC X(40).
       01  WS-PAGE43           PIC X(80).
       01  WS-DB-PASSWORD47    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW47        PIC X(12).
       01  WS-DB-PASSWORD50    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW50        PIC X(12).
       01  WS-FORM53           PIC X(40).
       01  WS-PAGE53           PIC X(80).
       01  WS-EXPORT-PATH62    PIC X(60).
       01  WS-USER65           PIC X(10).
       01  WS-PASSWORD-IN65    PIC X(12).
       01  WS-DB-PASSWORD66    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW66        PIC X(12).
       01  WS-EXPORT-PATH69    PIC X(60).
       01  WS-EXPORT-PATH71    PIC X(60).
       01  WS-EXPORT-PATH74    PIC X(60).
       01  WS-EXPORT-PATH75    PIC X(60).
       01  WS-EXPORT-PATH76    PIC X(60).
       01  WS-STMT78           PIC X(200).
       01  WS-FORM79           PIC X(40).
       01  WS-PAGE79           PIC X(80).
       01  WS-EXPORT-PATH80    PIC X(60).
       01  WS-CMD81            PIC X(100).
       01  WS-FORM82           PIC X(40).
       01  WS-PAGE82           PIC X(80).
       01  WS-DB-PASSWORD83    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW83        PIC X(12).
       01  WS-EXPORT-PATH84    PIC X(60).
       01  WS-EXPORT-PATH85    PIC X(60).
       01  WS-USER86           PIC X(10).
       01  WS-PASSWORD-IN86    PIC X(12).
       01  WS-STMT88           PIC X(200).
       01  WS-STMT89           PIC X(200).
       01  WS-EXPORT-PATH91    PIC X(60).
       01  WS-STMT92           PIC X(200).
       01  WS-CMD93            PIC X(100).
       01  WS-EXPORT-PATH94    PIC X(60).
       01  WS-STMT95           PIC X(200).
       01  WS-FORM96           PIC X(40).
       01  WS-PAGE96           PIC X(80).
       01  WS-CMD99            PIC X(100).
       01  WS-CMD100            PIC X(100).
       01  WS-FORM101           PIC X(40).
       01  WS-PAGE101           PIC X(80).
       01  WS-DB-PASSWORD105    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW105        PIC X(12).
       01  WS-CMD106            PIC X(100).
       01  WS-EXPORT-PATH107    PIC X(60).
       01  WS-FORM108           PIC X(40).
       01  WS-PAGE108           PIC X(80).
       01  WS-CMD110            PIC X(100).
       01  WS-CMD112            PIC X(100).
       01  WS-POS114            PIC 99.
       01  WS-RECORD114         PIC X(80).
       01  WS-PART114           PIC X(5).
       01  WS-DB-PASSWORD116    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW116        PIC X(12).
       01  WS-CMD117            PIC X(100).
       01  WS-STMT119           PIC X(200).
       01  WS-DB-PASSWORD120    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW120        PIC X(12).
       01  WS-CMD121            PIC X(100).
       01  WS-POS123            PIC 99.
       01  WS-RECORD123         PIC X(80).
       01  WS-PART123           PIC X(5).
       01  WS-POS125            PIC 99.
       01  WS-RECORD125         PIC X(80).
       01  WS-PART125           PIC X(5).
       01  WS-POS126            PIC 99.
       01  WS-RECORD126         PIC X(80).
       01  WS-PART126           PIC X(5).
       01  WS-STMT127           PIC X(200).
       01  WS-FORM128           PIC X(40).
       01  WS-PAGE128           PIC X(80).
       01  WS-EXPORT-PATH129    PIC X(60).
       01  WS-USER130           PIC X(10).
       01  WS-PASSWORD-IN130    PIC X(12).
       01  WS-DB-PASSWORD131    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW131        PIC X(12).
       01  WS-USER135           PIC X(10).
       01  WS-PASSWORD-IN135    PIC X(12).
       01  WS-USER136           PIC X(10).
       01  WS-PASSWORD-IN136    PIC X(12).
       01  WS-EXPORT-PATH140    PIC X(60).
       01  WS-FORM143           PIC X(40).
       01  WS-PAGE143           PIC X(80).
       01  WS-FORM146           PIC X(40).
       01  WS-PAGE146           PIC X(80).
       01  WS-DB-PASSWORD155    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW155        PIC X(12).
       01  WS-EXPORT-PATH157    PIC X(60).
       01  WS-EXPORT-PATH162    PIC X(60).
       01  WS-CMD163            PIC X(100).
       01  WS-USER164           PIC X(10).
       01  WS-PASSWORD-IN164    PIC X(12).
       01  WS-EXPORT-PATH165    PIC X(60).
       01  WS-POS166            PIC 99.
       01  WS-RECORD166         PIC X(80).
       01  WS-PART166           PIC X(5).
       01  WS-POS167            PIC 99.
       01  WS-RECORD167         PIC X(80).
       01  WS-PART167           PIC X(5).
       01  WS-STMT168           PIC X(200).
       01  WS-USER170           PIC X(10).
       01  WS-PASSWORD-IN170    PIC X(12).
       01  WS-FORM171           PIC X(40).
       01  WS-PAGE171           PIC X(80).
       01  WS-EXPORT-PATH173    PIC X(60).
       01  WS-STMT175           PIC X(200).
       01  WS-STMT176           PIC X(200).
       01  WS-STMT178           PIC X(200).
       01  WS-USER181           PIC X(10).
       01  WS-PASSWORD-IN181    PIC X(12).
       01  WS-EXPORT-PATH182    PIC X(60).
       01  WS-EXPORT-PATH184    PIC X(60).
       01  WS-STMT185           PIC X(200).
       01  WS-FORM188           PIC X(40).
       01  WS-PAGE188           PIC X(80).
       01  WS-FORM189           PIC X(40).
       01  WS-PAGE189           PIC X(80).
       01  WS-POS190            PIC 99.
       01  WS-RECORD190         PIC X(80).
       01  WS-PART190           PIC X(5).
       01  WS-USER192           PIC X(10).
       01  WS-PASSWORD-IN192    PIC X(12).
       01  WS-FORM197           PIC X(40).
       01  WS-PAGE197           PIC X(80).
       01  WS-EXPORT-PATH201    PIC X(60).
       01  WS-STMT204           PIC X(200).
       01  WS-TOTAL3          PIC 9(6) VALUE 0.
       01  WS-K3              PIC 99 VALUE 0.
       01  WS-AVERAGE3        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT7         PIC 9(6) VALUE 500.
       01  WS-FLAG7           PIC X VALUE 'N'.
       01  WS-AMOUNT10         PIC 9(6) VALUE 500.
       01  WS-FLAG10           PIC X VALUE 'N'.
       01  WS-AMOUNT12         PIC 9(6) VALUE 500.
       01  WS-FLAG12           PIC X VALUE 'N'.
       01  WS-TITLE16          PIC X(20) VALUE SPACES.
       01  WS-HEADER16         PIC X(40) VALUE SPACES.
       01  WS-CODE19           PIC 9 VALUE 1.
       01  WS-STATUS19         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT24         PIC 9(6) VALUE 500.
       01  WS-FLAG24           PIC X VALUE 'N'.
       01  WS-TOTAL25          PIC 9(6) VALUE 0.
       01  WS-K25              PIC 99 VALUE 0.
       01  WS-AVERAGE25        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE26          PIC X(20) VALUE SPACES.
       01  WS-HEADER26         PIC X(40) VALUE SPACES.
       01  WS-TITLE29          PIC X(20) VALUE SPACES.
       01  WS-HEADER29         PIC X(40) VALUE SPACES.
       01  WS-TITLE30          PIC X(20) VALUE SPACES.
       01  WS-HEADER30         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT32         PIC 9(6) VALUE 500.
       01  WS-FLAG32           PIC X VALUE 'N'.
       01  WS-CODE39           PIC 9 VALUE 1.
       01  WS-STATUS39         PIC X(6) VALUE SPACES.
       01  WS-CODE42           PIC 9 VALUE 1.
       01  WS-STATUS42         PIC X(6) VALUE SPACES.
       01  WS-CODE44           PIC 9 VALUE 1.
       01  WS-STATUS44         PIC X(6) VALUE SPACES.
       01  WS-TOTAL45          PIC 9(6) VALUE 0.
       01  WS-K45              PIC 99 VALUE 0.
       01  WS-AVERAGE45        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE46          PIC X(20) VALUE SPACES.
       01  WS-HEADER46         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT48         PIC 9(6) VALUE 500.
       01  WS-FLAG48           PIC X VALUE 'N'.
       01  WS-TOTAL49          PIC 9(6) VALUE 0.
       01  WS-K49              PIC 99 VALUE 0.
       01  WS-AVERAGE49        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT51         PIC 9(6) VALUE 500.
       01  WS-FLAG51           PIC X VALUE 'N'.
       01  WS-AMOUNT52         PIC 9(6) VALUE 500.
       01  WS-FLAG52           PIC X VALUE 'N'.
       01  WS-AMOUNT54         PIC 9(6) VALUE 500.
       01  WS-FLAG54           PIC X VALUE 'N'.
       01  WS-TITLE55          PIC X(20) VALUE SPACES.
       01  WS-HEADER55         PIC X(40) VALUE SPACES.
       01  WS-TOTAL56          PIC 9(6) VALUE 0.
       01  WS-K56              PIC 99 VALUE 0.
       01  WS-AVERAGE56        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL57          PIC 9(6) VALUE 0.
       01  WS-K57              PIC 99 VALUE 0.
       01  WS-AVERAGE57        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE58          PIC X(20) VALUE SPACES.
       01  WS-HEADER58         PIC X(40) VALUE SPACES.
       01  WS-CODE59           PIC 9 VALUE 1.
       01  WS-STATUS59         PIC X(6) VALUE SPACES.
       01  WS-TOTAL60          PIC 9(6) VALUE 0.
       01  WS-K60              PIC 99 VALUE 0.
       01  WS-AVERAGE60        PIC 9(6)V99 VALUE 0.
       01  WS-CODE61           PIC 9 VALUE 1.
       01  WS-STATUS61         PIC X(6) VALUE SPACES.
       01  WS-TOTAL63          PIC 9(6) VALUE 0.
       01  WS-K63              PIC 99 VALUE 0.
       01  WS-AVERAGE63        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL64          PIC 9(6) VALUE 0.
       01  WS-K64              PIC 99 VALUE 0.
       01  WS-AVERAGE64        PIC 9(6)V99 VALUE 0.
       01  WS-CODE67           PIC 9 VALUE 1.
       01  WS-STATUS67         PIC X(6) VALUE SPACES.
       01  WS-CODE68           PIC 9 VALUE 1.
       01  WS-STATUS68         PIC X(6) VALUE SPACES.
       01  WS-TITLE70          PIC X(20) VALUE SPACES.
       01  WS-HEADER70         PIC X(40) VALUE SPACES.
       01  WS-CODE72           PIC 9 VALUE 1.
       01  WS-STATUS72         PIC X(6) VALUE SPACES.
       01  WS-TITLE73          PIC X(20) VALUE SPACES.
       01  WS-HEADER73         PIC X(40) VALUE SPACES.
       01  WS-TITLE77          PIC X(20) VALUE SPACES.
       01  WS-HEADER77         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT87         PIC 9(6) VALUE 500.
       01  WS-FLAG87           PIC X VALUE 'N'.
       01  WS-TOTAL90          PIC 9(6) VALUE 0.
       01  WS-K90              PIC 99 VALUE 0.
       01  WS-AVERAGE90        PIC 9(6)V99 VALUE 0.
       01  WS-CODE97           PIC 9 VALUE 1.
       01  WS-STATUS97         PIC X(6) VALUE SPACES.
       01  WS-TITLE98          PIC X(20) VALUE SPACES.
       01  WS-HEADER98         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT102         PIC 9(6) VALUE 500.
       01  WS-FLAG102           PIC X VALUE 'N'.
       01  WS-TOTAL103          PIC 9(6) VALUE 0.
       01  WS-K103              PIC 99 VALUE 0.
       01  WS-AVERAGE103        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT104         PIC 9(6) VALUE 500.
       01  WS-FLAG104           PIC X VALUE 'N'.
       01  WS-CODE109           PIC 9 VALUE 1.
       01  WS-STATUS109         PIC X(6) VALUE SPACES.
       01  WS-CODE111           PIC 9 VALUE 1.
       01  WS-STATUS111         PIC X(6) VALUE SPACES.
       01  WS-TITLE113          PIC X(20) VALUE SPACES.
       01  WS-HEADER113         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT115         PIC 9(6) VALUE 500.
       01  WS-FLAG115           PIC X VALUE 'N'.
       01  WS-CODE118           PIC 9 VALUE 1.
       01  WS-STATUS118         PIC X(6) VALUE SPACES.
       01  WS-TITLE122          PIC X(20) VALUE SPACES.
       01  WS-HEADER122         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT124         PIC 9(6) VALUE 500.
       01  WS-FLAG124           PIC X VALUE 'N'.
       01  WS-TOTAL132          PIC 9(6) VALUE 0.
       01  WS-K132              PIC 99 VALUE 0.
       01  WS-AVERAGE132        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL133          PIC 9(6) VALUE 0.
       01  WS-K133              PIC 99 VALUE 0.
       01  WS-AVERAGE133        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE134          PIC X(20) VALUE SPACES.
       01  WS-HEADER134         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT137         PIC 9(6) VALUE 500.
       01  WS-FLAG137           PIC X VALUE 'N'.
       01  WS-CODE138           PIC 9 VALUE 1.
       01  WS-STATUS138         PIC X(6) VALUE SPACES.
       01  WS-TITLE139          PIC X(20) VALUE SPACES.
       01  WS-HEADER139         PIC X(40) VALUE SPACES.
       01  WS-TITLE141          PIC X(20) VALUE SPACES.
       01  WS-HEADER141         PIC X(40) VALUE SPACES.
       01  WS-CODE142           PIC 9 VALUE 1.
       01  WS-STATUS142         PIC X(6) VALUE SPACES.
       01  WS-TITLE144          PIC X(20) VALUE SPACES.
       01  WS-HEADER144         PIC X(40) VALUE SPACES.
       01  WS-TOTAL145          PIC 9(6) VALUE 0.
       01  WS-K145              PIC 99 VALUE 0.
       01  WS-AVERAGE145        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL147          PIC 9(6) VALUE 0.
       01  WS-K147              PIC 99 VALUE 0.
       01  WS-AVERAGE147        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL148          PIC 9(6) VALUE 0.
       01  WS-K148              PIC 99 VALUE 0.
       01  WS-AVERAGE148        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE149          PIC X(20) VALUE SPACES.
       01  WS-HEADER149         PIC X(40) VALUE SPACES.
       01  WS-CODE150           PIC 9 VALUE 1.
       01  WS-STATUS150         PIC X(6) VALUE SPACES.
       01  WS-TITLE151          PIC X(20) VALUE SPACES.
       01  WS-HEADER151         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT152         PIC 9(6) VALUE 500.
       01  WS-FLAG152           PIC X VALUE 'N'.
       01  WS-AMOUNT153         PIC 9(6) VALUE 500.
       01  WS-FLAG153           PIC X VALUE 'N'.
       01  WS-TOTAL154          PIC 9(6) VALUE 0.
       01  WS-K154              PIC 99 VALUE 0.
       01  WS-AVERAGE154        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE156          PIC X(20) VALUE SPACES.
       01  WS-HEADER156         PIC X(40) VALUE SPACES.
       01  WS-TOTAL158          PIC 9(6) VALUE 0.
       01  WS-K158              PIC 99 VALUE 0.
       01  WS-AVERAGE158        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL159          PIC 9(6) VALUE 0.
       01  WS-K159              PIC 99 VALUE 0.
       01  WS-AVERAGE159        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE160          PIC X(20) VALUE SPACES.
       01  WS-HEADER160         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT161         PIC 9(6) VALUE 500.
       01  WS-FLAG161           PIC X VALUE 'N'.
       01  WS-TITLE169          PIC X(20) VALUE SPACES.
       01  WS-HEADER169         PIC X(40) VALUE SPACES.
       01  WS-CODE172           PIC 9 VALUE 1.
       01  WS-STATUS172         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT174         PIC 9(6) VALUE 500.
       01  WS-FLAG174           PIC X VALUE 'N'.
       01  WS-AMOUNT177         PIC 9(6) VALUE 500.
       01  WS-FLAG177           PIC X VALUE 'N'.
       01  WS-CODE179           PIC 9 VALUE 1.
       01  WS-STATUS179         PIC X(6) VALUE SPACES.
       01  WS-TITLE180          PIC X(20) VALUE SPACES.
       01  WS-HEADER180         PIC X(40) VALUE SPACES.
       01  WS-CODE183           PIC 9 VALUE 1.
       01  WS-STATUS183         PIC X(6) VALUE SPACES.
       01  WS-CODE186           PIC 9 VALUE 1.
       01  WS-STATUS186         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT187         PIC 9(6) VALUE 500.
       01  WS-FLAG187           PIC X VALUE 'N'.
       01  WS-TITLE191          PIC X(20) VALUE SPACES.
       01  WS-HEADER191         PIC X(40) VALUE SPACES.
       01  WS-TOTAL193          PIC 9(6) VALUE 0.
       01  WS-K193              PIC 99 VALUE 0.
       01  WS-AVERAGE193        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT194         PIC 9(6) VALUE 500.
       01  WS-FLAG194           PIC X VALUE 'N'.
       01  WS-TITLE195          PIC X(20) VALUE SPACES.
       01  WS-HEADER195         PIC X(40) VALUE SPACES.
       01  WS-CODE196           PIC 9 VALUE 1.
       01  WS-STATUS196         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT198         PIC 9(6) VALUE 500.
       01  WS-FLAG198           PIC X VALUE 'N'.
       01  WS-TITLE199          PIC X(20) VALUE SPACES.
       01  WS-HEADER199         PIC X(40) VALUE SPACES.
       01  WS-CODE200           PIC 9 VALUE 1.
       01  WS-STATUS200         PIC X(6) VALUE SPACES.
       01  WS-TITLE202          PIC X(20) VALUE SPACES.
       01  WS-HEADER202         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT203         PIC 9(6) VALUE 500.
       01  WS-FLAG203           PIC X VALUE 'N'.
       01  WS-CODE205           PIC 9 VALUE 1.
       01  WS-STATUS205         PIC X(6) VALUE SPACES.
       01  WS-TOTAL206          PIC 9(6) VALUE 0.
       01  WS-K206              PIC 99 VALUE 0.
       01  WS-AVERAGE206        PIC 9(6)V99 VALUE 0.
       01  WS-CODE207           PIC 9 VALUE 1.
       01  WS-STATUS207         PIC X(6) VALUE SPACES.
       01  WS-TITLE208          PIC X(20) VALUE SPACES.
       01  WS-HEADER208         PIC X(40) VALUE SPACES.
       01  WS-CODE209           PIC 9 VALUE 1.
       01  WS-STATUS209         PIC X(6) VALUE SPACES.
       LINKAGE SECTION.
       01  LK-FILTER17         PIC X(100).
       01  LK-PATH21           PIC X(60).
       01  LK-PATH28           PIC X(60).
       01  LK-NAME34           PIC X(40).
       01  LK-FILTER38         PIC X(100).
       01  LK-PATH41           PIC X(60).
       01  LK-PATH62           PIC X(60).
       01  LK-PATH69           PIC X(60).
       01  LK-PATH71           PIC X(60).
       01  LK-PATH74           PIC X(60).
       01  LK-PATH75           PIC X(60).
       01  LK-PATH76           PIC X(60).
       01  LK-FILTER78         PIC X(100).
       01  LK-PATH80           PIC X(60).
       01  LK-NAME81           PIC X(40).
       01  LK-PATH84           PIC X(60).
       01  LK-PATH85           PIC X(60).
       01  LK-FILTER88         PIC X(100).
       01  LK-FILTER89         PIC X(100).
       01  LK-PATH91           PIC X(60).
       01  LK-FILTER92         PIC X(100).
       01  LK-NAME93           PIC X(40).
       01  LK-PATH94           PIC X(60).
       01  LK-FILTER95         PIC X(100).
       01  LK-NAME99           PIC X(40).
       01  LK-NAME100           PIC X(40).
       01  LK-NAME106           PIC X(40).
       01  LK-PATH107           PIC X(60).
       01  LK-NAME110           PIC X(40).
       01  LK-NAME112           PIC X(40).
       01  LK-NAME117           PIC X(40).
       01  LK-FILTER119         PIC X(100).
       01  LK-NAME121           PIC X(40).
       01  LK-FILTER127         PIC X(100).
       01  LK-PATH129           PIC X(60).
       01  LK-PATH140           PIC X(60).
       01  LK-PATH157           PIC X(60).
       01  LK-PATH162           PIC X(60).
       01  LK-NAME163           PIC X(40).
       01  LK-PATH165           PIC X(60).
       01  LK-FILTER168         PIC X(100).
       01  LK-PATH173           PIC X(60).
       01  LK-FILTER175         PIC X(100).
       01  LK-FILTER176         PIC X(100).
       01  LK-FILTER178         PIC X(100).
       01  LK-PATH182           PIC X(60).
       01  LK-PATH184           PIC X(60).
       01  LK-FILTER185         PIC X(100).
       01  LK-PATH201           PIC X(60).
       01  LK-FILTER204         PIC X(100).
       PROCEDURE DIVISION USING LK-FILTER17 LK-PATH21 LK-PATH28 LK-NAME34 LK-FILTER38 LK-PATH41 LK-PATH62 LK-PATH69 LK-PATH71 LK-PATH74 LK-PATH75 LK-PATH76 LK-FILTER78 LK-PATH80 LK-NAME81 LK-PATH84 LK-PATH85 LK-FILTER88 LK-FILTER89 LK-PATH91 LK-FILTER92 LK-NAME93 LK-PATH94 LK-FILTER95 LK-NAME99 LK-NAME100 LK-NAME106 LK-PATH107 LK-NAME110 LK-NAME112 LK-NAME117 LK-FILTER119 LK-NAME121 LK-FILTER127 LK-PATH129 LK-PATH140 LK-PATH157 LK-PATH162 LK-NAME163 LK-PATH165 LK-FILTER168 LK-PATH173 LK-FILTER175 LK-FILTER176 LK-FILTER178 LK-PATH182 LK-PATH184 LK-FILTER185 LK-PATH201 LK-FILTER204.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       CHECK-LIMIT7.
           IF WS-AMOUNT7 > 1000
               MOVE 'Y' TO WS-FLAG7
           ELSE
               MOVE 'N' TO WS-FLAG7
           END-IF.

       EXTRACT-FIELD-SAFE167.
           ACCEPT WS-POS167.
           IF WS-POS167 IS NUMERIC AND WS-POS167 > 0 AND WS-POS167 < 76
               MOVE WS-RECORD167(WS-POS167:5) TO WS-PART167
           END-IF.

       CONVERT-FILE-SAFE93.
           MOVE "convert /srv/in/report.txt" TO WS-CMD93.
           CALL 'SYSTEM' USING WS-CMD93.

       CHECK-LIMIT10.
           IF WS-AMOUNT10 > 1000
               MOVE 'Y' TO WS-FLAG10
           ELSE
               MOVE 'N' TO WS-FLAG10
           END-IF.

       FORMAT-HEADER16.
           MOVE 'MONTHLY REPORT' TO WS-TITLE16.
           STRING WS-TITLE16 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER16.
           DISPLAY WS-HEADER16.

       LOG-LOGIN15.
           DISPLAY 'LOGIN ' WS-USER15 ' ' WS-PASSWORD-IN15.

       FORMAT-HEADER202.
           MOVE 'MONTHLY REPORT' TO WS-TITLE202.
           STRING WS-TITLE202 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER202.
           DISPLAY WS-HEADER202.

       WRITE-EXPORT-SAFE75.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH75.
           OPEN OUTPUT EXPORT-FILE75.
           CLOSE EXPORT-FILE75.

       CLASSIFY-CODE200.
           EVALUATE WS-CODE200
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS200
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS200
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS200
           END-EVALUATE.

       FORMAT-HEADER169.
           MOVE 'MONTHLY REPORT' TO WS-TITLE169.
           STRING WS-TITLE169 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER169.
           DISPLAY WS-HEADER169.

       FORMAT-HEADER113.
           MOVE 'MONTHLY REPORT' TO WS-TITLE113.
           STRING WS-TITLE113 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER113.
           DISPLAY WS-HEADER113.

       COMPUTE-TOTALS154.
           MOVE 0 TO WS-TOTAL154.
           PERFORM VARYING WS-K154 FROM 1 BY 1 UNTIL WS-K154 > 10
               ADD WS-K154 TO WS-TOTAL154
           END-PERFORM.
           COMPUTE WS-AVERAGE154 = WS-TOTAL154 / 10.

       CONNECT-DB105.
           MOVE WS-DB-PASSWORD105 TO WS-CONN-PW105.

       CLASSIFY-CODE138.
           EVALUATE WS-CODE138
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS138
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS138
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS138
           END-EVALUATE.

       CHECK-LIMIT32.
           IF WS-AMOUNT32 > 1000
               MOVE 'Y' TO WS-FLAG32
           ELSE
               MOVE 'N' TO WS-FLAG32
           END-IF.

       ECHO-NAME171.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM171) END-EXEC.
           STRING '<p>' WS-FORM171 '</p>' DELIMITED BY SIZE INTO WS-PAGE171.
           EXEC CICS WEB SEND FROM(WS-PAGE171) END-EXEC.

       EXTRACT-FIELD-SAFE9.
           ACCEPT WS-POS9.
           IF WS-POS9 IS NUMERIC AND WS-POS9 > 0 AND WS-POS9 < 76
               MOVE WS-RECORD9(WS-POS9:5) TO WS-PART9
           END-IF.

       FORMAT-HEADER156.
           MOVE 'MONTHLY REPORT' TO WS-TITLE156.
           STRING WS-TITLE156 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER156.
           DISPLAY WS-HEADER156.

       FORMAT-HEADER139.
           MOVE 'MONTHLY REPORT' TO WS-TITLE139.
           STRING WS-TITLE139 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER139.
           DISPLAY WS-HEADER139.

       WRITE-EXPORT-SAFE107.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH107.
           OPEN OUTPUT EXPORT-FILE107.
           CLOSE EXPORT-FILE107.

       FORMAT-HEADER160.
           MOVE 'MONTHLY REPORT' TO WS-TITLE160.
           STRING WS-TITLE160 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER160.
           DISPLAY WS-HEADER160.

       CLASSIFY-CODE67.
           EVALUATE WS-CODE67
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS67
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS67
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS67
           END-EVALUATE.

       PREPARE-QUERY-SAFE38.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT38.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT38 END-EXEC.

       COMPUTE-TOTALS132.
           MOVE 0 TO WS-TOTAL132.
           PERFORM VARYING WS-K132 FROM 1 BY 1 UNTIL WS-K132 > 10
               ADD WS-K132 TO WS-TOTAL132
           END-PERFORM.
           COMPUTE WS-AVERAGE132 = WS-TOTAL132 / 10.

       EXTRACT-FIELD20.
           ACCEPT WS-POS20.
           MOVE WS-RECORD20(WS-POS20:5) TO WS-PART20.

       CONNECT-DB-SAFE83.
           ACCEPT WS-CONN-PW83 FROM ENVIRONMENT 'DB_PASSWORD'.

       COMPUTE-TOTALS45.
           MOVE 0 TO WS-TOTAL45.
           PERFORM VARYING WS-K45 FROM 1 BY 1 UNTIL WS-K45 > 10
               ADD WS-K45 TO WS-TOTAL45
           END-PERFORM.
           COMPUTE WS-AVERAGE45 = WS-TOTAL45 / 10.

       COMPUTE-TOTALS145.
           MOVE 0 TO WS-TOTAL145.
           PERFORM VARYING WS-K145 FROM 1 BY 1 UNTIL WS-K145 > 10
               ADD WS-K145 TO WS-TOTAL145
           END-PERFORM.
           COMPUTE WS-AVERAGE145 = WS-TOTAL145 / 10.

       WRITE-EXPORT140.
           MOVE LK-PATH140 TO WS-EXPORT-PATH140.
           OPEN OUTPUT EXPORT-FILE140.
           CLOSE EXPORT-FILE140.

       CONVERT-FILE121.
           STRING "convert " LK-NAME121 DELIMITED BY SIZE INTO WS-CMD121.
           CALL 'SYSTEM' USING WS-CMD121.

       COMPUTE-TOTALS147.
           MOVE 0 TO WS-TOTAL147.
           PERFORM VARYING WS-K147 FROM 1 BY 1 UNTIL WS-K147 > 10
               ADD WS-K147 TO WS-TOTAL147
           END-PERFORM.
           COMPUTE WS-AVERAGE147 = WS-TOTAL147 / 10.

       CONVERT-FILE-SAFE99.
           MOVE "convert /srv/in/report.txt" TO WS-CMD99.
           CALL 'SYSTEM' USING WS-CMD99.

       EXTRACT-FIELD126.
           ACCEPT WS-POS126.
           MOVE WS-RECORD126(WS-POS126:5) TO WS-PART126.

       ECHO-NAME-SAFE33.
           MOVE '<p>Thank you</p>' TO WS-PAGE33.
           EXEC CICS WEB SEND FROM(WS-PAGE33) END-EXEC.

       COMPUTE-TOTALS49.
           MOVE 0 TO WS-TOTAL49.
           PERFORM VARYING WS-K49 FROM 1 BY 1 UNTIL WS-K49 > 10
               ADD WS-K49 TO WS-TOTAL49
           END-PERFORM.
           COMPUTE WS-AVERAGE49 = WS-TOTAL49 / 10.

       CLASSIFY-CODE179.
           EVALUATE WS-CODE179
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS179
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS179
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS179
           END-EVALUATE.

       CONVERT-FILE-SAFE106.
           MOVE "convert /srv/in/report.txt" TO WS-CMD106.
           CALL 'SYSTEM' USING WS-CMD106.

       FORMAT-HEADER149.
           MOVE 'MONTHLY REPORT' TO WS-TITLE149.
           STRING WS-TITLE149 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER149.
           DISPLAY WS-HEADER149.

       FORMAT-HEADER70.
           MOVE 'MONTHLY REPORT' TO WS-TITLE70.
           STRING WS-TITLE70 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER70.
           DISPLAY WS-HEADER70.

       CONVERT-FILE81.
           STRING "convert " LK-NAME81 DELIMITED BY SIZE INTO WS-CMD81.
           CALL 'SYSTEM' USING WS-CMD81.

       WRITE-EXPORT-SAFE21.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH21.
           OPEN OUTPUT EXPORT-FILE21.
           CLOSE EXPORT-FILE21.

       FORMAT-HEADER29.
           MOVE 'MONTHLY REPORT' TO WS-TITLE29.
           STRING WS-TITLE29 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER29.
           DISPLAY WS-HEADER29.

       EXTRACT-FIELD31.
           ACCEPT WS-POS31.
           MOVE WS-RECORD31(WS-POS31:5) TO WS-PART31.

       CLASSIFY-CODE205.
           EVALUATE WS-CODE205
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS205
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS205
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS205
           END-EVALUATE.

       LOG-LOGIN-SAFE86.
           DISPLAY 'LOGIN ' WS-USER86.

       FORMAT-HEADER73.
           MOVE 'MONTHLY REPORT' TO WS-TITLE73.
           STRING WS-TITLE73 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER73.
           DISPLAY WS-HEADER73.

       EXTRACT-FIELD-SAFE123.
           ACCEPT WS-POS123.
           IF WS-POS123 IS NUMERIC AND WS-POS123 > 0 AND WS-POS123 < 76
               MOVE WS-RECORD123(WS-POS123:5) TO WS-PART123
           END-IF.

       PREPARE-QUERY-SAFE178.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT178.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT178 END-EXEC.

       EXTRACT-FIELD-SAFE190.
           ACCEPT WS-POS190.
           IF WS-POS190 IS NUMERIC AND WS-POS190 > 0 AND WS-POS190 < 76
               MOVE WS-RECORD190(WS-POS190:5) TO WS-PART190
           END-IF.

       CHECK-LIMIT102.
           IF WS-AMOUNT102 > 1000
               MOVE 'Y' TO WS-FLAG102
           ELSE
               MOVE 'N' TO WS-FLAG102
           END-IF.

       FORMAT-HEADER30.
           MOVE 'MONTHLY REPORT' TO WS-TITLE30.
           STRING WS-TITLE30 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER30.
           DISPLAY WS-HEADER30.

       CLASSIFY-CODE118.
           EVALUATE WS-CODE118
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS118
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS118
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS118
           END-EVALUATE.

       CLASSIFY-CODE42.
           EVALUATE WS-CODE42
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS42
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS42
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS42
           END-EVALUATE.

       ECHO-NAME79.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM79) END-EXEC.
           STRING '<p>' WS-FORM79 '</p>' DELIMITED BY SIZE INTO WS-PAGE79.
           EXEC CICS WEB SEND FROM(WS-PAGE79) END-EXEC.

       ECHO-NAME43.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM43) END-EXEC.
           STRING '<p>' WS-FORM43 '</p>' DELIMITED BY SIZE INTO WS-PAGE43.
           EXEC CICS WEB SEND FROM(WS-PAGE43) END-EXEC.

       FORMAT-HEADER144.
           MOVE 'MONTHLY REPORT' TO WS-TITLE144.
           STRING WS-TITLE144 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER144.
           DISPLAY WS-HEADER144.

       CLASSIFY-CODE109.
           EVALUATE WS-CODE109
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS109
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS109
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS109
           END-EVALUATE.

       FORMAT-HEADER141.
           MOVE 'MONTHLY REPORT' TO WS-TITLE141.
           STRING WS-TITLE141 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER141.
           DISPLAY WS-HEADER141.

       ECHO-NAME128.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM128) END-EXEC.
           STRING '<p>' WS-FORM128 '</p>' DELIMITED BY SIZE INTO WS-PAGE128.
           EXEC CICS WEB SEND FROM(WS-PAGE128) END-EXEC.

       PREPARE-QUERY176.
           MOVE LK-FILTER176 TO WS-STMT176.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT176 END-EXEC.

       CLASSIFY-CODE150.
           EVALUATE WS-CODE150
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS150
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS150
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS150
           END-EVALUATE.

       CONVERT-FILE-SAFE117.
           MOVE "convert /srv/in/report.txt" TO WS-CMD117.
           CALL 'SYSTEM' USING WS-CMD117.

       WRITE-EXPORT80.
           MOVE LK-PATH80 TO WS-EXPORT-PATH80.
           OPEN OUTPUT EXPORT-FILE80.
           CLOSE EXPORT-FILE80.

       ECHO-NAME53.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM53) END-EXEC.
           STRING '<p>' WS-FORM53 '</p>' DELIMITED BY SIZE INTO WS-PAGE53.
           EXEC CICS WEB SEND FROM(WS-PAGE53) END-EXEC.

       CLASSIFY-CODE209.
           EVALUATE WS-CODE209
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS209
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS209
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS209
           END-EVALUATE.

       CONNECT-DB-SAFE120.
           ACCEPT WS-CONN-PW120 FROM ENVIRONMENT 'DB_PASSWORD'.

       EXTRACT-FIELD-SAFE114.
           ACCEPT WS-POS114.
           IF WS-POS114 IS NUMERIC AND WS-POS114 > 0 AND WS-POS114 < 76
               MOVE WS-RECORD114(WS-POS114:5) TO WS-PART114
           END-IF.

       WRITE-EXPORT-SAFE28.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH28.
           OPEN OUTPUT EXPORT-FILE28.
           CLOSE EXPORT-FILE28.

       EXTRACT-FIELD11.
           ACCEPT WS-POS11.
           MOVE WS-RECORD11(WS-POS11:5) TO WS-PART11.

       COMPUTE-TOTALS133.
           MOVE 0 TO WS-TOTAL133.
           PERFORM VARYING WS-K133 FROM 1 BY 1 UNTIL WS-K133 > 10
               ADD WS-K133 TO WS-TOTAL133
           END-PERFORM.
           COMPUTE WS-AVERAGE133 = WS-TOTAL133 / 10.

       PREPARE-QUERY89.
           MOVE LK-FILTER89 TO WS-STMT89.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT89 END-EXEC.

       ECHO-NAME-SAFE143.
           MOVE '<p>Thank you</p>' TO WS-PAGE143.
           EXEC CICS WEB SEND FROM(WS-PAGE143) END-EXEC.

       LOG-LOGIN136.
           DISPLAY 'LOGIN ' WS-USER136 ' ' WS-PASSWORD-IN136.

       WRITE-EXPORT-SAFE69.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH69.
           OPEN OUTPUT EXPORT-FILE69.
           CLOSE EXPORT-FILE69.

       ECHO-NAME101.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM101) END-EXEC.
           STRING '<p>' WS-FORM101 '</p>' DELIMITED BY SIZE INTO WS-PAGE101.
           EXEC CICS WEB SEND FROM(WS-PAGE101) END-EXEC.

       FORMAT-HEADER55.
           MOVE 'MONTHLY REPORT' TO WS-TITLE55.
           STRING WS-TITLE55 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER55.
           DISPLAY WS-HEADER55.

       CHECK-LIMIT153.
           IF WS-AMOUNT153 > 1000
               MOVE 'Y' TO WS-FLAG153
           ELSE
               MOVE 'N' TO WS-FLAG153
           END-IF.

       FORMAT-HEADER191.
           MOVE 'MONTHLY REPORT' TO WS-TITLE191.
           STRING WS-TITLE191 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER191.
           DISPLAY WS-HEADER191.

       LOG-LOGIN14.
           DISPLAY 'LOGIN ' WS-USER14 ' ' WS-PASSWORD-IN14.

       COMPUTE-TOTALS90.
           MOVE 0 TO WS-TOTAL90.
           PERFORM VARYING WS-K90 FROM 1 BY 1 UNTIL WS-K90 > 10
               ADD WS-K90 TO WS-TOTAL90
           END-PERFORM.
           COMPUTE WS-AVERAGE90 = WS-TOTAL90 / 10.

       CLASSIFY-CODE186.
           EVALUATE WS-CODE186
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS186
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS186
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS186
           END-EVALUATE.

       FORMAT-HEADER195.
           MOVE 'MONTHLY REPORT' TO WS-TITLE195.
           STRING WS-TITLE195 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER195.
           DISPLAY WS-HEADER195.

       WRITE-EXPORT-SAFE165.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH165.
           OPEN OUTPUT EXPORT-FILE165.
           CLOSE EXPORT-FILE165.

       PREPARE-QUERY204.
           MOVE LK-FILTER204 TO WS-STMT204.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT204 END-EXEC.

       CHECK-LIMIT52.
           IF WS-AMOUNT52 > 1000
               MOVE 'Y' TO WS-FLAG52
           ELSE
               MOVE 'N' TO WS-FLAG52
           END-IF.

       WRITE-EXPORT-SAFE162.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH162.
           OPEN OUTPUT EXPORT-FILE162.
           CLOSE EXPORT-FILE162.

       ECHO-NAME5.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM5) END-EXEC.
           STRING '<p>' WS-FORM5 '</p>' DELIMITED BY SIZE INTO WS-PAGE5.
           EXEC CICS WEB SEND FROM(WS-PAGE5) END-EXEC.

       WRITE-EXPORT-SAFE62.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH62.
           OPEN OUTPUT EXPORT-FILE62.
           CLOSE EXPORT-FILE62.

       CLASSIFY-CODE59.
           EVALUATE WS-CODE59
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS59
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS59
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS59
           END-EVALUATE.

       CLASSIFY-CODE111.
           EVALUATE WS-CODE111
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS111
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS111
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS111
           END-EVALUATE.

       WRITE-EXPORT-SAFE41.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH41.
           OPEN OUTPUT EXPORT-FILE41.
           CLOSE EXPORT-FILE41.

       EXTRACT-FIELD-SAFE166.
           ACCEPT WS-POS166.
           IF WS-POS166 IS NUMERIC AND WS-POS166 > 0 AND WS-POS166 < 76
               MOVE WS-RECORD166(WS-POS166:5) TO WS-PART166
           END-IF.

       CONVERT-FILE163.
           STRING "convert " LK-NAME163 DELIMITED BY SIZE INTO WS-CMD163.
           CALL 'SYSTEM' USING WS-CMD163.

       CHECK-LIMIT104.
           IF WS-AMOUNT104 > 1000
               MOVE 'Y' TO WS-FLAG104
           ELSE
               MOVE 'N' TO WS-FLAG104
           END-IF.

       CHECK-LIMIT187.
           IF WS-AMOUNT187 > 1000
               MOVE 'Y' TO WS-FLAG187
           ELSE
               MOVE 'N' TO WS-FLAG187
           END-IF.

       ECHO-NAME-SAFE35.
           MOVE '<p>Thank you</p>' TO WS-PAGE35.
           EXEC CICS WEB SEND FROM(WS-PAGE35) END-EXEC.

       CHECK-LIMIT51.
           IF WS-AMOUNT51 > 1000
               MOVE 'Y' TO WS-FLAG51
           ELSE
               MOVE 'N' TO WS-FLAG51
           END-IF.

       CLASSIFY-CODE39.
           EVALUATE WS-CODE39
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS39
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS39
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS39
           END-EVALUATE.

       LOG-LOGIN2.
           DISPLAY 'LOGIN ' WS-USER2 ' ' WS-PASSWORD-IN2.

       COMPUTE-TOTALS158.
           MOVE 0 TO WS-TOTAL158.
           PERFORM VARYING WS-K158 FROM 1 BY 1 UNTIL WS-K158 > 10
               ADD WS-K158 TO WS-TOTAL158
           END-PERFORM.
           COMPUTE WS-AVERAGE158 = WS-TOTAL158 / 10.

       CONVERT-FILE112.
           STRING "convert " LK-NAME112 DELIMITED BY SIZE INTO WS-CMD112.
           CALL 'SYSTEM' USING WS-CMD112.

       CLASSIFY-CODE61.
           EVALUATE WS-CODE61
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS61
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS61
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS61
           END-EVALUATE.

       CHECK-LIMIT137.
           IF WS-AMOUNT137 > 1000
               MOVE 'Y' TO WS-FLAG137
           ELSE
               MOVE 'N' TO WS-FLAG137
           END-IF.

       PREPARE-QUERY185.
           MOVE LK-FILTER185 TO WS-STMT185.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT185 END-EXEC.

       LOG-LOGIN65.
           DISPLAY 'LOGIN ' WS-USER65 ' ' WS-PASSWORD-IN65.

       CONNECT-DB47.
           MOVE WS-DB-PASSWORD47 TO WS-CONN-PW47.

       CLASSIFY-CODE68.
           EVALUATE WS-CODE68
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS68
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS68
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS68
           END-EVALUATE.

       WRITE-EXPORT-SAFE76.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH76.
           OPEN OUTPUT EXPORT-FILE76.
           CLOSE EXPORT-FILE76.

       PREPARE-QUERY-SAFE175.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT175.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT175 END-EXEC.

       ECHO-NAME22.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM22) END-EXEC.
           STRING '<p>' WS-FORM22 '</p>' DELIMITED BY SIZE INTO WS-PAGE22.
           EXEC CICS WEB SEND FROM(WS-PAGE22) END-EXEC.

       PREPARE-QUERY-SAFE168.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT168.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT168 END-EXEC.

       WRITE-EXPORT91.
           MOVE LK-PATH91 TO WS-EXPORT-PATH91.
           OPEN OUTPUT EXPORT-FILE91.
           CLOSE EXPORT-FILE91.

       COMPUTE-TOTALS3.
           MOVE 0 TO WS-TOTAL3.
           PERFORM VARYING WS-K3 FROM 1 BY 1 UNTIL WS-K3 > 10
               ADD WS-K3 TO WS-TOTAL3
           END-PERFORM.
           COMPUTE WS-AVERAGE3 = WS-TOTAL3 / 10.

       FORMAT-HEADER46.
           MOVE 'MONTHLY REPORT' TO WS-TITLE46.
           STRING WS-TITLE46 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER46.
           DISPLAY WS-HEADER46.

       COMPUTE-TOTALS57.
           MOVE 0 TO WS-TOTAL57.
           PERFORM VARYING WS-K57 FROM 1 BY 1 UNTIL WS-K57 > 10
               ADD WS-K57 TO WS-TOTAL57
           END-PERFORM.
           COMPUTE WS-AVERAGE57 = WS-TOTAL57 / 10.

       COMPUTE-TOTALS63.
           MOVE 0 TO WS-TOTAL63.
           PERFORM VARYING WS-K63 FROM 1 BY 1 UNTIL WS-K63 > 10
               ADD WS-K63 TO WS-TOTAL63
           END-PERFORM.
           COMPUTE WS-AVERAGE63 = WS-TOTAL63 / 10.

       PREPARE-QUERY88.
           MOVE LK-FILTER88 TO WS-STMT88.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT88 END-EXEC.

       FORMAT-HEADER98.
           MOVE 'MONTHLY REPORT' TO WS-TITLE98.
           STRING WS-TITLE98 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER98.
           DISPLAY WS-HEADER98.

       EXTRACT-FIELD-SAFE125.
           ACCEPT WS-POS125.
           IF WS-POS125 IS NUMERIC AND WS-POS125 > 0 AND WS-POS125 < 76
               MOVE WS-RECORD125(WS-POS125:5) TO WS-PART125
           END-IF.

       WRITE-EXPORT201.
           MOVE LK-PATH201 TO WS-EXPORT-PATH201.
           OPEN OUTPUT EXPORT-FILE201.
           CLOSE EXPORT-FILE201.

       PREPARE-QUERY-SAFE119.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT119.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT119 END-EXEC.

       ECHO-NAME-SAFE1.
           MOVE '<p>Thank you</p>' TO WS-PAGE1.
           EXEC CICS WEB SEND FROM(WS-PAGE1) END-EXEC.

       CONVERT-FILE100.
           STRING "convert " LK-NAME100 DELIMITED BY SIZE INTO WS-CMD100.
           CALL 'SYSTEM' USING WS-CMD100.

       PREPARE-QUERY95.
           MOVE LK-FILTER95 TO WS-STMT95.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT95 END-EXEC.

       CHECK-LIMIT87.
           IF WS-AMOUNT87 > 1000
               MOVE 'Y' TO WS-FLAG87
           ELSE
               MOVE 'N' TO WS-FLAG87
           END-IF.

       FORMAT-HEADER151.
           MOVE 'MONTHLY REPORT' TO WS-TITLE151.
           STRING WS-TITLE151 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER151.
           DISPLAY WS-HEADER151.

       WRITE-EXPORT157.
           MOVE LK-PATH157 TO WS-EXPORT-PATH157.
           OPEN OUTPUT EXPORT-FILE157.
           CLOSE EXPORT-FILE157.

       ECHO-NAME-SAFE197.
           MOVE '<p>Thank you</p>' TO WS-PAGE197.
           EXEC CICS WEB SEND FROM(WS-PAGE197) END-EXEC.

       FORMAT-HEADER26.
           MOVE 'MONTHLY REPORT' TO WS-TITLE26.
           STRING WS-TITLE26 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER26.
           DISPLAY WS-HEADER26.

       ECHO-NAME-SAFE36.
           MOVE '<p>Thank you</p>' TO WS-PAGE36.
           EXEC CICS WEB SEND FROM(WS-PAGE36) END-EXEC.

       CHECK-LIMIT161.
           IF WS-AMOUNT161 > 1000
               MOVE 'Y' TO WS-FLAG161
           ELSE
               MOVE 'N' TO WS-FLAG161
           END-IF.

       WRITE-EXPORT129.
           MOVE LK-PATH129 TO WS-EXPORT-PATH129.
           OPEN OUTPUT EXPORT-FILE129.
           CLOSE EXPORT-FILE129.

       LOG-LOGIN164.
           DISPLAY 'LOGIN ' WS-USER164 ' ' WS-PASSWORD-IN164.

       CONNECT-DB13.
           MOVE WS-DB-PASSWORD13 TO WS-CONN-PW13.

       CONNECT-DB155.
           MOVE WS-DB-PASSWORD155 TO WS-CONN-PW155.

       WRITE-EXPORT71.
           MOVE LK-PATH71 TO WS-EXPORT-PATH71.
           OPEN OUTPUT EXPORT-FILE71.
           CLOSE EXPORT-FILE71.

       COMPUTE-TOTALS206.
           MOVE 0 TO WS-TOTAL206.
           PERFORM VARYING WS-K206 FROM 1 BY 1 UNTIL WS-K206 > 10
               ADD WS-K206 TO WS-TOTAL206
           END-PERFORM.
           COMPUTE WS-AVERAGE206 = WS-TOTAL206 / 10.

       ECHO-NAME188.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM188) END-EXEC.
           STRING '<p>' WS-FORM188 '</p>' DELIMITED BY SIZE INTO WS-PAGE188.
           EXEC CICS WEB SEND FROM(WS-PAGE188) END-EXEC.

       EXTRACT-FIELD4.
           ACCEPT WS-POS4.
           MOVE WS-RECORD4(WS-POS4:5) TO WS-PART4.

       LOG-LOGIN6.
           DISPLAY 'LOGIN ' WS-USER6 ' ' WS-PASSWORD-IN6.

       WRITE-EXPORT84.
           MOVE LK-PATH84 TO WS-EXPORT-PATH84.
           OPEN OUTPUT EXPORT-FILE84.
           CLOSE EXPORT-FILE84.

       CHECK-LIMIT194.
           IF WS-AMOUNT194 > 1000
               MOVE 'Y' TO WS-FLAG194
           ELSE
               MOVE 'N' TO WS-FLAG194
           END-IF.

       CONNECT-DB-SAFE50.
           ACCEPT WS-CONN-PW50 FROM ENVIRONMENT 'DB_PASSWORD'.

       LOG-LOGIN170.
           DISPLAY 'LOGIN ' WS-USER170 ' ' WS-PASSWORD-IN170.

       LOG-LOGIN-SAFE181.
           DISPLAY 'LOGIN ' WS-USER181.

       CONVERT-FILE34.
           STRING "convert " LK-NAME34 DELIMITED BY SIZE INTO WS-CMD34.
           CALL 'SYSTEM' USING WS-CMD34.

       CONNECT-DB-SAFE8.
           ACCEPT WS-CONN-PW8 FROM ENVIRONMENT 'DB_PASSWORD'.

       CONNECT-DB27.
           MOVE WS-DB-PASSWORD27 TO WS-CONN-PW27.

       PREPARE-QUERY127.
           MOVE LK-FILTER127 TO WS-STMT127.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT127 END-EXEC.

       CHECK-LIMIT12.
           IF WS-AMOUNT12 > 1000
               MOVE 'Y' TO WS-FLAG12
           ELSE
               MOVE 'N' TO WS-FLAG12
           END-IF.

       WRITE-EXPORT184.
           MOVE LK-PATH184 TO WS-EXPORT-PATH184.
           OPEN OUTPUT EXPORT-FILE184.
           CLOSE EXPORT-FILE184.

       COMPUTE-TOTALS159.
           MOVE 0 TO WS-TOTAL159.
           PERFORM VARYING WS-K159 FROM 1 BY 1 UNTIL WS-K159 > 10
               ADD WS-K159 TO WS-TOTAL159
           END-PERFORM.
           COMPUTE WS-AVERAGE159 = WS-TOTAL159 / 10.

       PREPARE-QUERY-SAFE17.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT17.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT17 END-EXEC.

       WRITE-EXPORT74.
           MOVE LK-PATH74 TO WS-EXPORT-PATH74.
           OPEN OUTPUT EXPORT-FILE74.
           CLOSE EXPORT-FILE74.

       CONNECT-DB-SAFE37.
           ACCEPT WS-CONN-PW37 FROM ENVIRONMENT 'DB_PASSWORD'.

       FORMAT-HEADER134.
           MOVE 'MONTHLY REPORT' TO WS-TITLE134.
           STRING WS-TITLE134 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER134.
           DISPLAY WS-HEADER134.

       WRITE-EXPORT-SAFE173.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH173.
           OPEN OUTPUT EXPORT-FILE173.
           CLOSE EXPORT-FILE173.

       WRITE-EXPORT85.
           MOVE LK-PATH85 TO WS-EXPORT-PATH85.
           OPEN OUTPUT EXPORT-FILE85.
           CLOSE EXPORT-FILE85.

       COMPUTE-TOTALS193.
           MOVE 0 TO WS-TOTAL193.
           PERFORM VARYING WS-K193 FROM 1 BY 1 UNTIL WS-K193 > 10
               ADD WS-K193 TO WS-TOTAL193
           END-PERFORM.
           COMPUTE WS-AVERAGE193 = WS-TOTAL193 / 10.

       CHECK-LIMIT198.
           IF WS-AMOUNT198 > 1000
               MOVE 'Y' TO WS-FLAG198
           ELSE
               MOVE 'N' TO WS-FLAG198
           END-IF.

       ECHO-NAME-SAFE23.
           MOVE '<p>Thank you</p>' TO WS-PAGE23.
           EXEC CICS WEB SEND FROM(WS-PAGE23) END-EXEC.

       WRITE-EXPORT-SAFE182.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH182.
           OPEN OUTPUT EXPORT-FILE182.
           CLOSE EXPORT-FILE182.

       ECHO-NAME146.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM146) END-EXEC.
           STRING '<p>' WS-FORM146 '</p>' DELIMITED BY SIZE INTO WS-PAGE146.
           EXEC CICS WEB SEND FROM(WS-PAGE146) END-EXEC.

       CONVERT-FILE-SAFE110.
           MOVE "convert /srv/in/report.txt" TO WS-CMD110.
           CALL 'SYSTEM' USING WS-CMD110.

       ECHO-NAME-SAFE82.
           MOVE '<p>Thank you</p>' TO WS-PAGE82.
           EXEC CICS WEB SEND FROM(WS-PAGE82) END-EXEC.

       COMPUTE-TOTALS25.
           MOVE 0 TO WS-TOTAL25.
           PERFORM VARYING WS-K25 FROM 1 BY 1 UNTIL WS-K25 > 10
               ADD WS-K25 TO WS-TOTAL25
           END-PERFORM.
           COMPUTE WS-AVERAGE25 = WS-TOTAL25 / 10.

       FORMAT-HEADER180.
           MOVE 'MONTHLY REPORT' TO WS-TITLE180.
           STRING WS-TITLE180 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER180.
           DISPLAY WS-HEADER180.

       FORMAT-HEADER208.
           MOVE 'MONTHLY REPORT' TO WS-TITLE208.
           STRING WS-TITLE208 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER208.
           DISPLAY WS-HEADER208.

       CLASSIFY-CODE207.
           EVALUATE WS-CODE207
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS207
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS207
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS207
           END-EVALUATE.

       COMPUTE-TOTALS56.
           MOVE 0 TO WS-TOTAL56.
           PERFORM VARYING WS-K56 FROM 1 BY 1 UNTIL WS-K56 > 10
               ADD WS-K56 TO WS-TOTAL56
           END-PERFORM.
           COMPUTE WS-AVERAGE56 = WS-TOTAL56 / 10.

       CLASSIFY-CODE196.
           EVALUATE WS-CODE196
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS196
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS196
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS196
           END-EVALUATE.

       ECHO-NAME96.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM96) END-EXEC.
           STRING '<p>' WS-FORM96 '</p>' DELIMITED BY SIZE INTO WS-PAGE96.
           EXEC CICS WEB SEND FROM(WS-PAGE96) END-EXEC.

       CLASSIFY-CODE172.
           EVALUATE WS-CODE172
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS172
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS172
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS172
           END-EVALUATE.

       FORMAT-HEADER122.
           MOVE 'MONTHLY REPORT' TO WS-TITLE122.
           STRING WS-TITLE122 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER122.
           DISPLAY WS-HEADER122.

       ECHO-NAME-SAFE189.
           MOVE '<p>Thank you</p>' TO WS-PAGE189.
           EXEC CICS WEB SEND FROM(WS-PAGE189) END-EXEC.

       CHECK-LIMIT124.
           IF WS-AMOUNT124 > 1000
               MOVE 'Y' TO WS-FLAG124
           ELSE
               MOVE 'N' TO WS-FLAG124
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

       LOG-LOGIN135.
           DISPLAY 'LOGIN ' WS-USER135 ' ' WS-PASSWORD-IN135.

       CHECK-LIMIT152.
           IF WS-AMOUNT152 > 1000
               MOVE 'Y' TO WS-FLAG152
           ELSE
               MOVE 'N' TO WS-FLAG152
           END-IF.

       ECHO-NAME108.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM108) END-EXEC.
           STRING '<p>' WS-FORM108 '</p>' DELIMITED BY SIZE INTO WS-PAGE108.
           EXEC CICS WEB SEND FROM(WS-PAGE108) END-EXEC.

       CHECK-LIMIT203.
           IF WS-AMOUNT203 > 1000
               MOVE 'Y' TO WS-FLAG203
           ELSE
               MOVE 'N' TO WS-FLAG203
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

       COMPUTE-TOTALS64.
           MOVE 0 TO WS-TOTAL64.
           PERFORM VARYING WS-K64 FROM 1 BY 1 UNTIL WS-K64 > 10
               ADD WS-K64 TO WS-TOTAL64
           END-PERFORM.
           COMPUTE WS-AVERAGE64 = WS-TOTAL64 / 10.

       CHECK-LIMIT115.
           IF WS-AMOUNT115 > 1000
               MOVE 'Y' TO WS-FLAG115
           ELSE
               MOVE 'N' TO WS-FLAG115
           END-IF.

       COMPUTE-TOTALS103.
           MOVE 0 TO WS-TOTAL103.
           PERFORM VARYING WS-K103 FROM 1 BY 1 UNTIL WS-K103 > 10
               ADD WS-K103 TO WS-TOTAL103
           END-PERFORM.
           COMPUTE WS-AVERAGE103 = WS-TOTAL103 / 10.

       EXTRACT-FIELD-SAFE18.
           ACCEPT WS-POS18.
           IF WS-POS18 IS NUMERIC AND WS-POS18 > 0 AND WS-POS18 < 76
               MOVE WS-RECORD18(WS-POS18:5) TO WS-PART18
           END-IF.

       LOG-LOGIN-SAFE130.
           DISPLAY 'LOGIN ' WS-USER130.

       COMPUTE-TOTALS148.
           MOVE 0 TO WS-TOTAL148.
           PERFORM VARYING WS-K148 FROM 1 BY 1 UNTIL WS-K148 > 10
               ADD WS-K148 TO WS-TOTAL148
           END-PERFORM.
           COMPUTE WS-AVERAGE148 = WS-TOTAL148 / 10.

       FORMAT-HEADER77.
           MOVE 'MONTHLY REPORT' TO WS-TITLE77.
           STRING WS-TITLE77 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER77.
           DISPLAY WS-HEADER77.

       CONNECT-DB-SAFE116.
           ACCEPT WS-CONN-PW116 FROM ENVIRONMENT 'DB_PASSWORD'.

       CHECK-LIMIT48.
           IF WS-AMOUNT48 > 1000
               MOVE 'Y' TO WS-FLAG48
           ELSE
               MOVE 'N' TO WS-FLAG48
           END-IF.

       FORMAT-HEADER199.
           MOVE 'MONTHLY REPORT' TO WS-TITLE199.
           STRING WS-TITLE199 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER199.
           DISPLAY WS-HEADER199.

       FORMAT-HEADER58.
           MOVE 'MONTHLY REPORT' TO WS-TITLE58.
           STRING WS-TITLE58 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER58.
           DISPLAY WS-HEADER58.

       WRITE-EXPORT-SAFE94.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH94.
           OPEN OUTPUT EXPORT-FILE94.
           CLOSE EXPORT-FILE94.

       COMPUTE-TOTALS60.
           MOVE 0 TO WS-TOTAL60.
           PERFORM VARYING WS-K60 FROM 1 BY 1 UNTIL WS-K60 > 10
               ADD WS-K60 TO WS-TOTAL60
           END-PERFORM.
           COMPUTE WS-AVERAGE60 = WS-TOTAL60 / 10.

       CONNECT-DB-SAFE66.
           ACCEPT WS-CONN-PW66 FROM ENVIRONMENT 'DB_PASSWORD'.

       ECHO-NAME-SAFE40.
           MOVE '<p>Thank you</p>' TO WS-PAGE40.
           EXEC CICS WEB SEND FROM(WS-PAGE40) END-EXEC.

       CHECK-LIMIT54.
           IF WS-AMOUNT54 > 1000
               MOVE 'Y' TO WS-FLAG54
           ELSE
               MOVE 'N' TO WS-FLAG54
           END-IF.

       CONNECT-DB131.
           MOVE WS-DB-PASSWORD131 TO WS-CONN-PW131.

       PREPARE-QUERY-SAFE92.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT92.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT92 END-EXEC.

       CLASSIFY-CODE142.
           EVALUATE WS-CODE142
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS142
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS142
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS142
           END-EVALUATE.

       PREPARE-QUERY78.
           MOVE LK-FILTER78 TO WS-STMT78.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT78 END-EXEC.

       CLASSIFY-CODE97.
           EVALUATE WS-CODE97
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS97
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS97
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS97
           END-EVALUATE.

       CHECK-LIMIT24.
           IF WS-AMOUNT24 > 1000
               MOVE 'Y' TO WS-FLAG24
           ELSE
               MOVE 'N' TO WS-FLAG24
           END-IF.

       CLASSIFY-CODE72.
           EVALUATE WS-CODE72
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS72
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS72
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS72
           END-EVALUATE.

       LOG-LOGIN192.
           DISPLAY 'LOGIN ' WS-USER192 ' ' WS-PASSWORD-IN192.

       CHECK-LIMIT177.
           IF WS-AMOUNT177 > 1000
               MOVE 'Y' TO WS-FLAG177
           ELSE
               MOVE 'N' TO WS-FLAG177
           END-IF.

       CLASSIFY-CODE183.
           EVALUATE WS-CODE183
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS183
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS183
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS183
           END-EVALUATE.

       CHECK-LIMIT174.
           IF WS-AMOUNT174 > 1000
               MOVE 'Y' TO WS-FLAG174
           ELSE
               MOVE 'N' TO WS-FLAG174
           END-IF.

