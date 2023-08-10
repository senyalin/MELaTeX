from PyPDF2 import PdfFileMerger as PdfMerger
import os

for i,file_name in enumerate(os.listdir("test_files")):
    merger = PdfMerger()
    temp = []
    for page in os.listdir("test_files/"+file_name+"/"+file_name):
        if not page.endswith("_7_step.pdf"):
            continue
        temp.append((page,int(page.split("_")[1].split(".")[0].removeprefix("p"))))
    temp.sort(key=lambda i:i[1])
    for i in temp:
        merger.append("test_files/"+file_name+"/"+file_name+"/"+i[0])
    merger.write("extracted/{}.pdf".format(file_name))
    merger.close()
        