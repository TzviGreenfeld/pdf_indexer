import os
import PyPDF2
import tempfile
from pathlib import Path

class PDFMerger:
    def __init__(self, files: list, output: str, index_page: bool = False):
        self.output = output
        self.file_names = list(map(self.get_file_name, files))
        self.files = list(map(self.open_file, files))
        self.fileReaders = list(map(self.to_fileReader, files))
        self.merged = None
        self.index = None

    def __del__(self):
        for f in self.files:
            f.close()

    def open_file(self, file_name: str):
        return Path(file_name).open('rb')

    def to_fileReader(self, file_name: str):
        return PyPDF2.PdfFileReader(file_name)

    def get_file_name(self, filename: str):
        base = os.path.basename(filename)
        name = os.path.splitext(base)[0]
        return name

    def merge_files(self, bookmark: bool = True):

        pdf_merger = PyPDF2.PdfFileMerger()
        for f in self.fileReaders:
            pdf_merger.append(f)

        if bookmark:
            for name, page in self.gen_bookmarks():
                pdf_merger.addBookmark(name, page)

        temp_file = tempfile.NamedTemporaryFile(mode='wb+')
        pdf_merger.write(temp_file)
        temp_file.seek(0)
        self.merged = temp_file

        return temp_file

    def gen_bookmarks(self):
        page = 0 if not self.index else self.indexPage.getNumPages()
        bookmarks = []
        for name, f in zip(self.file_names, self.fileReaders):
            bookmarks.append((name, page))
            page += f.getNumPages()
        return bookmarks

    def add_index(self):
        pass

    def save(self):
        with Path(self.output).open('wb') as f:
            f.write(self.merged.read())
        return


if __name__ == "__main__":
    base = "D:\\code\\pdf_indexer\\lectures"
    files = [base + "\\" + f for f in os.listdir(base)]
    output = "merged.pdf"
    merger = PDFMerger(files, output)
    merger.merge_files(bookmark=True)
    merger.add_index()
    merger.save()
