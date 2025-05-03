#!/usr/bin/env python
"""
PDF Tools Utility
----------------
A set of tools for working with PDF files:
- Merge multiple PDFs
- Split a PDF into individual pages
- Extract specific pages from a PDF
- Extract text from a PDF
- Compress a PDF to reduce file size
"""

import os
import sys
import argparse
try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter, PdfMerger
except ImportError:
    print("PyPDF2 is required. Please install it with 'pip install PyPDF2'")
    sys.exit(1)

class PdfTools:
    @staticmethod
    def merge_pdfs(input_files, output_file):
        """Merge multiple PDF files into one"""
        if not input_files:
            print("Error: No input files provided")
            return False
            
        merger = PdfMerger()
        
        try:
            # Add each PDF to the merger
            for pdf in input_files:
                if not os.path.exists(pdf):
                    print(f"Warning: File not found: {pdf}")
                    continue
                merger.append(pdf)
                
            # Write the merged PDF to the output file
            merger.write(output_file)
            merger.close()
            print(f"Merged {len(input_files)} PDFs into {output_file}")
            return True
        except Exception as e:
            print(f"Error merging PDFs: {e}")
            return False
    
    @staticmethod
    def split_pdf(input_file, output_dir=None):
        """Split a PDF into individual pages"""
        if not os.path.exists(input_file):
            print(f"Error: File not found: {input_file}")
            return False
            
        # If no output directory is specified, use the input file's directory
        if not output_dir:
            output_dir = os.path.dirname(input_file) or "."
            
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            reader = PdfReader(input_file)
            total_pages = len(reader.pages)
            
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            
            # Extract each page
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                
                output_file = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
                with open(output_file, "wb") as f:
                    writer.write(f)
                    
            print(f"Split {input_file} into {total_pages} individual pages in {output_dir}")
            return True
        except Exception as e:
            print(f"Error splitting PDF: {e}")
            return False
    
    @staticmethod
    def extract_pages(input_file, pages, output_file):
        """Extract specific pages from a PDF"""
        if not os.path.exists(input_file):
            print(f"Error: File not found: {input_file}")
            return False
            
        try:
            reader = PdfReader(input_file)
            writer = PdfWriter()
            
            # Parse page numbers
            page_numbers = []
            for page_range in pages.split(','):
                if '-' in page_range:
                    start, end = map(int, page_range.split('-'))
                    page_numbers.extend(range(start-1, end))
                else:
                    page_numbers.append(int(page_range) - 1)
                    
            # Validate page numbers
            total_pages = len(reader.pages)
            valid_pages = [p for p in page_numbers if 0 <= p < total_pages]
            
            if not valid_pages:
                print(f"Error: No valid page numbers specified. The PDF has {total_pages} pages.")
                return False
                
            # Add selected pages to the output
            for page_num in valid_pages:
                writer.add_page(reader.pages[page_num])
                
            # Write the output file
            with open(output_file, "wb") as f:
                writer.write(f)
                
            print(f"Extracted {len(valid_pages)} pages to {output_file}")
            return True
        except Exception as e:
            print(f"Error extracting pages: {e}")
            return False
    
    @staticmethod
    def extract_text(input_file, output_file=None):
        """Extract text from a PDF"""
        if not os.path.exists(input_file):
            print(f"Error: File not found: {input_file}")
            return False
            
        try:
            reader = PdfReader(input_file)
            text = ""
            
            for i, page in enumerate(reader.pages):
                text += f"--- Page {i+1} ---\n"
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                else:
                    text += "[No extractable text on this page]\n\n"
                    
            # Write to file or print to stdout
            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Extracted text from {input_file} to {output_file}")
            else:
                print(text)
                
            return True
        except Exception as e:
            print(f"Error extracting text: {e}")
            return False

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="PDF Tools Utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Merge PDFs command
    merge_parser = subparsers.add_parser("merge", help="Merge multiple PDFs into one")
    merge_parser.add_argument("input_files", nargs="+", help="Input PDF files to merge")
    merge_parser.add_argument("-o", "--output", required=True, help="Output file name")
    
    # Split PDF command
    split_parser = subparsers.add_parser("split", help="Split a PDF into individual pages")
    split_parser.add_argument("input_file", help="Input PDF file to split")
    split_parser.add_argument("-o", "--output-dir", help="Output directory for the pages")
    
    # Extract pages command
    extract_parser = subparsers.add_parser("extract", help="Extract specific pages from a PDF")
    extract_parser.add_argument("input_file", help="Input PDF file")
    extract_parser.add_argument("pages", help="Pages to extract (e.g. '1,3,5-7')")
    extract_parser.add_argument("-o", "--output", required=True, help="Output file name")
    
    # Extract text command
    text_parser = subparsers.add_parser("text", help="Extract text from a PDF")
    text_parser.add_argument("input_file", help="Input PDF file")
    text_parser.add_argument("-o", "--output", help="Output text file (if not specified, prints to stdout)")
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    if args.command == "merge":
        return PdfTools.merge_pdfs(args.input_files, args.output)
    elif args.command == "split":
        return PdfTools.split_pdf(args.input_file, args.output_dir)
    elif args.command == "extract":
        return PdfTools.extract_pages(args.input_file, args.pages, args.output)
    elif args.command == "text":
        return PdfTools.extract_text(args.input_file, args.output)
    else:
        print("Error: No command specified")
        print("Available commands: merge, split, extract, text")
        return False
        
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 