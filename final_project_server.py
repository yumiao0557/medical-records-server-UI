import pymodm.errors
from flask import Flask, request, jsonify
from pymodm import connect, MongoModel, fields
import ssl
import base64
import ssl
import pymongo
import pandas as pd
from ecg_analysis import read_csv
import io
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
# from skimage.io import imsave
from datetime import datetime
import os.path
import requests

app = Flask(__name__)

clt = pymongo.MongoClient("mongodb+srv://ym168:My3970151@bme547.zftiu.mongodb."
                          "net/monitor_station?retryWrites=true&w=majority",
                          ssl_cert_reqs=ssl.CERT_NONE)

lists = []


class User(MongoModel):
    name = fields.CharField()
    mrn = fields.IntegerField()
    latest_hr = fields.IntegerField()
    ECG_img = fields.CharField()
    medical_img = fields.CharField()
    time_stamp = fields.CharField()


def str_2_img(b64_string, new_filename):
    """ Converts string to image file

    This function converts an inputted encoded string and decodes it into an
    image file that can be displayed in the GUI.
    """
    image_bytes = base64.b64decode(b64_string)
    with open(new_filename, "wb") as out_file:
        out_file.write(image_bytes)


def img_2_str(filename):
    """ Converts image to string

    This function converts an inputted image and encodes it into a b64 string
    that can be sent to the database.
    """
    with open(filename, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')
    return b64_string


def initialize_server():
    """ Initializes server conditions
    This function initializes the server log as well as creates a connection
    with the MongoDB database.  The connection string connects the user to our
    MongoDB database.
    Note:  Just because the `connect` function completes does not ensure that
    the connection was actually made.  You will need to check that data is
    successfully stored in your MongoDB database.
    Note:  This function does not need a unit test.
    """
    print("Connecting to MongoDB...")
    connect("mongodb+srv://ym168:My3970151@bme547.zftiu.mongodb.net"
            "/monitor_station?retryWrites=true&w=majority",
            ssl_cert_reqs=ssl.CERT_NONE)

    print("Connection attempt finished.")

    db = clt["monitor_station"]
    col = db["user"]
    return


@app.route("/new_entry", methods=["POST"])
def new_entry():
    """Uploads patient information to database
    This is a POST server route that takes the inputted information from the
    patient side GUI and saves it to the MongoDB database for later use.
    It makes use of the previously define MongoModel to input information in
    each field. Fields without information will be saved with the proper
    indication.
    Returns:
        (str): a string indicating which patient MRN was last updated
    """
    in_data = request.get_json()
    expected_keys = {"name": str, "mrn": int, "latest_hr": int, "ECG_img": str,
                     "medical_img": str, "time_stamp": str}
    error_string, status_code = validate_server_input(in_data, expected_keys)
    if error_string is not True:
        return error_string, status_code
    entry = User(name=in_data["name"],
                 mrn=in_data["mrn"],
                 latest_hr=in_data["latest_hr"],
                 ECG_img=in_data["ECG_img"],
                 medical_img=in_data["medical_img"],
                 time_stamp=in_data["time_stamp"])
    entry.save()
    return "Patient MRN {} Uploaded".format(in_data['mrn']), status_code


def validate_server_input(in_data, expected_keys):
    """Validates that input data to server contains a dictionary with the
    correct keys and data types
    Various routes for this server are POST requests that receive JSON-encoded
    strings which should contain dictionaries.  To avoid server errors, this
    function checks that the input data is a dictionary, that it has the
    specified keys, and specified data types.
    To specify what the needed keys and data types are, a dictionary is sent
    as a parameter to this function.  The keys of this dictionary are the
    needed keys for the input data and the value for each key is the Python
    data type that should be in the input.
    Args:
        in_data (any type): the input data to a route that has been
            deserialized from a JSON string.  Ideally, it is a dictionary.
        expected_keys (dict): a dictionary with keys matching the keys that
            should be in the input data dictionary and values of the
            corresponding data type.
    Returns:
        str or bool , int: returns True, 200 if data validation is successful.
            Returns an error message string and 400 if data validation is
            unsuccessful.
    """
    if type(in_data) is not dict:
        return "The input was not a dictionary.", 400
    for key in expected_keys:
        if key not in in_data:
            return "The key {} is missing from input".format(key), 400
        if type(in_data[key]) is not expected_keys[key]:
            return "The key {} has the wrong data type".format(key), 400
    return True, 200


@app.route("/", methods=["GET"])
def status():
    """Used to indicate that the server is running
    """
    return "Server is on"


@app.route("/get_mrn", methods=["GET"])
def get_mrn():
    """Used to get all distinct mrns in the database

    It will check with the database and get the data from "monitor_station"
    and collection from "user"

    :returns:
        - jsonify(mrns) - the string of list of distinct mrn
    """
    db = clt["monitor_station"]
    col = db["user"]
    mrns = db.user.distinct("mrn")
    return jsonify(mrns), 200


@app.route("/get_one/<mrn>", methods=["GET"])
def get_one(mrn):
    """Used to get the name based on mrn provided

    It will check with the database and get the data from "monitor_station"
    and collection from "user" to get the patient name corresponding with
    the patient mrn

    :returns:
        - name - the string of patient name
    """
    name_list = []
    db = clt["monitor_station"]
    col = db["user"]
    my_query = {'mrn': int(mrn)}
    my_list = col.find(my_query)
    for data in my_list:
        data.pop("ECG_img")
        data.pop("medical_img")
        name_list.append(data)

    sorted_list = sorted(name_list,
                         key=lambda t: datetime.strptime(t["time_stamp"],
                                                         '%Y-%m-%d %H:%M:%S.%f'
                                                         ))
    latest_name = sorted_list[-1]["name"]
    return jsonify(latest_name), 200


@app.route("/get_hr/<mrn>", methods=["GET"])
def get_hr(mrn):
    """Used to get the latest heart rate based on mrn provided

    It will check with the database and get the data from "monitor_station"
    and collection from "user" to get the patient latest heart rate
    corresponding with the patient mrn

    :returns:
        - jsonify(latest_hr) - the string of patient's latest heart rate
    """
    hr_list = []
    db = clt["monitor_station"]
    col = db["user"]
    my_query = {'mrn': int(mrn)}
    my_list = col.find(my_query)
    for data in my_list:
        data.pop("ECG_img")
        data.pop("medical_img")
        hr_list.append(data)

    sorted_list = sorted(hr_list,
                         key=lambda t: datetime.strptime(t["time_stamp"],
                                                         '%Y-%m-%d %H:%M:%S.%f'
                                                         ))
    latest_hr = sorted_list[-1]["latest_hr"]
    return jsonify(latest_hr), 200


@app.route("/get_latest_time/<mrn>", methods=["GET"])
def get_latest_time(mrn):
    """Used to get the latest time stamp based on mrn provided

    It will check with the database and get the data from "monitor_station"
    and collection from "user" to get the patient latest upload time stamp
    corresponding with the patient mrn

    :returns:
        - jsonify(latest_time) - the string of patient's latest time stamp
    """
    time_list = []
    db = clt["monitor_station"]
    col = db["user"]
    my_query = {'mrn': int(mrn)}
    my_list = col.find(my_query)
    for data in my_list:
        data.pop("ECG_img")
        data.pop("medical_img")
        time_list.append(data)
    sorted_list = sorted(time_list,
                         key=lambda t: datetime.strptime(t["time_stamp"],
                                                         '%Y-%m-%d %H:%M:%S.%f'
                                                         ))
    latest_time = sorted_list[-1]["time_stamp"]
    return jsonify(latest_time), 200


@app.route("/get_time/<mrn>", methods=["GET"])
def get_time(mrn):
    """Used to get the all time stamps based on mrn provided

    It will check with the database and get the data from "monitor_station"
    and collection from "user" to get the patient all upload time stamp
    corresponding with the patient mrn

    :returns:
        - jsonify(time_stamps) - the string of patient's all time stamp
    """
    time_stamps = []
    db = clt["monitor_station"]
    col = db["user"]
    my_query = {"mrn": int(mrn)}
    patient_all_lists = col.find(my_query)
    for data in patient_all_lists:
        time_stamps.append(data["time_stamp"])
    return jsonify(time_stamps), 200


@app.route("/show_image_latest/<mrn>", methods=["GET"])
def show_image_latest(mrn):
    """Used to get the string of the latest ECG image based on mrn provided

    It will check with the database and get the data from "monitor_station"
    and collection from "user" to get the patient latest ECG image
    corresponding with the patient mrn

    :returns:
        - img_name - the patient's latest ECG image
    """
    img_name = "latest_ecg_for_mrn{}.jpg".format(mrn)
    img_list = []
    db = clt["monitor_station"]
    col = db["user"]
    my_query = {'mrn': int(mrn)}
    my_list = col.find(my_query)
    for data in my_list:
        img_list.append(data)
    sorted_list = sorted(img_list,
                         key=lambda t: datetime.strptime(t["time_stamp"],
                                                         '%Y-%m-%d %H:%M:%S.%f'
                                                         ))
    latest_img = sorted_list[-1]["ECG_img"]
    str_2_img(latest_img, img_name)
    return img_name, 200


@app.route("/show_image_latest_element/<mrn>", methods=["GET"])
def show_image_latest_element(mrn):
    """Used to get the string of the latest ECG image based on mrn provided

    It will check with the database and get the data from "monitor_station"
    and collection from "user" to get the patient latest ECG image string
    corresponding with the patient mrn

    :returns:
        - result - the string of patient's latest ECG image
    """
    img_name = "latest_ecg_for_mrn{}.jpg".format(mrn)
    img_list = []
    db = clt["monitor_station"]
    col = db["user"]
    my_query = {'mrn': int(mrn)}
    my_list = col.find(my_query)
    for data in my_list:
        img_list.append(data)
    sorted_list = sorted(img_list,
                         key=lambda t: datetime.strptime(t["time_stamp"],
                                                         '%Y-%m-%d %H:%M:%S.%f'
                                                         ))
    latest_img = sorted_list[-1]["ECG_img"]
    # str_2_img(latest_img, img_name)

    return latest_img, 200


@app.route("/get_img/<mrn>", methods=["GET"])
def get_img(mrn):
    """Used to get the list of all JSON based on mrn provided

    It will check with the database and get the data from "monitor_station"
    and collection from "user" to get the list of all JSON corresponding
    with the patient mrn

    :returns:
        - jsonify(whole_list) - the string of the list of all JSON based on mrn
    """
    whole_list = []
    db = clt["monitor_station"]
    col = db["user"]
    my_query = {"mrn": int(mrn)}
    patient_all_lists = col.find(my_query)
    for data in patient_all_lists:
        data.pop('_id')
        whole_list.append(data)
    return jsonify(whole_list), 200


if __name__ == '__main__':
    initialize_server()
    app.run(host="0.0.0.0")
