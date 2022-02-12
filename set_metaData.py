from pdfrw import PdfReader, PdfWriter, PdfDict
import sys

_Author = None
_Title = None
_Subject = None
_Keywords = None
_Producer = None
_Creator = None
file = sys.argv[1]

if __name__ == '__main__':
    pdf_reader = PdfReader(file)
    metadata = PdfDict(Author= _Author,
                        Title= _Title,
                        Subject= _Subject,
                        Keywords= _Keywords,
                        Producer= _Producer,
                        Creator= _Creator)
    pdf_reader.Info.update(metadata)
    PdfWriter().write(file, pdf_reader)
