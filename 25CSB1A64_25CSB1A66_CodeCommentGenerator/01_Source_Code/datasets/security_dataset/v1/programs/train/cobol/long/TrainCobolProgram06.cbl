       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTR06.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EXPORT-FILE57 ASSIGN TO DYNAMIC WS-EXPORT-PATH57
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE68 ASSIGN TO DYNAMIC WS-EXPORT-PATH68
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE96 ASSIGN TO DYNAMIC WS-EXPORT-PATH96
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE117 ASSIGN TO DYNAMIC WS-EXPORT-PATH117
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE121 ASSIGN TO DYNAMIC WS-EXPORT-PATH121
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE124 ASSIGN TO DYNAMIC WS-EXPORT-PATH124
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE125 ASSIGN TO DYNAMIC WS-EXPORT-PATH125
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE129 ASSIGN TO DYNAMIC WS-EXPORT-PATH129
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE133 ASSIGN TO DYNAMIC WS-EXPORT-PATH133
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE134 ASSIGN TO DYNAMIC WS-EXPORT-PATH134
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE142 ASSIGN TO DYNAMIC WS-EXPORT-PATH142
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE158 ASSIGN TO DYNAMIC WS-EXPORT-PATH158
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE164 ASSIGN TO DYNAMIC WS-EXPORT-PATH164
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE173 ASSIGN TO DYNAMIC WS-EXPORT-PATH173
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE175 ASSIGN TO DYNAMIC WS-EXPORT-PATH175
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE185 ASSIGN TO DYNAMIC WS-EXPORT-PATH185
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE188 ASSIGN TO DYNAMIC WS-EXPORT-PATH188
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE190 ASSIGN TO DYNAMIC WS-EXPORT-PATH190
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE194 ASSIGN TO DYNAMIC WS-EXPORT-PATH194
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE201 ASSIGN TO DYNAMIC WS-EXPORT-PATH201
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  EXPORT-FILE57.
       01  EXPORT-LINE57         PIC X(80).
       FD  EXPORT-FILE68.
       01  EXPORT-LINE68         PIC X(80).
       FD  EXPORT-FILE96.
       01  EXPORT-LINE96         PIC X(80).
       FD  EXPORT-FILE117.
       01  EXPORT-LINE117         PIC X(80).
       FD  EXPORT-FILE121.
       01  EXPORT-LINE121         PIC X(80).
       FD  EXPORT-FILE124.
       01  EXPORT-LINE124         PIC X(80).
       FD  EXPORT-FILE125.
       01  EXPORT-LINE125         PIC X(80).
       FD  EXPORT-FILE129.
       01  EXPORT-LINE129         PIC X(80).
       FD  EXPORT-FILE133.
       01  EXPORT-LINE133         PIC X(80).
       FD  EXPORT-FILE134.
       01  EXPORT-LINE134         PIC X(80).
       FD  EXPORT-FILE142.
       01  EXPORT-LINE142         PIC X(80).
       FD  EXPORT-FILE158.
       01  EXPORT-LINE158         PIC X(80).
       FD  EXPORT-FILE164.
       01  EXPORT-LINE164         PIC X(80).
       FD  EXPORT-FILE173.
       01  EXPORT-LINE173         PIC X(80).
       FD  EXPORT-FILE175.
       01  EXPORT-LINE175         PIC X(80).
       FD  EXPORT-FILE185.
       01  EXPORT-LINE185         PIC X(80).
       FD  EXPORT-FILE188.
       01  EXPORT-LINE188         PIC X(80).
       FD  EXPORT-FILE190.
       01  EXPORT-LINE190         PIC X(80).
       FD  EXPORT-FILE194.
       01  EXPORT-LINE194         PIC X(80).
       FD  EXPORT-FILE201.
       01  EXPORT-LINE201         PIC X(80).
       WORKING-STORAGE SECTION.
       01  WS-USER1           PIC X(10).
       01  WS-PASSWORD-IN1    PIC X(12).
       01  WS-STMT2           PIC X(200).
       01  WS-DB-PASSWORD3    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW3        PIC X(12).
       01  WS-POS7            PIC 99.
       01  WS-RECORD7         PIC X(80).
       01  WS-PART7           PIC X(5).
       01  WS-POS9            PIC 99.
       01  WS-RECORD9         PIC X(80).
       01  WS-PART9           PIC X(5).
       01  WS-USER10           PIC X(10).
       01  WS-PASSWORD-IN10    PIC X(12).
       01  WS-POS11            PIC 99.
       01  WS-RECORD11         PIC X(80).
       01  WS-PART11           PIC X(5).
       01  WS-DB-PASSWORD12    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW12        PIC X(12).
       01  WS-CMD13            PIC X(100).
       01  WS-USER16           PIC X(10).
       01  WS-PASSWORD-IN16    PIC X(12).
       01  WS-POS18            PIC 99.
       01  WS-RECORD18         PIC X(80).
       01  WS-PART18           PIC X(5).
       01  WS-STMT19           PIC X(200).
       01  WS-DB-PASSWORD21    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW21        PIC X(12).
       01  WS-FORM22           PIC X(40).
       01  WS-PAGE22           PIC X(80).
       01  WS-FORM23           PIC X(40).
       01  WS-PAGE23           PIC X(80).
       01  WS-POS26            PIC 99.
       01  WS-RECORD26         PIC X(80).
       01  WS-PART26           PIC X(5).
       01  WS-DB-PASSWORD29    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW29        PIC X(12).
       01  WS-STMT31           PIC X(200).
       01  WS-DB-PASSWORD34    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW34        PIC X(12).
       01  WS-STMT36           PIC X(200).
       01  WS-FORM40           PIC X(40).
       01  WS-PAGE40           PIC X(80).
       01  WS-POS41            PIC 99.
       01  WS-RECORD41         PIC X(80).
       01  WS-PART41           PIC X(5).
       01  WS-FORM45           PIC X(40).
       01  WS-PAGE45           PIC X(80).
       01  WS-FORM46           PIC X(40).
       01  WS-PAGE46           PIC X(80).
       01  WS-FORM47           PIC X(40).
       01  WS-PAGE47           PIC X(80).
       01  WS-USER48           PIC X(10).
       01  WS-PASSWORD-IN48    PIC X(12).
       01  WS-CMD49            PIC X(100).
       01  WS-POS50            PIC 99.
       01  WS-RECORD50         PIC X(80).
       01  WS-PART50           PIC X(5).
       01  WS-USER52           PIC X(10).
       01  WS-PASSWORD-IN52    PIC X(12).
       01  WS-CMD56            PIC X(100).
       01  WS-EXPORT-PATH57    PIC X(60).
       01  WS-USER58           PIC X(10).
       01  WS-PASSWORD-IN58    PIC X(12).
       01  WS-POS59            PIC 99.
       01  WS-RECORD59         PIC X(80).
       01  WS-PART59           PIC X(5).
       01  WS-USER62           PIC X(10).
       01  WS-PASSWORD-IN62    PIC X(12).
       01  WS-POS65            PIC 99.
       01  WS-RECORD65         PIC X(80).
       01  WS-PART65           PIC X(5).
       01  WS-USER66           PIC X(10).
       01  WS-PASSWORD-IN66    PIC X(12).
       01  WS-POS67            PIC 99.
       01  WS-RECORD67         PIC X(80).
       01  WS-PART67           PIC X(5).
       01  WS-EXPORT-PATH68    PIC X(60).
       01  WS-POS69            PIC 99.
       01  WS-RECORD69         PIC X(80).
       01  WS-PART69           PIC X(5).
       01  WS-POS71            PIC 99.
       01  WS-RECORD71         PIC X(80).
       01  WS-PART71           PIC X(5).
       01  WS-USER72           PIC X(10).
       01  WS-PASSWORD-IN72    PIC X(12).
       01  WS-CMD74            PIC X(100).
       01  WS-FORM75           PIC X(40).
       01  WS-PAGE75           PIC X(80).
       01  WS-POS76            PIC 99.
       01  WS-RECORD76         PIC X(80).
       01  WS-PART76           PIC X(5).
       01  WS-DB-PASSWORD78    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW78        PIC X(12).
       01  WS-STMT79           PIC X(200).
       01  WS-FORM82           PIC X(40).
       01  WS-PAGE82           PIC X(80).
       01  WS-CMD83            PIC X(100).
       01  WS-FORM84           PIC X(40).
       01  WS-PAGE84           PIC X(80).
       01  WS-STMT85           PIC X(200).
       01  WS-FORM86           PIC X(40).
       01  WS-PAGE86           PIC X(80).
       01  WS-POS88            PIC 99.
       01  WS-RECORD88         PIC X(80).
       01  WS-PART88           PIC X(5).
       01  WS-FORM89           PIC X(40).
       01  WS-PAGE89           PIC X(80).
       01  WS-USER90           PIC X(10).
       01  WS-PASSWORD-IN90    PIC X(12).
       01  WS-STMT91           PIC X(200).
       01  WS-FORM92           PIC X(40).
       01  WS-PAGE92           PIC X(80).
       01  WS-FORM93           PIC X(40).
       01  WS-PAGE93           PIC X(80).
       01  WS-USER94           PIC X(10).
       01  WS-PASSWORD-IN94    PIC X(12).
       01  WS-STMT95           PIC X(200).
       01  WS-EXPORT-PATH96    PIC X(60).
       01  WS-CMD97            PIC X(100).
       01  WS-STMT103           PIC X(200).
       01  WS-DB-PASSWORD104    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW104        PIC X(12).
       01  WS-STMT106           PIC X(200).
       01  WS-POS107            PIC 99.
       01  WS-RECORD107         PIC X(80).
       01  WS-PART107           PIC X(5).
       01  WS-STMT109           PIC X(200).
       01  WS-USER110           PIC X(10).
       01  WS-PASSWORD-IN110    PIC X(12).
       01  WS-DB-PASSWORD112    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW112        PIC X(12).
       01  WS-STMT113           PIC X(200).
       01  WS-CMD115            PIC X(100).
       01  WS-EXPORT-PATH117    PIC X(60).
       01  WS-POS118            PIC 99.
       01  WS-RECORD118         PIC X(80).
       01  WS-PART118           PIC X(5).
       01  WS-FORM119           PIC X(40).
       01  WS-PAGE119           PIC X(80).
       01  WS-FORM120           PIC X(40).
       01  WS-PAGE120           PIC X(80).
       01  WS-EXPORT-PATH121    PIC X(60).
       01  WS-POS122            PIC 99.
       01  WS-RECORD122         PIC X(80).
       01  WS-PART122           PIC X(5).
       01  WS-EXPORT-PATH124    PIC X(60).
       01  WS-EXPORT-PATH125    PIC X(60).
       01  WS-USER126           PIC X(10).
       01  WS-PASSWORD-IN126    PIC X(12).
       01  WS-STMT128           PIC X(200).
       01  WS-EXPORT-PATH129    PIC X(60).
       01  WS-STMT130           PIC X(200).
       01  WS-EXPORT-PATH133    PIC X(60).
       01  WS-EXPORT-PATH134    PIC X(60).
       01  WS-POS136            PIC 99.
       01  WS-RECORD136         PIC X(80).
       01  WS-PART136           PIC X(5).
       01  WS-STMT139           PIC X(200).
       01  WS-USER140           PIC X(10).
       01  WS-PASSWORD-IN140    PIC X(12).
       01  WS-FORM141           PIC X(40).
       01  WS-PAGE141           PIC X(80).
       01  WS-EXPORT-PATH142    PIC X(60).
       01  WS-FORM143           PIC X(40).
       01  WS-PAGE143           PIC X(80).
       01  WS-DB-PASSWORD145    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW145        PIC X(12).
       01  WS-FORM146           PIC X(40).
       01  WS-PAGE146           PIC X(80).
       01  WS-CMD148            PIC X(100).
       01  WS-USER151           PIC X(10).
       01  WS-PASSWORD-IN151    PIC X(12).
       01  WS-USER152           PIC X(10).
       01  WS-PASSWORD-IN152    PIC X(12).
       01  WS-USER153           PIC X(10).
       01  WS-PASSWORD-IN153    PIC X(12).
       01  WS-FORM155           PIC X(40).
       01  WS-PAGE155           PIC X(80).
       01  WS-USER156           PIC X(10).
       01  WS-PASSWORD-IN156    PIC X(12).
       01  WS-CMD157            PIC X(100).
       01  WS-EXPORT-PATH158    PIC X(60).
       01  WS-CMD163            PIC X(100).
       01  WS-EXPORT-PATH164    PIC X(60).
       01  WS-USER165           PIC X(10).
       01  WS-PASSWORD-IN165    PIC X(12).
       01  WS-POS166            PIC 99.
       01  WS-RECORD166         PIC X(80).
       01  WS-PART166           PIC X(5).
       01  WS-POS167            PIC 99.
       01  WS-RECORD167         PIC X(80).
       01  WS-PART167           PIC X(5).
       01  WS-DB-PASSWORD168    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW168        PIC X(12).
       01  WS-EXPORT-PATH173    PIC X(60).
       01  WS-STMT174           PIC X(200).
       01  WS-EXPORT-PATH175    PIC X(60).
       01  WS-DB-PASSWORD176    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW176        PIC X(12).
       01  WS-POS181            PIC 99.
       01  WS-RECORD181         PIC X(80).
       01  WS-PART181           PIC X(5).
       01  WS-EXPORT-PATH185    PIC X(60).
       01  WS-USER187           PIC X(10).
       01  WS-PASSWORD-IN187    PIC X(12).
       01  WS-EXPORT-PATH188    PIC X(60).
       01  WS-CMD189            PIC X(100).
       01  WS-EXPORT-PATH190    PIC X(60).
       01  WS-STMT193           PIC X(200).
       01  WS-EXPORT-PATH194    PIC X(60).
       01  WS-FORM196           PIC X(40).
       01  WS-PAGE196           PIC X(80).
       01  WS-USER197           PIC X(10).
       01  WS-PASSWORD-IN197    PIC X(12).
       01  WS-DB-PASSWORD198    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW198        PIC X(12).
       01  WS-STMT199           PIC X(200).
       01  WS-FORM200           PIC X(40).
       01  WS-PAGE200           PIC X(80).
       01  WS-EXPORT-PATH201    PIC X(60).
       01  WS-TITLE4          PIC X(20) VALUE SPACES.
       01  WS-HEADER4         PIC X(40) VALUE SPACES.
       01  WS-TOTAL5          PIC 9(6) VALUE 0.
       01  WS-K5              PIC 99 VALUE 0.
       01  WS-AVERAGE5        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL6          PIC 9(6) VALUE 0.
       01  WS-K6              PIC 99 VALUE 0.
       01  WS-AVERAGE6        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL8          PIC 9(6) VALUE 0.
       01  WS-K8              PIC 99 VALUE 0.
       01  WS-AVERAGE8        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT14         PIC 9(6) VALUE 500.
       01  WS-FLAG14           PIC X VALUE 'N'.
       01  WS-CODE15           PIC 9 VALUE 1.
       01  WS-STATUS15         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT17         PIC 9(6) VALUE 500.
       01  WS-FLAG17           PIC X VALUE 'N'.
       01  WS-AMOUNT20         PIC 9(6) VALUE 500.
       01  WS-FLAG20           PIC X VALUE 'N'.
       01  WS-CODE24           PIC 9 VALUE 1.
       01  WS-STATUS24         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT25         PIC 9(6) VALUE 500.
       01  WS-FLAG25           PIC X VALUE 'N'.
       01  WS-CODE27           PIC 9 VALUE 1.
       01  WS-STATUS27         PIC X(6) VALUE SPACES.
       01  WS-TOTAL28          PIC 9(6) VALUE 0.
       01  WS-K28              PIC 99 VALUE 0.
       01  WS-AVERAGE28        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL30          PIC 9(6) VALUE 0.
       01  WS-K30              PIC 99 VALUE 0.
       01  WS-AVERAGE30        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL32          PIC 9(6) VALUE 0.
       01  WS-K32              PIC 99 VALUE 0.
       01  WS-AVERAGE32        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL33          PIC 9(6) VALUE 0.
       01  WS-K33              PIC 99 VALUE 0.
       01  WS-AVERAGE33        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT35         PIC 9(6) VALUE 500.
       01  WS-FLAG35           PIC X VALUE 'N'.
       01  WS-AMOUNT37         PIC 9(6) VALUE 500.
       01  WS-FLAG37           PIC X VALUE 'N'.
       01  WS-TITLE38          PIC X(20) VALUE SPACES.
       01  WS-HEADER38         PIC X(40) VALUE SPACES.
       01  WS-TOTAL39          PIC 9(6) VALUE 0.
       01  WS-K39              PIC 99 VALUE 0.
       01  WS-AVERAGE39        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT42         PIC 9(6) VALUE 500.
       01  WS-FLAG42           PIC X VALUE 'N'.
       01  WS-AMOUNT43         PIC 9(6) VALUE 500.
       01  WS-FLAG43           PIC X VALUE 'N'.
       01  WS-TOTAL44          PIC 9(6) VALUE 0.
       01  WS-K44              PIC 99 VALUE 0.
       01  WS-AVERAGE44        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE51          PIC X(20) VALUE SPACES.
       01  WS-HEADER51         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT53         PIC 9(6) VALUE 500.
       01  WS-FLAG53           PIC X VALUE 'N'.
       01  WS-AMOUNT54         PIC 9(6) VALUE 500.
       01  WS-FLAG54           PIC X VALUE 'N'.
       01  WS-TITLE55          PIC X(20) VALUE SPACES.
       01  WS-HEADER55         PIC X(40) VALUE SPACES.
       01  WS-CODE60           PIC 9 VALUE 1.
       01  WS-STATUS60         PIC X(6) VALUE SPACES.
       01  WS-TITLE61          PIC X(20) VALUE SPACES.
       01  WS-HEADER61         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT63         PIC 9(6) VALUE 500.
       01  WS-FLAG63           PIC X VALUE 'N'.
       01  WS-TITLE64          PIC X(20) VALUE SPACES.
       01  WS-HEADER64         PIC X(40) VALUE SPACES.
       01  WS-TOTAL70          PIC 9(6) VALUE 0.
       01  WS-K70              PIC 99 VALUE 0.
       01  WS-AVERAGE70        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL73          PIC 9(6) VALUE 0.
       01  WS-K73              PIC 99 VALUE 0.
       01  WS-AVERAGE73        PIC 9(6)V99 VALUE 0.
       01  WS-CODE77           PIC 9 VALUE 1.
       01  WS-STATUS77         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT80         PIC 9(6) VALUE 500.
       01  WS-FLAG80           PIC X VALUE 'N'.
       01  WS-CODE81           PIC 9 VALUE 1.
       01  WS-STATUS81         PIC X(6) VALUE SPACES.
       01  WS-TOTAL87          PIC 9(6) VALUE 0.
       01  WS-K87              PIC 99 VALUE 0.
       01  WS-AVERAGE87        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT98         PIC 9(6) VALUE 500.
       01  WS-FLAG98           PIC X VALUE 'N'.
       01  WS-CODE99           PIC 9 VALUE 1.
       01  WS-STATUS99         PIC X(6) VALUE SPACES.
       01  WS-TOTAL100          PIC 9(6) VALUE 0.
       01  WS-K100              PIC 99 VALUE 0.
       01  WS-AVERAGE100        PIC 9(6)V99 VALUE 0.
       01  WS-CODE101           PIC 9 VALUE 1.
       01  WS-STATUS101         PIC X(6) VALUE SPACES.
       01  WS-TOTAL102          PIC 9(6) VALUE 0.
       01  WS-K102              PIC 99 VALUE 0.
       01  WS-AVERAGE102        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE105          PIC X(20) VALUE SPACES.
       01  WS-HEADER105         PIC X(40) VALUE SPACES.
       01  WS-CODE108           PIC 9 VALUE 1.
       01  WS-STATUS108         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT111         PIC 9(6) VALUE 500.
       01  WS-FLAG111           PIC X VALUE 'N'.
       01  WS-CODE114           PIC 9 VALUE 1.
       01  WS-STATUS114         PIC X(6) VALUE SPACES.
       01  WS-CODE116           PIC 9 VALUE 1.
       01  WS-STATUS116         PIC X(6) VALUE SPACES.
       01  WS-TOTAL123          PIC 9(6) VALUE 0.
       01  WS-K123              PIC 99 VALUE 0.
       01  WS-AVERAGE123        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL127          PIC 9(6) VALUE 0.
       01  WS-K127              PIC 99 VALUE 0.
       01  WS-AVERAGE127        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL131          PIC 9(6) VALUE 0.
       01  WS-K131              PIC 99 VALUE 0.
       01  WS-AVERAGE131        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT132         PIC 9(6) VALUE 500.
       01  WS-FLAG132           PIC X VALUE 'N'.
       01  WS-TOTAL135          PIC 9(6) VALUE 0.
       01  WS-K135              PIC 99 VALUE 0.
       01  WS-AVERAGE135        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL137          PIC 9(6) VALUE 0.
       01  WS-K137              PIC 99 VALUE 0.
       01  WS-AVERAGE137        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT138         PIC 9(6) VALUE 500.
       01  WS-FLAG138           PIC X VALUE 'N'.
       01  WS-CODE144           PIC 9 VALUE 1.
       01  WS-STATUS144         PIC X(6) VALUE SPACES.
       01  WS-CODE147           PIC 9 VALUE 1.
       01  WS-STATUS147         PIC X(6) VALUE SPACES.
       01  WS-TOTAL149          PIC 9(6) VALUE 0.
       01  WS-K149              PIC 99 VALUE 0.
       01  WS-AVERAGE149        PIC 9(6)V99 VALUE 0.
       01  WS-CODE150           PIC 9 VALUE 1.
       01  WS-STATUS150         PIC X(6) VALUE SPACES.
       01  WS-TITLE154          PIC X(20) VALUE SPACES.
       01  WS-HEADER154         PIC X(40) VALUE SPACES.
       01  WS-TOTAL159          PIC 9(6) VALUE 0.
       01  WS-K159              PIC 99 VALUE 0.
       01  WS-AVERAGE159        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL160          PIC 9(6) VALUE 0.
       01  WS-K160              PIC 99 VALUE 0.
       01  WS-AVERAGE160        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT161         PIC 9(6) VALUE 500.
       01  WS-FLAG161           PIC X VALUE 'N'.
       01  WS-TOTAL162          PIC 9(6) VALUE 0.
       01  WS-K162              PIC 99 VALUE 0.
       01  WS-AVERAGE162        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL169          PIC 9(6) VALUE 0.
       01  WS-K169              PIC 99 VALUE 0.
       01  WS-AVERAGE169        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT170         PIC 9(6) VALUE 500.
       01  WS-FLAG170           PIC X VALUE 'N'.
       01  WS-AMOUNT171         PIC 9(6) VALUE 500.
       01  WS-FLAG171           PIC X VALUE 'N'.
       01  WS-CODE172           PIC 9 VALUE 1.
       01  WS-STATUS172         PIC X(6) VALUE SPACES.
       01  WS-TOTAL177          PIC 9(6) VALUE 0.
       01  WS-K177              PIC 99 VALUE 0.
       01  WS-AVERAGE177        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE178          PIC X(20) VALUE SPACES.
       01  WS-HEADER178         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT179         PIC 9(6) VALUE 500.
       01  WS-FLAG179           PIC X VALUE 'N'.
       01  WS-CODE180           PIC 9 VALUE 1.
       01  WS-STATUS180         PIC X(6) VALUE SPACES.
       01  WS-TITLE182          PIC X(20) VALUE SPACES.
       01  WS-HEADER182         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT183         PIC 9(6) VALUE 500.
       01  WS-FLAG183           PIC X VALUE 'N'.
       01  WS-CODE184           PIC 9 VALUE 1.
       01  WS-STATUS184         PIC X(6) VALUE SPACES.
       01  WS-TOTAL186          PIC 9(6) VALUE 0.
       01  WS-K186              PIC 99 VALUE 0.
       01  WS-AVERAGE186        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL191          PIC 9(6) VALUE 0.
       01  WS-K191              PIC 99 VALUE 0.
       01  WS-AVERAGE191        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE192          PIC X(20) VALUE SPACES.
       01  WS-HEADER192         PIC X(40) VALUE SPACES.
       01  WS-TOTAL195          PIC 9(6) VALUE 0.
       01  WS-K195              PIC 99 VALUE 0.
       01  WS-AVERAGE195        PIC 9(6)V99 VALUE 0.
       01  WS-CODE202           PIC 9 VALUE 1.
       01  WS-STATUS202         PIC X(6) VALUE SPACES.
       01  WS-TOTAL203          PIC 9(6) VALUE 0.
       01  WS-K203              PIC 99 VALUE 0.
       01  WS-AVERAGE203        PIC 9(6)V99 VALUE 0.
       LINKAGE SECTION.
       01  LK-FILTER2         PIC X(100).
       01  LK-NAME13           PIC X(40).
       01  LK-FILTER19         PIC X(100).
       01  LK-FILTER31         PIC X(100).
       01  LK-FILTER36         PIC X(100).
       01  LK-NAME49           PIC X(40).
       01  LK-NAME56           PIC X(40).
       01  LK-PATH57           PIC X(60).
       01  LK-PATH68           PIC X(60).
       01  LK-NAME74           PIC X(40).
       01  LK-FILTER79         PIC X(100).
       01  LK-NAME83           PIC X(40).
       01  LK-FILTER85         PIC X(100).
       01  LK-FILTER91         PIC X(100).
       01  LK-FILTER95         PIC X(100).
       01  LK-PATH96           PIC X(60).
       01  LK-NAME97           PIC X(40).
       01  LK-FILTER103         PIC X(100).
       01  LK-FILTER106         PIC X(100).
       01  LK-FILTER109         PIC X(100).
       01  LK-FILTER113         PIC X(100).
       01  LK-NAME115           PIC X(40).
       01  LK-PATH117           PIC X(60).
       01  LK-PATH121           PIC X(60).
       01  LK-PATH124           PIC X(60).
       01  LK-PATH125           PIC X(60).
       01  LK-FILTER128         PIC X(100).
       01  LK-PATH129           PIC X(60).
       01  LK-FILTER130         PIC X(100).
       01  LK-PATH133           PIC X(60).
       01  LK-PATH134           PIC X(60).
       01  LK-FILTER139         PIC X(100).
       01  LK-PATH142           PIC X(60).
       01  LK-NAME148           PIC X(40).
       01  LK-NAME157           PIC X(40).
       01  LK-PATH158           PIC X(60).
       01  LK-NAME163           PIC X(40).
       01  LK-PATH164           PIC X(60).
       01  LK-PATH173           PIC X(60).
       01  LK-FILTER174         PIC X(100).
       01  LK-PATH175           PIC X(60).
       01  LK-PATH185           PIC X(60).
       01  LK-PATH188           PIC X(60).
       01  LK-NAME189           PIC X(40).
       01  LK-PATH190           PIC X(60).
       01  LK-FILTER193         PIC X(100).
       01  LK-PATH194           PIC X(60).
       01  LK-FILTER199         PIC X(100).
       01  LK-PATH201           PIC X(60).
       PROCEDURE DIVISION USING LK-FILTER2 LK-NAME13 LK-FILTER19 LK-FILTER31 LK-FILTER36 LK-NAME49 LK-NAME56 LK-PATH57 LK-PATH68 LK-NAME74 LK-FILTER79 LK-NAME83 LK-FILTER85 LK-FILTER91 LK-FILTER95 LK-PATH96 LK-NAME97 LK-FILTER103 LK-FILTER106 LK-FILTER109 LK-FILTER113 LK-NAME115 LK-PATH117 LK-PATH121 LK-PATH124 LK-PATH125 LK-FILTER128 LK-PATH129 LK-FILTER130 LK-PATH133 LK-PATH134 LK-FILTER139 LK-PATH142 LK-NAME148 LK-NAME157 LK-PATH158 LK-NAME163 LK-PATH164 LK-PATH173 LK-FILTER174 LK-PATH175 LK-PATH185 LK-PATH188 LK-NAME189 LK-PATH190 LK-FILTER193 LK-PATH194 LK-FILTER199 LK-PATH201.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       CONNECT-DB145.
           MOVE WS-DB-PASSWORD145 TO WS-CONN-PW145.

       FORMAT-HEADER64.
           MOVE 'MONTHLY REPORT' TO WS-TITLE64.
           STRING WS-TITLE64 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER64.
           DISPLAY WS-HEADER64.

       WRITE-EXPORT-SAFE96.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH96.
           OPEN OUTPUT EXPORT-FILE96.
           CLOSE EXPORT-FILE96.

       CLASSIFY-CODE77.
           EVALUATE WS-CODE77
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS77
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS77
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS77
           END-EVALUATE.

       FORMAT-HEADER61.
           MOVE 'MONTHLY REPORT' TO WS-TITLE61.
           STRING WS-TITLE61 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER61.
           DISPLAY WS-HEADER61.

       EXTRACT-FIELD-SAFE67.
           ACCEPT WS-POS67.
           IF WS-POS67 IS NUMERIC AND WS-POS67 > 0 AND WS-POS67 < 76
               MOVE WS-RECORD67(WS-POS67:5) TO WS-PART67
           END-IF.

       CONVERT-FILE49.
           STRING "convert " LK-NAME49 DELIMITED BY SIZE INTO WS-CMD49.
           CALL 'SYSTEM' USING WS-CMD49.

       COMPUTE-TOTALS169.
           MOVE 0 TO WS-TOTAL169.
           PERFORM VARYING WS-K169 FROM 1 BY 1 UNTIL WS-K169 > 10
               ADD WS-K169 TO WS-TOTAL169
           END-PERFORM.
           COMPUTE WS-AVERAGE169 = WS-TOTAL169 / 10.

       CONVERT-FILE-SAFE97.
           MOVE "convert /srv/in/report.txt" TO WS-CMD97.
           CALL 'SYSTEM' USING WS-CMD97.

       LOG-LOGIN-SAFE126.
           DISPLAY 'LOGIN ' WS-USER126.

       CONNECT-DB-SAFE29.
           ACCEPT WS-CONN-PW29 FROM ENVIRONMENT 'DB_PASSWORD'.

       COMPUTE-TOTALS177.
           MOVE 0 TO WS-TOTAL177.
           PERFORM VARYING WS-K177 FROM 1 BY 1 UNTIL WS-K177 > 10
               ADD WS-K177 TO WS-TOTAL177
           END-PERFORM.
           COMPUTE WS-AVERAGE177 = WS-TOTAL177 / 10.

       COMPUTE-TOTALS100.
           MOVE 0 TO WS-TOTAL100.
           PERFORM VARYING WS-K100 FROM 1 BY 1 UNTIL WS-K100 > 10
               ADD WS-K100 TO WS-TOTAL100
           END-PERFORM.
           COMPUTE WS-AVERAGE100 = WS-TOTAL100 / 10.

       EXTRACT-FIELD-SAFE65.
           ACCEPT WS-POS65.
           IF WS-POS65 IS NUMERIC AND WS-POS65 > 0 AND WS-POS65 < 76
               MOVE WS-RECORD65(WS-POS65:5) TO WS-PART65
           END-IF.

       CHECK-LIMIT14.
           IF WS-AMOUNT14 > 1000
               MOVE 'Y' TO WS-FLAG14
           ELSE
               MOVE 'N' TO WS-FLAG14
           END-IF.

       CONNECT-DB78.
           MOVE WS-DB-PASSWORD78 TO WS-CONN-PW78.

       EXTRACT-FIELD-SAFE50.
           ACCEPT WS-POS50.
           IF WS-POS50 IS NUMERIC AND WS-POS50 > 0 AND WS-POS50 < 76
               MOVE WS-RECORD50(WS-POS50:5) TO WS-PART50
           END-IF.

       WRITE-EXPORT158.
           MOVE LK-PATH158 TO WS-EXPORT-PATH158.
           OPEN OUTPUT EXPORT-FILE158.
           CLOSE EXPORT-FILE158.

       CONVERT-FILE13.
           STRING "convert " LK-NAME13 DELIMITED BY SIZE INTO WS-CMD13.
           CALL 'SYSTEM' USING WS-CMD13.

       PREPARE-QUERY139.
           MOVE LK-FILTER139 TO WS-STMT139.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT139 END-EXEC.

       CONNECT-DB-SAFE3.
           ACCEPT WS-CONN-PW3 FROM ENVIRONMENT 'DB_PASSWORD'.

       WRITE-EXPORT-SAFE57.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH57.
           OPEN OUTPUT EXPORT-FILE57.
           CLOSE EXPORT-FILE57.

       CLASSIFY-CODE150.
           EVALUATE WS-CODE150
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS150
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS150
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS150
           END-EVALUATE.

       CHECK-LIMIT20.
           IF WS-AMOUNT20 > 1000
               MOVE 'Y' TO WS-FLAG20
           ELSE
               MOVE 'N' TO WS-FLAG20
           END-IF.

       LOG-LOGIN153.
           DISPLAY 'LOGIN ' WS-USER153 ' ' WS-PASSWORD-IN153.

       ECHO-NAME82.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM82) END-EXEC.
           STRING '<p>' WS-FORM82 '</p>' DELIMITED BY SIZE INTO WS-PAGE82.
           EXEC CICS WEB SEND FROM(WS-PAGE82) END-EXEC.

       COMPUTE-TOTALS160.
           MOVE 0 TO WS-TOTAL160.
           PERFORM VARYING WS-K160 FROM 1 BY 1 UNTIL WS-K160 > 10
               ADD WS-K160 TO WS-TOTAL160
           END-PERFORM.
           COMPUTE WS-AVERAGE160 = WS-TOTAL160 / 10.

       EXTRACT-FIELD-SAFE166.
           ACCEPT WS-POS166.
           IF WS-POS166 IS NUMERIC AND WS-POS166 > 0 AND WS-POS166 < 76
               MOVE WS-RECORD166(WS-POS166:5) TO WS-PART166
           END-IF.

       CLASSIFY-CODE144.
           EVALUATE WS-CODE144
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS144
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS144
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS144
           END-EVALUATE.

       PREPARE-QUERY-SAFE174.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT174.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT174 END-EXEC.

       CHECK-LIMIT183.
           IF WS-AMOUNT183 > 1000
               MOVE 'Y' TO WS-FLAG183
           ELSE
               MOVE 'N' TO WS-FLAG183
           END-IF.

       ECHO-NAME47.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM47) END-EXEC.
           STRING '<p>' WS-FORM47 '</p>' DELIMITED BY SIZE INTO WS-PAGE47.
           EXEC CICS WEB SEND FROM(WS-PAGE47) END-EXEC.

       COMPUTE-TOTALS195.
           MOVE 0 TO WS-TOTAL195.
           PERFORM VARYING WS-K195 FROM 1 BY 1 UNTIL WS-K195 > 10
               ADD WS-K195 TO WS-TOTAL195
           END-PERFORM.
           COMPUTE WS-AVERAGE195 = WS-TOTAL195 / 10.

       CLASSIFY-CODE15.
           EVALUATE WS-CODE15
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS15
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS15
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS15
           END-EVALUATE.

       COMPUTE-TOTALS159.
           MOVE 0 TO WS-TOTAL159.
           PERFORM VARYING WS-K159 FROM 1 BY 1 UNTIL WS-K159 > 10
               ADD WS-K159 TO WS-TOTAL159
           END-PERFORM.
           COMPUTE WS-AVERAGE159 = WS-TOTAL159 / 10.

       CLASSIFY-CODE108.
           EVALUATE WS-CODE108
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS108
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS108
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS108
           END-EVALUATE.

       PREPARE-QUERY-SAFE130.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT130.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT130 END-EXEC.

       EXTRACT-FIELD88.
           ACCEPT WS-POS88.
           MOVE WS-RECORD88(WS-POS88:5) TO WS-PART88.

       CHECK-LIMIT35.
           IF WS-AMOUNT35 > 1000
               MOVE 'Y' TO WS-FLAG35
           ELSE
               MOVE 'N' TO WS-FLAG35
           END-IF.

       EXTRACT-FIELD59.
           ACCEPT WS-POS59.
           MOVE WS-RECORD59(WS-POS59:5) TO WS-PART59.

       ECHO-NAME-SAFE84.
           MOVE '<p>Thank you</p>' TO WS-PAGE84.
           EXEC CICS WEB SEND FROM(WS-PAGE84) END-EXEC.

       WRITE-EXPORT-SAFE117.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH117.
           OPEN OUTPUT EXPORT-FILE117.
           CLOSE EXPORT-FILE117.

       FORMAT-HEADER192.
           MOVE 'MONTHLY REPORT' TO WS-TITLE192.
           STRING WS-TITLE192 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER192.
           DISPLAY WS-HEADER192.

       LOG-LOGIN156.
           DISPLAY 'LOGIN ' WS-USER156 ' ' WS-PASSWORD-IN156.

       CHECK-LIMIT17.
           IF WS-AMOUNT17 > 1000
               MOVE 'Y' TO WS-FLAG17
           ELSE
               MOVE 'N' TO WS-FLAG17
           END-IF.

       WRITE-EXPORT-SAFE68.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH68.
           OPEN OUTPUT EXPORT-FILE68.
           CLOSE EXPORT-FILE68.

       CONNECT-DB-SAFE198.
           ACCEPT WS-CONN-PW198 FROM ENVIRONMENT 'DB_PASSWORD'.

       EXTRACT-FIELD9.
           ACCEPT WS-POS9.
           MOVE WS-RECORD9(WS-POS9:5) TO WS-PART9.

       WRITE-EXPORT194.
           MOVE LK-PATH194 TO WS-EXPORT-PATH194.
           OPEN OUTPUT EXPORT-FILE194.
           CLOSE EXPORT-FILE194.

       EXTRACT-FIELD26.
           ACCEPT WS-POS26.
           MOVE WS-RECORD26(WS-POS26:5) TO WS-PART26.

       FORMAT-HEADER178.
           MOVE 'MONTHLY REPORT' TO WS-TITLE178.
           STRING WS-TITLE178 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER178.
           DISPLAY WS-HEADER178.

       COMPUTE-TOTALS191.
           MOVE 0 TO WS-TOTAL191.
           PERFORM VARYING WS-K191 FROM 1 BY 1 UNTIL WS-K191 > 10
               ADD WS-K191 TO WS-TOTAL191
           END-PERFORM.
           COMPUTE WS-AVERAGE191 = WS-TOTAL191 / 10.

       EXTRACT-FIELD-SAFE122.
           ACCEPT WS-POS122.
           IF WS-POS122 IS NUMERIC AND WS-POS122 > 0 AND WS-POS122 < 76
               MOVE WS-RECORD122(WS-POS122:5) TO WS-PART122
           END-IF.

       CLASSIFY-CODE172.
           EVALUATE WS-CODE172
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS172
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS172
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS172
           END-EVALUATE.

       WRITE-EXPORT142.
           MOVE LK-PATH142 TO WS-EXPORT-PATH142.
           OPEN OUTPUT EXPORT-FILE142.
           CLOSE EXPORT-FILE142.

       WRITE-EXPORT190.
           MOVE LK-PATH190 TO WS-EXPORT-PATH190.
           OPEN OUTPUT EXPORT-FILE190.
           CLOSE EXPORT-FILE190.

       FORMAT-HEADER154.
           MOVE 'MONTHLY REPORT' TO WS-TITLE154.
           STRING WS-TITLE154 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER154.
           DISPLAY WS-HEADER154.

       CLASSIFY-CODE116.
           EVALUATE WS-CODE116
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS116
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS116
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS116
           END-EVALUATE.

       WRITE-EXPORT124.
           MOVE LK-PATH124 TO WS-EXPORT-PATH124.
           OPEN OUTPUT EXPORT-FILE124.
           CLOSE EXPORT-FILE124.

       CLASSIFY-CODE147.
           EVALUATE WS-CODE147
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS147
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS147
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS147
           END-EVALUATE.

       COMPUTE-TOTALS39.
           MOVE 0 TO WS-TOTAL39.
           PERFORM VARYING WS-K39 FROM 1 BY 1 UNTIL WS-K39 > 10
               ADD WS-K39 TO WS-TOTAL39
           END-PERFORM.
           COMPUTE WS-AVERAGE39 = WS-TOTAL39 / 10.

       WRITE-EXPORT-SAFE133.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH133.
           OPEN OUTPUT EXPORT-FILE133.
           CLOSE EXPORT-FILE133.

       CHECK-LIMIT53.
           IF WS-AMOUNT53 > 1000
               MOVE 'Y' TO WS-FLAG53
           ELSE
               MOVE 'N' TO WS-FLAG53
           END-IF.

       EXTRACT-FIELD76.
           ACCEPT WS-POS76.
           MOVE WS-RECORD76(WS-POS76:5) TO WS-PART76.

       WRITE-EXPORT121.
           MOVE LK-PATH121 TO WS-EXPORT-PATH121.
           OPEN OUTPUT EXPORT-FILE121.
           CLOSE EXPORT-FILE121.

       LOG-LOGIN-SAFE58.
           DISPLAY 'LOGIN ' WS-USER58.

       CHECK-LIMIT132.
           IF WS-AMOUNT132 > 1000
               MOVE 'Y' TO WS-FLAG132
           ELSE
               MOVE 'N' TO WS-FLAG132
           END-IF.

       COMPUTE-TOTALS186.
           MOVE 0 TO WS-TOTAL186.
           PERFORM VARYING WS-K186 FROM 1 BY 1 UNTIL WS-K186 > 10
               ADD WS-K186 TO WS-TOTAL186
           END-PERFORM.
           COMPUTE WS-AVERAGE186 = WS-TOTAL186 / 10.

       PREPARE-QUERY-SAFE31.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT31.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT31 END-EXEC.

       ECHO-NAME-SAFE22.
           MOVE '<p>Thank you</p>' TO WS-PAGE22.
           EXEC CICS WEB SEND FROM(WS-PAGE22) END-EXEC.

       ECHO-NAME86.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM86) END-EXEC.
           STRING '<p>' WS-FORM86 '</p>' DELIMITED BY SIZE INTO WS-PAGE86.
           EXEC CICS WEB SEND FROM(WS-PAGE86) END-EXEC.

       FORMAT-HEADER182.
           MOVE 'MONTHLY REPORT' TO WS-TITLE182.
           STRING WS-TITLE182 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER182.
           DISPLAY WS-HEADER182.

       LOG-LOGIN-SAFE62.
           DISPLAY 'LOGIN ' WS-USER62.

       ECHO-NAME120.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM120) END-EXEC.
           STRING '<p>' WS-FORM120 '</p>' DELIMITED BY SIZE INTO WS-PAGE120.
           EXEC CICS WEB SEND FROM(WS-PAGE120) END-EXEC.

       ECHO-NAME-SAFE143.
           MOVE '<p>Thank you</p>' TO WS-PAGE143.
           EXEC CICS WEB SEND FROM(WS-PAGE143) END-EXEC.

       LOG-LOGIN-SAFE52.
           DISPLAY 'LOGIN ' WS-USER52.

       PREPARE-QUERY-SAFE106.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT106.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT106 END-EXEC.

       EXTRACT-FIELD-SAFE118.
           ACCEPT WS-POS118.
           IF WS-POS118 IS NUMERIC AND WS-POS118 > 0 AND WS-POS118 < 76
               MOVE WS-RECORD118(WS-POS118:5) TO WS-PART118
           END-IF.

       CHECK-LIMIT170.
           IF WS-AMOUNT170 > 1000
               MOVE 'Y' TO WS-FLAG170
           ELSE
               MOVE 'N' TO WS-FLAG170
           END-IF.

       LOG-LOGIN90.
           DISPLAY 'LOGIN ' WS-USER90 ' ' WS-PASSWORD-IN90.

       CHECK-LIMIT111.
           IF WS-AMOUNT111 > 1000
               MOVE 'Y' TO WS-FLAG111
           ELSE
               MOVE 'N' TO WS-FLAG111
           END-IF.

       PREPARE-QUERY113.
           MOVE LK-FILTER113 TO WS-STMT113.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT113 END-EXEC.

       PREPARE-QUERY-SAFE109.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT109.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT109 END-EXEC.

       CONNECT-DB-SAFE104.
           ACCEPT WS-CONN-PW104 FROM ENVIRONMENT 'DB_PASSWORD'.

       CHECK-LIMIT179.
           IF WS-AMOUNT179 > 1000
               MOVE 'Y' TO WS-FLAG179
           ELSE
               MOVE 'N' TO WS-FLAG179
           END-IF.

       LOG-LOGIN94.
           DISPLAY 'LOGIN ' WS-USER94 ' ' WS-PASSWORD-IN94.

       COMPUTE-TOTALS44.
           MOVE 0 TO WS-TOTAL44.
           PERFORM VARYING WS-K44 FROM 1 BY 1 UNTIL WS-K44 > 10
               ADD WS-K44 TO WS-TOTAL44
           END-PERFORM.
           COMPUTE WS-AVERAGE44 = WS-TOTAL44 / 10.

       ECHO-NAME92.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM92) END-EXEC.
           STRING '<p>' WS-FORM92 '</p>' DELIMITED BY SIZE INTO WS-PAGE92.
           EXEC CICS WEB SEND FROM(WS-PAGE92) END-EXEC.

       ECHO-NAME93.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM93) END-EXEC.
           STRING '<p>' WS-FORM93 '</p>' DELIMITED BY SIZE INTO WS-PAGE93.
           EXEC CICS WEB SEND FROM(WS-PAGE93) END-EXEC.

       CONNECT-DB-SAFE21.
           ACCEPT WS-CONN-PW21 FROM ENVIRONMENT 'DB_PASSWORD'.

       EXTRACT-FIELD-SAFE7.
           ACCEPT WS-POS7.
           IF WS-POS7 IS NUMERIC AND WS-POS7 > 0 AND WS-POS7 < 76
               MOVE WS-RECORD7(WS-POS7:5) TO WS-PART7
           END-IF.

       CONVERT-FILE-SAFE56.
           MOVE "convert /srv/in/report.txt" TO WS-CMD56.
           CALL 'SYSTEM' USING WS-CMD56.

       LOG-LOGIN-SAFE151.
           DISPLAY 'LOGIN ' WS-USER151.

       COMPUTE-TOTALS87.
           MOVE 0 TO WS-TOTAL87.
           PERFORM VARYING WS-K87 FROM 1 BY 1 UNTIL WS-K87 > 10
               ADD WS-K87 TO WS-TOTAL87
           END-PERFORM.
           COMPUTE WS-AVERAGE87 = WS-TOTAL87 / 10.

       PREPARE-QUERY199.
           MOVE LK-FILTER199 TO WS-STMT199.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT199 END-EXEC.

       COMPUTE-TOTALS123.
           MOVE 0 TO WS-TOTAL123.
           PERFORM VARYING WS-K123 FROM 1 BY 1 UNTIL WS-K123 > 10
               ADD WS-K123 TO WS-TOTAL123
           END-PERFORM.
           COMPUTE WS-AVERAGE123 = WS-TOTAL123 / 10.

       CONNECT-DB168.
           MOVE WS-DB-PASSWORD168 TO WS-CONN-PW168.

       WRITE-EXPORT-SAFE185.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH185.
           OPEN OUTPUT EXPORT-FILE185.
           CLOSE EXPORT-FILE185.

       CLASSIFY-CODE27.
           EVALUATE WS-CODE27
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS27
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS27
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS27
           END-EVALUATE.

       CHECK-LIMIT161.
           IF WS-AMOUNT161 > 1000
               MOVE 'Y' TO WS-FLAG161
           ELSE
               MOVE 'N' TO WS-FLAG161
           END-IF.

       WRITE-EXPORT164.
           MOVE LK-PATH164 TO WS-EXPORT-PATH164.
           OPEN OUTPUT EXPORT-FILE164.
           CLOSE EXPORT-FILE164.

       ECHO-NAME-SAFE141.
           MOVE '<p>Thank you</p>' TO WS-PAGE141.
           EXEC CICS WEB SEND FROM(WS-PAGE141) END-EXEC.

       LOG-LOGIN48.
           DISPLAY 'LOGIN ' WS-USER48 ' ' WS-PASSWORD-IN48.

       CONNECT-DB176.
           MOVE WS-DB-PASSWORD176 TO WS-CONN-PW176.

       ECHO-NAME-SAFE155.
           MOVE '<p>Thank you</p>' TO WS-PAGE155.
           EXEC CICS WEB SEND FROM(WS-PAGE155) END-EXEC.

       CLASSIFY-CODE24.
           EVALUATE WS-CODE24
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS24
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS24
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS24
           END-EVALUATE.

       PREPARE-QUERY36.
           MOVE LK-FILTER36 TO WS-STMT36.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT36 END-EXEC.

       CONVERT-FILE-SAFE163.
           MOVE "convert /srv/in/report.txt" TO WS-CMD163.
           CALL 'SYSTEM' USING WS-CMD163.

       PREPARE-QUERY128.
           MOVE LK-FILTER128 TO WS-STMT128.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT128 END-EXEC.

       COMPUTE-TOTALS30.
           MOVE 0 TO WS-TOTAL30.
           PERFORM VARYING WS-K30 FROM 1 BY 1 UNTIL WS-K30 > 10
               ADD WS-K30 TO WS-TOTAL30
           END-PERFORM.
           COMPUTE WS-AVERAGE30 = WS-TOTAL30 / 10.

       COMPUTE-TOTALS102.
           MOVE 0 TO WS-TOTAL102.
           PERFORM VARYING WS-K102 FROM 1 BY 1 UNTIL WS-K102 > 10
               ADD WS-K102 TO WS-TOTAL102
           END-PERFORM.
           COMPUTE WS-AVERAGE102 = WS-TOTAL102 / 10.

       PREPARE-QUERY2.
           MOVE LK-FILTER2 TO WS-STMT2.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT2 END-EXEC.

       WRITE-EXPORT-SAFE125.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH125.
           OPEN OUTPUT EXPORT-FILE125.
           CLOSE EXPORT-FILE125.

       LOG-LOGIN-SAFE152.
           DISPLAY 'LOGIN ' WS-USER152.

       CONVERT-FILE189.
           STRING "convert " LK-NAME189 DELIMITED BY SIZE INTO WS-CMD189.
           CALL 'SYSTEM' USING WS-CMD189.

       WRITE-EXPORT173.
           MOVE LK-PATH173 TO WS-EXPORT-PATH173.
           OPEN OUTPUT EXPORT-FILE173.
           CLOSE EXPORT-FILE173.

       COMPUTE-TOTALS73.
           MOVE 0 TO WS-TOTAL73.
           PERFORM VARYING WS-K73 FROM 1 BY 1 UNTIL WS-K73 > 10
               ADD WS-K73 TO WS-TOTAL73
           END-PERFORM.
           COMPUTE WS-AVERAGE73 = WS-TOTAL73 / 10.

       FORMAT-HEADER38.
           MOVE 'MONTHLY REPORT' TO WS-TITLE38.
           STRING WS-TITLE38 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER38.
           DISPLAY WS-HEADER38.

       CHECK-LIMIT63.
           IF WS-AMOUNT63 > 1000
               MOVE 'Y' TO WS-FLAG63
           ELSE
               MOVE 'N' TO WS-FLAG63
           END-IF.

       CHECK-LIMIT54.
           IF WS-AMOUNT54 > 1000
               MOVE 'Y' TO WS-FLAG54
           ELSE
               MOVE 'N' TO WS-FLAG54
           END-IF.

       ECHO-NAME-SAFE40.
           MOVE '<p>Thank you</p>' TO WS-PAGE40.
           EXEC CICS WEB SEND FROM(WS-PAGE40) END-EXEC.

       CLASSIFY-CODE202.
           EVALUATE WS-CODE202
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS202
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS202
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS202
           END-EVALUATE.

       EXTRACT-FIELD136.
           ACCEPT WS-POS136.
           MOVE WS-RECORD136(WS-POS136:5) TO WS-PART136.

       ECHO-NAME-SAFE89.
           MOVE '<p>Thank you</p>' TO WS-PAGE89.
           EXEC CICS WEB SEND FROM(WS-PAGE89) END-EXEC.

       FORMAT-HEADER105.
           MOVE 'MONTHLY REPORT' TO WS-TITLE105.
           STRING WS-TITLE105 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER105.
           DISPLAY WS-HEADER105.

       CHECK-LIMIT43.
           IF WS-AMOUNT43 > 1000
               MOVE 'Y' TO WS-FLAG43
           ELSE
               MOVE 'N' TO WS-FLAG43
           END-IF.

       CHECK-LIMIT138.
           IF WS-AMOUNT138 > 1000
               MOVE 'Y' TO WS-FLAG138
           ELSE
               MOVE 'N' TO WS-FLAG138
           END-IF.

       CONVERT-FILE115.
           STRING "convert " LK-NAME115 DELIMITED BY SIZE INTO WS-CMD115.
           CALL 'SYSTEM' USING WS-CMD115.

       LOG-LOGIN-SAFE110.
           DISPLAY 'LOGIN ' WS-USER110.

       CLASSIFY-CODE60.
           EVALUATE WS-CODE60
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS60
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS60
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS60
           END-EVALUATE.

       CLASSIFY-CODE184.
           EVALUATE WS-CODE184
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS184
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS184
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS184
           END-EVALUATE.

       CONNECT-DB34.
           MOVE WS-DB-PASSWORD34 TO WS-CONN-PW34.

       COMPUTE-TOTALS135.
           MOVE 0 TO WS-TOTAL135.
           PERFORM VARYING WS-K135 FROM 1 BY 1 UNTIL WS-K135 > 10
               ADD WS-K135 TO WS-TOTAL135
           END-PERFORM.
           COMPUTE WS-AVERAGE135 = WS-TOTAL135 / 10.

       LOG-LOGIN66.
           DISPLAY 'LOGIN ' WS-USER66 ' ' WS-PASSWORD-IN66.

       COMPUTE-TOTALS127.
           MOVE 0 TO WS-TOTAL127.
           PERFORM VARYING WS-K127 FROM 1 BY 1 UNTIL WS-K127 > 10
               ADD WS-K127 TO WS-TOTAL127
           END-PERFORM.
           COMPUTE WS-AVERAGE127 = WS-TOTAL127 / 10.

       EXTRACT-FIELD-SAFE41.
           ACCEPT WS-POS41.
           IF WS-POS41 IS NUMERIC AND WS-POS41 > 0 AND WS-POS41 < 76
               MOVE WS-RECORD41(WS-POS41:5) TO WS-PART41
           END-IF.

       CLASSIFY-CODE114.
           EVALUATE WS-CODE114
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS114
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS114
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS114
           END-EVALUATE.

       PREPARE-QUERY85.
           MOVE LK-FILTER85 TO WS-STMT85.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT85 END-EXEC.

       PREPARE-QUERY79.
           MOVE LK-FILTER79 TO WS-STMT79.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT79 END-EXEC.

       ECHO-NAME46.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM46) END-EXEC.
           STRING '<p>' WS-FORM46 '</p>' DELIMITED BY SIZE INTO WS-PAGE46.
           EXEC CICS WEB SEND FROM(WS-PAGE46) END-EXEC.

       WRITE-EXPORT175.
           MOVE LK-PATH175 TO WS-EXPORT-PATH175.
           OPEN OUTPUT EXPORT-FILE175.
           CLOSE EXPORT-FILE175.

       COMPUTE-TOTALS28.
           MOVE 0 TO WS-TOTAL28.
           PERFORM VARYING WS-K28 FROM 1 BY 1 UNTIL WS-K28 > 10
               ADD WS-K28 TO WS-TOTAL28
           END-PERFORM.
           COMPUTE WS-AVERAGE28 = WS-TOTAL28 / 10.

       ECHO-NAME-SAFE119.
           MOVE '<p>Thank you</p>' TO WS-PAGE119.
           EXEC CICS WEB SEND FROM(WS-PAGE119) END-EXEC.

       FORMAT-HEADER51.
           MOVE 'MONTHLY REPORT' TO WS-TITLE51.
           STRING WS-TITLE51 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER51.
           DISPLAY WS-HEADER51.

       LOG-LOGIN140.
           DISPLAY 'LOGIN ' WS-USER140 ' ' WS-PASSWORD-IN140.

       EXTRACT-FIELD11.
           ACCEPT WS-POS11.
           MOVE WS-RECORD11(WS-POS11:5) TO WS-PART11.

       ECHO-NAME23.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM23) END-EXEC.
           STRING '<p>' WS-FORM23 '</p>' DELIMITED BY SIZE INTO WS-PAGE23.
           EXEC CICS WEB SEND FROM(WS-PAGE23) END-EXEC.

       COMPUTE-TOTALS70.
           MOVE 0 TO WS-TOTAL70.
           PERFORM VARYING WS-K70 FROM 1 BY 1 UNTIL WS-K70 > 10
               ADD WS-K70 TO WS-TOTAL70
           END-PERFORM.
           COMPUTE WS-AVERAGE70 = WS-TOTAL70 / 10.

       ECHO-NAME200.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM200) END-EXEC.
           STRING '<p>' WS-FORM200 '</p>' DELIMITED BY SIZE INTO WS-PAGE200.
           EXEC CICS WEB SEND FROM(WS-PAGE200) END-EXEC.

       WRITE-EXPORT201.
           MOVE LK-PATH201 TO WS-EXPORT-PATH201.
           OPEN OUTPUT EXPORT-FILE201.
           CLOSE EXPORT-FILE201.

       ECHO-NAME75.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM75) END-EXEC.
           STRING '<p>' WS-FORM75 '</p>' DELIMITED BY SIZE INTO WS-PAGE75.
           EXEC CICS WEB SEND FROM(WS-PAGE75) END-EXEC.

       EXTRACT-FIELD18.
           ACCEPT WS-POS18.
           MOVE WS-RECORD18(WS-POS18:5) TO WS-PART18.

       COMPUTE-TOTALS162.
           MOVE 0 TO WS-TOTAL162.
           PERFORM VARYING WS-K162 FROM 1 BY 1 UNTIL WS-K162 > 10
               ADD WS-K162 TO WS-TOTAL162
           END-PERFORM.
           COMPUTE WS-AVERAGE162 = WS-TOTAL162 / 10.

       WRITE-EXPORT188.
           MOVE LK-PATH188 TO WS-EXPORT-PATH188.
           OPEN OUTPUT EXPORT-FILE188.
           CLOSE EXPORT-FILE188.

       LOG-LOGIN187.
           DISPLAY 'LOGIN ' WS-USER187 ' ' WS-PASSWORD-IN187.

       EXTRACT-FIELD-SAFE107.
           ACCEPT WS-POS107.
           IF WS-POS107 IS NUMERIC AND WS-POS107 > 0 AND WS-POS107 < 76
               MOVE WS-RECORD107(WS-POS107:5) TO WS-PART107
           END-IF.

       CONNECT-DB12.
           MOVE WS-DB-PASSWORD12 TO WS-CONN-PW12.

       PREPARE-QUERY193.
           MOVE LK-FILTER193 TO WS-STMT193.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT193 END-EXEC.

       PREPARE-QUERY103.
           MOVE LK-FILTER103 TO WS-STMT103.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT103 END-EXEC.

       WRITE-EXPORT134.
           MOVE LK-PATH134 TO WS-EXPORT-PATH134.
           OPEN OUTPUT EXPORT-FILE134.
           CLOSE EXPORT-FILE134.

       CLASSIFY-CODE101.
           EVALUATE WS-CODE101
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS101
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS101
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS101
           END-EVALUATE.

       FORMAT-HEADER55.
           MOVE 'MONTHLY REPORT' TO WS-TITLE55.
           STRING WS-TITLE55 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER55.
           DISPLAY WS-HEADER55.

       LOG-LOGIN-SAFE165.
           DISPLAY 'LOGIN ' WS-USER165.

       CONVERT-FILE74.
           STRING "convert " LK-NAME74 DELIMITED BY SIZE INTO WS-CMD74.
           CALL 'SYSTEM' USING WS-CMD74.

       COMPUTE-TOTALS137.
           MOVE 0 TO WS-TOTAL137.
           PERFORM VARYING WS-K137 FROM 1 BY 1 UNTIL WS-K137 > 10
               ADD WS-K137 TO WS-TOTAL137
           END-PERFORM.
           COMPUTE WS-AVERAGE137 = WS-TOTAL137 / 10.

       CLASSIFY-CODE180.
           EVALUATE WS-CODE180
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS180
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS180
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS180
           END-EVALUATE.

       COMPUTE-TOTALS8.
           MOVE 0 TO WS-TOTAL8.
           PERFORM VARYING WS-K8 FROM 1 BY 1 UNTIL WS-K8 > 10
               ADD WS-K8 TO WS-TOTAL8
           END-PERFORM.
           COMPUTE WS-AVERAGE8 = WS-TOTAL8 / 10.

       CONVERT-FILE-SAFE157.
           MOVE "convert /srv/in/report.txt" TO WS-CMD157.
           CALL 'SYSTEM' USING WS-CMD157.

       CHECK-LIMIT171.
           IF WS-AMOUNT171 > 1000
               MOVE 'Y' TO WS-FLAG171
           ELSE
               MOVE 'N' TO WS-FLAG171
           END-IF.

       COMPUTE-TOTALS203.
           MOVE 0 TO WS-TOTAL203.
           PERFORM VARYING WS-K203 FROM 1 BY 1 UNTIL WS-K203 > 10
               ADD WS-K203 TO WS-TOTAL203
           END-PERFORM.
           COMPUTE WS-AVERAGE203 = WS-TOTAL203 / 10.

       CHECK-LIMIT25.
           IF WS-AMOUNT25 > 1000
               MOVE 'Y' TO WS-FLAG25
           ELSE
               MOVE 'N' TO WS-FLAG25
           END-IF.

       EXTRACT-FIELD-SAFE71.
           ACCEPT WS-POS71.
           IF WS-POS71 IS NUMERIC AND WS-POS71 > 0 AND WS-POS71 < 76
               MOVE WS-RECORD71(WS-POS71:5) TO WS-PART71
           END-IF.

       CHECK-LIMIT42.
           IF WS-AMOUNT42 > 1000
               MOVE 'Y' TO WS-FLAG42
           ELSE
               MOVE 'N' TO WS-FLAG42
           END-IF.

       CLASSIFY-CODE99.
           EVALUATE WS-CODE99
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS99
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS99
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS99
           END-EVALUATE.

       COMPUTE-TOTALS131.
           MOVE 0 TO WS-TOTAL131.
           PERFORM VARYING WS-K131 FROM 1 BY 1 UNTIL WS-K131 > 10
               ADD WS-K131 TO WS-TOTAL131
           END-PERFORM.
           COMPUTE WS-AVERAGE131 = WS-TOTAL131 / 10.

       COMPUTE-TOTALS33.
           MOVE 0 TO WS-TOTAL33.
           PERFORM VARYING WS-K33 FROM 1 BY 1 UNTIL WS-K33 > 10
               ADD WS-K33 TO WS-TOTAL33
           END-PERFORM.
           COMPUTE WS-AVERAGE33 = WS-TOTAL33 / 10.

       ECHO-NAME146.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM146) END-EXEC.
           STRING '<p>' WS-FORM146 '</p>' DELIMITED BY SIZE INTO WS-PAGE146.
           EXEC CICS WEB SEND FROM(WS-PAGE146) END-EXEC.

       CHECK-LIMIT98.
           IF WS-AMOUNT98 > 1000
               MOVE 'Y' TO WS-FLAG98
           ELSE
               MOVE 'N' TO WS-FLAG98
           END-IF.

       PREPARE-QUERY91.
           MOVE LK-FILTER91 TO WS-STMT91.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT91 END-EXEC.

       CONVERT-FILE83.
           STRING "convert " LK-NAME83 DELIMITED BY SIZE INTO WS-CMD83.
           CALL 'SYSTEM' USING WS-CMD83.

       CHECK-LIMIT37.
           IF WS-AMOUNT37 > 1000
               MOVE 'Y' TO WS-FLAG37
           ELSE
               MOVE 'N' TO WS-FLAG37
           END-IF.

       CLASSIFY-CODE81.
           EVALUATE WS-CODE81
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS81
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS81
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS81
           END-EVALUATE.

       COMPUTE-TOTALS32.
           MOVE 0 TO WS-TOTAL32.
           PERFORM VARYING WS-K32 FROM 1 BY 1 UNTIL WS-K32 > 10
               ADD WS-K32 TO WS-TOTAL32
           END-PERFORM.
           COMPUTE WS-AVERAGE32 = WS-TOTAL32 / 10.

       CONNECT-DB112.
           MOVE WS-DB-PASSWORD112 TO WS-CONN-PW112.

       WRITE-EXPORT129.
           MOVE LK-PATH129 TO WS-EXPORT-PATH129.
           OPEN OUTPUT EXPORT-FILE129.
           CLOSE EXPORT-FILE129.

       PREPARE-QUERY95.
           MOVE LK-FILTER95 TO WS-STMT95.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT95 END-EXEC.

       EXTRACT-FIELD69.
           ACCEPT WS-POS69.
           MOVE WS-RECORD69(WS-POS69:5) TO WS-PART69.

       LOG-LOGIN-SAFE197.
           DISPLAY 'LOGIN ' WS-USER197.

       EXTRACT-FIELD181.
           ACCEPT WS-POS181.
           MOVE WS-RECORD181(WS-POS181:5) TO WS-PART181.

       ECHO-NAME196.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM196) END-EXEC.
           STRING '<p>' WS-FORM196 '</p>' DELIMITED BY SIZE INTO WS-PAGE196.
           EXEC CICS WEB SEND FROM(WS-PAGE196) END-EXEC.

       ECHO-NAME-SAFE45.
           MOVE '<p>Thank you</p>' TO WS-PAGE45.
           EXEC CICS WEB SEND FROM(WS-PAGE45) END-EXEC.

       LOG-LOGIN72.
           DISPLAY 'LOGIN ' WS-USER72 ' ' WS-PASSWORD-IN72.

       CHECK-LIMIT80.
           IF WS-AMOUNT80 > 1000
               MOVE 'Y' TO WS-FLAG80
           ELSE
               MOVE 'N' TO WS-FLAG80
           END-IF.

       LOG-LOGIN1.
           DISPLAY 'LOGIN ' WS-USER1 ' ' WS-PASSWORD-IN1.

       CONVERT-FILE148.
           STRING "convert " LK-NAME148 DELIMITED BY SIZE INTO WS-CMD148.
           CALL 'SYSTEM' USING WS-CMD148.

       PREPARE-QUERY-SAFE19.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT19.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT19 END-EXEC.

       LOG-LOGIN10.
           DISPLAY 'LOGIN ' WS-USER10 ' ' WS-PASSWORD-IN10.

       EXTRACT-FIELD167.
           ACCEPT WS-POS167.
           MOVE WS-RECORD167(WS-POS167:5) TO WS-PART167.

       COMPUTE-TOTALS6.
           MOVE 0 TO WS-TOTAL6.
           PERFORM VARYING WS-K6 FROM 1 BY 1 UNTIL WS-K6 > 10
               ADD WS-K6 TO WS-TOTAL6
           END-PERFORM.
           COMPUTE WS-AVERAGE6 = WS-TOTAL6 / 10.

       LOG-LOGIN-SAFE16.
           DISPLAY 'LOGIN ' WS-USER16.

       COMPUTE-TOTALS5.
           MOVE 0 TO WS-TOTAL5.
           PERFORM VARYING WS-K5 FROM 1 BY 1 UNTIL WS-K5 > 10
               ADD WS-K5 TO WS-TOTAL5
           END-PERFORM.
           COMPUTE WS-AVERAGE5 = WS-TOTAL5 / 10.

       FORMAT-HEADER4.
           MOVE 'MONTHLY REPORT' TO WS-TITLE4.
           STRING WS-TITLE4 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER4.
           DISPLAY WS-HEADER4.

       COMPUTE-TOTALS149.
           MOVE 0 TO WS-TOTAL149.
           PERFORM VARYING WS-K149 FROM 1 BY 1 UNTIL WS-K149 > 10
               ADD WS-K149 TO WS-TOTAL149
           END-PERFORM.
           COMPUTE WS-AVERAGE149 = WS-TOTAL149 / 10.

