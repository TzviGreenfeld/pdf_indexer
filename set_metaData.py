from pdfrw import PdfReader, PdfWriter, PdfDict

_Author = None
_Title = None
_Subject = None
_Keywords = None
_Producer = None
_Creator = None


if __name__ == '__main__':
    pdf_reader = PdfReader('bookmarked_calculus.pdf')
    metadata = PdfDict(Author= _Author,
                        Title= _Title,
                        Subject= _Subject,
                        Keywords= _Keywords,
                        Producer= _Producer,
                        Creator= _Creator)
    pdf_reader.Info.update(metadata)
    PdfWriter().write('lectures.pdf', pdf_reader)
