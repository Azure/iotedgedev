import json


def assert_list_equal(list1, list2):
    assert len(list1) == len(list2) and sorted(list1) == sorted(list2)


def assert_json_file_equal(file1, file2):
    with open(file1, "r") as f1:
        with open(file2, "r") as f2:
            assert json.load(f1) == json.load(f2)
