import matplotlib

matplotlib.use('Agg')


def test_img_2_str():
    from monitoring_station_gui import img_2_str
    b64str = img_2_str("test_image.jpg")
    assert b64str[0:20] == "/9j/4AAQSkZJRgABAQEA"


def test_str_2_img():
    from monitoring_station_gui import img_2_str
    from monitoring_station_gui import str_2_img
    import filecmp
    import os
    b64str = img_2_str("test_image.jpg")
    str_2_img(b64str, "test_image_output.jpg")
    answer = filecmp.cmp("test_image.jpg",
                         "test_image_output.jpg")
    # os.remove("test_image_output.jpg")
    assert answer


def test_load_and_resize_image():
    from PIL import Image, ImageTk
    from monitoring_station_gui import load_and_resize_image
    new_width, new_height = load_and_resize_image("test_image.jpg")
    test_width = 320
    test_height = 240
    assert test_height == new_height
    assert test_width == new_width


def test_time_stamps_manipulation():
    from monitoring_station_gui import time_stamps_manipulation
    test_time_stamps = time_stamps_manipulation('"[{time_stamps: 2021-02-04 '
                                                '12:03:05}, '
                                                '{time_stamps: 2021-02-07 '
                                                '12:03:12}]"')
    answer = ['{time_stamps: 2021-02-04 12:03:05}', ' {time_stamps: '
                                                    '2021-02-07 12:03:12}']
    assert test_time_stamps == answer
