def test_initialize_server():
    pass


def test_status():
    pass


def test_validate_server_input():
    from final_project_server import validate_server_input
    keys = {"name": str, "mrn": int, "latest_hr": int, "ECG_img": str,
            "medical_img": str, "time_stamp": str}
    test_data1 = "Hello"
    test_data2 = {"name": "Thomas",
                  "mrn": 1,
                  "latest_hr": 100,
                  "ECG_img": "",
                  "medical_img": "IMG",
                  "time_stamp": "Time"}
    test_data3 = {"mrn": 1,
                  "latest_hr": 100,
                  "ECG_img": "",
                  "medical_img": "IMG",
                  "time_stamp": "Time"}
    test_data4 = {"name": 1,
                  "mrn": 1,
                  "latest_hr": 100,
                  "ECG_img": "",
                  "medical_img": "IMG",
                  "time_stamp": "Time"}

    answer1 = validate_server_input(test_data1, keys)
    answer2 = validate_server_input(test_data2, keys)
    answer3 = validate_server_input(test_data3, keys)
    answer4 = validate_server_input(test_data4, keys)
    expected1 = "The input was not a dictionary.", 400
    expected2 = True, 200
    expected3 = "The key name is missing from input", 400
    expected4 = "The key name has the wrong data type", 400
    assert answer1 == expected1
    assert answer2 == expected2
    assert answer3 == expected3
    assert answer4 == expected4
