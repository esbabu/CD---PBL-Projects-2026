       IDENTIFICATION DIVISION.
       PROGRAM-ID. LTR01.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EXPORT-FILE2 ASSIGN TO DYNAMIC WS-EXPORT-PATH2
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE6 ASSIGN TO DYNAMIC WS-EXPORT-PATH6
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE26 ASSIGN TO DYNAMIC WS-EXPORT-PATH26
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE27 ASSIGN TO DYNAMIC WS-EXPORT-PATH27
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE31 ASSIGN TO DYNAMIC WS-EXPORT-PATH31
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE46 ASSIGN TO DYNAMIC WS-EXPORT-PATH46
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE53 ASSIGN TO DYNAMIC WS-EXPORT-PATH53
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE54 ASSIGN TO DYNAMIC WS-EXPORT-PATH54
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE56 ASSIGN TO DYNAMIC WS-EXPORT-PATH56
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE64 ASSIGN TO DYNAMIC WS-EXPORT-PATH64
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE74 ASSIGN TO DYNAMIC WS-EXPORT-PATH74
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE94 ASSIGN TO DYNAMIC WS-EXPORT-PATH94
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE109 ASSIGN TO DYNAMIC WS-EXPORT-PATH109
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE128 ASSIGN TO DYNAMIC WS-EXPORT-PATH128
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE129 ASSIGN TO DYNAMIC WS-EXPORT-PATH129
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE132 ASSIGN TO DYNAMIC WS-EXPORT-PATH132
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE151 ASSIGN TO DYNAMIC WS-EXPORT-PATH151
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE175 ASSIGN TO DYNAMIC WS-EXPORT-PATH175
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE190 ASSIGN TO DYNAMIC WS-EXPORT-PATH190
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT EXPORT-FILE194 ASSIGN TO DYNAMIC WS-EXPORT-PATH194
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  EXPORT-FILE2.
       01  EXPORT-LINE2         PIC X(80).
       FD  EXPORT-FILE6.
       01  EXPORT-LINE6         PIC X(80).
       FD  EXPORT-FILE26.
       01  EXPORT-LINE26         PIC X(80).
       FD  EXPORT-FILE27.
       01  EXPORT-LINE27         PIC X(80).
       FD  EXPORT-FILE31.
       01  EXPORT-LINE31         PIC X(80).
       FD  EXPORT-FILE46.
       01  EXPORT-LINE46         PIC X(80).
       FD  EXPORT-FILE53.
       01  EXPORT-LINE53         PIC X(80).
       FD  EXPORT-FILE54.
       01  EXPORT-LINE54         PIC X(80).
       FD  EXPORT-FILE56.
       01  EXPORT-LINE56         PIC X(80).
       FD  EXPORT-FILE64.
       01  EXPORT-LINE64         PIC X(80).
       FD  EXPORT-FILE74.
       01  EXPORT-LINE74         PIC X(80).
       FD  EXPORT-FILE94.
       01  EXPORT-LINE94         PIC X(80).
       FD  EXPORT-FILE109.
       01  EXPORT-LINE109         PIC X(80).
       FD  EXPORT-FILE128.
       01  EXPORT-LINE128         PIC X(80).
       FD  EXPORT-FILE129.
       01  EXPORT-LINE129         PIC X(80).
       FD  EXPORT-FILE132.
       01  EXPORT-LINE132         PIC X(80).
       FD  EXPORT-FILE151.
       01  EXPORT-LINE151         PIC X(80).
       FD  EXPORT-FILE175.
       01  EXPORT-LINE175         PIC X(80).
       FD  EXPORT-FILE190.
       01  EXPORT-LINE190         PIC X(80).
       FD  EXPORT-FILE194.
       01  EXPORT-LINE194         PIC X(80).
       WORKING-STORAGE SECTION.
       01  WS-EXPORT-PATH2    PIC X(60).
       01  WS-STMT5           PIC X(200).
       01  WS-EXPORT-PATH6    PIC X(60).
       01  WS-CMD7            PIC X(100).
       01  WS-USER9           PIC X(10).
       01  WS-PASSWORD-IN9    PIC X(12).
       01  WS-DB-PASSWORD10    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW10        PIC X(12).
       01  WS-POS11            PIC 99.
       01  WS-RECORD11         PIC X(80).
       01  WS-PART11           PIC X(5).
       01  WS-STMT12           PIC X(200).
       01  WS-CMD14            PIC X(100).
       01  WS-POS16            PIC 99.
       01  WS-RECORD16         PIC X(80).
       01  WS-PART16           PIC X(5).
       01  WS-USER19           PIC X(10).
       01  WS-PASSWORD-IN19    PIC X(12).
       01  WS-FORM20           PIC X(40).
       01  WS-PAGE20           PIC X(80).
       01  WS-STMT21           PIC X(200).
       01  WS-DB-PASSWORD22    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW22        PIC X(12).
       01  WS-CMD23            PIC X(100).
       01  WS-STMT24           PIC X(200).
       01  WS-EXPORT-PATH26    PIC X(60).
       01  WS-EXPORT-PATH27    PIC X(60).
       01  WS-DB-PASSWORD28    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW28        PIC X(12).
       01  WS-CMD29            PIC X(100).
       01  WS-EXPORT-PATH31    PIC X(60).
       01  WS-USER37           PIC X(10).
       01  WS-PASSWORD-IN37    PIC X(12).
       01  WS-FORM39           PIC X(40).
       01  WS-PAGE39           PIC X(80).
       01  WS-STMT41           PIC X(200).
       01  WS-POS42            PIC 99.
       01  WS-RECORD42         PIC X(80).
       01  WS-PART42           PIC X(5).
       01  WS-USER43           PIC X(10).
       01  WS-PASSWORD-IN43    PIC X(12).
       01  WS-USER44           PIC X(10).
       01  WS-PASSWORD-IN44    PIC X(12).
       01  WS-POS45            PIC 99.
       01  WS-RECORD45         PIC X(80).
       01  WS-PART45           PIC X(5).
       01  WS-EXPORT-PATH46    PIC X(60).
       01  WS-FORM47           PIC X(40).
       01  WS-PAGE47           PIC X(80).
       01  WS-EXPORT-PATH53    PIC X(60).
       01  WS-EXPORT-PATH54    PIC X(60).
       01  WS-EXPORT-PATH56    PIC X(60).
       01  WS-FORM58           PIC X(40).
       01  WS-PAGE58           PIC X(80).
       01  WS-STMT60           PIC X(200).
       01  WS-DB-PASSWORD61    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW61        PIC X(12).
       01  WS-EXPORT-PATH64    PIC X(60).
       01  WS-USER66           PIC X(10).
       01  WS-PASSWORD-IN66    PIC X(12).
       01  WS-USER70           PIC X(10).
       01  WS-PASSWORD-IN70    PIC X(12).
       01  WS-POS72            PIC 99.
       01  WS-RECORD72         PIC X(80).
       01  WS-PART72           PIC X(5).
       01  WS-EXPORT-PATH74    PIC X(60).
       01  WS-USER75           PIC X(10).
       01  WS-PASSWORD-IN75    PIC X(12).
       01  WS-POS77            PIC 99.
       01  WS-RECORD77         PIC X(80).
       01  WS-PART77           PIC X(5).
       01  WS-USER78           PIC X(10).
       01  WS-PASSWORD-IN78    PIC X(12).
       01  WS-CMD80            PIC X(100).
       01  WS-DB-PASSWORD81    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW81        PIC X(12).
       01  WS-POS83            PIC 99.
       01  WS-RECORD83         PIC X(80).
       01  WS-PART83           PIC X(5).
       01  WS-FORM84           PIC X(40).
       01  WS-PAGE84           PIC X(80).
       01  WS-POS85            PIC 99.
       01  WS-RECORD85         PIC X(80).
       01  WS-PART85           PIC X(5).
       01  WS-CMD86            PIC X(100).
       01  WS-USER87           PIC X(10).
       01  WS-PASSWORD-IN87    PIC X(12).
       01  WS-POS89            PIC 99.
       01  WS-RECORD89         PIC X(80).
       01  WS-PART89           PIC X(5).
       01  WS-FORM91           PIC X(40).
       01  WS-PAGE91           PIC X(80).
       01  WS-USER92           PIC X(10).
       01  WS-PASSWORD-IN92    PIC X(12).
       01  WS-POS93            PIC 99.
       01  WS-RECORD93         PIC X(80).
       01  WS-PART93           PIC X(5).
       01  WS-EXPORT-PATH94    PIC X(60).
       01  WS-DB-PASSWORD95    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW95        PIC X(12).
       01  WS-STMT98           PIC X(200).
       01  WS-FORM103           PIC X(40).
       01  WS-PAGE103           PIC X(80).
       01  WS-STMT104           PIC X(200).
       01  WS-STMT108           PIC X(200).
       01  WS-EXPORT-PATH109    PIC X(60).
       01  WS-USER110           PIC X(10).
       01  WS-PASSWORD-IN110    PIC X(12).
       01  WS-POS112            PIC 99.
       01  WS-RECORD112         PIC X(80).
       01  WS-PART112           PIC X(5).
       01  WS-DB-PASSWORD113    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW113        PIC X(12).
       01  WS-FORM116           PIC X(40).
       01  WS-PAGE116           PIC X(80).
       01  WS-CMD118            PIC X(100).
       01  WS-STMT119           PIC X(200).
       01  WS-STMT122           PIC X(200).
       01  WS-EXPORT-PATH128    PIC X(60).
       01  WS-EXPORT-PATH129    PIC X(60).
       01  WS-POS130            PIC 99.
       01  WS-RECORD130         PIC X(80).
       01  WS-PART130           PIC X(5).
       01  WS-EXPORT-PATH132    PIC X(60).
       01  WS-STMT137           PIC X(200).
       01  WS-USER138           PIC X(10).
       01  WS-PASSWORD-IN138    PIC X(12).
       01  WS-DB-PASSWORD142    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW142        PIC X(12).
       01  WS-DB-PASSWORD143    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW143        PIC X(12).
       01  WS-CMD144            PIC X(100).
       01  WS-CMD145            PIC X(100).
       01  WS-STMT147           PIC X(200).
       01  WS-FORM148           PIC X(40).
       01  WS-PAGE148           PIC X(80).
       01  WS-STMT149           PIC X(200).
       01  WS-DB-PASSWORD150    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW150        PIC X(12).
       01  WS-EXPORT-PATH151    PIC X(60).
       01  WS-FORM152           PIC X(40).
       01  WS-PAGE152           PIC X(80).
       01  WS-POS153            PIC 99.
       01  WS-RECORD153         PIC X(80).
       01  WS-PART153           PIC X(5).
       01  WS-USER154           PIC X(10).
       01  WS-PASSWORD-IN154    PIC X(12).
       01  WS-DB-PASSWORD155    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW155        PIC X(12).
       01  WS-USER156           PIC X(10).
       01  WS-PASSWORD-IN156    PIC X(12).
       01  WS-CMD157            PIC X(100).
       01  WS-DB-PASSWORD158    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW158        PIC X(12).
       01  WS-CMD160            PIC X(100).
       01  WS-CMD161            PIC X(100).
       01  WS-POS162            PIC 99.
       01  WS-RECORD162         PIC X(80).
       01  WS-PART162           PIC X(5).
       01  WS-DB-PASSWORD163    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW163        PIC X(12).
       01  WS-STMT166           PIC X(200).
       01  WS-FORM170           PIC X(40).
       01  WS-PAGE170           PIC X(80).
       01  WS-FORM172           PIC X(40).
       01  WS-PAGE172           PIC X(80).
       01  WS-DB-PASSWORD174    PIC X(12) VALUE 'Tiger2026!'.
       01  WS-CONN-PW174        PIC X(12).
       01  WS-EXPORT-PATH175    PIC X(60).
       01  WS-FORM177           PIC X(40).
       01  WS-PAGE177           PIC X(80).
       01  WS-POS180            PIC 99.
       01  WS-RECORD180         PIC X(80).
       01  WS-PART180           PIC X(5).
       01  WS-POS181            PIC 99.
       01  WS-RECORD181         PIC X(80).
       01  WS-PART181           PIC X(5).
       01  WS-CMD186            PIC X(100).
       01  WS-USER188           PIC X(10).
       01  WS-PASSWORD-IN188    PIC X(12).
       01  WS-USER189           PIC X(10).
       01  WS-PASSWORD-IN189    PIC X(12).
       01  WS-EXPORT-PATH190    PIC X(60).
       01  WS-USER193           PIC X(10).
       01  WS-PASSWORD-IN193    PIC X(12).
       01  WS-EXPORT-PATH194    PIC X(60).
       01  WS-STMT196           PIC X(200).
       01  WS-USER197           PIC X(10).
       01  WS-PASSWORD-IN197    PIC X(12).
       01  WS-CMD198            PIC X(100).
       01  WS-FORM199           PIC X(40).
       01  WS-PAGE199           PIC X(80).
       01  WS-STMT202           PIC X(200).
       01  WS-AMOUNT1         PIC 9(6) VALUE 500.
       01  WS-FLAG1           PIC X VALUE 'N'.
       01  WS-TOTAL3          PIC 9(6) VALUE 0.
       01  WS-K3              PIC 99 VALUE 0.
       01  WS-AVERAGE3        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL4          PIC 9(6) VALUE 0.
       01  WS-K4              PIC 99 VALUE 0.
       01  WS-AVERAGE4        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL8          PIC 9(6) VALUE 0.
       01  WS-K8              PIC 99 VALUE 0.
       01  WS-AVERAGE8        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL13          PIC 9(6) VALUE 0.
       01  WS-K13              PIC 99 VALUE 0.
       01  WS-AVERAGE13        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT15         PIC 9(6) VALUE 500.
       01  WS-FLAG15           PIC X VALUE 'N'.
       01  WS-CODE17           PIC 9 VALUE 1.
       01  WS-STATUS17         PIC X(6) VALUE SPACES.
       01  WS-CODE18           PIC 9 VALUE 1.
       01  WS-STATUS18         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT25         PIC 9(6) VALUE 500.
       01  WS-FLAG25           PIC X VALUE 'N'.
       01  WS-CODE30           PIC 9 VALUE 1.
       01  WS-STATUS30         PIC X(6) VALUE SPACES.
       01  WS-TOTAL32          PIC 9(6) VALUE 0.
       01  WS-K32              PIC 99 VALUE 0.
       01  WS-AVERAGE32        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT33         PIC 9(6) VALUE 500.
       01  WS-FLAG33           PIC X VALUE 'N'.
       01  WS-TOTAL34          PIC 9(6) VALUE 0.
       01  WS-K34              PIC 99 VALUE 0.
       01  WS-AVERAGE34        PIC 9(6)V99 VALUE 0.
       01  WS-CODE35           PIC 9 VALUE 1.
       01  WS-STATUS35         PIC X(6) VALUE SPACES.
       01  WS-CODE36           PIC 9 VALUE 1.
       01  WS-STATUS36         PIC X(6) VALUE SPACES.
       01  WS-TITLE38          PIC X(20) VALUE SPACES.
       01  WS-HEADER38         PIC X(40) VALUE SPACES.
       01  WS-TOTAL40          PIC 9(6) VALUE 0.
       01  WS-K40              PIC 99 VALUE 0.
       01  WS-AVERAGE40        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT48         PIC 9(6) VALUE 500.
       01  WS-FLAG48           PIC X VALUE 'N'.
       01  WS-TOTAL49          PIC 9(6) VALUE 0.
       01  WS-K49              PIC 99 VALUE 0.
       01  WS-AVERAGE49        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT50         PIC 9(6) VALUE 500.
       01  WS-FLAG50           PIC X VALUE 'N'.
       01  WS-CODE51           PIC 9 VALUE 1.
       01  WS-STATUS51         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT52         PIC 9(6) VALUE 500.
       01  WS-FLAG52           PIC X VALUE 'N'.
       01  WS-TITLE55          PIC X(20) VALUE SPACES.
       01  WS-HEADER55         PIC X(40) VALUE SPACES.
       01  WS-TOTAL57          PIC 9(6) VALUE 0.
       01  WS-K57              PIC 99 VALUE 0.
       01  WS-AVERAGE57        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE59          PIC X(20) VALUE SPACES.
       01  WS-HEADER59         PIC X(40) VALUE SPACES.
       01  WS-TITLE62          PIC X(20) VALUE SPACES.
       01  WS-HEADER62         PIC X(40) VALUE SPACES.
       01  WS-TITLE63          PIC X(20) VALUE SPACES.
       01  WS-HEADER63         PIC X(40) VALUE SPACES.
       01  WS-TOTAL65          PIC 9(6) VALUE 0.
       01  WS-K65              PIC 99 VALUE 0.
       01  WS-AVERAGE65        PIC 9(6)V99 VALUE 0.
       01  WS-CODE67           PIC 9 VALUE 1.
       01  WS-STATUS67         PIC X(6) VALUE SPACES.
       01  WS-CODE68           PIC 9 VALUE 1.
       01  WS-STATUS68         PIC X(6) VALUE SPACES.
       01  WS-TITLE69          PIC X(20) VALUE SPACES.
       01  WS-HEADER69         PIC X(40) VALUE SPACES.
       01  WS-TITLE71          PIC X(20) VALUE SPACES.
       01  WS-HEADER71         PIC X(40) VALUE SPACES.
       01  WS-CODE73           PIC 9 VALUE 1.
       01  WS-STATUS73         PIC X(6) VALUE SPACES.
       01  WS-TOTAL76          PIC 9(6) VALUE 0.
       01  WS-K76              PIC 99 VALUE 0.
       01  WS-AVERAGE76        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL79          PIC 9(6) VALUE 0.
       01  WS-K79              PIC 99 VALUE 0.
       01  WS-AVERAGE79        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL82          PIC 9(6) VALUE 0.
       01  WS-K82              PIC 99 VALUE 0.
       01  WS-AVERAGE82        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL88          PIC 9(6) VALUE 0.
       01  WS-K88              PIC 99 VALUE 0.
       01  WS-AVERAGE88        PIC 9(6)V99 VALUE 0.
       01  WS-CODE90           PIC 9 VALUE 1.
       01  WS-STATUS90         PIC X(6) VALUE SPACES.
       01  WS-TOTAL96          PIC 9(6) VALUE 0.
       01  WS-K96              PIC 99 VALUE 0.
       01  WS-AVERAGE96        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL97          PIC 9(6) VALUE 0.
       01  WS-K97              PIC 99 VALUE 0.
       01  WS-AVERAGE97        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL99          PIC 9(6) VALUE 0.
       01  WS-K99              PIC 99 VALUE 0.
       01  WS-AVERAGE99        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT100         PIC 9(6) VALUE 500.
       01  WS-FLAG100           PIC X VALUE 'N'.
       01  WS-AMOUNT101         PIC 9(6) VALUE 500.
       01  WS-FLAG101           PIC X VALUE 'N'.
       01  WS-TITLE102          PIC X(20) VALUE SPACES.
       01  WS-HEADER102         PIC X(40) VALUE SPACES.
       01  WS-TITLE105          PIC X(20) VALUE SPACES.
       01  WS-HEADER105         PIC X(40) VALUE SPACES.
       01  WS-TOTAL106          PIC 9(6) VALUE 0.
       01  WS-K106              PIC 99 VALUE 0.
       01  WS-AVERAGE106        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE107          PIC X(20) VALUE SPACES.
       01  WS-HEADER107         PIC X(40) VALUE SPACES.
       01  WS-CODE111           PIC 9 VALUE 1.
       01  WS-STATUS111         PIC X(6) VALUE SPACES.
       01  WS-TITLE114          PIC X(20) VALUE SPACES.
       01  WS-HEADER114         PIC X(40) VALUE SPACES.
       01  WS-TITLE115          PIC X(20) VALUE SPACES.
       01  WS-HEADER115         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT117         PIC 9(6) VALUE 500.
       01  WS-FLAG117           PIC X VALUE 'N'.
       01  WS-TOTAL120          PIC 9(6) VALUE 0.
       01  WS-K120              PIC 99 VALUE 0.
       01  WS-AVERAGE120        PIC 9(6)V99 VALUE 0.
       01  WS-CODE121           PIC 9 VALUE 1.
       01  WS-STATUS121         PIC X(6) VALUE SPACES.
       01  WS-TOTAL123          PIC 9(6) VALUE 0.
       01  WS-K123              PIC 99 VALUE 0.
       01  WS-AVERAGE123        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL124          PIC 9(6) VALUE 0.
       01  WS-K124              PIC 99 VALUE 0.
       01  WS-AVERAGE124        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL125          PIC 9(6) VALUE 0.
       01  WS-K125              PIC 99 VALUE 0.
       01  WS-AVERAGE125        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL126          PIC 9(6) VALUE 0.
       01  WS-K126              PIC 99 VALUE 0.
       01  WS-AVERAGE126        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT127         PIC 9(6) VALUE 500.
       01  WS-FLAG127           PIC X VALUE 'N'.
       01  WS-TOTAL131          PIC 9(6) VALUE 0.
       01  WS-K131              PIC 99 VALUE 0.
       01  WS-AVERAGE131        PIC 9(6)V99 VALUE 0.
       01  WS-CODE133           PIC 9 VALUE 1.
       01  WS-STATUS133         PIC X(6) VALUE SPACES.
       01  WS-TOTAL134          PIC 9(6) VALUE 0.
       01  WS-K134              PIC 99 VALUE 0.
       01  WS-AVERAGE134        PIC 9(6)V99 VALUE 0.
       01  WS-AMOUNT135         PIC 9(6) VALUE 500.
       01  WS-FLAG135           PIC X VALUE 'N'.
       01  WS-AMOUNT136         PIC 9(6) VALUE 500.
       01  WS-FLAG136           PIC X VALUE 'N'.
       01  WS-CODE139           PIC 9 VALUE 1.
       01  WS-STATUS139         PIC X(6) VALUE SPACES.
       01  WS-AMOUNT140         PIC 9(6) VALUE 500.
       01  WS-FLAG140           PIC X VALUE 'N'.
       01  WS-AMOUNT141         PIC 9(6) VALUE 500.
       01  WS-FLAG141           PIC X VALUE 'N'.
       01  WS-TITLE146          PIC X(20) VALUE SPACES.
       01  WS-HEADER146         PIC X(40) VALUE SPACES.
       01  WS-TOTAL159          PIC 9(6) VALUE 0.
       01  WS-K159              PIC 99 VALUE 0.
       01  WS-AVERAGE159        PIC 9(6)V99 VALUE 0.
       01  WS-CODE164           PIC 9 VALUE 1.
       01  WS-STATUS164         PIC X(6) VALUE SPACES.
       01  WS-CODE165           PIC 9 VALUE 1.
       01  WS-STATUS165         PIC X(6) VALUE SPACES.
       01  WS-TITLE167          PIC X(20) VALUE SPACES.
       01  WS-HEADER167         PIC X(40) VALUE SPACES.
       01  WS-TOTAL168          PIC 9(6) VALUE 0.
       01  WS-K168              PIC 99 VALUE 0.
       01  WS-AVERAGE168        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE169          PIC X(20) VALUE SPACES.
       01  WS-HEADER169         PIC X(40) VALUE SPACES.
       01  WS-TOTAL171          PIC 9(6) VALUE 0.
       01  WS-K171              PIC 99 VALUE 0.
       01  WS-AVERAGE171        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE173          PIC X(20) VALUE SPACES.
       01  WS-HEADER173         PIC X(40) VALUE SPACES.
       01  WS-TOTAL176          PIC 9(6) VALUE 0.
       01  WS-K176              PIC 99 VALUE 0.
       01  WS-AVERAGE176        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL178          PIC 9(6) VALUE 0.
       01  WS-K178              PIC 99 VALUE 0.
       01  WS-AVERAGE178        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE179          PIC X(20) VALUE SPACES.
       01  WS-HEADER179         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT182         PIC 9(6) VALUE 500.
       01  WS-FLAG182           PIC X VALUE 'N'.
       01  WS-CODE183           PIC 9 VALUE 1.
       01  WS-STATUS183         PIC X(6) VALUE SPACES.
       01  WS-TOTAL184          PIC 9(6) VALUE 0.
       01  WS-K184              PIC 99 VALUE 0.
       01  WS-AVERAGE184        PIC 9(6)V99 VALUE 0.
       01  WS-CODE185           PIC 9 VALUE 1.
       01  WS-STATUS185         PIC X(6) VALUE SPACES.
       01  WS-TOTAL187          PIC 9(6) VALUE 0.
       01  WS-K187              PIC 99 VALUE 0.
       01  WS-AVERAGE187        PIC 9(6)V99 VALUE 0.
       01  WS-TOTAL191          PIC 9(6) VALUE 0.
       01  WS-K191              PIC 99 VALUE 0.
       01  WS-AVERAGE191        PIC 9(6)V99 VALUE 0.
       01  WS-TITLE192          PIC X(20) VALUE SPACES.
       01  WS-HEADER192         PIC X(40) VALUE SPACES.
       01  WS-TITLE195          PIC X(20) VALUE SPACES.
       01  WS-HEADER195         PIC X(40) VALUE SPACES.
       01  WS-CODE200           PIC 9 VALUE 1.
       01  WS-STATUS200         PIC X(6) VALUE SPACES.
       01  WS-TITLE201          PIC X(20) VALUE SPACES.
       01  WS-HEADER201         PIC X(40) VALUE SPACES.
       01  WS-AMOUNT203         PIC 9(6) VALUE 500.
       01  WS-FLAG203           PIC X VALUE 'N'.
       LINKAGE SECTION.
       01  LK-PATH2           PIC X(60).
       01  LK-FILTER5         PIC X(100).
       01  LK-PATH6           PIC X(60).
       01  LK-NAME7           PIC X(40).
       01  LK-FILTER12         PIC X(100).
       01  LK-NAME14           PIC X(40).
       01  LK-FILTER21         PIC X(100).
       01  LK-NAME23           PIC X(40).
       01  LK-FILTER24         PIC X(100).
       01  LK-PATH26           PIC X(60).
       01  LK-PATH27           PIC X(60).
       01  LK-NAME29           PIC X(40).
       01  LK-PATH31           PIC X(60).
       01  LK-FILTER41         PIC X(100).
       01  LK-PATH46           PIC X(60).
       01  LK-PATH53           PIC X(60).
       01  LK-PATH54           PIC X(60).
       01  LK-PATH56           PIC X(60).
       01  LK-FILTER60         PIC X(100).
       01  LK-PATH64           PIC X(60).
       01  LK-PATH74           PIC X(60).
       01  LK-NAME80           PIC X(40).
       01  LK-NAME86           PIC X(40).
       01  LK-PATH94           PIC X(60).
       01  LK-FILTER98         PIC X(100).
       01  LK-FILTER104         PIC X(100).
       01  LK-FILTER108         PIC X(100).
       01  LK-PATH109           PIC X(60).
       01  LK-NAME118           PIC X(40).
       01  LK-FILTER119         PIC X(100).
       01  LK-FILTER122         PIC X(100).
       01  LK-PATH128           PIC X(60).
       01  LK-PATH129           PIC X(60).
       01  LK-PATH132           PIC X(60).
       01  LK-FILTER137         PIC X(100).
       01  LK-NAME144           PIC X(40).
       01  LK-NAME145           PIC X(40).
       01  LK-FILTER147         PIC X(100).
       01  LK-FILTER149         PIC X(100).
       01  LK-PATH151           PIC X(60).
       01  LK-NAME157           PIC X(40).
       01  LK-NAME160           PIC X(40).
       01  LK-NAME161           PIC X(40).
       01  LK-FILTER166         PIC X(100).
       01  LK-PATH175           PIC X(60).
       01  LK-NAME186           PIC X(40).
       01  LK-PATH190           PIC X(60).
       01  LK-PATH194           PIC X(60).
       01  LK-FILTER196         PIC X(100).
       01  LK-NAME198           PIC X(40).
       01  LK-FILTER202         PIC X(100).
       PROCEDURE DIVISION USING LK-PATH2 LK-FILTER5 LK-PATH6 LK-NAME7 LK-FILTER12 LK-NAME14 LK-FILTER21 LK-NAME23 LK-FILTER24 LK-PATH26 LK-PATH27 LK-NAME29 LK-PATH31 LK-FILTER41 LK-PATH46 LK-PATH53 LK-PATH54 LK-PATH56 LK-FILTER60 LK-PATH64 LK-PATH74 LK-NAME80 LK-NAME86 LK-PATH94 LK-FILTER98 LK-FILTER104 LK-FILTER108 LK-PATH109 LK-NAME118 LK-FILTER119 LK-FILTER122 LK-PATH128 LK-PATH129 LK-PATH132 LK-FILTER137 LK-NAME144 LK-NAME145 LK-FILTER147 LK-FILTER149 LK-PATH151 LK-NAME157 LK-NAME160 LK-NAME161 LK-FILTER166 LK-PATH175 LK-NAME186 LK-PATH190 LK-PATH194 LK-FILTER196 LK-NAME198 LK-FILTER202.
       MAIN-PARA.
           DISPLAY 'START'.
           GOBACK.

       CLASSIFY-CODE200.
           EVALUATE WS-CODE200
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS200
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS200
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS200
           END-EVALUATE.

       LOG-LOGIN78.
           DISPLAY 'LOGIN ' WS-USER78 ' ' WS-PASSWORD-IN78.

       COMPUTE-TOTALS106.
           MOVE 0 TO WS-TOTAL106.
           PERFORM VARYING WS-K106 FROM 1 BY 1 UNTIL WS-K106 > 10
               ADD WS-K106 TO WS-TOTAL106
           END-PERFORM.
           COMPUTE WS-AVERAGE106 = WS-TOTAL106 / 10.

       ECHO-NAME170.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM170) END-EXEC.
           STRING '<p>' WS-FORM170 '</p>' DELIMITED BY SIZE INTO WS-PAGE170.
           EXEC CICS WEB SEND FROM(WS-PAGE170) END-EXEC.

       LOG-LOGIN-SAFE138.
           DISPLAY 'LOGIN ' WS-USER138.

       WRITE-EXPORT-SAFE129.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH129.
           OPEN OUTPUT EXPORT-FILE129.
           CLOSE EXPORT-FILE129.

       ECHO-NAME-SAFE84.
           MOVE '<p>Thank you</p>' TO WS-PAGE84.
           EXEC CICS WEB SEND FROM(WS-PAGE84) END-EXEC.

       CONVERT-FILE23.
           STRING "convert " LK-NAME23 DELIMITED BY SIZE INTO WS-CMD23.
           CALL 'SYSTEM' USING WS-CMD23.

       ECHO-NAME-SAFE58.
           MOVE '<p>Thank you</p>' TO WS-PAGE58.
           EXEC CICS WEB SEND FROM(WS-PAGE58) END-EXEC.

       EXTRACT-FIELD11.
           ACCEPT WS-POS11.
           MOVE WS-RECORD11(WS-POS11:5) TO WS-PART11.

       CONVERT-FILE-SAFE118.
           MOVE "convert /srv/in/report.txt" TO WS-CMD118.
           CALL 'SYSTEM' USING WS-CMD118.

       ECHO-NAME20.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM20) END-EXEC.
           STRING '<p>' WS-FORM20 '</p>' DELIMITED BY SIZE INTO WS-PAGE20.
           EXEC CICS WEB SEND FROM(WS-PAGE20) END-EXEC.

       WRITE-EXPORT-SAFE128.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH128.
           OPEN OUTPUT EXPORT-FILE128.
           CLOSE EXPORT-FILE128.

       PREPARE-QUERY60.
           MOVE LK-FILTER60 TO WS-STMT60.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT60 END-EXEC.

       WRITE-EXPORT56.
           MOVE LK-PATH56 TO WS-EXPORT-PATH56.
           OPEN OUTPUT EXPORT-FILE56.
           CLOSE EXPORT-FILE56.

       PREPARE-QUERY-SAFE104.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT104.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT104 END-EXEC.

       COMPUTE-TOTALS88.
           MOVE 0 TO WS-TOTAL88.
           PERFORM VARYING WS-K88 FROM 1 BY 1 UNTIL WS-K88 > 10
               ADD WS-K88 TO WS-TOTAL88
           END-PERFORM.
           COMPUTE WS-AVERAGE88 = WS-TOTAL88 / 10.

       LOG-LOGIN-SAFE110.
           DISPLAY 'LOGIN ' WS-USER110.

       COMPUTE-TOTALS176.
           MOVE 0 TO WS-TOTAL176.
           PERFORM VARYING WS-K176 FROM 1 BY 1 UNTIL WS-K176 > 10
               ADD WS-K176 TO WS-TOTAL176
           END-PERFORM.
           COMPUTE WS-AVERAGE176 = WS-TOTAL176 / 10.

       WRITE-EXPORT-SAFE132.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH132.
           OPEN OUTPUT EXPORT-FILE132.
           CLOSE EXPORT-FILE132.

       ECHO-NAME103.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM103) END-EXEC.
           STRING '<p>' WS-FORM103 '</p>' DELIMITED BY SIZE INTO WS-PAGE103.
           EXEC CICS WEB SEND FROM(WS-PAGE103) END-EXEC.

       COMPUTE-TOTALS65.
           MOVE 0 TO WS-TOTAL65.
           PERFORM VARYING WS-K65 FROM 1 BY 1 UNTIL WS-K65 > 10
               ADD WS-K65 TO WS-TOTAL65
           END-PERFORM.
           COMPUTE WS-AVERAGE65 = WS-TOTAL65 / 10.

       COMPUTE-TOTALS99.
           MOVE 0 TO WS-TOTAL99.
           PERFORM VARYING WS-K99 FROM 1 BY 1 UNTIL WS-K99 > 10
               ADD WS-K99 TO WS-TOTAL99
           END-PERFORM.
           COMPUTE WS-AVERAGE99 = WS-TOTAL99 / 10.

       FORMAT-HEADER192.
           MOVE 'MONTHLY REPORT' TO WS-TITLE192.
           STRING WS-TITLE192 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER192.
           DISPLAY WS-HEADER192.

       CLASSIFY-CODE17.
           EVALUATE WS-CODE17
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS17
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS17
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS17
           END-EVALUATE.

       COMPUTE-TOTALS187.
           MOVE 0 TO WS-TOTAL187.
           PERFORM VARYING WS-K187 FROM 1 BY 1 UNTIL WS-K187 > 10
               ADD WS-K187 TO WS-TOTAL187
           END-PERFORM.
           COMPUTE WS-AVERAGE187 = WS-TOTAL187 / 10.

       COMPUTE-TOTALS134.
           MOVE 0 TO WS-TOTAL134.
           PERFORM VARYING WS-K134 FROM 1 BY 1 UNTIL WS-K134 > 10
               ADD WS-K134 TO WS-TOTAL134
           END-PERFORM.
           COMPUTE WS-AVERAGE134 = WS-TOTAL134 / 10.

       EXTRACT-FIELD16.
           ACCEPT WS-POS16.
           MOVE WS-RECORD16(WS-POS16:5) TO WS-PART16.

       CONNECT-DB-SAFE163.
           ACCEPT WS-CONN-PW163 FROM ENVIRONMENT 'DB_PASSWORD'.

       EXTRACT-FIELD42.
           ACCEPT WS-POS42.
           MOVE WS-RECORD42(WS-POS42:5) TO WS-PART42.

       PREPARE-QUERY-SAFE24.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT24.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT24 END-EXEC.

       COMPUTE-TOTALS34.
           MOVE 0 TO WS-TOTAL34.
           PERFORM VARYING WS-K34 FROM 1 BY 1 UNTIL WS-K34 > 10
               ADD WS-K34 TO WS-TOTAL34
           END-PERFORM.
           COMPUTE WS-AVERAGE34 = WS-TOTAL34 / 10.

       COMPUTE-TOTALS13.
           MOVE 0 TO WS-TOTAL13.
           PERFORM VARYING WS-K13 FROM 1 BY 1 UNTIL WS-K13 > 10
               ADD WS-K13 TO WS-TOTAL13
           END-PERFORM.
           COMPUTE WS-AVERAGE13 = WS-TOTAL13 / 10.

       CLASSIFY-CODE18.
           EVALUATE WS-CODE18
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS18
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS18
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS18
           END-EVALUATE.

       WRITE-EXPORT94.
           MOVE LK-PATH94 TO WS-EXPORT-PATH94.
           OPEN OUTPUT EXPORT-FILE94.
           CLOSE EXPORT-FILE94.

       CLASSIFY-CODE30.
           EVALUATE WS-CODE30
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS30
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS30
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS30
           END-EVALUATE.

       COMPUTE-TOTALS8.
           MOVE 0 TO WS-TOTAL8.
           PERFORM VARYING WS-K8 FROM 1 BY 1 UNTIL WS-K8 > 10
               ADD WS-K8 TO WS-TOTAL8
           END-PERFORM.
           COMPUTE WS-AVERAGE8 = WS-TOTAL8 / 10.

       COMPUTE-TOTALS32.
           MOVE 0 TO WS-TOTAL32.
           PERFORM VARYING WS-K32 FROM 1 BY 1 UNTIL WS-K32 > 10
               ADD WS-K32 TO WS-TOTAL32
           END-PERFORM.
           COMPUTE WS-AVERAGE32 = WS-TOTAL32 / 10.

       CONVERT-FILE198.
           STRING "convert " LK-NAME198 DELIMITED BY SIZE INTO WS-CMD198.
           CALL 'SYSTEM' USING WS-CMD198.

       CONVERT-FILE29.
           STRING "convert " LK-NAME29 DELIMITED BY SIZE INTO WS-CMD29.
           CALL 'SYSTEM' USING WS-CMD29.

       CLASSIFY-CODE73.
           EVALUATE WS-CODE73
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS73
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS73
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS73
           END-EVALUATE.

       COMPUTE-TOTALS57.
           MOVE 0 TO WS-TOTAL57.
           PERFORM VARYING WS-K57 FROM 1 BY 1 UNTIL WS-K57 > 10
               ADD WS-K57 TO WS-TOTAL57
           END-PERFORM.
           COMPUTE WS-AVERAGE57 = WS-TOTAL57 / 10.

       COMPUTE-TOTALS159.
           MOVE 0 TO WS-TOTAL159.
           PERFORM VARYING WS-K159 FROM 1 BY 1 UNTIL WS-K159 > 10
               ADD WS-K159 TO WS-TOTAL159
           END-PERFORM.
           COMPUTE WS-AVERAGE159 = WS-TOTAL159 / 10.

       WRITE-EXPORT46.
           MOVE LK-PATH46 TO WS-EXPORT-PATH46.
           OPEN OUTPUT EXPORT-FILE46.
           CLOSE EXPORT-FILE46.

       WRITE-EXPORT-SAFE54.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH54.
           OPEN OUTPUT EXPORT-FILE54.
           CLOSE EXPORT-FILE54.

       PREPARE-QUERY41.
           MOVE LK-FILTER41 TO WS-STMT41.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT41 END-EXEC.

       COMPUTE-TOTALS76.
           MOVE 0 TO WS-TOTAL76.
           PERFORM VARYING WS-K76 FROM 1 BY 1 UNTIL WS-K76 > 10
               ADD WS-K76 TO WS-TOTAL76
           END-PERFORM.
           COMPUTE WS-AVERAGE76 = WS-TOTAL76 / 10.

       CLASSIFY-CODE67.
           EVALUATE WS-CODE67
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS67
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS67
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS67
           END-EVALUATE.

       CONNECT-DB-SAFE81.
           ACCEPT WS-CONN-PW81 FROM ENVIRONMENT 'DB_PASSWORD'.

       FORMAT-HEADER115.
           MOVE 'MONTHLY REPORT' TO WS-TITLE115.
           STRING WS-TITLE115 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER115.
           DISPLAY WS-HEADER115.

       CLASSIFY-CODE35.
           EVALUATE WS-CODE35
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS35
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS35
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS35
           END-EVALUATE.

       PREPARE-QUERY119.
           MOVE LK-FILTER119 TO WS-STMT119.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT119 END-EXEC.

       CONVERT-FILE144.
           STRING "convert " LK-NAME144 DELIMITED BY SIZE INTO WS-CMD144.
           CALL 'SYSTEM' USING WS-CMD144.

       FORMAT-HEADER55.
           MOVE 'MONTHLY REPORT' TO WS-TITLE55.
           STRING WS-TITLE55 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER55.
           DISPLAY WS-HEADER55.

       CONVERT-FILE-SAFE161.
           MOVE "convert /srv/in/report.txt" TO WS-CMD161.
           CALL 'SYSTEM' USING WS-CMD161.

       CONNECT-DB150.
           MOVE WS-DB-PASSWORD150 TO WS-CONN-PW150.

       CONVERT-FILE-SAFE160.
           MOVE "convert /srv/in/report.txt" TO WS-CMD160.
           CALL 'SYSTEM' USING WS-CMD160.

       COMPUTE-TOTALS4.
           MOVE 0 TO WS-TOTAL4.
           PERFORM VARYING WS-K4 FROM 1 BY 1 UNTIL WS-K4 > 10
               ADD WS-K4 TO WS-TOTAL4
           END-PERFORM.
           COMPUTE WS-AVERAGE4 = WS-TOTAL4 / 10.

       LOG-LOGIN-SAFE43.
           DISPLAY 'LOGIN ' WS-USER43.

       CHECK-LIMIT50.
           IF WS-AMOUNT50 > 1000
               MOVE 'Y' TO WS-FLAG50
           ELSE
               MOVE 'N' TO WS-FLAG50
           END-IF.

       CHECK-LIMIT33.
           IF WS-AMOUNT33 > 1000
               MOVE 'Y' TO WS-FLAG33
           ELSE
               MOVE 'N' TO WS-FLAG33
           END-IF.

       FORMAT-HEADER169.
           MOVE 'MONTHLY REPORT' TO WS-TITLE169.
           STRING WS-TITLE169 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER169.
           DISPLAY WS-HEADER169.

       FORMAT-HEADER38.
           MOVE 'MONTHLY REPORT' TO WS-TITLE38.
           STRING WS-TITLE38 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER38.
           DISPLAY WS-HEADER38.

       LOG-LOGIN154.
           DISPLAY 'LOGIN ' WS-USER154 ' ' WS-PASSWORD-IN154.

       PREPARE-QUERY-SAFE166.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT166.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT166 END-EXEC.

       FORMAT-HEADER114.
           MOVE 'MONTHLY REPORT' TO WS-TITLE114.
           STRING WS-TITLE114 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER114.
           DISPLAY WS-HEADER114.

       CONNECT-DB-SAFE95.
           ACCEPT WS-CONN-PW95 FROM ENVIRONMENT 'DB_PASSWORD'.

       LOG-LOGIN-SAFE193.
           DISPLAY 'LOGIN ' WS-USER193.

       CHECK-LIMIT25.
           IF WS-AMOUNT25 > 1000
               MOVE 'Y' TO WS-FLAG25
           ELSE
               MOVE 'N' TO WS-FLAG25
           END-IF.

       WRITE-EXPORT-SAFE190.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH190.
           OPEN OUTPUT EXPORT-FILE190.
           CLOSE EXPORT-FILE190.

       WRITE-EXPORT31.
           MOVE LK-PATH31 TO WS-EXPORT-PATH31.
           OPEN OUTPUT EXPORT-FILE31.
           CLOSE EXPORT-FILE31.

       ECHO-NAME-SAFE148.
           MOVE '<p>Thank you</p>' TO WS-PAGE148.
           EXEC CICS WEB SEND FROM(WS-PAGE148) END-EXEC.

       FORMAT-HEADER69.
           MOVE 'MONTHLY REPORT' TO WS-TITLE69.
           STRING WS-TITLE69 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER69.
           DISPLAY WS-HEADER69.

       CHECK-LIMIT127.
           IF WS-AMOUNT127 > 1000
               MOVE 'Y' TO WS-FLAG127
           ELSE
               MOVE 'N' TO WS-FLAG127
           END-IF.

       CONVERT-FILE86.
           STRING "convert " LK-NAME86 DELIMITED BY SIZE INTO WS-CMD86.
           CALL 'SYSTEM' USING WS-CMD86.

       ECHO-NAME177.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM177) END-EXEC.
           STRING '<p>' WS-FORM177 '</p>' DELIMITED BY SIZE INTO WS-PAGE177.
           EXEC CICS WEB SEND FROM(WS-PAGE177) END-EXEC.

       COMPUTE-TOTALS49.
           MOVE 0 TO WS-TOTAL49.
           PERFORM VARYING WS-K49 FROM 1 BY 1 UNTIL WS-K49 > 10
               ADD WS-K49 TO WS-TOTAL49
           END-PERFORM.
           COMPUTE WS-AVERAGE49 = WS-TOTAL49 / 10.

       WRITE-EXPORT151.
           MOVE LK-PATH151 TO WS-EXPORT-PATH151.
           OPEN OUTPUT EXPORT-FILE151.
           CLOSE EXPORT-FILE151.

       CHECK-LIMIT100.
           IF WS-AMOUNT100 > 1000
               MOVE 'Y' TO WS-FLAG100
           ELSE
               MOVE 'N' TO WS-FLAG100
           END-IF.

       COMPUTE-TOTALS3.
           MOVE 0 TO WS-TOTAL3.
           PERFORM VARYING WS-K3 FROM 1 BY 1 UNTIL WS-K3 > 10
               ADD WS-K3 TO WS-TOTAL3
           END-PERFORM.
           COMPUTE WS-AVERAGE3 = WS-TOTAL3 / 10.

       COMPUTE-TOTALS124.
           MOVE 0 TO WS-TOTAL124.
           PERFORM VARYING WS-K124 FROM 1 BY 1 UNTIL WS-K124 > 10
               ADD WS-K124 TO WS-TOTAL124
           END-PERFORM.
           COMPUTE WS-AVERAGE124 = WS-TOTAL124 / 10.

       LOG-LOGIN-SAFE19.
           DISPLAY 'LOGIN ' WS-USER19.

       EXTRACT-FIELD-SAFE77.
           ACCEPT WS-POS77.
           IF WS-POS77 IS NUMERIC AND WS-POS77 > 0 AND WS-POS77 < 76
               MOVE WS-RECORD77(WS-POS77:5) TO WS-PART77
           END-IF.

       ECHO-NAME-SAFE172.
           MOVE '<p>Thank you</p>' TO WS-PAGE172.
           EXEC CICS WEB SEND FROM(WS-PAGE172) END-EXEC.

       COMPUTE-TOTALS131.
           MOVE 0 TO WS-TOTAL131.
           PERFORM VARYING WS-K131 FROM 1 BY 1 UNTIL WS-K131 > 10
               ADD WS-K131 TO WS-TOTAL131
           END-PERFORM.
           COMPUTE WS-AVERAGE131 = WS-TOTAL131 / 10.

       EXTRACT-FIELD-SAFE93.
           ACCEPT WS-POS93.
           IF WS-POS93 IS NUMERIC AND WS-POS93 > 0 AND WS-POS93 < 76
               MOVE WS-RECORD93(WS-POS93:5) TO WS-PART93
           END-IF.

       WRITE-EXPORT27.
           MOVE LK-PATH27 TO WS-EXPORT-PATH27.
           OPEN OUTPUT EXPORT-FILE27.
           CLOSE EXPORT-FILE27.

       LOG-LOGIN-SAFE9.
           DISPLAY 'LOGIN ' WS-USER9.

       LOG-LOGIN197.
           DISPLAY 'LOGIN ' WS-USER197 ' ' WS-PASSWORD-IN197.

       LOG-LOGIN156.
           DISPLAY 'LOGIN ' WS-USER156 ' ' WS-PASSWORD-IN156.

       FORMAT-HEADER146.
           MOVE 'MONTHLY REPORT' TO WS-TITLE146.
           STRING WS-TITLE146 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER146.
           DISPLAY WS-HEADER146.

       CONNECT-DB-SAFE22.
           ACCEPT WS-CONN-PW22 FROM ENVIRONMENT 'DB_PASSWORD'.

       LOG-LOGIN188.
           DISPLAY 'LOGIN ' WS-USER188 ' ' WS-PASSWORD-IN188.

       COMPUTE-TOTALS82.
           MOVE 0 TO WS-TOTAL82.
           PERFORM VARYING WS-K82 FROM 1 BY 1 UNTIL WS-K82 > 10
               ADD WS-K82 TO WS-TOTAL82
           END-PERFORM.
           COMPUTE WS-AVERAGE82 = WS-TOTAL82 / 10.

       CONVERT-FILE-SAFE7.
           MOVE "convert /srv/in/report.txt" TO WS-CMD7.
           CALL 'SYSTEM' USING WS-CMD7.

       PREPARE-QUERY-SAFE196.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT196.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT196 END-EXEC.

       FORMAT-HEADER63.
           MOVE 'MONTHLY REPORT' TO WS-TITLE63.
           STRING WS-TITLE63 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER63.
           DISPLAY WS-HEADER63.

       LOG-LOGIN-SAFE75.
           DISPLAY 'LOGIN ' WS-USER75.

       CONVERT-FILE-SAFE80.
           MOVE "convert /srv/in/report.txt" TO WS-CMD80.
           CALL 'SYSTEM' USING WS-CMD80.

       CHECK-LIMIT52.
           IF WS-AMOUNT52 > 1000
               MOVE 'Y' TO WS-FLAG52
           ELSE
               MOVE 'N' TO WS-FLAG52
           END-IF.

       ECHO-NAME199.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM199) END-EXEC.
           STRING '<p>' WS-FORM199 '</p>' DELIMITED BY SIZE INTO WS-PAGE199.
           EXEC CICS WEB SEND FROM(WS-PAGE199) END-EXEC.

       FORMAT-HEADER107.
           MOVE 'MONTHLY REPORT' TO WS-TITLE107.
           STRING WS-TITLE107 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER107.
           DISPLAY WS-HEADER107.

       LOG-LOGIN-SAFE70.
           DISPLAY 'LOGIN ' WS-USER70.

       COMPUTE-TOTALS126.
           MOVE 0 TO WS-TOTAL126.
           PERFORM VARYING WS-K126 FROM 1 BY 1 UNTIL WS-K126 > 10
               ADD WS-K126 TO WS-TOTAL126
           END-PERFORM.
           COMPUTE WS-AVERAGE126 = WS-TOTAL126 / 10.

       FORMAT-HEADER105.
           MOVE 'MONTHLY REPORT' TO WS-TITLE105.
           STRING WS-TITLE105 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER105.
           DISPLAY WS-HEADER105.

       CLASSIFY-CODE36.
           EVALUATE WS-CODE36
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS36
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS36
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS36
           END-EVALUATE.

       ECHO-NAME-SAFE39.
           MOVE '<p>Thank you</p>' TO WS-PAGE39.
           EXEC CICS WEB SEND FROM(WS-PAGE39) END-EXEC.

       CHECK-LIMIT182.
           IF WS-AMOUNT182 > 1000
               MOVE 'Y' TO WS-FLAG182
           ELSE
               MOVE 'N' TO WS-FLAG182
           END-IF.

       FORMAT-HEADER173.
           MOVE 'MONTHLY REPORT' TO WS-TITLE173.
           STRING WS-TITLE173 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER173.
           DISPLAY WS-HEADER173.

       FORMAT-HEADER62.
           MOVE 'MONTHLY REPORT' TO WS-TITLE62.
           STRING WS-TITLE62 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER62.
           DISPLAY WS-HEADER62.

       FORMAT-HEADER167.
           MOVE 'MONTHLY REPORT' TO WS-TITLE167.
           STRING WS-TITLE167 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER167.
           DISPLAY WS-HEADER167.

       FORMAT-HEADER102.
           MOVE 'MONTHLY REPORT' TO WS-TITLE102.
           STRING WS-TITLE102 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER102.
           DISPLAY WS-HEADER102.

       FORMAT-HEADER59.
           MOVE 'MONTHLY REPORT' TO WS-TITLE59.
           STRING WS-TITLE59 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER59.
           DISPLAY WS-HEADER59.

       COMPUTE-TOTALS168.
           MOVE 0 TO WS-TOTAL168.
           PERFORM VARYING WS-K168 FROM 1 BY 1 UNTIL WS-K168 > 10
               ADD WS-K168 TO WS-TOTAL168
           END-PERFORM.
           COMPUTE WS-AVERAGE168 = WS-TOTAL168 / 10.

       WRITE-EXPORT-SAFE26.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH26.
           OPEN OUTPUT EXPORT-FILE26.
           CLOSE EXPORT-FILE26.

       EXTRACT-FIELD-SAFE162.
           ACCEPT WS-POS162.
           IF WS-POS162 IS NUMERIC AND WS-POS162 > 0 AND WS-POS162 < 76
               MOVE WS-RECORD162(WS-POS162:5) TO WS-PART162
           END-IF.

       PREPARE-QUERY-SAFE122.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT122.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT122 END-EXEC.

       CHECK-LIMIT140.
           IF WS-AMOUNT140 > 1000
               MOVE 'Y' TO WS-FLAG140
           ELSE
               MOVE 'N' TO WS-FLAG140
           END-IF.

       LOG-LOGIN87.
           DISPLAY 'LOGIN ' WS-USER87 ' ' WS-PASSWORD-IN87.

       ECHO-NAME47.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM47) END-EXEC.
           STRING '<p>' WS-FORM47 '</p>' DELIMITED BY SIZE INTO WS-PAGE47.
           EXEC CICS WEB SEND FROM(WS-PAGE47) END-EXEC.

       ECHO-NAME91.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM91) END-EXEC.
           STRING '<p>' WS-FORM91 '</p>' DELIMITED BY SIZE INTO WS-PAGE91.
           EXEC CICS WEB SEND FROM(WS-PAGE91) END-EXEC.

       ECHO-NAME152.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM152) END-EXEC.
           STRING '<p>' WS-FORM152 '</p>' DELIMITED BY SIZE INTO WS-PAGE152.
           EXEC CICS WEB SEND FROM(WS-PAGE152) END-EXEC.

       CHECK-LIMIT117.
           IF WS-AMOUNT117 > 1000
               MOVE 'Y' TO WS-FLAG117
           ELSE
               MOVE 'N' TO WS-FLAG117
           END-IF.

       CONNECT-DB-SAFE155.
           ACCEPT WS-CONN-PW155 FROM ENVIRONMENT 'DB_PASSWORD'.

       CLASSIFY-CODE121.
           EVALUATE WS-CODE121
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS121
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS121
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS121
           END-EVALUATE.

       EXTRACT-FIELD-SAFE181.
           ACCEPT WS-POS181.
           IF WS-POS181 IS NUMERIC AND WS-POS181 > 0 AND WS-POS181 < 76
               MOVE WS-RECORD181(WS-POS181:5) TO WS-PART181
           END-IF.

       FORMAT-HEADER195.
           MOVE 'MONTHLY REPORT' TO WS-TITLE195.
           STRING WS-TITLE195 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER195.
           DISPLAY WS-HEADER195.

       CLASSIFY-CODE90.
           EVALUATE WS-CODE90
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS90
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS90
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS90
           END-EVALUATE.

       EXTRACT-FIELD83.
           ACCEPT WS-POS83.
           MOVE WS-RECORD83(WS-POS83:5) TO WS-PART83.

       FORMAT-HEADER201.
           MOVE 'MONTHLY REPORT' TO WS-TITLE201.
           STRING WS-TITLE201 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER201.
           DISPLAY WS-HEADER201.

       CONNECT-DB-SAFE61.
           ACCEPT WS-CONN-PW61 FROM ENVIRONMENT 'DB_PASSWORD'.

       CONNECT-DB143.
           MOVE WS-DB-PASSWORD143 TO WS-CONN-PW143.

       EXTRACT-FIELD180.
           ACCEPT WS-POS180.
           MOVE WS-RECORD180(WS-POS180:5) TO WS-PART180.

       CONNECT-DB142.
           MOVE WS-DB-PASSWORD142 TO WS-CONN-PW142.

       CLASSIFY-CODE68.
           EVALUATE WS-CODE68
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS68
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS68
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS68
           END-EVALUATE.

       WRITE-EXPORT-SAFE194.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH194.
           OPEN OUTPUT EXPORT-FILE194.
           CLOSE EXPORT-FILE194.

       CLASSIFY-CODE133.
           EVALUATE WS-CODE133
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS133
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS133
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS133
           END-EVALUATE.

       COMPUTE-TOTALS171.
           MOVE 0 TO WS-TOTAL171.
           PERFORM VARYING WS-K171 FROM 1 BY 1 UNTIL WS-K171 > 10
               ADD WS-K171 TO WS-TOTAL171
           END-PERFORM.
           COMPUTE WS-AVERAGE171 = WS-TOTAL171 / 10.

       CONNECT-DB-SAFE28.
           ACCEPT WS-CONN-PW28 FROM ENVIRONMENT 'DB_PASSWORD'.

       EXTRACT-FIELD-SAFE153.
           ACCEPT WS-POS153.
           IF WS-POS153 IS NUMERIC AND WS-POS153 > 0 AND WS-POS153 < 76
               MOVE WS-RECORD153(WS-POS153:5) TO WS-PART153
           END-IF.

       CLASSIFY-CODE51.
           EVALUATE WS-CODE51
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS51
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS51
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS51
           END-EVALUATE.

       EXTRACT-FIELD-SAFE45.
           ACCEPT WS-POS45.
           IF WS-POS45 IS NUMERIC AND WS-POS45 > 0 AND WS-POS45 < 76
               MOVE WS-RECORD45(WS-POS45:5) TO WS-PART45
           END-IF.

       CLASSIFY-CODE111.
           EVALUATE WS-CODE111
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS111
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS111
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS111
           END-EVALUATE.

       LOG-LOGIN44.
           DISPLAY 'LOGIN ' WS-USER44 ' ' WS-PASSWORD-IN44.

       PREPARE-QUERY108.
           MOVE LK-FILTER108 TO WS-STMT108.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT108 END-EXEC.

       CHECK-LIMIT203.
           IF WS-AMOUNT203 > 1000
               MOVE 'Y' TO WS-FLAG203
           ELSE
               MOVE 'N' TO WS-FLAG203
           END-IF.

       CHECK-LIMIT1.
           IF WS-AMOUNT1 > 1000
               MOVE 'Y' TO WS-FLAG1
           ELSE
               MOVE 'N' TO WS-FLAG1
           END-IF.

       COMPUTE-TOTALS96.
           MOVE 0 TO WS-TOTAL96.
           PERFORM VARYING WS-K96 FROM 1 BY 1 UNTIL WS-K96 > 10
               ADD WS-K96 TO WS-TOTAL96
           END-PERFORM.
           COMPUTE WS-AVERAGE96 = WS-TOTAL96 / 10.

       CHECK-LIMIT48.
           IF WS-AMOUNT48 > 1000
               MOVE 'Y' TO WS-FLAG48
           ELSE
               MOVE 'N' TO WS-FLAG48
           END-IF.

       WRITE-EXPORT2.
           MOVE LK-PATH2 TO WS-EXPORT-PATH2.
           OPEN OUTPUT EXPORT-FILE2.
           CLOSE EXPORT-FILE2.

       WRITE-EXPORT53.
           MOVE LK-PATH53 TO WS-EXPORT-PATH53.
           OPEN OUTPUT EXPORT-FILE53.
           CLOSE EXPORT-FILE53.

       COMPUTE-TOTALS79.
           MOVE 0 TO WS-TOTAL79.
           PERFORM VARYING WS-K79 FROM 1 BY 1 UNTIL WS-K79 > 10
               ADD WS-K79 TO WS-TOTAL79
           END-PERFORM.
           COMPUTE WS-AVERAGE79 = WS-TOTAL79 / 10.

       FORMAT-HEADER71.
           MOVE 'MONTHLY REPORT' TO WS-TITLE71.
           STRING WS-TITLE71 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER71.
           DISPLAY WS-HEADER71.

       CONNECT-DB-SAFE10.
           ACCEPT WS-CONN-PW10 FROM ENVIRONMENT 'DB_PASSWORD'.

       CLASSIFY-CODE164.
           EVALUATE WS-CODE164
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS164
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS164
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS164
           END-EVALUATE.

       WRITE-EXPORT64.
           MOVE LK-PATH64 TO WS-EXPORT-PATH64.
           OPEN OUTPUT EXPORT-FILE64.
           CLOSE EXPORT-FILE64.

       CHECK-LIMIT135.
           IF WS-AMOUNT135 > 1000
               MOVE 'Y' TO WS-FLAG135
           ELSE
               MOVE 'N' TO WS-FLAG135
           END-IF.

       COMPUTE-TOTALS125.
           MOVE 0 TO WS-TOTAL125.
           PERFORM VARYING WS-K125 FROM 1 BY 1 UNTIL WS-K125 > 10
               ADD WS-K125 TO WS-TOTAL125
           END-PERFORM.
           COMPUTE WS-AVERAGE125 = WS-TOTAL125 / 10.

       EXTRACT-FIELD72.
           ACCEPT WS-POS72.
           MOVE WS-RECORD72(WS-POS72:5) TO WS-PART72.

       CONNECT-DB113.
           MOVE WS-DB-PASSWORD113 TO WS-CONN-PW113.

       CONVERT-FILE-SAFE14.
           MOVE "convert /srv/in/report.txt" TO WS-CMD14.
           CALL 'SYSTEM' USING WS-CMD14.

       ECHO-NAME116.
           EXEC CICS WEB READ FORMFIELD('name') VALUE(WS-FORM116) END-EXEC.
           STRING '<p>' WS-FORM116 '</p>' DELIMITED BY SIZE INTO WS-PAGE116.
           EXEC CICS WEB SEND FROM(WS-PAGE116) END-EXEC.

       CHECK-LIMIT141.
           IF WS-AMOUNT141 > 1000
               MOVE 'Y' TO WS-FLAG141
           ELSE
               MOVE 'N' TO WS-FLAG141
           END-IF.

       COMPUTE-TOTALS120.
           MOVE 0 TO WS-TOTAL120.
           PERFORM VARYING WS-K120 FROM 1 BY 1 UNTIL WS-K120 > 10
               ADD WS-K120 TO WS-TOTAL120
           END-PERFORM.
           COMPUTE WS-AVERAGE120 = WS-TOTAL120 / 10.

       PREPARE-QUERY12.
           MOVE LK-FILTER12 TO WS-STMT12.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT12 END-EXEC.

       PREPARE-QUERY-SAFE5.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT5.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT5 END-EXEC.

       WRITE-EXPORT-SAFE6.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH6.
           OPEN OUTPUT EXPORT-FILE6.
           CLOSE EXPORT-FILE6.

       CHECK-LIMIT136.
           IF WS-AMOUNT136 > 1000
               MOVE 'Y' TO WS-FLAG136
           ELSE
               MOVE 'N' TO WS-FLAG136
           END-IF.

       PREPARE-QUERY202.
           MOVE LK-FILTER202 TO WS-STMT202.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT202 END-EXEC.

       EXTRACT-FIELD130.
           ACCEPT WS-POS130.
           MOVE WS-RECORD130(WS-POS130:5) TO WS-PART130.

       CONVERT-FILE-SAFE186.
           MOVE "convert /srv/in/report.txt" TO WS-CMD186.
           CALL 'SYSTEM' USING WS-CMD186.

       CONVERT-FILE-SAFE145.
           MOVE "convert /srv/in/report.txt" TO WS-CMD145.
           CALL 'SYSTEM' USING WS-CMD145.

       CHECK-LIMIT15.
           IF WS-AMOUNT15 > 1000
               MOVE 'Y' TO WS-FLAG15
           ELSE
               MOVE 'N' TO WS-FLAG15
           END-IF.

       LOG-LOGIN66.
           DISPLAY 'LOGIN ' WS-USER66 ' ' WS-PASSWORD-IN66.

       CHECK-LIMIT101.
           IF WS-AMOUNT101 > 1000
               MOVE 'Y' TO WS-FLAG101
           ELSE
               MOVE 'N' TO WS-FLAG101
           END-IF.

       EXTRACT-FIELD85.
           ACCEPT WS-POS85.
           MOVE WS-RECORD85(WS-POS85:5) TO WS-PART85.

       CONVERT-FILE157.
           STRING "convert " LK-NAME157 DELIMITED BY SIZE INTO WS-CMD157.
           CALL 'SYSTEM' USING WS-CMD157.

       EXTRACT-FIELD89.
           ACCEPT WS-POS89.
           MOVE WS-RECORD89(WS-POS89:5) TO WS-PART89.

       WRITE-EXPORT74.
           MOVE LK-PATH74 TO WS-EXPORT-PATH74.
           OPEN OUTPUT EXPORT-FILE74.
           CLOSE EXPORT-FILE74.

       CONNECT-DB-SAFE174.
           ACCEPT WS-CONN-PW174 FROM ENVIRONMENT 'DB_PASSWORD'.

       WRITE-EXPORT-SAFE175.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH175.
           OPEN OUTPUT EXPORT-FILE175.
           CLOSE EXPORT-FILE175.

       PREPARE-QUERY21.
           MOVE LK-FILTER21 TO WS-STMT21.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT21 END-EXEC.

       COMPUTE-TOTALS40.
           MOVE 0 TO WS-TOTAL40.
           PERFORM VARYING WS-K40 FROM 1 BY 1 UNTIL WS-K40 > 10
               ADD WS-K40 TO WS-TOTAL40
           END-PERFORM.
           COMPUTE WS-AVERAGE40 = WS-TOTAL40 / 10.

       EXTRACT-FIELD112.
           ACCEPT WS-POS112.
           MOVE WS-RECORD112(WS-POS112:5) TO WS-PART112.

       LOG-LOGIN-SAFE92.
           DISPLAY 'LOGIN ' WS-USER92.

       FORMAT-HEADER179.
           MOVE 'MONTHLY REPORT' TO WS-TITLE179.
           STRING WS-TITLE179 DELIMITED BY SIZE
                  ' - PAGE 1' DELIMITED BY SIZE
               INTO WS-HEADER179.
           DISPLAY WS-HEADER179.

       COMPUTE-TOTALS178.
           MOVE 0 TO WS-TOTAL178.
           PERFORM VARYING WS-K178 FROM 1 BY 1 UNTIL WS-K178 > 10
               ADD WS-K178 TO WS-TOTAL178
           END-PERFORM.
           COMPUTE WS-AVERAGE178 = WS-TOTAL178 / 10.

       PREPARE-QUERY-SAFE147.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT147.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT147 END-EXEC.

       CLASSIFY-CODE183.
           EVALUATE WS-CODE183
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS183
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS183
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS183
           END-EVALUATE.

       COMPUTE-TOTALS191.
           MOVE 0 TO WS-TOTAL191.
           PERFORM VARYING WS-K191 FROM 1 BY 1 UNTIL WS-K191 > 10
               ADD WS-K191 TO WS-TOTAL191
           END-PERFORM.
           COMPUTE WS-AVERAGE191 = WS-TOTAL191 / 10.

       LOG-LOGIN37.
           DISPLAY 'LOGIN ' WS-USER37 ' ' WS-PASSWORD-IN37.

       CLASSIFY-CODE165.
           EVALUATE WS-CODE165
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS165
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS165
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS165
           END-EVALUATE.

       PREPARE-QUERY149.
           MOVE LK-FILTER149 TO WS-STMT149.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT149 END-EXEC.

       WRITE-EXPORT-SAFE109.
           MOVE '/srv/export/daily.txt' TO WS-EXPORT-PATH109.
           OPEN OUTPUT EXPORT-FILE109.
           CLOSE EXPORT-FILE109.

       COMPUTE-TOTALS123.
           MOVE 0 TO WS-TOTAL123.
           PERFORM VARYING WS-K123 FROM 1 BY 1 UNTIL WS-K123 > 10
               ADD WS-K123 TO WS-TOTAL123
           END-PERFORM.
           COMPUTE WS-AVERAGE123 = WS-TOTAL123 / 10.

       PREPARE-QUERY-SAFE98.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT98.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT98 END-EXEC.

       COMPUTE-TOTALS97.
           MOVE 0 TO WS-TOTAL97.
           PERFORM VARYING WS-K97 FROM 1 BY 1 UNTIL WS-K97 > 10
               ADD WS-K97 TO WS-TOTAL97
           END-PERFORM.
           COMPUTE WS-AVERAGE97 = WS-TOTAL97 / 10.

       CONNECT-DB-SAFE158.
           ACCEPT WS-CONN-PW158 FROM ENVIRONMENT 'DB_PASSWORD'.

       PREPARE-QUERY-SAFE137.
           MOVE 'SELECT NAME FROM CUST WHERE ID = ?' TO WS-STMT137.
           EXEC SQL PREPARE DYNSTMT FROM :WS-STMT137 END-EXEC.

       COMPUTE-TOTALS184.
           MOVE 0 TO WS-TOTAL184.
           PERFORM VARYING WS-K184 FROM 1 BY 1 UNTIL WS-K184 > 10
               ADD WS-K184 TO WS-TOTAL184
           END-PERFORM.
           COMPUTE WS-AVERAGE184 = WS-TOTAL184 / 10.

       CLASSIFY-CODE139.
           EVALUATE WS-CODE139
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS139
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS139
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS139
           END-EVALUATE.

       CLASSIFY-CODE185.
           EVALUATE WS-CODE185
               WHEN 1
                   MOVE 'NEW' TO WS-STATUS185
               WHEN 2
                   MOVE 'OPEN' TO WS-STATUS185
               WHEN OTHER
                   MOVE 'CLOSED' TO WS-STATUS185
           END-EVALUATE.

       LOG-LOGIN189.
           DISPLAY 'LOGIN ' WS-USER189 ' ' WS-PASSWORD-IN189.

