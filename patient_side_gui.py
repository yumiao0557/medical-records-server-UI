import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import ecg_analysis
import requests
# from flask import jsonify
from datetime import datetime
import base64


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


blank_img = img_2_str("blank.jpg")

name = ""
ecg_path = ""
ecg_string = blank_img
med_string = blank_img
img_path = ""
mean_hr_bpm = 0
server_name = "http://vcm-23099.vm.duke.edu:5000"


def create_output(name, mrn, ecg_filename, img_filename, mean_hr_bpm):
    """Interface between GUI and server
    This function is called by the GUI command function attached to the "Ok"
    button of the GUI.  As input, it takes the data entered into the GUI.
    It creates an output string that is sent back to the GUI that is
    printed in the console. If no data was entered, the field will return
    no data for name and a blank string for all other fields.
    Args:
        name (str): patient name entered in GUI
        mrn (str): patient id (medical record number) entered in GUI
        ecg_filename (str): filename of inputted ecg data
        img_filename (str): filename of inputed image file
    Returns:
        str: a formatted string containing patient information from the
            GUI
    """
    out_string = "Patient name: {}\n".format(name)
    out_string += "Patient MRN: {}\n".format(mrn)
    out_string += "ECG File Uploaded: {}\n".format(ecg_filename)
    out_string += "Image File Uploaded: {}\n".format(img_filename)
    out_string += "Patient Heart Rate: {}\n".format(mean_hr_bpm)
    return out_string


def design_window():
    """Creates the main patient-side GUI window
    A GUI window is created that is the main interface for database.
    It accepts information from the user (patient name, patient mrn,
    an ecg data file, and an image).  Upon hitting the Ok button, this
    information is sent to the server.  Upon hitting the Cancel button,
    the window closes.
    Returns: None
    """

    def run_ecg_analysis(ecg_path):
        """ Runs ecg_analysis script
        This function runs each ecg_analysis module function and ouputs the
        calculated heart rate of the patient based on the inputted ecg data
        file.
        Args:
            ecg_path (str): file path to ecg data file selected
        Returns:
            mean_hr_bpm (float): the patient's average heart rate over the
                ecg trace
        """
        df = ecg_analysis.read_csv(ecg_path)
        duration = ecg_analysis.duration(df)
        num_beats = ecg_analysis.num_beats(df)
        mean_hr_bpm = ecg_analysis.mean_hr_bpm(num_beats, duration)
        ecg_analysis.plot_ecg(df)
        return mean_hr_bpm

    def ok_button_cmd():
        """Event to run when Ok button is pressed
        This function is connected to the "Ok" button of the GUI.  It follows
        the typical pattern for these command functions:
        1. It gets the needed information from the GUI.
        2. It calls a function external to the GUI to process the data and
        receive the results
        3. It updates the GUI based on the received results.  In this case,
        that includes printing to the console and updating a Label in the GUI.
        If no data was entered for name, it will return "no data."
        If no data was entered for ecg_path and img_path, they will each return
        a blank string "" for their filenames.
        Returns:
            out_string (str): a string that lists out all entered data in the
            GUI. Includes: name, mrn, ecg_filename, img_filename, and
            heart_rate.
        """
        # Get needed data from GUI
        name = name_data.get()

        if name == "":
            name = "_"

        mrn = mrn_data.get()

        if ecg_path != "":
            mean_hr_bpm = run_ecg_analysis(ecg_path)
            ecg_filename = os.path.basename(os.path.normpath(ecg_path))
        else:
            mean_hr_bpm = 0
            ecg_filename = "_"

        if img_path != "":
            img_filename = os.path.basename(os.path.normpath(img_path))
        else:
            img_filename = "_"

        # Call external function to do the work that can be tested
        out_string = create_output(name, mrn, ecg_filename, img_filename,
                                   mean_hr_bpm)

        # Update GUI
        print(out_string)
        output_string.configure(text=out_string)
        server_request(name, mrn, img_path, mean_hr_bpm, server_name)
        return out_string

    def cancel_cmd():
        """Closes window upon click of Cancel button
        This function is connected to the "Cancel" button of the GUI.  It
        destroys the root window causing the GUI interface to close.
        """
        root.destroy()

    def change_picture_cmd():
        """Allows user to select a new image to display
        This function opens a dialog box to allow the user to choose an image
        file.  If the user does not cancel the dialog box, the chosen filename
        is sent to an external function for opening and resizing.  The
        returned image is then added to the image_label widget for display
        on the GUI.
        returns:
            img_path (str): file path to image file
        """
        global img_path
        global med_string
        img_path = filedialog.askopenfilename(initialdir="images")
        print(img_path)
        if img_path == "":
            messagebox.showinfo("Cancel", "You cancelled the image load")
            return
        med_string = img_2_str(img_path)
        tk_image, _, _ = load_and_resize_image(img_path)
        image_label.configure(image=tk_image)
        image_label.image = tk_image  # Stores image as part of widget to
        # prevent garbage collection and loss of image
        return img_path

    def change_ecg_cmd():
        """Allows user to select an ecg data file to upload
        This function opens a dialog box to allow the user to choose an ecg
        file.  If the user does not cancel the dialog box, the chosen filename
        is displayed in the GUI. Also runs run_ecg_analysis() to create an
        image of the ecg data to show the user before submitting. Image is
        shown through show_ecg_image().
        returns:
            ecg_path (str): file path to ecg data file
        """
        global ecg_path
        ecg_path = filedialog.askopenfilename(initialdir="ecg_data")
        print(ecg_path)
        if ecg_path == "":
            messagebox.showinfo("Cancel", "You cancelled the ECG data load")
            return
        ecg_filename = os.path.basename(os.path.normpath(ecg_path))
        ecg_label.configure(text="{} selected for upload".format(ecg_filename))
        ecg_label.text = ecg_filename
        run_ecg_analysis(ecg_path)
        show_ecg_image()
        return ecg_path

    def show_ecg_image():
        """ Displays ECG trace image in GUI
        This function is responsible for displaying a label and image for the
        chosen ECG data in the GUI. This is done after opening the desired
        file to be uploaded in the change_ecg_cmd function.
        Args:
            None
        Returns:
            None
        """
        # Output ECG trace image
        global ecg_string
        ecg_string = img_2_str('ecg_plot.jpg')

        ecg_image, _, _ = load_and_resize_image('ecg_plot.jpg')
        ecg_plot_label = ttk.Label(root, text="---Chosen ECG Trace---")
        ecg_plot_label.grid(column=0, row=11, padx=10, columnspan=2,
                            sticky='s')
        ecg_plot = ttk.Label(root, image=ecg_image)
        ecg_plot.grid(column=0, row=12)
        ecg_plot.configure(image=ecg_image)
        ecg_plot.image = ecg_image  # Stores image as part of widget to
        # prevent garbage collection and loss of image
        return

    # Window title
    root = tk.Tk()
    root.title("Patient-Side GUI")

    # Left column label
    top_label = ttk.Label(root, text="---Enter Patient Information---")
    top_label.grid(column=0, row=0, columnspan=2, sticky='s')

    # Patient name entry
    ttk.Label(root, text="Patient Name:").grid(column=0, row=1, sticky='w')

    name_data = tk.StringVar()
    name_entry_box = ttk.Entry(root, width=20, textvariable=name_data)
    name_entry_box.grid(column=1, row=1, sticky='w', columnspan=2)

    ttk.Label(root, text="Patient MRN:").grid(column=0, row=2, sticky='w')

    mrn_data = tk.StringVar()
    mrn_entry_box = ttk.Entry(root, width=20, textvariable=mrn_data)
    mrn_entry_box.grid(column=1, row=2, sticky='w', columnspan=2)

    # Creates a place holder for an image.
    tk_image, _, _ = load_and_resize_image("images/blank.jpg")
    pic_label = ttk.Label(root, text="---Choose Image to Upload---")
    pic_label.grid(column=3, row=0, padx=10, columnspan=2, sticky='s')
    image_label = ttk.Label(root, image=tk_image)
    image_label.grid(column=4, row=1, padx=10, pady=10, sticky='e', rowspan=2)

    # Creates a button to allow user to change the image
    change_picture_btn = ttk.Button(root, text="Choose Image",
                                    command=change_picture_cmd)
    change_picture_btn.grid(column=4, row=5)

    # ECG Data Label
    ecg_label = ttk.Label(root, text="(No file selected)")
    ecg_label.grid(column=0, row=4)

    # Creates a button to allow user to choose the ecg data to upload
    ecg_btn = ttk.Button(root, text="Choose ECG File",
                         command=change_ecg_cmd)
    ecg_btn.grid(column=0, row=6)

    # Okay button
    ok_button = ttk.Button(root, text="Ok", command=ok_button_cmd)
    ok_button.grid(column=3, row=9, padx=20, pady=20)

    cancel_button = ttk.Button(root, text="Cancel", command=cancel_cmd)
    cancel_button.grid(column=4, row=9, sticky='w')

    # This output_string will be used to display results from the server
    output_string = ttk.Label(root)
    output_string.grid(column=0, row=10)

    root.mainloop()


def load_and_resize_image(img_path):
    """ Creates a tkinter image variable that can be displayed on GUI
    This function receives a filename as a parameter.  This should be the
    name of a file containing a digital image.  The file is first open
    and stored as a Pillow image file.  It uses the Image.size property and
    Image.resize() method to decrease the image size by 50%.  It then
    converts the Pillow image to a tk image.
    Note, while this code is written to decrease the size by 50%, a better
    approach may be to determine the aspect ratio of the picture and then
    adjust its size up or down to reach a default size.
    Args:
        img_path (str): the name of the file path containing an image to be
        loaded
    Returns:
        Pillow.ImageTk.PhotoImage: a tk-compatible image variable
    """
    pil_image = Image.open(img_path)
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


def server_request(name, mrn, img_path, mean_hr_bpm, server_name):
    """ Create server post request
    This function takes all of the necessary information from the patient that
    has been entered into the GUI and sends a request to the server. The
    request is a dictionary conatining the information from create_dictionary.
    It is a driver for the functions necessary to create the server request.
    Args:
        name (str): patient name entered in GUI
        mrn (str): patient id (medical record number) entered in GUI
        img_path (str): file path to the entered image in GUI
    Returns:
        None
    """
    if img_path != "":
        b64_img_string = convert_img_to_b64_string(img_path)
    else:
        b64_img_string = "_"

    if ecg_path != "":
        b64_ecg_string = convert_ecg_to_b64_string(ecg_path)
    else:
        b64_ecg_string = "_"

    in_data = create_dictionary(name, mrn, ecg_string, med_string,
                                mean_hr_bpm)
    r = requests.post(server_name + '/new_entry', json=in_data)
    print(r.text)
    return


def convert_img_to_b64_string(img_path):
    """ Converts medical image to b64 string
    This function takes the image filepath as an input and outputs it as a b64
    string. This string can be sent to the server and then the database.
    Args:
        img_path (str): the name of the file path containing an image to be
        loaded
    Returns:
        b64_img_string (str): the image file as a b64 string
    """
    with open(img_path, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_img_string = str(b64_bytes, encoding='utf-8')
    return b64_img_string


def convert_ecg_to_b64_string(ecg_path):
    """ Converts ecg trace to b64 string
    This function takes the ecg filepath as an input and outputs it as a b64
    string. This string can be sent to the server and then the database.
    Args:
        ecg_path (str): file path to ecg plot being uploaded
    Returns:
        b64_ecg_string (str): the ecg plot image as a b64 string
    """
    path = os.path.exists(ecg_path)
    if path is False:
        b64_ecg_string = ""
        return b64_ecg_string
    with open(ecg_path, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_ecg_string = str(b64_bytes, encoding='utf-8')
    return b64_ecg_string


def create_dictionary(name, mrn, b64_ecg_string, b64_img_string, mean_hr_bpm):
    """ Creates dictionary of entered information
    This function is responsible for creating the dictionary of patient
    information entered into the GUI. This information will eventually be sent
    to the server.
    Args:
        name (str): the patient's name
        mrn (str): the patient's medical record number
        b64_ecg_string (str): the ecg plot image as a b64 string
        b64_img_string (str): the medical image as a b64 string
        mean_hr_bpm (float): the average heart rate calculated from the ecg
    Returns:
        in_data (dict): a dictionary containing the above information and a
        timestamp key and value
        Ex:
        in_data = {"name": "Thomas",
                   "mrn": "5",
                   "latest_hr": 100,
                   "ECG_img": b64_ecg_string,
                   "medical_img": b64_img_string,
                   "time_stamp": "2000-01-01 12:00:00.000"}
    """
    current_time = datetime.now()
    current_time_string = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    in_data = {"name": name,
               "mrn": int(mrn),
               "latest_hr": int(mean_hr_bpm),
               "ECG_img": b64_ecg_string,
               "medical_img": b64_img_string,
               "time_stamp": current_time_string}
    return in_data


if __name__ == '__main__':
    design_window()
