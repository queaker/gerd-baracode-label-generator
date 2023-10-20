import sys
import os
import tempfile

from fpdf import FPDF

import barcode
from barcode.writer import ImageWriter

import qrcode

DRAW_LABEL_OUTLINES = False

with tempfile.TemporaryDirectory() as path:

    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()

    # Paper Params
    # Avery Zweckform L7872-20 (A4)
    #  35,6 x 16,9 mm
    #  5 labels / row, 16 rows
    #
    #  margin:
    #   left:      11   mm
    #   top:       13,1 mm
    #  padding:
    #   horizonal: 2,5  mm
    #   vertical:  0    mm

    pdf_w       = 210.0
    pdf_h       = 297.0

    width       = 35.6
    height      = 16.9

    left_margin = 11.0
    top_margin  = 13.1
    horizonal_padding = 2.5
    vertical_padding = 0.0

    label_margin = 1.5

    columns = 5
    rows = 16

    # Label Params
    # first asn
    start_asn = 188
    asn = start_asn

    # Text Color
    pdf.set_text_color(200, 1, 20)

    # Registers at the corners
    # rect( x: float, y:float, w:float, h:float, style='')
    pdf.rect(0.0,      0.0,         10.0, 10.0)           # top left
    pdf.rect(pdf_w-10, 0.0,         10.0, 10.0)           # top right
    pdf.rect(0.0,      pdf_h-10.0,  10.0, 10.0)           # bottom left
    pdf.rect(pdf_w-10, pdf_h-10.0,  10.0, 10.0)           # bottom right

    # Print label Borders
    for column in range(columns):
        for row in range(rows):

            x = left_margin + (column * (horizonal_padding + width))
            y = top_margin + (row * (vertical_padding + height))

            # Label Outlines
            if (DRAW_LABEL_OUTLINES):
                pdf.set_draw_color(32.0, 47.0, 250.0)
                pdf.rect(x, y, width, height, 'D')
                print (column, row)

            # Human Readable text
            pdf.set_font('Helvetica', 'B', 16)
            txt = "{:05d}".format(asn)
            pdf.text(
                x + height + label_margin, 
                y + (height/2) + label_margin + 3, 
                txt)
            pdf.set_font('Helvetica', '', 7)
            pdf.text(
                x + height + label_margin, 
                y + (height/2) + label_margin - 3, 
                "ASN")

            # QR-Barcode
            barcode_content = "ASN" + txt + ""
            barcode_file = os.path.join(path, "qrcode-" + str(asn) + ".png")
            qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=0,
            )
            qr.add_data(barcode_content)
            qr.make(fit=True)

            # Render to File
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(barcode_file)

            # Add to PDF
            pdf.image(barcode_file, 
                x=x + label_margin, 
                y=y + label_margin,
                w = height - (2 * label_margin),
                h = height - (2 * label_margin) )

            # asn_barcode = barcode.get('code128', barcode_content, writer=ImageWriter())
            # barcode_file = asn_barcode.save('asn_barcode', options={'quiet_zone': 0, "write_text": False})

            # pdf.image(barcode_file, 
            #     x=x + label_margin, 
            #     y=y + label_margin,
            #     w = width - (2 * label_margin),
            #     h = 6 )

            asn += 1

    filename = "barcodes-" + str(start_asn) + "_" + str(asn-1) + ".pdf"
    pdf.output(filename,"F")

    if sys.platform.startswith("linux"):
        os.system("xdg-open " + filename)
    else:
        os.system("open " + filename)
