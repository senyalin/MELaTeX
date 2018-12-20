# This is the web portal for pdfxml convertor 
* Convert any PDF file to document XML.
* the files ending with web means sub module
* the files ending with util is to support other functions.

# Step to deploy the web portal
1. install the python 2.7 on your system
2. check out this repository to a project directory
3. add the project directory to the environemnt variable PYTHONPATH
4. install the followings python packages:
   * intervaltree 2.1.0
   * Whoosh 2.7.4
   * celery 4.2.0rc2
5. put the file "me.xlsx" under "C:/pdfxml_data/InftyCDB-1/resources"
6. download the dataset from http://www.inftyproject.org/download/inftydb/InftyCDB-1.zip for training the layout module
   * put the images ".png" under "C:/pdfxml_data/InftyCDB-1/Images"
7. nevigate to the website directory and run "python main.py"
8. use http://{service_ip}:{service_port}/nlp/get_pub_xml to retrieve .xml for a given .pdf
