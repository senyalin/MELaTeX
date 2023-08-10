from tools.class_define import Char, Chunk, Chunk
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from setting import FILE_NAME,DRAW_MODE

def draw_list_of_char(target:list[Char],name:str,existing_pdf:PdfFileReader):
    print("drawwww")
    # if DRAW_MODE == False:
    #     return
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    for char in target:
        char.draw_can(can)
    can.save()
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    output = PdfFileWriter()
    page = existing_pdf.getPage(0)
    try:
        page.mergePage(new_pdf.getPage(0))
    except:
        pass
    output.addPage(page)
    if not os.path.exists("debug/"+FILE_NAME):
        os.mkdir("debug/"+FILE_NAME)
    outputStream = open("debug/"+FILE_NAME+"/"+FILE_NAME+name+".pdf", "wb")
    output.write(outputStream)
    outputStream.close()

def draw_list_of_super_chunk(target:list[Chunk],name:str,existing_pdf:PdfFileReader):
    # if DRAW_MODE == False:
    #     return
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    for chunk in target:
        chunk.draw_can(can)
    can.save()
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    output = PdfFileWriter()
    page = existing_pdf.getPage(0)
    try:
        page.mergePage(new_pdf.getPage(0))
    except:
        pass
    output.addPage(page)
    if not os.path.exists("debug/"+FILE_NAME):
        os.mkdir("debug/"+FILE_NAME)
    outputStream = open("debug/"+FILE_NAME+"/"+FILE_NAME+name+".pdf", "wb")
    output.write(outputStream)
    outputStream.close()