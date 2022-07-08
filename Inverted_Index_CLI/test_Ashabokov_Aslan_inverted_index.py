"""
Tests for Inverted Index module

"""

from collections import defaultdict
import json
from argparse import Namespace

import pytest

from task_Ashabokov_Aslan_inverted_index import InvertedIndex, \
    StoragePolicy, JsonPolicy, load_documents, build_inverted_index, \
        callback_query, callback_build, setup_parser


SAMPLE_DATASET_PATH = "sample.txt"
SMALL_DATASET_PATH = "small_dataset.txt"
TINY_DATASET_PATH = "tiny_dataset.txt"
STRUCT_INDEX_PATH = "struct_inverted_index.txt"
JSON_INVERTED_INDEX = "json_inverted_index.txt"


def test_load_documents_invalid_path_name():
    """Test load_documents with invalid file path"""

    invalid_path = "some/invalid/path"
    with pytest.raises(FileNotFoundError):
        load_documents(invalid_path)


def test_load_documents_read_invalid_data(tmp_path):
    """Test load documents with invalid input data"""

    invalid_data = 'input string 1\n1 input_string 2\n\t3 input string 3\n\t4\tinput 5\n'
    invalid_data_path = tmp_path / "invalid_data.txt"

    with open(invalid_data_path, 'w') as file:
        file.write(invalid_data)

    with pytest.raises(ValueError):
        load_documents(invalid_data_path)

    invalid_data = "1\tsome text\na\tsome text\n"

    with open(invalid_data_path, 'w') as file:
        file.write(invalid_data)

    with pytest.raises(ValueError):
        load_documents(invalid_data_path)


def test_load_documents_read_valid_data(tmp_path):
    """Test load documents with valid input data"""

    valid_data = "1\tfirst text line\n2\tsecond text line\n3\tthird text line\n"
    valid_data_path = tmp_path / "valid_data.txt"
    valid_result = {
        1: "first text line",
        2: "second text line",
        3: "third text line"
    }

    with open(valid_data_path, 'w') as file:
        file.write(valid_data)

    result = load_documents(valid_data_path)

    assert result == valid_result, (
        f"Result must be: {valid_result}\nGot: {result}\n"
    )

def test_setup_parser():
    """Test setup_parser function"""

    setup_parser()

# build_inverted_index tests

def test_build_inverted_index_correct_result_type():
    """Test build if it creates InvertedIndex"""

    data_dict = {
        1: "first text line",
        2: "second text line",
        3: "third text line"
    }
    result = build_inverted_index(data_dict)

    assert isinstance(result, InvertedIndex), (
        f"result must be type of {type(InvertedIndex)}\nGot: {type(result)}"
    )

def test_build_inverted_index_empty_input():
    """Test build with empty input dict"""

    empty_dict = {}
    result = build_inverted_index(empty_dict)

    assert result.data_ == empty_dict, (
        f"result.data_ must be empty dict\nGot: {result.data_}"
    )

def test_build_inverted_index_invalid_input():
    """Test build with invalid input data"""

    invalid_data = {
        '1': 'aa',
        '2': 'asdcd',
        '3': "wefwer"
    }

    with pytest.raises(ValueError):
        build_inverted_index(invalid_data)

    invalid_data = {
        1: 1,
        2: 2,
        3: 3
    }

    with pytest.raises(ValueError):
        build_inverted_index(invalid_data)

def test_build_inverted_index_valid_input():
    """Test build with valid input data"""
    valid_input = {
        1: "first text line",
        2: "second text line",
        3: "third text line"
    }
    valid_output = {
        'first': [1],
        'text': [1, 2, 3],
        'line': [1, 2, 3],
        'second': [2],
        'third': [3]
    }
    result = build_inverted_index(valid_input)
    is_result_valid = True

    for key in result.data_:
        if key not in valid_output:
            is_result_valid = False

    for key in valid_output:
        if key not in result.data_:
            is_result_valid = False

    if is_result_valid:
        for key in valid_output:
            valid_lst = valid_output[key]
            result_lst = result.data_[key]

            for item in valid_lst:
                if item not in result_lst:
                    is_result_valid = False

            for item in result_lst:
                if item not in valid_lst:
                    is_result_valid = False

    assert is_result_valid, (
        f"result.data_ must be: {valid_output}\nGot: {result.data_}\n"
    )

# InvertedIndex.__init__ test

def test_init_type_error():
    """Test InvertedIndex init with wrong type input"""

    with pytest.raises(TypeError):
        InvertedIndex("dict")

def test_init_value_error():
    """Test InvertedIndex init with invalid input data"""

    invalid_dict = {
        1: "asad",
        2: "asdasedc"
    }

    with pytest.raises(ValueError):
        InvertedIndex(invalid_dict)

    invalid_dict = {
        "asdasdf": 1,
        'sdfdsf': 4
    }

    with pytest.raises(ValueError):
        InvertedIndex(invalid_dict)

# InvertedIndex.dump tests

def test_dump_invalid_path_name():
    """Test dump to json with invalid path"""

    file_path = "some/invalid/path"
    valid_dict = {
        'a': [1],
        'b': [2, 3]
    }
    valid_dict = defaultdict(list, valid_dict)
    inverted_index = InvertedIndex(valid_dict)

    with pytest.raises(FileNotFoundError):
        inverted_index.dump(file_path)

def test_dump_valid_data_to_json(tmp_path):
    """Test dump to json with valid data"""

    file_path = tmp_path / "inverted.index"
    valid_dict = {
        'a': [1],
        'b': [2, 3]
    }
    valid_dict = defaultdict(list, valid_dict)
    inverted_index = InvertedIndex(valid_dict)
    inverted_index.dump(file_path)

    with open(file_path, 'r') as file:
        dumped_data = json.load(file)

    assert dumped_data == valid_dict, (
        f"Valid data: {valid_dict}\nGot: {dumped_data}\n"
    )

# InvertedIndex.load tests

def test_load_invalid_path_name():
    """Test load with invalid path"""

    invalid_path = "some/invalid/path"
    with pytest.raises(FileNotFoundError):
        InvertedIndex.load(invalid_path)

def test_load_read_invalid_json(tmp_path):
    """Test load with invalid json"""

    file_path = tmp_path / "invalid.json"
    invalid_data = "sdjfkjsd"

    with open(file_path, 'w') as file:
        file.write(invalid_data)

    with pytest.raises(ValueError):
        InvertedIndex.load(file_path)

def test_load_read_empty_dict(tmp_path):
    """Test load with empy json"""

    empty_dict_path = tmp_path / "empty_dict.json"
    empty_dict_path.touch()
    with open(empty_dict_path, 'w') as file:
        json.dump({}, file)

    result = InvertedIndex.load(empty_dict_path)

    assert len(result.data_) == 0, (
        f"result must be empty dict. Got: {result.data_}\n"
    )

def test_load_read_invalid_dict_from_json(tmp_path):
    """Test load with invalid data from json"""

    invalid_data_path = tmp_path / "invalid_dict.json"
    invalid_data_path.touch()
    invalid_dict = {
        'a': ['a', 'b', 'c'],
        'b': None
    }

    with open(invalid_data_path, 'w') as file:
        json.dump(invalid_dict, file)

    with pytest.raises(Exception):
        InvertedIndex.load(invalid_data_path)

def test_load_result_type_from_json(tmp_path):
    """Test load function output from json"""

    valid_data_path = tmp_path / "valid_dict.json"
    valid_data = {
        'a': [1, 2, 3],
        'abc': [5, 1, 19]
    }
    valid_data = defaultdict(list, valid_data)

    with open(valid_data_path, 'w') as file:
        json.dump(valid_data, file)

    result = InvertedIndex.load(valid_data_path)

    assert isinstance(result, InvertedIndex), (
        f"Result must be type of InvertedIndex\nGot: {type(result)}\n"
    )
    assert valid_data == result.data_, (
        f"Result.data_ must be: {valid_data}\nGot: {result.data_}"
    )

# InvertedIndex.query tests

def test_query_invalid_input():
    """Test query with invalid input"""

    valid_data = {
        'a': [1, 2, 3],
        'abc': [5, 1, 19]
    }
    inverted_index = InvertedIndex(valid_data)
    invalid_input = "ewdfewf"

    with pytest.raises(TypeError):
        inverted_index.query(invalid_input)

    invalid_input = [1, 2, 3, None]

    with pytest.raises(TypeError):
        inverted_index.query(invalid_input)

    invalid_input = ['a', 'b', None]

    with pytest.raises(TypeError):
        inverted_index.query(invalid_input)

def test_query_valid_input():
    """Test query with valid input data"""

    valid_data = {
        'a': [1, 2, 3],
        'abc': [5, 1, 2],
        'c': [2, 6, 3]
    }
    inverted_index = InvertedIndex(valid_data)

    assert  len(set(inverted_index.query([]))) == 0
    assert len(set([1, 2, 3]).symmetric_difference(inverted_index.query(['a']))) == 0
    assert len(set([1, 2]).symmetric_difference(inverted_index.query(['a', 'abc']))) == 0
    assert len(set([2, 3]).symmetric_difference(inverted_index.query(['a', 'c']))) == 0
    assert len(set([2]).symmetric_difference(inverted_index.query(['abc', 'c', 'a']))) == 0

# tests

def test_full():
    """Full test"""

    filename = SAMPLE_DATASET_PATH
    dump_name = JSON_INVERTED_INDEX
    documents = load_documents(filename)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(dump_name)
    inverted_index = InvertedIndex.load(dump_name)
    document_ids = inverted_index.query(["two", "words"])
    result = set()
    assert len(result.symmetric_difference(set(document_ids))) == 0, (
        "full test 1 failed\n"
    )
    document_ids = inverted_index.query(["text", "line"])
    result = set([5, 7])
    assert len(result.symmetric_difference(document_ids)) == 0, (
        "full test 2 failed\n"
    )
    document_ids = inverted_index.query(["something", "else"])
    result = set([78])
    assert len(result.symmetric_difference(document_ids)) == 0, (
        "full test 3 failed\n"
    )
    document_ids = inverted_index.query(["something", "ggvp"])
    result = set([])
    assert len(result.symmetric_difference(document_ids)) == 0, (
        "full test 4 failed\n"
    )

def test_compare_objects():
    """Tests for InvertedIndex.__eq__() and InvertedIndex.__ne__()"""

    filename = "sample.txt"
    inverted_index_1 = build_inverted_index(load_documents(filename))
    inverted_index_2 = build_inverted_index(load_documents(filename))

    with pytest.raises(NotImplementedError):
        assert inverted_index_1 != {}, (
            f"inverted_index_1 must not be equal to {dict()}"
        )

    assert inverted_index_1 == inverted_index_2, (
        f"inverted_index_1 {inverted_index_1} must be equal to inverted_index_2\
            {inverted_index_2}\n"
    )

    assert not (inverted_index_1 != inverted_index_2), (
        f"inverted_index_1 {inverted_index_1} must not be not equal to inverted_index_2\
            {inverted_index_2}\n"
    )

    inverted_index_2.data_["first"].append(13)

    assert inverted_index_1 != inverted_index_2, (
        f"inverted_index_1 {inverted_index_1} must not be equal to inverted_index_2\
            {inverted_index_2}\n"
    )

    assert not (inverted_index_1 == inverted_index_2), (
        f"inverted_index_1 {inverted_index_1} must be not equal to inverted_index_2\
            {inverted_index_2}\n"
    )

    assert inverted_index_1 != inverted_index_2, (
        f"inverted_index_1 {inverted_index_1} must not be equal to inverted_index_2\
            {inverted_index_2}\n"
    )

    inverted_index_2.data_["ggg"] = [4, 5, 6]

    assert not (inverted_index_1 == inverted_index_2), (
        f"inverted_index_1 {inverted_index_1} must be not equal to inverted_index_2\
            {inverted_index_2}\n"
    )

def test_eq_for_inverted_index_objects(tmp_path):
    """Test for loading from dump"""

    filename = "sample.txt"
    dump_filename = tmp_path / "dump.index"

    inverted_index = build_inverted_index(load_documents(filename))
    inverted_index.dump(dump_filename)
    inverted_index_after_load = InvertedIndex.load(dump_filename)

    assert inverted_index_after_load == inverted_index, (
        f"InvertedIndex.load(build_inverted_index(load_documents(...)).dump()) must be\
            same as build_inverted_index(load_documents(...))\n\
                Got:\n\
                    - before dump: {inverted_index}\n\
                        - after load: {inverted_index_after_load}\n"
    )

def test_repr_and_str():
    """Test for InvertedIndex.__repr__() and InvertedIndex.__str__()"""
    filename = "sample.txt"
    inverted_index = build_inverted_index(load_documents(filename))

    assert isinstance(str(inverted_index), str), (
        f"InvertedIndex.__str__() must be type of {type(str)}\n\
            Got: {type(str(inverted_index))}"
    )

    assert isinstance(inverted_index.__repr__(), str), (
        f"InvertedIndex.__repr__() must be type of {type(str)}\n\
            Got: {type(inverted_index.__repr__())}"
    )

# StoragePolicy & JsonPolicy tests

def test_storage_policy_has_dump_and_load_methods():
    """Abstract class StoragePolicy must have load and dump methods"""

    test_mapping_dict = {
        'a': [1, 2, 3],
        'b': [4, 5]
    }
    StoragePolicy.dump(test_mapping_dict, "some_path")
    StoragePolicy.load("some_path")

def test_json_policy_dump(tmp_path):
    """Test dump to json with valid data"""

    file_path = tmp_path / "inverted.index"
    valid_dict = {
        'a': [1],
        'b': [2, 3]
    }
    valid_dict = defaultdict(list, valid_dict)
    JsonPolicy.dump(valid_dict, file_path)

    with open(file_path, 'r') as file:
        dumped_data = json.load(file)

    assert dumped_data == valid_dict, (
        f"Valid data: {valid_dict}\nGot: {dumped_data}\n"
    )

def test_json_policy_load(tmp_path):
    """Test load from json with valid data"""

    file_path = tmp_path / "inverted.index"
    valid_dict = {
        'a': [1],
        'b': [2, 3]
    }
    valid_dict = defaultdict(list, valid_dict)

    with open(file_path, 'w') as file:
        json.dump(valid_dict, file)

    inverted_index = JsonPolicy.load(file_path)

    assert inverted_index.data_ == valid_dict, (
        f"Valid data: {valid_dict}\nGot: {inverted_index}\n"
    )

# Arguments parsing tests

@pytest.mark.parametrize(
    "dataset_path",
    [
        SMALL_DATASET_PATH,
        TINY_DATASET_PATH,
    ],
)
def test_dump_to_struct_and_load_from_struct(tmp_path, dataset_path):
    """Test dump in binary format"""

    dump_path_name = tmp_path / "inverted.index"
    documents = load_documents(dataset_path)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(dump_path_name, method='struct')
    loaded_inverted_index = InvertedIndex.load(dump_path_name, method='struct')

    assert inverted_index == loaded_inverted_index

@pytest.mark.parametrize(
    "namespace",
    [
        Namespace(
            callback=callback_query,
            command='query',
            index=STRUCT_INDEX_PATH,
            query_input=['text', 'some', 'first', 'second text'],
            strategy='struct',
        ),
        Namespace(
            callback=callback_build,
            command='build',
            dataset_filename='tiny_dataset.txt',
            output_filename='inverted_index.txt',
            strategy='struct',
        )
    ]
)
def test_callbacks(namespace: Namespace):
    """Test query callbeck with specific arguments"""

    namespace.callback(namespace)
