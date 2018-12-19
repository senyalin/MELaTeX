import os
import getpass
import socket
import hashlib
import shutil
import string

# basic information about the system
user_name, host_name = getpass.getuser(), socket.gethostname()
env_dict = {
    'os.name': os.name,
    'hostname': host_name,
    'username': user_name
}
print env_dict

valid_chars = "-_{}{}".format(string.ascii_letters, string.digits)
sub_folder_len = 3
PARALLEL_SIZE = 1
DPI = 300


if user_name == "senyalin":
    SHARED_FOLDER = "C:/pdfxml_data"  # if would like to map the shared folder
    PROJECT_FOLDER = "C:/Users/senyalin/Dropbox/test/pdfxml"  # Where all the python packages lie in
    INTERMEDIATE_DATA_FOLDER = "{}/tmp".format(SHARED_FOLDER)  # Hold intermediate result
    ENABLE_CID_EQUQL = ""
    ME_RESOURCE_FOLDER = "{}/me_ext/resources".format(SHARED_FOLDER)
    JAR_FOLDER = "{}/pdfbox/target".format(SHARED_FOLDER)
    gn_me_prob_path = "{}/me_ext/resources/gn_me_prob.txt".format(SHARED_FOLDER)
    # Only valid on Xing workstation for the intialization of the ME layout analysis
    infty_cdb_folder = "{}/InftyCDB-1".format(SHARED_FOLDER)
    infty_cdb_tmp_folder = "{}/{}".format(infty_cdb_folder, "tmp")
elif user_name == "user":
    SHARED_FOLDER = None  # if would like to map the shared folder
    PROJECT_FOLDER = "C:/Users/user/Dropbox/test/pdfxml"  # Where all the python packages lie in
    INTERMEDIATE_DATA_FOLDER = "{}/tmp".format(SHARED_FOLDER)  # Hold intermediate result
    ENABLE_CID_EQUQL = ""
    ME_RESOURCE_FOLDER = "{}/me_ext/resources".format(SHARED_FOLDER)
    JAR_FOLDER = "{}/pdfbox/target".format(SHARED_FOLDER)
    gn_me_prob_path = "{}/me_ext/resources/gn_me_prob.txt".format(SHARED_FOLDER)
    # Only valid on Xing workstation for the intialization of the ME layout analysis
    infty_cdb_folder = "{}/InftyCDB-1".format(SHARED_FOLDER)
    infty_cdb_tmp_folder = "{}/{}".format(infty_cdb_folder, "tmp")
else:
    #os.name != "nt"
    pass

def change2website_root():
    os.chdir("{}".format(PROJECT_FOLDER))


# -*- coding: utf-8 -*-
"""
Directories utilities
only as the prefix for other utilities
"""
def short_name(pdf_fname):
    if len(pdf_fname) > 25:
        # to solve the error of window not handling long file name

        #pdf_fname = pdf_fname[:10] + str(md5_crypt(pdf_fname))
        #tmp_str = md5_crypt.hash(pdf_fname)
        tmp_str = hashlib.md5(pdf_fname).digest()

        tmp_str = ''.join([c for c in tmp_str if c in valid_chars])
        pdf_fname = pdf_fname[:10] + tmp_str

    return pdf_fname


def get_tmp_path(pdf_path):
    """
    This tmp path only holds the pdf related files

    pdf_pdf E:/d/f.pdf,

    {ROOT_PATH}/test_tmp/f/f.pdf

    :param pdf_path:
    :return: return
    """

    #print "HOWDY!!! ", pdf_path

    pdf_path = pdf_path.replace("\\", "/")
    pdf_fname = short_name(pdf_path[pdf_path.rindex('/')+1:pdf_path.rindex('.')])
    #print "pdf_fname: ", pdf_fname
    tmp_path = "{}/pdf_cache/{}/{}.pdf".format(
        INTERMEDIATE_DATA_FOLDER,
        pdf_fname,
        pdf_fname
    )

    tmp_fold = tmp_path[:tmp_path.rindex('/')+1]
    #print "tmp_fold: ", tmp_fold
    if not os.path.exists(tmp_fold):
        #print tmp_fold
        os.makedirs(tmp_fold)
    if not os.path.isfile(tmp_path) and os.path.isfile(pdf_path):
        shutil.copy(pdf_path, tmp_path)

    #print "tmp_path: ", tmp_path
    return tmp_path


def get_fig_path(pdf_path):
    """

    :param pdf_path:
    :return:
    """
    pdf_path = pdf_path.replace("\\", "/")
    pdf_fname = pdf_path[pdf_path.rindex('/') + 1:pdf_path.rindex('.')]
    pdf_fname = short_name(pdf_fname)
    fig_path = "{}/test_fig/{}/{}/{}.pdf".format(
        INTERMEDIATE_DATA_FOLDER,
        pdf_fname[:sub_folder_len],  # to avoid too many file in one level
        pdf_fname,
        pdf_fname
    )
    fig_fold = fig_path[:fig_path.rindex('/') + 1]
    if not os.path.exists(fig_fold):
        os.makedirs(fig_fold)
    return fig_path


def get_txt_path(pdf_path):
    """

    :param pdf_path:
    :return:
    """
    tmp_pdf_path = get_tmp_path(pdf_path)
    out_path = "{}.txt".format(tmp_pdf_path)
    return out_path


def get_page_char_path(pdf_path, pid):
    """
    export the txt path from the pdf path

    :param pdf_path:
    :param pid:
    :return:
    """
    tmp_pdf_path = get_tmp_path(pdf_path)
    page_char_path = "{}.{}.txt".format(tmp_pdf_path, pid)
    #print "page_char_path: ", page_char_path
    return page_char_path


def get_font_state_path(pdf_path):
    pdf_path = pdf_path.replace("\\", "/")
    pdf_fname = short_name(pdf_path[pdf_path.rindex('/') + 1:pdf_path.rindex('.')])
    pkl_path = "{}/me_ext/{}/{}.pdf".format(
        INTERMEDIATE_DATA_FOLDER,
        pdf_fname,
        pdf_fname
    )
    pkl_fold = pkl_path[:pkl_path.rindex('/') + 1]
    if not os.path.exists(pkl_fold):
        try:
            os.makedirs(pkl_fold)
        except Exception as e:
            print e
    #print "pkl_path: ", pkl_path
    return pkl_path


def get_xml_path(pdf_path):
    """
    pdf_pdf E:/d/f.pdf,

    {ROOT_PATH}/test_xml/f/f.pdf

    :param pdf_path:
    :return:
    """
    pdf_path = pdf_path.replace("\\", "/")
    pdf_fname = short_name(pdf_path[pdf_path.rindex('/')+1:pdf_path.rindex('.')])

    #sub_folder_name = pdf_fname[:sub_folder_len]
    #while sub_folder_name.endswith('.'):
    #    sub_folder_name = sub_folder_name[:-1]

    xml_path = "{}/xml_cache/{}/{}.pdf".format(
        INTERMEDIATE_DATA_FOLDER,
        pdf_fname,
        pdf_fname
    )
    #print xml_path

    xml_fold = xml_path[:xml_path.rindex('/')+1]
    if not os.path.exists(xml_fold):
        os.makedirs(xml_fold)
    return xml_path


def get_eme_path(pdf_path, pid):
    """

    :param pdf_path:
    :param pid:
    :return:
    """
    xml_pdf_path = get_xml_path(pdf_path)
    return "{}.eme.{}.xml".format(xml_pdf_path, pid)


def get_ime_path(pdf_path, pid):
    """

    :param pdf_path:
    :param pid:
    :return:
    """
    xml_pdf_path = get_xml_path(pdf_path)
    return "{}.ime.{}.xml".format(xml_pdf_path, pid)


if __name__ == '__main__':
    pdf_path = "E:/MyWeb/MECA/pdfxml/test/lda2vec.pdf"
    print get_tmp_path(pdf_path)
    print get_font_state_path(pdf_path)
    print get_page_char_path(pdf_path, 0)
    print get_xml_path(pdf_path)

