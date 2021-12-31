![npm](https://img.shields.io/github/followers/YuMiao329?style=flat-square)
![Github Actions Status](https://github.com/BME547-Fall2021/final-project-jimmyu/actions/workflows/pytest_runner.yml/badge.svg)
# BME 547 Final Project
## By: Jimmy Butch & Yu Miao

The purpose of this repository and program is to run a patient monitoring
that has a patient-side client/GUI, a monitoring-station client/GUI, and a server/database that
allows patient data to be uploaded and stored on the server and retrieved for ad-hoc and
continuous monitoring.

## Virtual Environment
- Please ensure this is done in a virtual environment before installing.
- A virtual environment can be created by entering 'python -m venv <venv_name>' in the command line.
- To activate your virtual environment, enter 'source <venv_name>/Scripts/activate' in the command line.
- All necessary packages can be installed by entering 'pip install -r requirements.txt' in the command line

## Required Packages:
- sphinx
- pytest
- pytest-pycodestyle
- flask
- testfixtures
- pillow
- pandas
- scipy
- matplotlib
- pymodm
- dnspython
- Ipython
- scikit-image

## Running the Program
### Patient-Side Client/GUI:
1. First, index to the repository 'final-project-jimmyu'
2. Run the server
	- You may run the server locally, but it will be running on a virtual machine (shown below)
3. To run the patient-side client, enter 'python_patient_side_gui.py' in the command line.
4. In this GUI, you may enter the following information:
	- Patient Name
	- Patient MRN (required)
	- Medical Image
	- ECG Trace File
5. To enter an ECG Trace File, hit the 'Choose ECG File' button
	- Another window will open to the 'ecg_data' folder where you can choose a file
	- All ECG Trace Files should be saved in the 'ecg_data' folder in the repository
6. To enter a medical image, hit the 'Choose Image' button
	- Another window will open to the 'images' folder where you can choose an image to upload
	- All image files should be saved to the 'images' folder in the repository
7. Hit the 'OK' button to upload the information to the database
	- The 'Cancel' button may also be hit to cancel the upload
### Monitoring Station Client/GUI:
1. First, index to the repository 'final-project-jimmyu'
2. Run the server
    - You may run the server locally, but it will be running on a virtual machine (shown below)
3. To run the monitoring station client, enter 'python monitoring_station-gui.py' in the command line
4. The monitoring station GUI window will pop up
5. First click the dropdown menu in the top left corner and select the medical record number for the patient
6. The most recent ECG image will be displayed after selection of MRN of patient
7. The second and third dropdown menus are:
   1. Historical ECG image selection menu
   2. Historical medical image selection menu
8. Select the time stamp associated with the menu options and the image will pop up under the dropdown menu widgets
9. The `Save Latest Image` will save the latest ECG image to local
10. The `Save Selected Image` will save the selected historical ECG image to local
11. The `Save Medical Image` will save the selected historical medical image to local

## API Reference Guide
### Server Hostnames:
Server Hostname: hostname = "http://vcm-23099.vm.duke.edu:5000/"
(This is the hostname for the server running on Jimmy's virtual machine)

### Flask API

The Flask API was used to create the server and send and receive information from python. Flask is a RESTful API that creates "micro-frameworks" for simple web applications. It has several functions and extensions that were used in this program. They include:

- Flask
- request
- requests
- jsonify

### Server Routes
- hostname
	- GET route to indicate if the server is running
	- When running, route will show "Server is on"
- hostname/new_entry
	- POST route to show latest entry to database
- hostname/get_mrn
	- GET route to show all unique MRNs in the database
- hostname/get_one/<mrn>
	- GET route to show the patient's name associated with the entered patient MRN
- hostname/get_hr/<mrn>
	- GET route to show the latest heart rate for the entered patient MRN
- hostname/get_latest_time/<mrn>
	- GET route to show the latest timestamp for the entered patient MRN
- hostname/get_time/<mrn>
	- GET route to show all timestamps for the entered patient MRN
- hostname/get_latest_image/<mrn>
	- GET route to show the last medical image enterd for the chosen patient MRN
- hostname/show_image_latest_element/<mrn>
	- GET route to show the latest ECG image enterd for the chosen patient MRN
- hostname/get_img/<mrn>
	- GET route to show all information for the entered patient MRN

## Database Structure
We used MongoDB to create our online database structure.
Using the MongoModel package, structure is as follows:
- name = string
- mrn = integer
- latest_hr = integer
- ECG_img = string
- medical_img = string
- time_stamp = string

Note: The ECG_img and medical_img fields are b64 strings that will be encoded and decoded by the program.

## Software License:

This program has an MIT License. All of the code is open to be edited and distributed.

## Author Information

We are both biomedical engineering Master of Engineering students at Duke University This repository we created as part of the BME 547 course

## Links
[github repository](https://github.com/BME547-Fall2021/final-project-jimmyu) \
[flask documentation](https://flask.palletsprojects.com/en/2.0.x/)