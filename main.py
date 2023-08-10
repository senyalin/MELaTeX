import xml.etree.ElementTree as ET
from tools.xml2latex import xml2latex as x2l
from PyPDF2 import PdfFileMerger as PdfMerger
from setting import FILE_NAME
import os


#one file at a time
def main():
    print("Target :",FILE_NAME)

    page = ET.parse("data/{}/{}.xml".format(FILE_NAME,FILE_NAME)).getroot()
    for formula in page:
            if formula.tag == "EmbeddedFormula":
                pass
            else :
                try:
                    temp =  x2l(formula,("data/{}/{}.pdf".format(FILE_NAME,FILE_NAME)))
                    print(temp)
                    pdfs = ["output/{}/{}_{}_.pdf".format(FILE_NAME,FILE_NAME,i) for i in range(1,4)]
                    merger = PdfMerger()
                    for pdf in pdfs:
                        merger.append(pdf)
                    merger.write("output/{}/result.pdf".format(FILE_NAME))
                    merger.close()
                    input()
                except:
                    pass

#multi file
def main2():
    fail_list = []
    for i,file_name in enumerate(os.listdir("test_files")):
        print("\n",i,"/",len(os.listdir("test_files")),"\n")
        print(file_name)
        with open("test_files/"+file_name+"/"+file_name+"result.txt", "w") as f:
            for xml_file in os.listdir("test_files/"+file_name+"/"+file_name):
                if not xml_file.endswith(".xml"):
                    continue
                page = ET.parse("test_files/"+file_name+"/"+file_name+"/"+xml_file).getroot()
                print("Start page",page.attrib['PageNum'])

                for formula in page:
                    try:
                        if formula.tag == "EmbeddedFormula":
                            pass
                        else :
                            temp =  x2l(formula,("test_files/"+file_name+"/"+file_name+"/"+xml_file).replace(".xml",".pdf"))
                            f.write(temp+"\n")
                            print(temp)
                    except:
                        print("failed")
                        fail_list.append(file_name+"/"+xml_file)
    with open("fails.txt","w") as fa:
        fa.write(str(fail_list))

#multi file
def main3():
    for test_case in os.listdir("data2"):
        with open("data2/{}/{}.txt".format(test_case,test_case)) as ans:
            with open("data2/{}/{}result.txt".format(test_case,test_case),"w") as result:
                for i,ans_line in enumerate(ans.read().split("\n")[:-1]):
                    page = ET.parse("data2/{}/{}.xml".format(test_case,i+1)).getroot()
                    print(ans_line)
                    temp = x2l(page[0],"data2/{}/{}.pdf".format(test_case,i+1))+"\n"
                    print(temp)
                    result.write(temp)

if __name__ == "__main__":
    main()


