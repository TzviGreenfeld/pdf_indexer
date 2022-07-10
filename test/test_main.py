from fpdf import FPDF
import os

# init
TEST_FILE = "test.pdf"


def generate_different_dimensions_pdf():
    orientations = ['P', 'L']
    formats = ["A3", "A4", "A5", "Letter", "Legal"]

    pdf = FPDF()
    pdf.set_font("Arial", size=25)
    for _orientation, _format in ((x, y) for x in orientations for y in formats):
        pdf.add_page(orientation=_orientation, format=_format)
        pdf.cell(200, 10, txt=f"{_orientation}_{_format}", align='C')
    pdf.output(TEST_FILE)


generate_different_dimensions_pdf()