"""
All nlp work in Java now, abandon

should have the syntactic role prediction API here

Also including services related to the
mixed ME-plaintext (MEP) analysis
"""
import time
import web

urls = (
    # advanced analytics
    '/get_pub_xml', 'get_pub_xml',
)


class get_pub_xml:
    """
    convert PDF file into Publication
    """
    def GET(self):
        return "POST only"

    def POST(self):
        """
        give the PDF file, convert to XML representation

        :return: the return is an XML file
        """
        from pdf_doc import PDFDoc
        from pdfxml.file_util import test_folder_exist_for_file_path
        from pdfxml.path_util import INTERMEDIATE_DATA_FOLDER

        d = web.input()
        print d.keys()

        #The following path stored the pdf document and its intermediate folder at server side
        pdf_path = "%s/pdf/%d-%s" % (INTERMEDIATE_DATA_FOLDER, time.time(), d['fname'])
        test_folder_exist_for_file_path(pdf_path)

        #print pdf_path
        with open(pdf_path, 'wb') as f:
            f.write(d[d['fname']])

        xml_path = "%s/xml/%d-%s.xml" % (INTERMEDIATE_DATA_FOLDER, time.time(), d['fname'][:d['fname'].rindex('.')])
        test_folder_exist_for_file_path(xml_path)
        #print xml_path

        #PDF MEExtraction Phase
        pdf_doc = PDFDoc(pdf_path)
        #print pdf_doc

        pdf_doc.export_xml(xml_path)
        content = open(xml_path).read()
        return content


app_nlp = web.application(urls, locals())

if __name__ == "__main__":
    #print os.getcwd()
    pass
