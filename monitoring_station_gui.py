import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from tkinter.messagebox import showinfo
# import pymodm
import ssl
from pymodm import connect, MongoModel, fields
import pymongo
from datetime import datetime
import time
from IPython.display import Image as Img
import base64
import io
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
import ast
import requests
import json

server_name = "http://vcm-23099.vm.duke.edu:5000"

ecg_path = "No file selected"
img_path = "No file selected"
mean_hr_bpm = "No ECG file selected"


class User(MongoModel):
    """Create the fields for database

    Creating fields for name, mrn, latest_hr, ECG_img, time_stamp
    and medical_img for database savings

    :param MongoModel: save this as mongoDB model
    """
    name = fields.CharField()
    mrn = fields.IntegerField()
    latest_hr = fields.IntegerField()
    ECG_img = fields.CharField()
    time_stamp = fields.CharField()
    medical_img = fields.CharField()


def img_2_str(filename):
    """Change the image file to string

    Load csv data from test_data files and will be transformed from
    pandas form into python general list of variables.

    :param filename: the file found locally
    :returns:
        - b64_string - the transferred string from image file
    """
    with open(filename, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')
    return b64_string


def str_2_img(b64_string, new_filename):
    """Change the string to image file

    Load string from local or server database and change it to image file and
    save it locally.

    :param b64_string: the string of the image file
    :param new_filename: the saving file name of the image
    """
    image_bytes = base64.b64decode(b64_string)
    with open(new_filename, "wb") as out_file:
        out_file.write(image_bytes)


def design_window():
    """Creates the main monitoring station GUI window

    A GUI window is created that is the main interface for database.
    It accepts information from the server (patient name, patient mrn,
    an ecg data file, and an image).
    """

    def save_selected_img():
        """Save the image by the dialog box

        The function will save a JPG image based on the string provided. The
        string is expected to be the selected ECG image file.
        """
        filename = filedialog. \
            asksaveasfilename(defaultextension=".jpg",
                              filetypes=(("JPG file", "*.jpg"),
                                         ("All Files", "*.*")),
                              initialdir=os.getcwd())
        if filename == "":
            return
        save_latest_img_string = img_selected
        # print(save_latest_img_string)
        image_bytes = base64.b64decode(save_latest_img_string)
        with open(filename, "wb") as out_file:
            out_file.write(image_bytes)

    def save_latest_img():
        """Save the image by the dialog box

        The function will save a JPG image based on the string provided. The
        string is expected to be the latest ECG image file.
        """
        filename = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                filetypes=(("JPG file",
                                                            "*.jpg"),
                                                           ("All Files",
                                                            "*.*")),
                                                initialdir=os.getcwd())
        if filename == "":
            return
        save_latest_img_string = img_latest
        # print(save_latest_img_string)
        image_bytes = base64.b64decode(save_latest_img_string)
        with open(filename, "wb") as out_file:
            out_file.write(image_bytes)

    def save_medical_img():
        """Save the image by the dialog box

        The function will save a JPG image based on the string provided. The
        string is expected to be the selected medical image file.
        """
        filename = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                filetypes=(("JPG file",
                                                            "*.jpg"),
                                                           ("All Files",
                                                            "*.*")),
                                                initialdir=os.getcwd())
        if filename == "":
            return
        save_medical_img_string = img_medical
        # print(save_medical_img_string)
        image_bytes = base64.b64decode(save_medical_img_string)
        with open(filename, "wb") as out_file:
            out_file.write(image_bytes)

    root = tk.Tk()
    root.title("Monitor Station GUI")
    root.geometry("1000x1000")

    canvas = tk.Canvas(root, width=100, height=100, background="grey")
    canvas.pack(expand=1, fill=tk.BOTH)

    top_label = ttk.Label(canvas, text="---Select Patient MRN---")
    top_label.grid(column=0, row=0, sticky='w')

    mrn_label = ttk.Label(canvas, text="MRN:")
    mrn_label.grid(column=0, row=2, sticky='w')

    name_label = ttk.Label(canvas, text="Patient Name:")
    name_label.grid(column=0, row=3, sticky='w')

    hr_label = ttk.Label(canvas, text="Latest HR:")
    hr_label.grid(column=0, row=4, sticky='w')

    time_label = ttk.Label(canvas, text="Time:")
    time_label.grid(column=0, row=5, sticky='w')

    latest_ecg_img_label = ttk.Label(canvas, text="Latest ECG:")
    latest_ecg_img_label.grid(column=0, row=6, sticky='w')

    latest_ecg_img = ttk.Label(canvas, image="")
    # tk_image.image=""
    latest_ecg_img.grid(column=0, row=8,
                        padx=10, pady=10, sticky='w', rowspan=2)

    selected_ecg_img_label = ttk.Label(canvas, text="Selected ECG Image:")
    selected_ecg_img_label.grid(column=1, row=6, sticky='w')

    selected_ecg_img = ttk.Label(canvas, image="")
    selected_ecg_img.grid(column=1, row=8,
                          padx=10, pady=10, sticky='w', rowspan=2)

    medical_img_title_label = ttk.Label(canvas, text="---Select Patient "
                                                     "Medical Image---")
    medical_img_title_label.grid(column=2, row=0, sticky='w')

    medical_img_label = ttk.Label(canvas, text="Medical Image:")
    medical_img_label.grid(column=2, row=6, sticky='w')

    medical_img = ttk.Label(canvas, image="")
    # tk_image.image=""
    medical_img.grid(column=2, row=8,
                     padx=10, pady=10, sticky='w', rowspan=2)

    patient_img_data = tk.StringVar()
    combo_box_img = ttk.Combobox(canvas, textvariable=patient_img_data)
    combo_box_img.state(["readonly"])
    combo_box_img.grid(column=1, row=1, columnspan=2, sticky='w')

    patient_medical_data = tk.StringVar()
    combo_box_medical = ttk.Combobox(canvas, textvariable=patient_medical_data)
    combo_box_medical.state(["readonly"])
    combo_box_medical.grid(column=2, row=1, columnspan=2, sticky='w')

    donation_center_data = tk.StringVar()
    combo_box = ttk.Combobox(canvas, textvariable=donation_center_data)

    list_of_mrn = requests.get(server_name + "/get_mrn")
    list_of_mrn = list_of_mrn.text

    combo_box["values"] = ast.literal_eval(list_of_mrn)
    combo_box.state(["readonly"])
    combo_box.grid(column=0, row=1, sticky='w')

    history_img_label = ttk.Label(canvas,
                                  text="--Historical Images Selection--")
    history_img_label.grid(column=1, row=0, sticky='w')

    latest_ecg_img = ttk.Label(canvas)
    latest_ecg_img.grid(column=0, row=8,
                        padx=10, pady=10, sticky='w', rowspan=2)

    save_latest_button = ttk.Button(canvas,
                                    text="Save Latest Image",
                                    command=save_latest_img,
                                    state="disabled")
    save_latest_button.grid(column=0, row=7, columnspan=2, sticky='w')

    save_selected_button = ttk.Button(canvas,
                                      text="Save Selected Image",
                                      command=save_selected_img,
                                      state="disabled")
    save_selected_button.grid(column=1, row=7,
                              columnspan=2, sticky='w')

    save_medical_button = ttk.Button(canvas,
                                     text="Save Medical Image",
                                     command=save_medical_img,
                                     state="disabled")
    save_medical_button.grid(column=2, row=7,
                             columnspan=2, sticky='w')

    def mrn_changed(event):
        """This will execute the subsequent functions after the mrn number
        has been selected

        After selecting the mrn number of the patient, it will enable
        subsequent functions including saving images, enabling selection of
        historical ECG images, and selection of medical images.

        :param event: the selection event of mrn drop box
        """

        def clock():
            """This is the refreshing function for the GUI window.

            It will refresh the GUI by checking with the server to make sure
            if there is new data/image uploaded onto the database. It will
            automatically replace the old ECG image with the latest one if
            exists. The refreshing rate is 1 second.
            """
            mrn = combo_box.get()

            get_name = requests.get(server_name + "/get_one/{}".format(mrn))
            patient_name = get_name.text
            name_label.configure(text="Patient Name:{}"
                                 .format(patient_name))

            get_latest_time = requests.get(
                server_name + "/get_latest_time/{}".format(mrn))
            latest_time = get_latest_time.text
            time_label.configure(text="Latest Time:{}"
                                 .format(latest_time))

            get_hr = requests.get(server_name + "/get_hr/{}".format(mrn))
            patient_hr = get_hr.text
            hr_label.configure(text="Latest HR:{}"
                               .format(patient_hr))

            img_name_latest = requests.get(
                server_name + "/show_image_latest/{}".format(mrn))
            img_latest = requests.get(
                server_name + "/show_image_latest_element/{}".format(mrn))
            img_latest = img_latest.text
            img_name_latest = img_name_latest.text
            str_2_img(img_latest, img_name_latest)
            tk_image1, _, _ = load_and_resize_image(img_name_latest)
            tk_image1.image = tk_image1
            latest_ecg_img.configure(image=tk_image1)

            img_name_latest = requests.get(
                server_name + "/show_image_latest/{}".format(mrn))
            img_latest = requests.get(
                server_name + "/show_image_latest_element/{}".format(mrn))
            img_latest = img_latest.text
            img_name_latest = img_name_latest.text

            with open('test.txt', 'w') as f:
                f.write(img_latest)
            str_2_img(img_latest, img_name_latest)
            tk_image1, _, _ = load_and_resize_image(img_name_latest)
            tk_image1.image = tk_image1
            latest_ecg_img.configure(image=tk_image1)

            history_img_label = ttk.Label(canvas,
                                          text="--Historical Images "
                                               "Selection--")
            history_img_label.grid(column=1, row=0, sticky='w')

            patient_img_data = tk.StringVar()
            combo_box_img = ttk.Combobox(canvas, textvariable=patient_img_data)

            patient_medical_data = tk.StringVar()
            combo_box_medical = ttk.Combobox(canvas,
                                             textvariable=patient_medical_data)

            time_stamps = requests.get(
                server_name + "/get_time/{}".format(mrn))
            time_stamps = time_stamps.text
            time_stamps = time_stamps_manipulation(time_stamps)

            combo_box_img["values"] = time_stamps
            combo_box_img.state(["readonly"])
            combo_box_img.grid(column=1, row=1, columnspan=2, sticky='w')

            combo_box_medical["values"] = time_stamps
            combo_box_medical.state(["readonly"])
            combo_box_medical.grid(column=2, row=1, columnspan=2, sticky='w')

            def clock_history_ecg(event):
                """This will display the medical image selected based on the
                 drop box selection

                After selecting the time stamp number of the medical image,
                it will display the medical image with corresponding time
                stamp and enable the image saving button.

                :param event: the selection event of historical medical
                image drop box
                """
                global img_selected
                mrn = combo_box.get()
                patient_all_lists = requests.get(
                    server_name + "/get_img/{}".format(mrn))
                patient_all_lists = patient_all_lists.text

                patient_all_lists = json.loads(patient_all_lists)
                for data in patient_all_lists:
                    # print(data.split('"'))
                    if data["time_stamp"] == combo_box_img.get():
                        # print(data)
                        history_img = data
                img_name_selected = "selected_historical_img_mrn{}.jpg" \
                    .format(history_img["mrn"])
                img_selected = history_img["ECG_img"]
                str_2_img(history_img["ECG_img"], img_name_selected)
                # print(img_name_selected)
                tk_image2, _, _ = load_and_resize_image(img_name_selected)
                tk_image2.image = tk_image2
                selected_ecg_img.configure(image=tk_image2)

                save_selected_button.configure(state="normal")

            def clock_history_medical(event):
                """This will display the medical image selected based on the
                 drop box selection

                After selecting the time stamp number of the medical image,
                it will display the medical image with corresponding time
                stamp and enable the image saving button.

                :param event: the selection event of historical medical
                image drop box
                """
                global img_medical
                # canvas.delete("all")
                mrn = combo_box.get()
                patient_all_lists = requests.get(
                    server_name + "/get_img/{}".format(mrn))
                patient_all_lists = patient_all_lists.text

                patient_all_lists = json.loads(patient_all_lists)
                for data in patient_all_lists:
                    # print(data.split('"'))
                    if data["time_stamp"] == combo_box_medical.get():
                        # print(data)
                        history_img = data
                img_name_selected = "selected_medical_img_mrn{}.jpg" \
                    .format(history_img["mrn"])
                img_medical = history_img["medical_img"]
                # print(img_selected)
                str_2_img(history_img["medical_img"], img_name_selected)
                # print(img_name_selected)
                tk_image3, _, _ = load_and_resize_image(img_name_selected)
                tk_image3.image = tk_image3
                medical_img.configure(image=tk_image3)

                save_medical_button.configure(state="normal")

            combo_box_img.bind('<<ComboboxSelected>>', clock_history_ecg)
            combo_box_medical.bind('<<ComboboxSelected>>',
                                   clock_history_medical)

            root.after(10000, clock)  # run itself again after 10000 ms

        global img_latest
        latest_ecg_img.configure(image="")
        selected_ecg_img.configure(image="")
        medical_img.configure(image="")
        # combo_box_medical.configure(value=[])
        save_selected_button.configure(state="disabled")
        save_medical_button.configure(state="disabled")

        msg = f'You selected {combo_box.get()}!'
        showinfo(title='Result', message=msg)
        mrn = combo_box.get()
        mrn_label.configure(text="MRN:{}".format(mrn))

        # patient_list = query_by_mrn(mrn)
        get_name = requests.get(server_name + "/get_one/{}".format(mrn))
        patient_name = get_name.text
        name_label.configure(text="Patient Name:{}"
                             .format(patient_name))

        get_hr = requests.get(server_name + "/get_hr/{}".format(mrn))
        patient_hr = get_hr.text
        hr_label.configure(text="Latest HR:{}"
                           .format(patient_hr))

        get_latest_time = requests.get(
            server_name + "/get_latest_time/{}".format(mrn))
        latest_time = get_latest_time.text
        time_label.configure(text="Latest Time:{}"
                             .format(latest_time))

        img_name_latest = requests.get(
            server_name + "/show_image_latest/{}".format(mrn))
        img_latest = requests.get(
            server_name + "/show_image_latest_element/{}".format(mrn))
        img_latest = img_latest.text
        img_name_latest = img_name_latest.text
        # print(img_latest)
        # print(img_name_latest)
        # img_name_latest = img_name_latest.text
        print(img_latest)
        print(img_name_latest)
        print(type(img_latest))
        print(type(img_name_latest))

        with open('test.txt', 'w') as f:
            f.write(img_latest)

        str_2_img(img_latest, img_name_latest)
        tk_image1, _, _ = load_and_resize_image(img_name_latest)
        tk_image1.image = tk_image1
        latest_ecg_img.configure(image=tk_image1)

        history_img_label = ttk.Label(canvas,
                                      text="--Historical Images Selection--")
        history_img_label.grid(column=1, row=0, sticky='w')

        patient_img_data = tk.StringVar()
        combo_box_img = ttk.Combobox(canvas, textvariable=patient_img_data)

        patient_medical_data = tk.StringVar()
        combo_box_medical = ttk.Combobox(canvas,
                                         textvariable=patient_medical_data)

        time_stamps = requests.get(server_name + "/get_time/{}".format(mrn))
        time_stamps = time_stamps.text
        time_stamps = time_stamps_manipulation(time_stamps)

        combo_box_img["values"] = time_stamps
        combo_box_img.state(["readonly"])
        combo_box_img.grid(column=1, row=1, columnspan=2, sticky='w')

        combo_box_medical["values"] = time_stamps
        combo_box_medical.state(["readonly"])
        combo_box_medical.grid(column=2, row=1, columnspan=2, sticky='w')

        def img_changed(event):
            """This will display the ECG image selected based on the drop box
            selection

            After selecting the time stamp number of the ECG image, it will
            display the ECG image with corresponding time stamp and enable the
            image saving button.

            :param event: the selection event of historical ECG image drop box
            """
            global img_selected
            mrn = combo_box.get()
            patient_all_lists = requests.get(
                server_name + "/get_img/{}".format(mrn))
            patient_all_lists = patient_all_lists.text

            patient_all_lists = json.loads(patient_all_lists)
            for data in patient_all_lists:
                # print(data.split('"'))
                if data["time_stamp"] == combo_box_img.get():
                    # print(data)
                    history_img = data
            img_name_selected = "selected_historical_img_mrn{}.jpg" \
                .format(history_img["mrn"])
            img_selected = history_img["ECG_img"]
            str_2_img(history_img["ECG_img"], img_name_selected)
            # print(img_name_selected)
            tk_image2, _, _ = load_and_resize_image(img_name_selected)
            tk_image2.image = tk_image2
            selected_ecg_img.configure(image=tk_image2)

            save_selected_button.configure(state="normal")

        def medical_changed(event):
            """This will display the medical image selected based on the
             drop box selection

            After selecting the time stamp number of the medical image, it will
            display the medical image with corresponding time stamp and enable
            the image saving button.

            :param event: the selection event of historical medical
            image drop box
            """
            global img_medical
            # canvas.delete("all")
            mrn = combo_box.get()
            patient_all_lists = requests.get(
                server_name + "/get_img/{}".format(mrn))
            patient_all_lists = patient_all_lists.text

            patient_all_lists = json.loads(patient_all_lists)
            for data in patient_all_lists:
                # print(data.split('"'))
                if data["time_stamp"] == combo_box_medical.get():
                    # print(data)
                    history_img = data
            img_name_selected = "selected_medical_img_mrn{}.jpg" \
                .format(history_img["mrn"])
            img_medical = history_img["medical_img"]
            # print(img_selected)
            str_2_img(history_img["medical_img"], img_name_selected)
            # print(img_name_selected)
            tk_image3, _, _ = load_and_resize_image(img_name_selected)
            tk_image3.image = tk_image3
            medical_img.configure(image=tk_image3)

            save_medical_button.configure(state="normal")

        combo_box_img.bind('<<ComboboxSelected>>', img_changed)
        combo_box_medical.bind('<<ComboboxSelected>>', medical_changed)
        root.update()

        save_latest_button.configure(state="normal")
        clock()
        # root.after(1000, clock)  # run itself again after 10000 ms
        # clock()
        # root.after(1000, clock)  # run itself again after 10000 ms

    combo_box.bind('<<ComboboxSelected>>', mrn_changed)
    root.update()

    root.mainloop()


def load_and_resize_image(filename):
    """ Creates a tkinter image variable that can be displayed on GUI
    This function receives a filename as a parameter.  This should be the
    name of a file containing a digital image.  The file is first open
    and stored as a Pillow image file.  It uses the Image.size property and
    Image.resize() method to decrease the image size by 50%.  It then
    converts the Pillow image to a tk image.
    Note, while this code is written to decrease the size by 50%, a better
    approach may be to determine the aspect ratio of the picture and then
    adjust its size up or down to reach a default size.

    :param filename: the name of the file containing an image to be loaded
    :returns:
        - tk_image - a tk-compatible image variable
        - new_width - the width of the manipulated image
        - new_width - the height of the manipulated image
    """
    pil_image = Image.open(filename)
    original_size = pil_image.size
    adj_factor = 0.5
    new_width = round(original_size[0] * adj_factor)
    new_height = round(original_size[1] * adj_factor)
    resized_image = pil_image.resize((new_width, new_height))
    try:
        tk_image = ImageTk.PhotoImage(resized_image)
    except RuntimeError:
        return new_width, new_height
    return tk_image, new_width, new_height


def time_stamps_manipulation(time_stamp_text):
    """ Change the time stamps string into a standard JSON format
    This function receives the string of JSON file and convert the string
    into a standard and readable JSON file without quotation marks

    :param time_stamp_text: JSON string with quotations outside
    :returns:
        - time_stamps - the standard format of JSON string contains
                        time_stamps key
    """
    time_stamps = time_stamp_text
    time_stamps = time_stamps[0:-1]
    time_stamps = time_stamps.replace('"', "")
    time_stamps = time_stamps.replace('[', "")
    time_stamps = time_stamps.replace(']', "")
    time_stamps = time_stamps.split(",")
    return time_stamps


if __name__ == '__main__':
    design_window()
