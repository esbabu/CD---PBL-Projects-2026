import docx

doc = docx.Document(r'C:\Users\jaish\Desktop\TOC FINAL FOLDER\END FOLDER\Multiagnet-Source-Code-Optimizer End report.docx')
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if txt.startswith(('I.', 'II.', 'III.', 'IV.', 'V.', 'VI.', 'REF', 'APP')):
        print(f'P{i}: [{p.style.name}] "{txt}"')
