       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTR08.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EXPORT-FILE3 ASSIGN TO DYNAMIC WS-EXPORT-PATH3
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE8 ASSIGN TO DYNAMIC WS-EXPORT-PATH8
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE12 ASSIGN TO DYNAMIC WS-EXPORT-PATH12
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE27 ASSIGN TO DYNAMIC WS-EXPORT-PATH27
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE51 ASSIGN TO DYNAMIC WS-EXPORT-PATH51
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE62 ASSIGN TO DYNAMIC WS-EXPORT-PATH62
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE69 ASSIGN TO DYNAMIC WS-EXPORT-PATH69
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE75 ASSIGN TO DYNAMIC WS-EXPORT-PATH75
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE88 ASSIGN TO DYNAMIC WS-EXPORT-PATH88
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE103 ASSIGN TO DYNAMIC WS-EXPORT-PATH103
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE106 ASSIGN TO DYNAMIC WS-EXPORT-PATH106
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE109 ASSIGN TO DYNAMIC WS-EXPORT-PATH109
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE124 ASSIGN TO DYNAMIC WS-EXPORT-PATH124
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE134 ASSIGN TO DYNAMIC WS-EXPORT-PATH134
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE147 ASSIGN TO DYNAMIC WS-EXPORT-PATH147
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE151 ASSIGN TO DYNAMIC WS-EXPORT-PATH151
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE157 ASSIGN TO DYNAMIC WS-EXPORT-PATH157
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE167 ASSIGN TO DYNAMIC WS-EXPORT-PATH167
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE170 ASSIGN TO DYNAMIC WS-EXPORT-PATH170
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE176 ASSIGN TO DYNAMIC WS-EXPORT-PATH176
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE189 ASSIGN TO DYNAMIC WS-EXPORT-PATH189
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  EXPORT-FILE3.
       01  EXPORT-LINE3         PIC X(80).
       FD  EXPORT-FILE8.
       01  EXPORT-LINE8         PIC X(80).
       FD  EXPORT-FILE12.
       01  EXPORT-LINE12         PIC X(80).
       FD  EXPORT-FILE27.
       01  EXPORT-LINE27         PIC X(80).
       FD  EXPORT-FILE51.
       01  EXPORT-LINE51         PIC X(80).
       FD  EXPORT-FILE62.
       01  EXPORT-LINE62         PIC X(80).
       FD  EXPORT-FILE69.
       01  EXPORT-LINE69         PIC X(80).
       FD  EXPORT-FILE75.
       01  EXPORT-LINE75         PIC X(80).
       FD  EXPORT-FILE88.
       01  EXPORT-LINE88         PIC X(80).
       FD  EXPORT-FILE103.
       01  EXPORT-LINE103         PIC X(80).
       FD  EXPORT-FILE106.
       01  EXPORT-LINE106         PIC X(80).
       FD  EXPORT-FILE109.
       01  EXPORT-LINE109         PIC X(80).
       FD  EXPORT-FILE124.
       01  EXPORT-LINE124         PIC X(80).
       FD  EXPORT-FILE134.
       01  EXPORT-LINE134         PIC X(80).
       FD  EXPORT-FILE147.
       01  EXPORT-LINE147         PIC X(80).
       FD  EXPORT-FILE151.
       01  EXPORT-LINE151         PIC X(80).
       FD  EXPORT-FILE157.
       01  EXPORT-LINE157         PIC X(80).
       FD  EXPORT-FILE167.
       01  EXPORT-LINE167         PIC X(80).
       FD  EXPORT-FILE170.
       01  EXPORT-LINE170         PIC X(80).
       FD  EXPORT-FILE176.
       01  EXPORT-LINE176         PIC X(80).
       FD  EXPORT-FILE189.
       01  EXPORT-LINE189         PIC X(80).
       WORKING-STORAGE SECTION.
       01  WS-EXPORT-PATH3    PIC X(60).
       01  WS-DB-PASSWORD4    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW4        PIC X(12).
       01  WS-FORM6           PIC X(40).
       01  WS-PAGE6           PIC X(80).
       01  WS-EXPORT-PATH8    PIC X(60).
       01  WS-USER10           PIC X(10).
       01  WS-PASSWORD-IN10    PIC X(12).
       01  WS-EXPORT-PATH12    PIC X(60).
       01  WS-USER16           PIC X(10).
       01  WS-PASSWORD-IN16    PIC X(12).
       01  WS-USER17           PIC X(10).
       01  WS-PASSWORD-IN17    PIC X(12).
       01  WS-CMD18            PIC X(100).
       01  WS-STMT19           PIC X(200).
       01  WS-USER23           PIC X(10).
       01  WS-PASSWORD-IN23    PIC X(12).
       01  WS-USER24           PIC X(10).
       01  WS-PASSWORD-IN24    PIC X(12).
       01  WS-DB-PASSWORD25    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW25        PIC X(12).
       01  WS-CMD26            PIC X(100).
       01  WS-EXPORT-PATH27    PIC X(60).
       01  WS-DB-PASSWORD29    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW29        PIC X(12).
       01  WS-STMT31           PIC X(200).
       01  WS-FORM34           PIC X(40).
       01  WS-PAGE34           PIC X(80).
       01  WS-DB-PASSWORD36    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW36        PIC X(12).
       01  WS-FORM39           PIC X(40).
       01  WS-PAGE39           PIC X(80).
       01  WS-USER40           PIC X(10).
       01  WS-PASSWORD-IN40    PIC X(12).
       01  WS-POS42            PIC 99.
       01  WS-RECORD42         PIC X(80).
       01  WS-PART42           PIC X(5).
       01  WS-POS45            PIC 99.
       01  WS-RECORD45         PIC X(80).
       01  WS-PART45           PIC X(5).
       01  WS-USER46           PIC X(10).
       01  WS-PASSWORD-IN46    PIC X(12).
       01  WS-USER48           PIC X(10).
       01  WS-PASSWORD-IN48    PIC X(12).
       01  WS-STMT50           PIC X(200).
       01  WS-EXPORT-PATH51    PIC X(60).
       01  WS-POS53            PIC 99.
       01  WS-RECORD53         PIC X(80).
       01  WS-PART53           PIC X(5).
       01  WS-DB-PASSWORD58    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW58        PIC X(12).
       01  WS-EXPORT-PATH62    PIC X(60).
       01  WS-CMD63            PIC X(100).
       01  WS-USER67           PIC X(10).
       01  WS-PASSWORD-IN67    PIC X(12).
       01  WS-STMT68           PIC X(200).
       01  WS-EXPORT-PATH69    PIC X(60).
       01  WS-USER71           PIC X(10).
       01  WS-PASSWORD-IN71    PIC X(12).
       01  WS-CMD72            PIC X(100).
       01  WS-FORM74           PIC X(40).
       01  WS-PAGE74           PIC X(80).
       01  WS-EXPORT-PATH75    PIC X(60).
       01  WS-DB-PASSWORD76    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW76        PIC X(12).
       01  WS-DB-PASSWORD79    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW79        PIC X(12).
       01  WS-CMD80            PIC X(100).
       01  WS-DB-PASSWORD81    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW81        PIC X(12).
       01  WS-DB-PASSWORD86    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW86        PIC X(12).
       01  WS-DB-PASSWORD87    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW87        PIC X(12).
       01  WS-EXPORT-PATH88    PIC X(60).
       01  WS-USER92           PIC X(10).
       01  WS-PASSWORD-IN92    PIC X(12).
       01  WS-POS93            PIC 99.
       01  WS-RECORD93         PIC X(80).
       01  WS-PART93           PIC X(5).
       01  WS-DB-PASSWORD95    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW95        PIC X(12).
       01  WS-FORM96           PIC X(40).
       01  WS-PAGE96           PIC X(80).
       01  WS-DB-PASSWORD98    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW98        PIC X(12).
       01  WS-FORM99           PIC X(40).
       01  WS-PAGE99           PIC X(80).
       01  WS-USER102           PIC X(10).
       01  WS-PASSWORD-IN102    PIC X(12).
       01  WS-EXPORT-PATH103    PIC X(60).
       01  WS-STMT105           PIC X(200).
       01  WS-EXPORT-PATH106    PIC X(60).
       01  WS-POS107            PIC 99.
       01  WS-RECORD107         PIC X(80).
       01  WS-PART107           PIC X(5).
       01  WS-EXPORT-PATH109    PIC X(60).
       01  WS-DB-PASSWORD112    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW112        PIC X(12).
       01  WS-FORM116           PIC X(40).
       01  WS-PAGE116           PIC X(80).
       01  WS-USER117           PIC X(10).
       01  WS-PASSWORD-IN117    PIC X(12).
       01  WS-USER119           PIC X(10).
       01  WS-PASSWORD-IN119    PIC X(12).
       01  WS-DB-PASSWORD123    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW123        PIC X(12).
       01  WS-EXPORT-PATH124    PIC X(60).
       01  WS-USER126           PIC X(10).
       01  WS-PASSWORD-IN126    PIC X(12).
       01  WS-USER128           PIC X(10).
       01  WS-PASSWORD-IN128    PIC X(12).
       01  WS-FORM129           PIC X(40).
       01  WS-PAGE129           PIC X(80).
       01  WS-STMT130           PIC X(200).
       01  WS-STMT131           PIC X(200).
       01  WS-EXPORT-PATH134    PIC X(60).
       01  WS-POS137            PIC 99.
       01  WS-RECORD137         PIC X(80).
       01  WS-PART137           PIC X(5).
       01  WS-USER141           PIC X(10).
       01  WS-PASSWORD-IN141    PIC X(12).
       01  WS-CMD142            PIC X(100).
       01  WS-CMD143            PIC X(100).
       01  WS-EXPORT-PATH147    PIC X(60).
       01  WS-USER148           PIC X(10).
       01  WS-PASSWORD-IN148    PIC X(12).
       01  WS-STMT149           PIC X(200).
       01  WS-EXPORT-PATH151    PIC X(60).
       01  WS-FORM153           PIC X(40).
       01  WS-PAGE153           PIC X(80).
       01  WS-CMD155            PIC X(100).
       01  WS-EXPORT-PATH157    PIC X(60).
       01  WS-POS159            PIC 99.
       01  WS-RECORD159         PIC X(80).
       01  WS-PART159           PIC X(5).
       01  WS-POS160            PIC 99.
       01  WS-RECORD160         PIC X(80).
       01  WS-PART160           PIC X(5).
       01  WS-FORM162           PIC X(40).
       01  WS-PAGE162           PIC X(80).
       01  WS-CMD164            PIC X(100).
       01  WS-DB-PASSWORD166    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW166        PIC X(12).
       01  WS-EXPORT-PATH167    PIC X(60).
       01  WS-USER168           PIC X(10).
       01  WS-PASSWORD-IN168    PIC X(12).
       01  WS-USER169           PIC X(10).
       01  WS-PASSWORD-IN169    PIC X(12).
       01  WS-EXPORT-PATH170    PIC X(60).
       01  WS-POS171            PIC 99.
       01  WS-RECORD171         PIC X(80).
       01  WS-PART171           PIC X(5).
       01  WS-POS172            PIC 99.
       01  WS-RECORD172         PIC X(80).
       01  WS-PART172           PIC X(5).
       01  WS-USER173           PIC X(10).
       01  WS-PASSWORD-IN173    PIC X(12).
       01  WS-DB-PASSWORD174    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW174        PIC X(12).
       01  WS-EXPORT-PATH176    PIC X(60).
       01  WS-DB-PASSWORD177    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW177        PIC X(12).
       01  WS-STMT179           PIC X(200).
       01  WS-FORM181           PIC X(40).
       01  WS-PAGE181           PIC X(80).
       01  WS-DB-PASSWORD183    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW183        PIC X(12).
       01  WS-FORM185           PIC X(40).
       01  WS-PAGE185           PIC X(80).
       01  WS-POS188            PIC 99.
       01  WS-RECORD188         PIC X(80).
       01  WS-PART188           PIC X(5).
       01  WS-EXPORT-PATH189    PIC X(60).
       01  WS-DB-PASSWORD190    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW190        PIC X(12).
       01  WS-CMD191            PIC X(100).
       01  WS-FORM192           PIC X(40).
       01  WS-PAGE192           PIC X(80).
       01  WS-FORM193           PIC X(40).
       01  WS-PAGE193           PIC X(80).
       01  WS-STMT194           PIC X(200).
       01  WS-FORM195           PIC X(40).
       01  WS-PAGE195           PIC X(80).
       01  WS-FORM196           PIC X(40).
       01  WS-PAGE196           PIC X(80).
       01  WS-CODE1           PIC 9 VALUE 1.
       01  WS-STATUS1         PIC X(6) VALUE SPACES.
       01  WS-TITLE2          PIC X(20) VALUE SPACES.
       01  WS-HEADER2         PIC X(40) VALUE SPACES.
       01  WS-CODE5           PIC 9 VALUE 1.
       01  WS-STATUS5         PIC X(6) VALUE SPACES.
       01  WS-CODE7           PIC 9 VALUE 1.
       01  WS-STATUS7         PIC X(6) VALUE SPACES.
       01  WS-TOTAL9          PIC 9(6) VALUE 0.
       01  WS-K9              PIC 99 VALUE 0.
       01  WS-AVERAGE9        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL11          PIC 9(6) VALUE 0.
       01  WS-K11              PIC 99 VALUE 0.
       01  WS-AVERAGE11        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE13          PIC X(20) VALUE SPACES.
       01  WS-HEADER13         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT14         PIC 9(6) VALUE 500.
       01  WS-FLAG14           PIC X VALUE 'N'.
       01  WS-CODE15           PIC 9 VALUE 1.
       01  WS-STATUS15         PIC X(6) VALUE SPACES.
       01  WS-CODE20           PIC 9 VALUE 1.
       01  WS-STATUS20         PIC X(6) VALUE SPACES.
       01  WS-CODE21           PIC 9 VALUE 1.
       01  WS-STATUS21         PIC X(6) VALUE SPACES.
       01  WS-TITLE22          PIC X(20) VALUE SPACES.
       01  WS-HEADER22         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT28         PIC 9(6) VALUE 500.
       01  WS-FLAG28           PIC X VALUE 'N'.
       01  WS-AMOUNT30         PIC 9(6) VALUE 500.
       01  WS-FLAG30           PIC X VALUE 'N'.
       01  WS-CODE32           PIC 9 VALUE 1.
       01  WS-STATUS32         PIC X(6) VALUE SPACES.
       01  WS-TOTAL33          PIC 9(6) VALUE 0.
       01  WS-K33              PIC 99 VALUE 0.
       01  WS-AVERAGE33        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL35          PIC 9(6) VALUE 0.
       01  WS-K35              PIC 99 VALUE 0.
       01  WS-AVERAGE35        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE37          PIC X(20) VALUE SPACES.
       01  WS-HEADER37         PIC X(40) VALUE SPACES.
       01  WS-TOTAL38          PIC 9(6) VALUE 0.
       01  WS-K38              PIC 99 VALUE 0.
       01  WS-AVERAGE38        PIC 9(6)V99 VALUE 0.
       01  WS-CODE41           PIC 9 VALUE 1.
       01  WS-STATUS41         PIC X(6) VALUE SPACES.
       01  WS-TITLE43          PIC X(20) VALUE SPACES.
       01  WS-HEADER43         PIC X(40) VALUE SPACES.
       01  WS-TITLE44          PIC X(20) VALUE SPACES.
       01  WS-HEADER44         PIC X(40) VALUE SPACES.
       01  WS-TITLE47          PIC X(20) VALUE SPACES.
       01  WS-HEADER47         PIC X(40) VALUE SPACES.
       01  WS-CODE49           PIC 9 VALUE 1.
       01  WS-STATUS49         PIC X(6) VALUE SPACES.
       01  WS-TITLE52          PIC X(20) VALUE SPACES.
       01  WS-HEADER52         PIC X(40) VALUE SPACES.
       01  WS-CODE54           PIC 9 VALUE 1.
       01  WS-STATUS54         PIC X(6) VALUE SPACES.
       01  WS-TOTAL55          PIC 9(6) VALUE 0.
       01  WS-K55              PIC 99 VALUE 0.
       01  WS-AVERAGE55        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE56          PIC X(20) VALUE SPACES.
       01  WS-HEADER56         PIC X(40) VALUE SPACES.
       01  WS-TITLE57          PIC X(20) VALUE SPACES.
       01  WS-HEADER57         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT59         PIC 9(6) VALUE 500.
       01  WS-FLAG59           PIC X VALUE 'N'.
       01  WS-CODE60           PIC 9 VALUE 1.
       01  WS-STATUS60         PIC X(6) VALUE SPACES.
       01  WS-TOTAL61          PIC 9(6) VALUE 0.
       01  WS-K61              PIC 99 VALUE 0.
       01  WS-AVERAGE61        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE64          PIC X(20) VALUE SPACES.
       01  WS-HEADER64         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT65         PIC 9(6) VALUE 500.
       01  WS-FLAG65           PIC X VALUE 'N'.
       01  WS-TOTAL66          PIC 9(6) VALUE 0.
       01  WS-K66              PIC 99 VALUE 0.
       01  WS-AVERAGE66        PIC 9(6)V99 VALUE 0.
       01  WS-CODE70           PIC 9 VALUE 1.
       01  WS-STATUS70         PIC X(6) VALUE SPACES.
       01  WS-CODE73           PIC 9 VALUE 1.
       01  WS-STATUS73         PIC X(6) VALUE SPACES.
       01  WS-CODE77           PIC 9 VALUE 1.
       01  WS-STATUS77         PIC X(6) VALUE SPACES.
       01  WS-TOTAL78          PIC 9(6) VALUE 0.
       01  WS-K78              PIC 99 VALUE 0.
       01  WS-AVERAGE78        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL82          PIC 9(6) VALUE 0.
       01  WS-K82              PIC 99 VALUE 0.
       01  WS-AVERAGE82        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL83          PIC 9(6) VALUE 0.
       01  WS-K83              PIC 99 VALUE 0.
       01  WS-AVERAGE83        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE84          PIC X(20) VALUE SPACES.
       01  WS-HEADER84         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT85         PIC 9(6) VALUE 500.
       01  WS-FLAG85           PIC X VALUE 'N'.
       01  WS-CODE89           PIC 9 VALUE 1.
       01  WS-STATUS89         PIC X(6) VALUE SPACES.
       01  WS-TITLE90          PIC X(20) VALUE SPACES.
       01  WS-HEADER90         PIC X(40) VALUE SPACES.
       01  WS-TOTAL91          PIC 9(6) VALUE 0.
       01  WS-K91              PIC 99 VALUE 0.
       01  WS-AVERAGE91        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE94          PIC X(20) VALUE SPACES.
       01  WS-HEADER94         PIC X(40) VALUE SPACES.
       01  WS-TOTAL97          PIC 9(6) VALUE 0.
       01  WS-K97              PIC 99 VALUE 0.
       01  WS-AVERAGE97        PIC 9(6)V99 VALUE 0.
       01  WS-CODE100           PIC 9 VALUE 1.
       01  WS-STATUS100         PIC X(6) VALUE SPACES.
       01  WS-TOTAL101          PIC 9(6) VALUE 0.
       01  WS-K101              PIC 99 VALUE 0.
       01  WS-AVERAGE101        PIC 9(6)V99 VALUE 0.
       01  WS-CODE104           PIC 9 VALUE 1.
       01  WS-STATUS104         PIC X(6) VALUE SPACES.
       01  WS-CODE108           PIC 9 VALUE 1.
       01  WS-STATUS108         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT110         PIC 9(6) VALUE 500.
       01  WS-FLAG110           PIC X VALUE 'N'.
       01  WS-TOTAL111          PIC 9(6) VALUE 0.
       01  WS-K111              PIC 99 VALUE 0.
       01  WS-AVERAGE111        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL113          PIC 9(6) VALUE 0.
       01  WS-K113              PIC 99 VALUE 0.
       01  WS-AVERAGE113        PIC 9(6)V99 VALUE 0.
       01  WS-CODE114           PIC 9 VALUE 1.
       01  WS-STATUS114         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT115         PIC 9(6) VALUE 500.
       01  WS-FLAG115           PIC X VALUE 'N'.
       01  WS-TITLE118          PIC X(20) VALUE SPACES.
       01  WS-HEADER118         PIC X(40) VALUE SPACES.
       01  WS-CODE120           PIC 9 VALUE 1.
       01  WS-STATUS120         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT121         PIC 9(6) VALUE 500.
       01  WS-FLAG121           PIC X VALUE 'N'.
       01  WS-TITLE122          PIC X(20) VALUE SPACES.
       01  WS-HEADER122         PIC X(40) VALUE SPACES.
       01  WS-TITLE125          PIC X(20) VALUE SPACES.
       01  WS-HEADER125         PIC X(40) VALUE SPACES.
       01  WS-TOTAL127          PIC 9(6) VALUE 0.
       01  WS-K127              PIC 99 VALUE 0.
       01  WS-AVERAGE127        PIC 9(6)V99 VALUE 0.
       01  WS-CODE132           PIC 9 VALUE 1.
       01  WS-STATUS132         PIC X(6) VALUE SPACES.
       01  WS-TITLE133          PIC X(20) VALUE SPACES.
       01  WS-HEADER133         PIC X(40) VALUE SPACES.
       01  WS-TITLE135          PIC X(20) VALUE SPACES.
       01  WS-HEADER135         PIC X(40) VALUE SPACES.
       01  WS-CODE136           PIC 9 VALUE 1.
       01  WS-STATUS136         PIC X(6) VALUE SPACES.
       01  WS-CODE138           PIC 9 VALUE 1.
       01  WS-STATUS138         PIC X(6) VALUE SPACES.
       01  WS-CODE139           PIC 9 VALUE 1.
       01  WS-STATUS139         PIC X(6) VALUE SPACES.
       01  WS-TOTAL140          PIC 9(6) VALUE 0.
       01  WS-K140              PIC 99 VALUE 0.
       01  WS-AVERAGE140        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT144         PIC 9(6) VALUE 500.
       01  WS-FLAG144           PIC X VALUE 'N'.
       01  WS-CODE145           PIC 9 VALUE 1.
       01  WS-STATUS145         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT146         PIC 9(6) VALUE 500.
       01  WS-FLAG146           PIC X VALUE 'N'.
       01  WS-TOTAL150          PIC 9(6) VALUE 0.
       01  WS-K150              PIC 99 VALUE 0.
       01  WS-AVERAGE150        PIC 9(6)V99 VALUE 0.
       01  WS-CODE152           PIC 9 VALUE 1.
       01  WS-STATUS152         PIC X(6) VALUE SPACES.
       01  WS-TOTAL154          PIC 9(6) VALUE 0.
       01  WS-K154              PIC 99 VALUE 0.
       01  WS-AVERAGE154        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL156          PIC 9(6) VALUE 0.
       01  WS-K156              PIC 99 VALUE 0.
       01  WS-AVERAGE156        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT158         PIC 9(6) VALUE 500.
       01  WS-FLAG158           PIC X VALUE 'N'.
       01  WS-AMOUNT161         PIC 9(6) VALUE 500.
       01  WS-FLAG161           PIC X VALUE 'N'.
       01  WS-TITLE163          PIC X(20) VALUE SPACES.
       01  WS-HEADER163         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT165         PIC 9(6) VALUE 500.
       01  WS-FLAG165           PIC X VALUE 'N'.
       01  WS-AMOUNT175         PIC 9(6) VALUE 500.
       01  WS-FLAG175           PIC X VALUE 'N'.
       01  WS-TOTAL178          PIC 9(6) VALUE 0.
       01  WS-K178              PIC 99 VALUE 0.
       01  WS-AVERAGE178        PIC 9(6)V99 VALUE 0.
       01  WS-CODE180           PIC 9 VALUE 1.
       01  WS-STATUS180         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT182         PIC 9(6) VALUE 500.
       01  WS-FLAG182           PIC X VALUE 'N'.
       01  WS-TOTAL184          PIC 9(6) VALUE 0.
       01  WS-K184              PIC 99 VALUE 0.
       01  WS-AVERAGE184        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT186         PIC 9(6) VALUE 500.
       01  WS-FLAG186           PIC X VALUE 'N'.
       01  WS-CODE187           PIC 9 VALUE 1.
       01  WS-STATUS187         PIC X(6) VALUE SPACES.
       01  WS-TITLE197          PIC X(20) VALUE SPACES.
       01  WS-HEADER197         PIC X(40) VALUE SPACES.
       01  WS-CODE198           PIC 9 VALUE 1.
       01  WS-STATUS198         PIC X(6) VALUE SPACES.
       LINKAGE SECTION.
       01  LK-PATH3           PIC X(60).
       01  LK-PATH8           PIC X(60).
       01  LK-PATH12           PIC X(60).
       01  LK-NAME18           PIC X(40).
       01  LK-FILTER19         PIC X(100).
       01  LK-NAME26           PIC X(40).
       01  LK-PATH27           PIC X(60).
       01  LK-FILTER31         PIC X(100).
       01  LK-FILTER50         PIC X(100).
       01  LK-PATH51           PIC X(60).
       01  LK-PATH62           PIC X(60).
       01  LK-NAME63           PIC X(40).
       01  LK-FILTER68         PIC X(100).
       01  LK-PATH69           PIC X(60).
       01  LK-NAME72           PIC X(40).
       01  LK-PATH75           PIC X(60).
       01  LK-NAME80           PIC X(40).
       01  LK-PATH88           PIC X(60).
       01  LK-PATH103           PIC X(60).
       01  LK-FILTER105         PIC X(100).
       01  LK-PATH106           PIC X(60).
       01  LK-PATH109           PIC X(60).
       01  LK-PATH124           PIC X(60).
       01  LK-FILTER130         PIC X(100).
       01  LK-FILTER131         PIC X(100).
       01  LK-PATH134           PIC X(60).
       01  LK-NAME142           PIC X(40).
       01  LK-NAME143           PIC X(40).
       01  LK-PATH147           PIC X(60).
       01  LK-FILTER149         PIC X(100).
       01  LK-PATH151           PIC X(60).
       01  LK-NAME155           PIC X(40).
       01  LK-PATH157           PIC X(60).
       01  LK-NAME164           PIC X(40).
       01  LK-PATH167           PIC X(60).
       01  LK-PATH170           PIC X(60).
       01  LK-PATH176           PIC X(60).
       01  LK-FILTER179         PIC X(100).
       01  LK-PATH189           PIC X(60).
       01  LK-NAME191           PIC X(40).
       01  LK-FILTER194         PIC X(100).
       PROCEDURE DIVISION USING LK-PATH3 LK-PATH8 LK-PATH12 LK-NAME18 LK-FILTER19 LK-NAME26 LK-PATH27 LK-FILTER31 LK-FILTER50 LK-PATH51 LK-PATH62 LK-NAME63 LK-FILTER68 LK-PATH69 LK-NAME72 LK-PATH75 LK-NAME80 LK-PATH88 LK-PATH103 LK-FILTER105 LK-PATH106 LK-PATH109 LK-PATH124 LK-FILTER130 LK-FILTER131 LK-PATH134 LK-NAME142 LK-NAME143 LK-PATH147 LK-FILTER149 LK-PATH151 LK-NAME155 LK-PATH157 LK-NAME164 LK-PATH167 LK-PATH170 LK-PATH176 LK-FILTER179 LK-PATH189 LK-NAME191 LK-FILTER194.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       FORMAT-HEADER56.
           MOVE 'MONTHLY REPORT' TO WS-TITLE56.
           STRING WS-TITLE56 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER56.
           DISPLAY WS-HEADER56.

       CONNECT-DB-SAFE174.
           ACCEPT WS-CONN-PW174 FROM ENVIRONMENT 'DB_PASSWORD'.

       PREPARE-QUERY31.
           MOVE LK-FILTER31 TO WS-STMT31.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT31 END-EXEC.

       ECHO-NAME99.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM99) END-EXEC.
           STRING '<p>' WS-FORM99 '</p>' DELIMITED BY SIZE INTO WS-PAGE99.
           EXEC CICS WEB SEND FROM(WS-PAGE99) END-EXEC.

       CHECK-LIMIT175.
           IF WS-AMOUNT175 > 1000
               MOVE 'Y' TO WS-FLAG175
           ELSE
               MOVE 'N' TO WS-FLAG175
           END-IF.

       EXTRACT-FIELD-SAFE159.
           ACCEPT WS-POS159.
           IF WS-POS159 IS NUMERIC AND WS-POS159 > 0 AND WS-POS159 < 76
               MOVE WS-RECORD159(WS-POS159:5) TO WS-PART159
           END-IF.

       LOG-LOGIN169.
           DISPLAY 'LOGIN ' WS-USER169 ' ' WS-PASSWORD-IN169.

       CLASSIFY-CODE89.
           EVALUATE WS-CODE89
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS89
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS89
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS89
           END-EVALUATE.

       CONVERT-FILE-SAFE63.
           MOVE "convert /srv/in/report.txt" TO WS-CMD63.
           CALL 'SYSTEM' USING WS-CMD63.

       WRITE-EXPORT-SAFE176.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH176.
           OPEN OUTPUT EXPORT-FILE176.
           CLOSE EXPORT-FILE176.

       COMPUTE-TOTALS61.
           MOVE 0 TO WS-TOTAL61.
           PERFORM VARYING WS-K61 FROM 1 BY 1 UNTIL WS-K61 > 10
               ADD WS-K61 TO WS-TOTAL61
           END-PERFORM.
           COMPUTE WS-AVERAGE61 = WS-TOTAL61 / 10.

       CHECK-LIMIT85.
           IF WS-AMOUNT85 > 1000
               MOVE 'Y' TO WS-FLAG85
           ELSE
               MOVE 'N' TO WS-FLAG85
           END-IF.

       WRITE-EXPORT151.
           MOVE LK-PATH151 TO WS-EXPORT-PATH151.
           OPEN OUTPUT EXPORT-FILE151.
           CLOSE EXPORT-FILE151.

       CLASSIFY-CODE32.
           EVALUATE WS-CODE32
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS32
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS32
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS32
           END-EVALUATE.

       LOG-LOGIN16.
           DISPLAY 'LOGIN ' WS-USER16 ' ' WS-PASSWORD-IN16.

       CHECK-LIMIT28.
           IF WS-AMOUNT28 > 1000
               MOVE 'Y' TO WS-FLAG28
           ELSE
               MOVE 'N' TO WS-FLAG28
           END-IF.

       CONNECT-DB29.
           MOVE WS-DB-PASSWORD29 TO WS-CONN-PW29.

       CLASSIFY-CODE41.
           EVALUATE WS-CODE41
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS41
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS41
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS41
           END-EVALUATE.

       CONVERT-FILE-SAFE191.
           MOVE "convert /srv/in/report.txt" TO WS-CMD191.
           CALL 'SYSTEM' USING WS-CMD191.

       CONVERT-FILE142.
           STRING "convert " LK-NAME142 DELIMITED BY SIZE INTO WS-CMD142.
           CALL 'SYSTEM' USING WS-CMD142.

       CLASSIFY-CODE49.
           EVALUATE WS-CODE49
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS49
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS49
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS49
           END-EVALUATE.

       EXTRACT-FIELD-SAFE188.
           ACCEPT WS-POS188.
           IF WS-POS188 IS NUMERIC AND WS-POS188 > 0 AND WS-POS188 < 76
               MOVE WS-RECORD188(WS-POS188:5) TO WS-PART188
           END-IF.

       CHECK-LIMIT59.
           IF WS-AMOUNT59 > 1000
               MOVE 'Y' TO WS-FLAG59
           ELSE
               MOVE 'N' TO WS-FLAG59
           END-IF.

       LOG-LOGIN148.
           DISPLAY 'LOGIN ' WS-USER148 ' ' WS-PASSWORD-IN148.

       ECHO-NAME74.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM74) END-EXEC.
           STRING '<p>' WS-FORM74 '</p>' DELIMITED BY SIZE INTO WS-PAGE74.
           EXEC CICS WEB SEND FROM(WS-PAGE74) END-EXEC.

       FORMAT-HEADER135.
           MOVE 'MONTHLY REPORT' TO WS-TITLE135.
           STRING WS-TITLE135 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER135.
           DISPLAY WS-HEADER135.

       COMPUTE-TOTALS66.
           MOVE 0 TO WS-TOTAL66.
           PERFORM VARYING WS-K66 FROM 1 BY 1 UNTIL WS-K66 > 10
               ADD WS-K66 TO WS-TOTAL66
           END-PERFORM.
           COMPUTE WS-AVERAGE66 = WS-TOTAL66 / 10.

       ECHO-NAME193.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM193) END-EXEC.
           STRING '<p>' WS-FORM193 '</p>' DELIMITED BY SIZE INTO WS-PAGE193.
           EXEC CICS WEB SEND FROM(WS-PAGE193) END-EXEC.

       CHECK-LIMIT14.
           IF WS-AMOUNT14 > 1000
               MOVE 'Y' TO WS-FLAG14
           ELSE
               MOVE 'N' TO WS-FLAG14
           END-IF.

       LOG-LOGIN-SAFE24.
           DISPLAY 'LOGIN ' WS-USER24.

       CLASSIFY-CODE198.
           EVALUATE WS-CODE198
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS198
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS198
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS198
           END-EVALUATE.

       WRITE-EXPORT12.
           MOVE LK-PATH12 TO WS-EXPORT-PATH12.
           OPEN OUTPUT EXPORT-FILE12.
           CLOSE EXPORT-FILE12.

       FORMAT-HEADER43.
           MOVE 'MONTHLY REPORT' TO WS-TITLE43.
           STRING WS-TITLE43 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER43.
           DISPLAY WS-HEADER43.

       FORMAT-HEADER118.
           MOVE 'MONTHLY REPORT' TO WS-TITLE118.
           STRING WS-TITLE118 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER118.
           DISPLAY WS-HEADER118.

       PREPARE-QUERY194.
           MOVE LK-FILTER194 TO WS-STMT194.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT194 END-EXEC.

       CONVERT-FILE26.
           STRING "convert " LK-NAME26 DELIMITED BY SIZE INTO WS-CMD26.
           CALL 'SYSTEM' USING WS-CMD26.

       WRITE-EXPORT3.
           MOVE LK-PATH3 TO WS-EXPORT-PATH3.
           OPEN OUTPUT EXPORT-FILE3.
           CLOSE EXPORT-FILE3.

       FORMAT-HEADER94.
           MOVE 'MONTHLY REPORT' TO WS-TITLE94.
           STRING WS-TITLE94 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER94.
           DISPLAY WS-HEADER94.

       CONNECT-DB4.
           MOVE WS-DB-PASSWORD4 TO WS-CONN-PW4.

       WRITE-EXPORT-SAFE109.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH109.
           OPEN OUTPUT EXPORT-FILE109.
           CLOSE EXPORT-FILE109.

       ECHO-NAME-SAFE192.
           MOVE '<p>Thank you</p>' TO WS-PAGE192.
           EXEC CICS WEB SEND FROM(WS-PAGE192) END-EXEC.

       COMPUTE-TOTALS83.
           MOVE 0 TO WS-TOTAL83.
           PERFORM VARYING WS-K83 FROM 1 BY 1 UNTIL WS-K83 > 10
               ADD WS-K83 TO WS-TOTAL83
           END-PERFORM.
           COMPUTE WS-AVERAGE83 = WS-TOTAL83 / 10.

       FORMAT-HEADER57.
           MOVE 'MONTHLY REPORT' TO WS-TITLE57.
           STRING WS-TITLE57 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER57.
           DISPLAY WS-HEADER57.

       ECHO-NAME34.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM34) END-EXEC.
           STRING '<p>' WS-FORM34 '</p>' DELIMITED BY SIZE INTO WS-PAGE34.
           EXEC CICS WEB SEND FROM(WS-PAGE34) END-EXEC.

       CONNECT-DB76.
           MOVE WS-DB-PASSWORD76 TO WS-CONN-PW76.

       CLASSIFY-CODE1.
           EVALUATE WS-CODE1
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS1
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS1
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS1
           END-EVALUATE.

       WRITE-EXPORT134.
           MOVE LK-PATH134 TO WS-EXPORT-PATH134.
           OPEN OUTPUT EXPORT-FILE134.
           CLOSE EXPORT-FILE134.

       COMPUTE-TOTALS111.
           MOVE 0 TO WS-TOTAL111.
           PERFORM VARYING WS-K111 FROM 1 BY 1 UNTIL WS-K111 > 10
               ADD WS-K111 TO WS-TOTAL111
           END-PERFORM.
           COMPUTE WS-AVERAGE111 = WS-TOTAL111 / 10.

       ECHO-NAME96.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM96) END-EXEC.
           STRING '<p>' WS-FORM96 '</p>' DELIMITED BY SIZE INTO WS-PAGE96.
           EXEC CICS WEB SEND FROM(WS-PAGE96) END-EXEC.

       CONNECT-DB79.
           MOVE WS-DB-PASSWORD79 TO WS-CONN-PW79.

       COMPUTE-TOTALS35.
           MOVE 0 TO WS-TOTAL35.
           PERFORM VARYING WS-K35 FROM 1 BY 1 UNTIL WS-K35 > 10
               ADD WS-K35 TO WS-TOTAL35
           END-PERFORM.
           COMPUTE WS-AVERAGE35 = WS-TOTAL35 / 10.

       COMPUTE-TOTALS154.
           MOVE 0 TO WS-TOTAL154.
           PERFORM VARYING WS-K154 FROM 1 BY 1 UNTIL WS-K154 > 10
               ADD WS-K154 TO WS-TOTAL154
           END-PERFORM.
           COMPUTE WS-AVERAGE154 = WS-TOTAL154 / 10.

       ECHO-NAME195.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM195) END-EXEC.
           STRING '<p>' WS-FORM195 '</p>' DELIMITED BY SIZE INTO WS-PAGE195.
           EXEC CICS WEB SEND FROM(WS-PAGE195) END-EXEC.

       CONVERT-FILE143.
           STRING "convert " LK-NAME143 DELIMITED BY SIZE INTO WS-CMD143.
           CALL 'SYSTEM' USING WS-CMD143.

       CLASSIFY-CODE70.
           EVALUATE WS-CODE70
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS70
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS70
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS70
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

       CHECK-LIMIT161.
           IF WS-AMOUNT161 > 1000
               MOVE 'Y' TO WS-FLAG161
           ELSE
               MOVE 'N' TO WS-FLAG161
           END-IF.

       LOG-LOGIN141.
           DISPLAY 'LOGIN ' WS-USER141 ' ' WS-PASSWORD-IN141.

       WRITE-EXPORT-SAFE69.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH69.
           OPEN OUTPUT EXPORT-FILE69.
           CLOSE EXPORT-FILE69.

       WRITE-EXPORT-SAFE27.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH27.
           OPEN OUTPUT EXPORT-FILE27.
           CLOSE EXPORT-FILE27.

       CONVERT-FILE18.
           STRING "convert " LK-NAME18 DELIMITED BY SIZE INTO WS-CMD18.
           CALL 'SYSTEM' USING WS-CMD18.

       COMPUTE-TOTALS9.
           MOVE 0 TO WS-TOTAL9.
           PERFORM VARYING WS-K9 FROM 1 BY 1 UNTIL WS-K9 > 10
               ADD WS-K9 TO WS-TOTAL9
           END-PERFORM.
           COMPUTE WS-AVERAGE9 = WS-TOTAL9 / 10.

       PREPARE-QUERY105.
           MOVE LK-FILTER105 TO WS-STMT105.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT105 END-EXEC.

       COMPUTE-TOTALS97.
           MOVE 0 TO WS-TOTAL97.
           PERFORM VARYING WS-K97 FROM 1 BY 1 UNTIL WS-K97 > 10
               ADD WS-K97 TO WS-TOTAL97
           END-PERFORM.
           COMPUTE WS-AVERAGE97 = WS-TOTAL97 / 10.

       COMPUTE-TOTALS82.
           MOVE 0 TO WS-TOTAL82.
           PERFORM VARYING WS-K82 FROM 1 BY 1 UNTIL WS-K82 > 10
               ADD WS-K82 TO WS-TOTAL82
           END-PERFORM.
           COMPUTE WS-AVERAGE82 = WS-TOTAL82 / 10.

       ECHO-NAME-SAFE162.
           MOVE '<p>Thank you</p>' TO WS-PAGE162.
           EXEC CICS WEB SEND FROM(WS-PAGE162) END-EXEC.

       FORMAT-HEADER2.
           MOVE 'MONTHLY REPORT' TO WS-TITLE2.
           STRING WS-TITLE2 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER2.
           DISPLAY WS-HEADER2.

       CLASSIFY-CODE136.
           EVALUATE WS-CODE136
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS136
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS136
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS136
           END-EVALUATE.

       CONNECT-DB36.
           MOVE WS-DB-PASSWORD36 TO WS-CONN-PW36.

       ECHO-NAME-SAFE181.
           MOVE '<p>Thank you</p>' TO WS-PAGE181.
           EXEC CICS WEB SEND FROM(WS-PAGE181) END-EXEC.

       CLASSIFY-CODE77.
           EVALUATE WS-CODE77
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS77
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS77
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS77
           END-EVALUATE.

       ECHO-NAME-SAFE185.
           MOVE '<p>Thank you</p>' TO WS-PAGE185.
           EXEC CICS WEB SEND FROM(WS-PAGE185) END-EXEC.

       LOG-LOGIN46.
           DISPLAY 'LOGIN ' WS-USER46 ' ' WS-PASSWORD-IN46.

       COMPUTE-TOTALS91.
           MOVE 0 TO WS-TOTAL91.
           PERFORM VARYING WS-K91 FROM 1 BY 1 UNTIL WS-K91 > 10
               ADD WS-K91 TO WS-TOTAL91
           END-PERFORM.
           COMPUTE WS-AVERAGE91 = WS-TOTAL91 / 10.

       WRITE-EXPORT-SAFE8.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH8.
           OPEN OUTPUT EXPORT-FILE8.
           CLOSE EXPORT-FILE8.

       LOG-LOGIN92.
           DISPLAY 'LOGIN ' WS-USER92 ' ' WS-PASSWORD-IN92.

       COMPUTE-TOTALS113.
           MOVE 0 TO WS-TOTAL113.
           PERFORM VARYING WS-K113 FROM 1 BY 1 UNTIL WS-K113 > 10
               ADD WS-K113 TO WS-TOTAL113
           END-PERFORM.
           COMPUTE WS-AVERAGE113 = WS-TOTAL113 / 10.

       CONNECT-DB123.
           MOVE WS-DB-PASSWORD123 TO WS-CONN-PW123.

       COMPUTE-TOTALS156.
           MOVE 0 TO WS-TOTAL156.
           PERFORM VARYING WS-K156 FROM 1 BY 1 UNTIL WS-K156 > 10
               ADD WS-K156 TO WS-TOTAL156
           END-PERFORM.
           COMPUTE WS-AVERAGE156 = WS-TOTAL156 / 10.

       CHECK-LIMIT158.
           IF WS-AMOUNT158 > 1000
               MOVE 'Y' TO WS-FLAG158
           ELSE
               MOVE 'N' TO WS-FLAG158
           END-IF.

       PREPARE-QUERY149.
           MOVE LK-FILTER149 TO WS-STMT149.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT149 END-EXEC.

       EXTRACT-FIELD172.
           ACCEPT WS-POS172.
           MOVE WS-RECORD172(WS-POS172:5) TO WS-PART172.

       LOG-LOGIN128.
           DISPLAY 'LOGIN ' WS-USER128 ' ' WS-PASSWORD-IN128.

       CLASSIFY-CODE138.
           EVALUATE WS-CODE138
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS138
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS138
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS138
           END-EVALUATE.

       COMPUTE-TOTALS101.
           MOVE 0 TO WS-TOTAL101.
           PERFORM VARYING WS-K101 FROM 1 BY 1 UNTIL WS-K101 > 10
               ADD WS-K101 TO WS-TOTAL101
           END-PERFORM.
           COMPUTE WS-AVERAGE101 = WS-TOTAL101 / 10.

       WRITE-EXPORT75.
           MOVE LK-PATH75 TO WS-EXPORT-PATH75.
           OPEN OUTPUT EXPORT-FILE75.
           CLOSE EXPORT-FILE75.

       LOG-LOGIN173.
           DISPLAY 'LOGIN ' WS-USER173 ' ' WS-PASSWORD-IN173.

       ECHO-NAME-SAFE153.
           MOVE '<p>Thank you</p>' TO WS-PAGE153.
           EXEC CICS WEB SEND FROM(WS-PAGE153) END-EXEC.

       WRITE-EXPORT62.
           MOVE LK-PATH62 TO WS-EXPORT-PATH62.
           OPEN OUTPUT EXPORT-FILE62.
           CLOSE EXPORT-FILE62.

       FORMAT-HEADER64.
           MOVE 'MONTHLY REPORT' TO WS-TITLE64.
           STRING WS-TITLE64 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER64.
           DISPLAY WS-HEADER64.

       COMPUTE-TOTALS33.
           MOVE 0 TO WS-TOTAL33.
           PERFORM VARYING WS-K33 FROM 1 BY 1 UNTIL WS-K33 > 10
               ADD WS-K33 TO WS-TOTAL33
           END-PERFORM.
           COMPUTE WS-AVERAGE33 = WS-TOTAL33 / 10.

       CONVERT-FILE-SAFE155.
           MOVE "convert /srv/in/report.txt" TO WS-CMD155.
           CALL 'SYSTEM' USING WS-CMD155.

       CONVERT-FILE-SAFE72.
           MOVE "convert /srv/in/report.txt" TO WS-CMD72.
           CALL 'SYSTEM' USING WS-CMD72.

       CHECK-LIMIT165.
           IF WS-AMOUNT165 > 1000
               MOVE 'Y' TO WS-FLAG165
           ELSE
               MOVE 'N' TO WS-FLAG165
           END-IF.

       CONVERT-FILE164.
           STRING "convert " LK-NAME164 DELIMITED BY SIZE INTO WS-CMD164.
           CALL 'SYSTEM' USING WS-CMD164.

       CLASSIFY-CODE21.
           EVALUATE WS-CODE21
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS21
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS21
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS21
           END-EVALUATE.

       CLASSIFY-CODE5.
           EVALUATE WS-CODE5
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS5
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS5
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS5
           END-EVALUATE.

       CLASSIFY-CODE73.
           EVALUATE WS-CODE73
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS73
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS73
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS73
           END-EVALUATE.

       CONNECT-DB-SAFE98.
           ACCEPT WS-CONN-PW98 FROM ENVIRONMENT 'DB_PASSWORD'.

       CONNECT-DB-SAFE58.
           ACCEPT WS-CONN-PW58 FROM ENVIRONMENT 'DB_PASSWORD'.

       CLASSIFY-CODE145.
           EVALUATE WS-CODE145
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS145
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS145
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS145
           END-EVALUATE.

       ECHO-NAME-SAFE129.
           MOVE '<p>Thank you</p>' TO WS-PAGE129.
           EXEC CICS WEB SEND FROM(WS-PAGE129) END-EXEC.

       CONNECT-DB-SAFE87.
           ACCEPT WS-CONN-PW87 FROM ENVIRONMENT 'DB_PASSWORD'.

       FORMAT-HEADER47.
           MOVE 'MONTHLY REPORT' TO WS-TITLE47.
           STRING WS-TITLE47 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER47.
           DISPLAY WS-HEADER47.

       COMPUTE-TOTALS127.
           MOVE 0 TO WS-TOTAL127.
           PERFORM VARYING WS-K127 FROM 1 BY 1 UNTIL WS-K127 > 10
               ADD WS-K127 TO WS-TOTAL127
           END-PERFORM.
           COMPUTE WS-AVERAGE127 = WS-TOTAL127 / 10.

       WRITE-EXPORT-SAFE157.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH157.
           OPEN OUTPUT EXPORT-FILE157.
           CLOSE EXPORT-FILE157.

       CLASSIFY-CODE139.
           EVALUATE WS-CODE139
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS139
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS139
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS139
           END-EVALUATE.

       CONNECT-DB-SAFE166.
           ACCEPT WS-CONN-PW166 FROM ENVIRONMENT 'DB_PASSWORD'.

       CLASSIFY-CODE104.
           EVALUATE WS-CODE104
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS104
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS104
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS104
           END-EVALUATE.

       CHECK-LIMIT65.
           IF WS-AMOUNT65 > 1000
               MOVE 'Y' TO WS-FLAG65
           ELSE
               MOVE 'N' TO WS-FLAG65
           END-IF.

       EXTRACT-FIELD-SAFE160.
           ACCEPT WS-POS160.
           IF WS-POS160 IS NUMERIC AND WS-POS160 > 0 AND WS-POS160 < 76
               MOVE WS-RECORD160(WS-POS160:5) TO WS-PART160
           END-IF.

       LOG-LOGIN67.
           DISPLAY 'LOGIN ' WS-USER67 ' ' WS-PASSWORD-IN67.

       CHECK-LIMIT182.
           IF WS-AMOUNT182 > 1000
               MOVE 'Y' TO WS-FLAG182
           ELSE
               MOVE 'N' TO WS-FLAG182
           END-IF.

       CLASSIFY-CODE180.
           EVALUATE WS-CODE180
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS180
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS180
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS180
           END-EVALUATE.

       CONNECT-DB183.
           MOVE WS-DB-PASSWORD183 TO WS-CONN-PW183.

       EXTRACT-FIELD-SAFE171.
           ACCEPT WS-POS171.
           IF WS-POS171 IS NUMERIC AND WS-POS171 > 0 AND WS-POS171 < 76
               MOVE WS-RECORD171(WS-POS171:5) TO WS-PART171
           END-IF.

       CONNECT-DB-SAFE177.
           ACCEPT WS-CONN-PW177 FROM ENVIRONMENT 'DB_PASSWORD'.

       COMPUTE-TOTALS55.
           MOVE 0 TO WS-TOTAL55.
           PERFORM VARYING WS-K55 FROM 1 BY 1 UNTIL WS-K55 > 10
               ADD WS-K55 TO WS-TOTAL55
           END-PERFORM.
           COMPUTE WS-AVERAGE55 = WS-TOTAL55 / 10.

       CHECK-LIMIT121.
           IF WS-AMOUNT121 > 1000
               MOVE 'Y' TO WS-FLAG121
           ELSE
               MOVE 'N' TO WS-FLAG121
           END-IF.

       CHECK-LIMIT30.
           IF WS-AMOUNT30 > 1000
               MOVE 'Y' TO WS-FLAG30
           ELSE
               MOVE 'N' TO WS-FLAG30
           END-IF.

       CHECK-LIMIT186.
           IF WS-AMOUNT186 > 1000
               MOVE 'Y' TO WS-FLAG186
           ELSE
               MOVE 'N' TO WS-FLAG186
           END-IF.

       FORMAT-HEADER122.
           MOVE 'MONTHLY REPORT' TO WS-TITLE122.
           STRING WS-TITLE122 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER122.
           DISPLAY WS-HEADER122.

       CLASSIFY-CODE15.
           EVALUATE WS-CODE15
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS15
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS15
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS15
           END-EVALUATE.

       PREPARE-QUERY130.
           MOVE LK-FILTER130 TO WS-STMT130.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT130 END-EXEC.

       LOG-LOGIN-SAFE117.
           DISPLAY 'LOGIN ' WS-USER117.

       WRITE-EXPORT124.
           MOVE LK-PATH124 TO WS-EXPORT-PATH124.
           OPEN OUTPUT EXPORT-FILE124.
           CLOSE EXPORT-FILE124.

       EXTRACT-FIELD93.
           ACCEPT WS-POS93.
           MOVE WS-RECORD93(WS-POS93:5) TO WS-PART93.

       WRITE-EXPORT-SAFE147.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH147.
           OPEN OUTPUT EXPORT-FILE147.
           CLOSE EXPORT-FILE147.

       WRITE-EXPORT88.
           MOVE LK-PATH88 TO WS-EXPORT-PATH88.
           OPEN OUTPUT EXPORT-FILE88.
           CLOSE EXPORT-FILE88.

       CONNECT-DB-SAFE190.
           ACCEPT WS-CONN-PW190 FROM ENVIRONMENT 'DB_PASSWORD'.

       EXTRACT-FIELD107.
           ACCEPT WS-POS107.
           MOVE WS-RECORD107(WS-POS107:5) TO WS-PART107.

       LOG-LOGIN-SAFE10.
           DISPLAY 'LOGIN ' WS-USER10.

       FORMAT-HEADER90.
           MOVE 'MONTHLY REPORT' TO WS-TITLE90.
           STRING WS-TITLE90 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER90.
           DISPLAY WS-HEADER90.

       COMPUTE-TOTALS178.
           MOVE 0 TO WS-TOTAL178.
           PERFORM VARYING WS-K178 FROM 1 BY 1 UNTIL WS-K178 > 10
               ADD WS-K178 TO WS-TOTAL178
           END-PERFORM.
           COMPUTE WS-AVERAGE178 = WS-TOTAL178 / 10.

       LOG-LOGIN-SAFE168.
           DISPLAY 'LOGIN ' WS-USER168.

       CLASSIFY-CODE114.
           EVALUATE WS-CODE114
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS114
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS114
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS114
           END-EVALUATE.

       LOG-LOGIN-SAFE48.
           DISPLAY 'LOGIN ' WS-USER48.

       CLASSIFY-CODE54.
           EVALUATE WS-CODE54
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS54
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS54
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS54
           END-EVALUATE.

       LOG-LOGIN-SAFE71.
           DISPLAY 'LOGIN ' WS-USER71.

       COMPUTE-TOTALS78.
           MOVE 0 TO WS-TOTAL78.
           PERFORM VARYING WS-K78 FROM 1 BY 1 UNTIL WS-K78 > 10
               ADD WS-K78 TO WS-TOTAL78
           END-PERFORM.
           COMPUTE WS-AVERAGE78 = WS-TOTAL78 / 10.

       LOG-LOGIN-SAFE126.
           DISPLAY 'LOGIN ' WS-USER126.

       PREPARE-QUERY179.
           MOVE LK-FILTER179 TO WS-STMT179.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT179 END-EXEC.

       FORMAT-HEADER13.
           MOVE 'MONTHLY REPORT' TO WS-TITLE13.
           STRING WS-TITLE13 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER13.
           DISPLAY WS-HEADER13.

       FORMAT-HEADER197.
           MOVE 'MONTHLY REPORT' TO WS-TITLE197.
           STRING WS-TITLE197 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER197.
           DISPLAY WS-HEADER197.

       FORMAT-HEADER163.
           MOVE 'MONTHLY REPORT' TO WS-TITLE163.
           STRING WS-TITLE163 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER163.
           DISPLAY WS-HEADER163.

       EXTRACT-FIELD-SAFE42.
           ACCEPT WS-POS42.
           IF WS-POS42 IS NUMERIC AND WS-POS42 > 0 AND WS-POS42 < 76
               MOVE WS-RECORD42(WS-POS42:5) TO WS-PART42
           END-IF.

       PREPARE-QUERY-SAFE19.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT19.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT19 END-EXEC.

       CONNECT-DB25.
           MOVE WS-DB-PASSWORD25 TO WS-CONN-PW25.

       PREPARE-QUERY-SAFE68.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT68.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT68 END-EXEC.

       FORMAT-HEADER52.
           MOVE 'MONTHLY REPORT' TO WS-TITLE52.
           STRING WS-TITLE52 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER52.
           DISPLAY WS-HEADER52.

       CLASSIFY-CODE132.
           EVALUATE WS-CODE132
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS132
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS132
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS132
           END-EVALUATE.

       LOG-LOGIN-SAFE102.
           DISPLAY 'LOGIN ' WS-USER102.

       FORMAT-HEADER125.
           MOVE 'MONTHLY REPORT' TO WS-TITLE125.
           STRING WS-TITLE125 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER125.
           DISPLAY WS-HEADER125.

       FORMAT-HEADER22.
           MOVE 'MONTHLY REPORT' TO WS-TITLE22.
           STRING WS-TITLE22 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER22.
           DISPLAY WS-HEADER22.

       CHECK-LIMIT146.
           IF WS-AMOUNT146 > 1000
               MOVE 'Y' TO WS-FLAG146
           ELSE
               MOVE 'N' TO WS-FLAG146
           END-IF.

       WRITE-EXPORT-SAFE51.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH51.
           OPEN OUTPUT EXPORT-FILE51.
           CLOSE EXPORT-FILE51.

       CONNECT-DB95.
           MOVE WS-DB-PASSWORD95 TO WS-CONN-PW95.

       CLASSIFY-CODE100.
           EVALUATE WS-CODE100
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS100
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS100
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS100
           END-EVALUATE.

       COMPUTE-TOTALS11.
           MOVE 0 TO WS-TOTAL11.
           PERFORM VARYING WS-K11 FROM 1 BY 1 UNTIL WS-K11 > 10
               ADD WS-K11 TO WS-TOTAL11
           END-PERFORM.
           COMPUTE WS-AVERAGE11 = WS-TOTAL11 / 10.

       ECHO-NAME-SAFE6.
           MOVE '<p>Thank you</p>' TO WS-PAGE6.
           EXEC CICS WEB SEND FROM(WS-PAGE6) END-EXEC.

       LOG-LOGIN17.
           DISPLAY 'LOGIN ' WS-USER17 ' ' WS-PASSWORD-IN17.

       WRITE-EXPORT-SAFE106.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH106.
           OPEN OUTPUT EXPORT-FILE106.
           CLOSE EXPORT-FILE106.

       CLASSIFY-CODE120.
           EVALUATE WS-CODE120
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS120
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS120
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS120
           END-EVALUATE.

       CHECK-LIMIT144.
           IF WS-AMOUNT144 > 1000
               MOVE 'Y' TO WS-FLAG144
           ELSE
               MOVE 'N' TO WS-FLAG144
           END-IF.

       CLASSIFY-CODE7.
           EVALUATE WS-CODE7
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS7
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS7
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS7
           END-EVALUATE.

       CLASSIFY-CODE20.
           EVALUATE WS-CODE20
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS20
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS20
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS20
           END-EVALUATE.

       CLASSIFY-CODE187.
           EVALUATE WS-CODE187
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS187
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS187
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS187
           END-EVALUATE.

       PREPARE-QUERY-SAFE50.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT50.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT50 END-EXEC.

       WRITE-EXPORT189.
           MOVE LK-PATH189 TO WS-EXPORT-PATH189.
           OPEN OUTPUT EXPORT-FILE189.
           CLOSE EXPORT-FILE189.

       CHECK-LIMIT115.
           IF WS-AMOUNT115 > 1000
               MOVE 'Y' TO WS-FLAG115
           ELSE
               MOVE 'N' TO WS-FLAG115
           END-IF.

       EXTRACT-FIELD45.
           ACCEPT WS-POS45.
           MOVE WS-RECORD45(WS-POS45:5) TO WS-PART45.

       LOG-LOGIN119.
           DISPLAY 'LOGIN ' WS-USER119 ' ' WS-PASSWORD-IN119.

       COMPUTE-TOTALS150.
           MOVE 0 TO WS-TOTAL150.
           PERFORM VARYING WS-K150 FROM 1 BY 1 UNTIL WS-K150 > 10
               ADD WS-K150 TO WS-TOTAL150
           END-PERFORM.
           COMPUTE WS-AVERAGE150 = WS-TOTAL150 / 10.

       FORMAT-HEADER84.
           MOVE 'MONTHLY REPORT' TO WS-TITLE84.
           STRING WS-TITLE84 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER84.
           DISPLAY WS-HEADER84.

       ECHO-NAME196.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM196) END-EXEC.
           STRING '<p>' WS-FORM196 '</p>' DELIMITED BY SIZE INTO WS-PAGE196.
           EXEC CICS WEB SEND FROM(WS-PAGE196) END-EXEC.

       FORMAT-HEADER44.
           MOVE 'MONTHLY REPORT' TO WS-TITLE44.
           STRING WS-TITLE44 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER44.
           DISPLAY WS-HEADER44.

       FORMAT-HEADER133.
           MOVE 'MONTHLY REPORT' TO WS-TITLE133.
           STRING WS-TITLE133 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER133.
           DISPLAY WS-HEADER133.

       ECHO-NAME-SAFE39.
           MOVE '<p>Thank you</p>' TO WS-PAGE39.
           EXEC CICS WEB SEND FROM(WS-PAGE39) END-EXEC.

       PREPARE-QUERY131.
           MOVE LK-FILTER131 TO WS-STMT131.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT131 END-EXEC.

       COMPUTE-TOTALS140.
           MOVE 0 TO WS-TOTAL140.
           PERFORM VARYING WS-K140 FROM 1 BY 1 UNTIL WS-K140 > 10
               ADD WS-K140 TO WS-TOTAL140
           END-PERFORM.
           COMPUTE WS-AVERAGE140 = WS-TOTAL140 / 10.

       LOG-LOGIN23.
           DISPLAY 'LOGIN ' WS-USER23 ' ' WS-PASSWORD-IN23.

       FORMAT-HEADER37.
           MOVE 'MONTHLY REPORT' TO WS-TITLE37.
           STRING WS-TITLE37 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER37.
           DISPLAY WS-HEADER37.

       CONNECT-DB86.
           MOVE WS-DB-PASSWORD86 TO WS-CONN-PW86.

       EXTRACT-FIELD137.
           ACCEPT WS-POS137.
           MOVE WS-RECORD137(WS-POS137:5) TO WS-PART137.

       CHECK-LIMIT110.
           IF WS-AMOUNT110 > 1000
               MOVE 'Y' TO WS-FLAG110
           ELSE
               MOVE 'N' TO WS-FLAG110
           END-IF.

       EXTRACT-FIELD-SAFE53.
           ACCEPT WS-POS53.
           IF WS-POS53 IS NUMERIC AND WS-POS53 > 0 AND WS-POS53 < 76
               MOVE WS-RECORD53(WS-POS53:5) TO WS-PART53
           END-IF.

       WRITE-EXPORT-SAFE170.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH170.
           OPEN OUTPUT EXPORT-FILE170.
           CLOSE EXPORT-FILE170.

       ECHO-NAME-SAFE116.
           MOVE '<p>Thank you</p>' TO WS-PAGE116.
           EXEC CICS WEB SEND FROM(WS-PAGE116) END-EXEC.

       CLASSIFY-CODE108.
           EVALUATE WS-CODE108
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS108
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS108
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS108
           END-EVALUATE.

       COMPUTE-TOTALS184.
           MOVE 0 TO WS-TOTAL184.
           PERFORM VARYING WS-K184 FROM 1 BY 1 UNTIL WS-K184 > 10
               ADD WS-K184 TO WS-TOTAL184
           END-PERFORM.
           COMPUTE WS-AVERAGE184 = WS-TOTAL184 / 10.

       WRITE-EXPORT-SAFE167.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH167.
           OPEN OUTPUT EXPORT-FILE167.
           CLOSE EXPORT-FILE167.

       LOG-LOGIN-SAFE40.
           DISPLAY 'LOGIN ' WS-USER40.

       CLASSIFY-CODE60.
           EVALUATE WS-CODE60
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS60
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS60
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS60
           END-EVALUATE.

       CONNECT-DB81.
           MOVE WS-DB-PASSWORD81 TO WS-CONN-PW81.

       CONNECT-DB112.
           MOVE WS-DB-PASSWORD112 TO WS-CONN-PW112.

       WRITE-EXPORT103.
           MOVE LK-PATH103 TO WS-EXPORT-PATH103.
           OPEN OUTPUT EXPORT-FILE103.
           CLOSE EXPORT-FILE103.

       COMPUTE-TOTALS38.
           MOVE 0 TO WS-TOTAL38.
           PERFORM VARYING WS-K38 FROM 1 BY 1 UNTIL WS-K38 > 10
               ADD WS-K38 TO WS-TOTAL38
           END-PERFORM.
           COMPUTE WS-AVERAGE38 = WS-TOTAL38 / 10.

       CONVERT-FILE80.
           STRING "convert " LK-NAME80 DELIMITED BY SIZE INTO WS-CMD80.
           CALL 'SYSTEM' USING WS-CMD80.

