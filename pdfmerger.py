from PyPDF2 import PdfMerger

def merge_pdfs(pdf_files, output_file):
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    with open(output_file, "wb") as file:
        merger.write(file)
        print(f'Pdf files merged into {output_file}')

# example usage
# merge_pdfs(["file1.pdf", "file2.pdf", "file3.pdf"], "merged_output.pdf")
