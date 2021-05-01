"""
Add a Code 128A barcode to another PDF.

Basic usage:
    combiner = AppendBarcode(save_path="output/")
    combiner.add_barcode("Barcode", path/to/original/doc)

The Barcode generator is provided in a distinct class to allow it to be used to generate stand alone
barcode PDFs if required.

Basic usage:
    generator = Barcode()
    generator.generate_barcode("Barcode")

"""

import os

import PyPDF3
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class Barcode:
    """Generate a PDF document with containing a barcode"""

    def __init__(self, size=(30, 15), font_size=8, barcode_font_size=24):
        """
        :param size: length by width in mm
        :type size: tuple
        :param font_size: Size of the human readable text in pt
        :type font_size: int
        :param barcode_font_size: Size of the barcode in pt
        :type barcode_font_size: int
        """
        self._temp_path = 'barcode_temp.pdf'
        self._document = None
        self._font_size = font_size
        self._barcode_font_size = barcode_font_size
        self._pagesize = (size[0] * mm, size[1] * mm)
        pdfmetrics.registerFont(TTFont('Barcode', 'font/Code128400.ttf'))

    def _writetext(self, barcode):
        """Write the human readable section"""
        self._document.setFont("Helvetica", self._font_size)
        self._document.drawCentredString(self._pagesize[0] / 2,
                                         2 * mm,
                                         barcode
                                         )

    def _writebarcode(self, barcode):
        """Write the machine readable section"""
        self._document.setFont("Barcode", 24)
        barcode_string = f"{chr(203)}{barcode}{self._checksum(barcode)}{chr(206)}"
        self._document.drawCentredString(self._pagesize[0] / 2,
                                         5 * mm,
                                         barcode_string
                                         )

    def _checksum(self, barcodestring):
        """Calculate the checksum

        :param barcodestring: the barcode string.  Start code for code set A is assumed
        :return: the string value to put in the checksum position
        :rtype: str
        """
        char_sum = 103  # Start at 103 to assume a code set A start character
        for character in enumerate(barcodestring, start=1):  # Start at 1 to for multiplier
            char_sum += (ord(character[1]) - 32) * character[0]  # ord() is pretty handy
        return chr((char_sum % 103) + 32)  # +32 to offset to ASCII

    def generate_barcode(self, barcode):
        """
        Build the barcode PDF
        :param barcode:
        :return: path to the file.  Its going to be the same, but its just convenient to pass it back
        to the add_barcode function in the AppendBarcode class
        """
        self._document = canvas.Canvas(self._temp_path, pagesize=(self._pagesize[0], self._pagesize[1]))
        self._writetext(barcode.upper())
        self._writebarcode(barcode.upper())
        self._document.showPage()
        self._document.save()
        return self._temp_path


class AppendBarcode:
    def __init__(self, save_path="."):
        """

        :param save_path: Defaults to pwd.
        """
        self.save_path = save_path
        self.barcode_doc = Barcode()
        if not os.path.exists(save_path):
            os.mkdir(save_path)

    def add_barcode(self, barcode, original_path):
        """
        Adds a barcode to the first page of a document

        :param barcode: Barcode to add to the file specified in original_path
        :param original_path: Path to the original file.
        :return:
        """
        merger = PyPDF3.PdfFileReader(original_path)
        barcode_doc = PyPDF3.PdfFileReader(self.barcode_doc.generate_barcode(barcode)).getPage(0)
        first_page = merger.getPage(0)
        centre_pos = float(first_page.mediaBox[2]) / 2 - float(barcode_doc.mediaBox[2]) / 2
        first_page.mergeTranslatedPage(barcode_doc, centre_pos, 0)
        out = PyPDF3.PdfFileWriter()
        out.addPage(first_page)
        [out.addPage(page) for page in merger.pages[1:]]
        filename = original_path[original_path.rfind('/'):original_path.rfind('.')]
        output_filename = f"{self.save_path}/{filename}_{barcode}_coded.pdf"
        with open(output_filename, 'wb') as output:
            out.write(output)


if __name__ == '__main__':
    # generator = Barcode()
    # generator.generate_barcode("TWWWWWWW")
    from string import ascii_letters
    import random
    combiner = AppendBarcode(save_path="output/")
    look_in = "pdf/"
    rand_char = lambda _: ascii_letters[random.randrange(0, stop=len(ascii_letters))]
    for filen in os.listdir(look_in):
        print(look_in + filen)
        randbarcode = "T" + "".join([rand_char(x) for x in range(0, 7)])
        combiner.add_barcode(randbarcode, look_in + filen)
    os.remove("barcode_temp.pdf")
