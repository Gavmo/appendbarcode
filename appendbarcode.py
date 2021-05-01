"""
Add a barcode to a pdf

"""

import os

import PyPDF3
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class Barcode:
    """Generate a PDF document with containing a barcode"""

    def __init__(self, size=(50, 20), fontsize=8):
        """
        :param size: length by width in mm
        :type size: tuple
        :param fontsize: Size of the human readable section
        :type fontsize: int
        """
        self._temp_path = 'barcode_temp.pdf'
        self._document = None
        self._fontsize = fontsize
        self._pagesize = size
        pdfmetrics.registerFont(TTFont('Barcode', 'font/Code128400.ttf'))

    def _writetext(self, barcode):
        """Write the human readable section"""
        self._document.setFont("Helvetica", self._fontsize)
        self._document.drawString(self._pagesize[0],
                                  self._pagesize[1] / 2,
                                  barcode
                                  )

    def _writebarcode(self, barcode):
        """Write the machine readable section"""
        self._document.setFont("Barcode", 24)
        barcode_string = f"{chr(203)}{barcode}{self._checksum(barcode)}{chr(206)}"
        self._document.drawString(self._pagesize[0] / 2,
                                  self._pagesize[1] - 2,
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
        :return:
        """
        self._document = canvas.Canvas(self._temp_path, pagesize=(self._pagesize[0] * mm, self._pagesize[1] * mm))
        self._writetext(barcode.upper())
        self._writebarcode(barcode.upper())
        self._document.showPage()
        self._document.save()
        return self._temp_path


class AppendBarcode:
    def __init__(self, save_path="."):
        """

        """
        self.save_path = save_path
        self.barcode_doc = Barcode()
        if not os.path.exists(save_path):
            os.mkdir(save_path)

    def add_barcode(self, barcode, original_path):
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
    # generator.generate_barcode("T0S0ABCD")
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
