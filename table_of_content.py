from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from tempfile import TemporaryFile
from fpdf import FPDF
from pdfrw import PageMerge, PdfReader, PdfWriter


class TableOfContent:
    LINE_LENGTH = 60
    LINE_WIDTH = 200
    LINE_HEIGHT = 10

    def __init__(self, files: list, file_name=None):
        """"
        will only save file if file_name is not None
        """
        self.pdf = FPDF(format='A4')
        self.files = files
        self.file_len = -1
        self.pages_data = self.extract_data()
        self.index = self.create_table_of_content()

        for i in range(self.file_len):
            self.pdf.add_page()

        self.write_toc_page()
        if file_name is not None:
            self.file_name = file_name
            self.save()

    def create_table_of_content(self):
        curr_page_num = 2
        index = {}
        for (name, file_len) in self.pages_data:
            index.update({name: curr_page_num})
            curr_page_num += file_len

        self.file_len = curr_page_num
        return index

    def extract_data(self):
        files_data = []
        for name in self.files:
            with open(name, 'rb') as f:
                curr_file = PdfFileReader(f)
                curr_len = curr_file.numPages

                # get file name without extension and path
                curr_name = name[name.rfind("/") + 1: name.find('.pdf')]
                files_data.append((curr_name, curr_len))
        return files_data

    def write_toc_page(self):
        links = []
        for entry in self.index.items():
            filename, page_num = entry
            # links setup
            self.pdf.page = page_num
            links.append(self.pdf.add_link())

        # write text line by line
        self.pdf.page = 1
        self.pdf.set_font("Courier", size=30)
        curr_link_index = 0
        for entry in self.index.items():
            filename, page_num = entry
            # links
            curr_link = links[curr_link_index]
            self.pdf.set_link(curr_link, y=0.0, page=page_num)
            self.pdf.cell(self.LINE_WIDTH / 2, self.LINE_HEIGHT, txt=str(filename), align="L", ln=0, link=curr_link)
            self.pdf.cell(self.LINE_WIDTH / 2, self.LINE_HEIGHT, txt=str(page_num), align="R", ln=1, link=curr_link)
            curr_link_index += 1

    def save(self):
        self.pdf.page = self.file_len
        self.pdf.output(self.file_name)


if __name__ == '__main__':
    _files = ["sample/a.pdf", "sample/b.pdf"]

    toc = TableOfContent(_files, "out.pdf")


    # merge test
    def merge(files):
        merger = PdfFileMerger()

        for pdf in files:
            merger.append(pdf)
        output_name = "merged.pdf"
        merger.write(output_name)
        merger.close()


    merge(_files)
