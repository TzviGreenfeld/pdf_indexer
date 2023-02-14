from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_pdf(titles):
    # Create a new PDF file
    pdf_file = canvas.Canvas("output.pdf", pagesize=letter)
    for title in titles:
        pdf_file.setFont("Helvetica", 14)
        title_width = pdf_file.stringWidth(title)
        x = (letter[0] / 2) - (title_width / 2)
        y = letter[1] - 30
        pdf_file.drawString(x, y, title)
        pdf_file.showPage()
    pdf_file.save()


# Example usage

if __name__=='__main__':
    titles = ["Errors", "Floating point, IEEE, rounding, loss of significance", "Nonlinear equations",
          "Polynomial interpolation (including chebyshev points)", "PPI and spline interpolation", "Least Squares and curve fitting", "Numerical integration (trapezoidal, simpson)", "Numerical differentiation"]
    create_pdf(titles)
