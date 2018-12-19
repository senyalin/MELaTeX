"""
file utility
"""
import os
import codecs
import glob
import pickle
import json


#######################
#   File IO Utility   #
#######################
def get_folder_name_from_path(folder_path):
    """
    get the last chunk

    :param folder_path:
    :return:
    """
    folder_path = folder_path.replace("\\", '/')
    if folder_path.endswith("/"):
        folder_path = folder_path[:-1]
    if folder_path.count("/") > 0:
        return folder_path[folder_path.rindex('/')+1:]
    else:
        return folder_path


def get_file_name(file_path):
    """

    :param file_path:
    :return:
    """
    file_path = file_path.replace("\\", "/")
    file_name = file_path[file_path.rindex("/")+1:]
    return file_name


def get_file_name_prefix(file_path):
    """

    :param file_path:
    :return:
    """
    file_name = get_file_name(file_path)
    if '.' in file_name:
        return file_name[:file_name.rindex('.')]
    return file_name


def get_file_path_in_folder(folder_path, suffix=None):
    """

    :param folder_path:
    :param suffix:
    :return:
    """
    pattern = "{}/*".format(folder_path)
    if suffix is not None:
        pattern = "{}/*.{}".format(folder_path, suffix)
    file_path_list = []
    for file_path in glob.glob(pattern):
        file_path = file_path.replace("\\", "/")
        file_path_list.append(file_path)
    return file_path_list


def get_folder_from_path(file_path):
    """

    :param file_path:
    :return:
    """
    file_path = file_path.replace("\\", "/")
    return file_path[:file_path.rindex("/")]


def test_folder_exist_for_file_path(file_path):
    """

    :param file_path:
    :return:
    """
    folder = get_folder_from_path(file_path)
    if not os.path.isdir(folder):
        os.makedirs(folder)


def test_folder_exist(folder_path):
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)


#######################
#  Data Serialization #
#######################
def load_general(file_path):
    if file_path.endswith("json"):
        return load_json(file_path)
    elif file_path.endswith("pkl"):
        return load_serialization(file_path)
    else:
        raise Exception("unknown file extension")


def dump_general(obj, file_path):
    if file_path.endswith("json"):
        dump_json(obj, file_path)
    elif file_path.endswith("pkl"):
        dump_serialization(obj, file_path)
    else:
        raise Exception("unknown file extension for {}".format(file_path))


def load_serialization(file_path):
    if not os.path.isfile(file_path):
        raise Exception("{} file not exist".format(file_path))
    return pickle.load(open(file_path, "rb"))


def dump_serialization(obj, file_path):
    """
    write the pickle in binary mode

    :param obj: the object to write
    :param file_path: the out put path
    :return:
    """
    test_folder_exist_for_file_path(file_path)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)


def load_json(file_path):
    return json.load(open(file_path))


def dump_json(obj, file_path):
    with open(file_path, 'w') as f:
        json.dump(obj, f)


def encode2base64(data):
    return codecs.encode(pickle.dumps(data), "base64").decode()


def decode_from_base64(data):
    return pickle.loads(codecs.decode(data.encode(), "base64"))