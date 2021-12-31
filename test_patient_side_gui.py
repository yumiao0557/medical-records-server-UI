from datetime import datetime
from datetime import timedelta


# from datetime import timedelta


def test_create_output():
    from patient_side_gui import create_output
    test_name = 'Thomas'
    test_mrn = '1'
    test_ecg_filename = 'ecg1.xls'
    test_image_filename = 'knee.jpg'
    test_mean_hr_bpm = 100.1
    answer = create_output(test_name, test_mrn, test_ecg_filename,
                           test_image_filename, test_mean_hr_bpm)
    expected = "Patient name: Thomas\n"
    expected += "Patient MRN: 1\n"
    expected += "ECG File Uploaded: ecg1.xls\n"
    expected += "Image File Uploaded: knee.jpg\n"
    expected += "Patient Heart Rate: 100.1\n"
    assert answer == expected


def test_create_dictionary():
    from patient_side_gui import create_dictionary
    test_name = 'Thomas'
    test_mrn = '1'
    test_ecg_string = ""
    test_img_string = "IMG"
    test_mean_hr_bpm = 100.1
    answer = create_dictionary(test_name, test_mrn, test_ecg_string,
                               test_img_string, test_mean_hr_bpm)
    current_time = datetime.now()
    current_time_string = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    expected = {"name": "Thomas",
                "mrn": 1,
                "latest_hr": 100,
                "ECG_img": "",
                "medical_img": "IMG",
                "time_stamp": current_time_string}
    assert answer["name"] == expected["name"]
    assert answer["mrn"] == expected["mrn"]
    assert answer["latest_hr"] == expected["latest_hr"]
    assert answer["ECG_img"] == expected["ECG_img"]
    assert answer["medical_img"] == expected["medical_img"]
    ans_time_dt = datetime.strptime(answer["time_stamp"],
                                    "%Y-%m-%d %H:%M:%S.%f")
    exp_time_dt = datetime.strptime(expected["time_stamp"],
                                    "%Y-%m-%d %H:%M:%S.%f")
    assert ans_time_dt <= exp_time_dt + timedelta(minutes=1)


def test_load_and_resize_image():
    from monitoring_station_gui import load_and_resize_image
    new_width, new_height = load_and_resize_image("test_image.jpg")
    test_width = 320
    test_height = 240
    assert test_height == new_height
    assert test_width == new_width


def test_img_2_str():
    from patient_side_gui import img_2_str
    b64str = img_2_str("test_image.jpg")
    assert b64str[0:20] == "/9j/4AAQSkZJRgABAQEA"


def test_convert_img_to_b64_string():
    from patient_side_gui import convert_img_to_b64_string
    b64str = convert_img_to_b64_string("test_image.jpg")
    assert b64str[0:20] == "/9j/4AAQSkZJRgABAQEA"


def test_convert_ecg_to_b64_string():
    from patient_side_gui import convert_ecg_to_b64_string
    test_ecg_path1 = "photos/fake_ecg.jpg"
    test_ecg_path2 = 'test_image.jpg'
    answer1 = convert_ecg_to_b64_string(test_ecg_path1)
    expected1 = ""
    answer2 = convert_ecg_to_b64_string(test_ecg_path2)
    expected2 = "/9j/4AAQSkZJRgABAQEA"
    assert answer1 == expected1
    assert answer2[0:20] == expected2
