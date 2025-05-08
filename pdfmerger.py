from PyPDF2 import PdfFilemerger

def merge_pdfs(pdf_files, output_file): 
    merger = PddfFileMerger()
    for pdf in pdf_files: 
        with open(pdf, "rb") as file: 
            pdf_reader = PdfFilemerger()
            pdf_reader.append(file)
        merger.append(pdf_reader)
    with open(output_file, " wb") as file: 
        merger.write(file)
        print(f'Pdf files merged into {output_file}")


# example usage

merge_pdfs(["file1.pdf", "file2.pdf", "file3.pdf"], "merged_output.pdf")
