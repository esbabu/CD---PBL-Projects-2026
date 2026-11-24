import docx, time
from test_code_block_docx import add_code_block

doc = docx.Document()
t0 = time.time()
for i in range(198):
    doc.add_paragraph(f'• Test Case {i+1}')
    add_code_block(doc, 'void foo() {\n    int x = 1;\n    printf("%d", x);\n}')
    doc.add_paragraph('Description: test description')
    doc.add_paragraph('Screenshot .1')

doc.save('scratch/perf_test.docx')
print(f'Done in {time.time() - t0:.2f} seconds!')
