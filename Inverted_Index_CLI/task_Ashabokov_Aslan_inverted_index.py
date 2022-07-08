#!/usr/bin/env python
"""Inverted Index CLI

Inverted Index CLI: lib for loading, storing and processing inverted index
mappings


Classes
-------
- InvertedIndex         - Class for creating, dumping, loading inverted indices.
                            Also can find document indices in inverted index using query.
- load_documents        - Function for loading and preprocessing data from dataset.
- build_inverted_index  - Function for creating inverted index based on preprocessed data.
- StoragePolicy         - Abstract class for creating dump strategy policies.
- JsonPolicy            - Class based on StrategyPolicy for saving inverted index
                            in json on disk.
- StructPolicy          - Class based on StrategyPolicy for saving inverted index
                            in binary format on disk.
- setup_parser          - Function for creating parser with command line arguments.
- parse_arguments       - Function for parsing command line arguments.
- main                  - Function for running module as command line script.


Usage (inverted-index)
----------------------
optional arguments:
  -h, --help     show this help message and exit

commands:
  {build,query}
    build        Inverted Index CLI: build: build inverted index
    query        Inverted Index CLI: query: search for query result in
                 inverted index


Usage (inverted-index build)
----------------------------
inverted_index build [-h] [--strategy {json,struct}] --dataset
                            DATASET_FILENAME [--output OUTPUT_FILENAME]

optional arguments:
  -h, --help            show this help message and exit
  --strategy {json,struct}
                        dump strategy: dump to json or dump to struct
                        (default: json)
  --dataset DATASET_FILENAME
                        path to dataset
  --output OUTPUT_FILENAME
                        output file name (default: inverted.index)


Usage (inverted-index query)
----------------------------
inverted_index query [-h] [--json-index JSON_FILENAME]
                            [--struct-index STRUCT_FILENAME] --query QUERIES
                            [QUERIES ...]

optional arguments:
  -h, --help            show this help message and exit
  --json-index JSON_FILENAME
                        Load Inverted Index CLI from json
  --index STRUCT_FILENAME
                        Load Inverted Index CLI from struct
  --query QUERIES [QUERIES ...]


Usage Examples
--------------
$ ./inverted-index.py --help

$ ./inverted-index.py build --strategy json --dataset
/path/to/dataset --output /path/to/inverted.index

$ ./inverted-index.py build --strategy struct
--dataset /path/to/dataset --output /path/to/inverted.index

$ ./inverted-index.py build --dataset /path/to/dataset
--output /path/to/inverted.index

$ ./inverted-index.py query --json-index /path/to/inverted.index
--query first query --query xxx --query the second query
"""

from __future__ import annotations, absolute_import

import os
import sys
import json
import re
import struct
from itertools import chain
from collections import defaultdict
from typing import Dict, List
from io import TextIOWrapper
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, \
    FileType, Namespace


DEFAULT_OUTPUT_FILENAME = "inverted.index"


class InvertedIndex:
    """A class for searching through inverted index

    Attributes
    ----------
    data_: dict
        contains dict of inverted indices

    Methods
    -------
    dict_check(dict)
        raises error if dict is not valid
    query(list)
        returns a list with indices
    dump(filepath)
        dumps json to file
    load(filepath)
        loads json from file
    """

    def __init__(self, inverted_index_dict: Dict[int, str] = None) -> None:
        """Create inverted index from dict (based on defaultdict)"""

        inverted_index_dict = inverted_index_dict or dict()
        self.dict_check(inverted_index_dict)
        self.data_ = defaultdict(list, inverted_index_dict)

    def __eq__(self, other: InvertedIndex) -> bool:
        """Compares two InvertedIndex objects (true if they are equal)"""

        if not isinstance(other, InvertedIndex):
            raise NotImplementedError(
                f"InvertedIndex.__eq__() not implemented for objects type of {type(other)}"
            )

        if set(self.data_.keys()) != set(other.data_.keys()):
            return False

        is_eq = True

        for key in self.data_:
            if set(self.data_[key]) != set(other.data_[key]):
                is_eq = False
                break

        return is_eq

    def __ne__(self, other: InvertedIndex) -> bool:
        """Compares two InvertedIndex objects (true if they are not equal)"""

        return not self.__eq__(other)

    def __repr__(self) -> str:
        """For printing InvertedIndex objects"""

        return f"InvertedIndex: {self.data_.__repr__()}"

    def __str__(self) -> str:
        """For converting InvertedIndex objects to string"""

        return self.__repr__()

    @staticmethod
    def dict_check(input_dict: dict):
        """Checks if input_dict is a valid inverted index dict"""

        if not isinstance(input_dict, dict):
            raise TypeError(f"inverted_index_dict must be type of {type(dict)}\n\
                Got: {type(input_dict)}")

        for key in input_dict:
            if not isinstance(key, str):
                raise ValueError(f"dict keys must be type of {type(int)}\n\
                    Got: {type(input_dict)}")

            item_lst = input_dict[key]

            if not isinstance(item_lst, list):
                raise ValueError(f"dict values must be typeof {type(list)}\n\
                    Got: {type(item_lst)}")

            for item in item_lst:
                if not isinstance(item, int):
                    raise ValueError(f"dict must be list of elements type of {type(int)}\n\
                        Got: {type(item)}")

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""

        if not isinstance(words, list):
            raise TypeError(f"words must type of {type(list)}\n\
                Got: {type(words)}")

        for item in words:
            if not isinstance(item, str):
                raise TypeError(f"items of words must be type of {type(str)}\n\
                    Got: {type(item)}")

        if len(self.data_) == 0 or len(words) == 0:
            return []

        words = [word.lower().strip() for word in words]
        result = set(self.data_[words[0]])

        for word in words:
            result = result.intersection(set(self.data_[word]))

        result = list(result)

        return result

    def dump(self, filepath: str, method: str = 'json') -> None:
        """Dumps self.data_ to filepath in json format"""

        filepath = str(filepath)

        if method == 'json':
            JsonPolicy.dump(self.data_, filepath)
        elif method == 'struct':
            StructPolicy.dump(self.data_, filepath)
        else:
            raise NotImplementedError(f"InvertedIndex.dump: not implemented\
                for method={method}\n")

    @classmethod
    def load(cls, filepath: str, method: str = 'json') -> InvertedIndex:
        """Loads self.data_ from file in json format"""

        filepath = str(filepath)

        if method == 'json':
            inverted_index = JsonPolicy.load(filepath)
        elif method == 'struct':
            inverted_index = StructPolicy.load(filepath)
        else:
            raise NotImplementedError(f"InvertedIndex.load: not implemented\
                for method={method}\n")

        return inverted_index


def load_documents(filepath: str) -> Dict[int, str]:
    """Loads strings and row numbers from file with text"""

    filepath = str(filepath)

    if not os.path.exists(filepath):
        raise FileNotFoundError("load_documents: filepath doesn't exist\n")

    with open(filepath, 'r') as file:
        lines = file.readlines()

    data_dict = {}

    for line in lines:
        if len(line) > 0 and '\t' not in line:
            raise ValueError("load_documents: got invalid data\n")

        splited_line = line.lower().split('\t', maxsplit=1)

        try:
            index = int(splited_line[0])
        except:
            raise ValueError("load_documents: got invalid data\n")

        data_dict[index] = splited_line[1].strip()

    return data_dict


def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """Builds inverted index dict based on data, loaded with load_documents"""

    inverted_index_dict = defaultdict(list)

    for index in documents:
        if not isinstance(index, int):
            raise ValueError(f"Document index must be int\nGot: {type(index)}")
        if not isinstance(documents[index], str):
            raise ValueError(f"Document item must be str\nGot: {type(documents[index])}\n")
        item_lst = documents[index].strip()
        item_lst = re.split(r"\W+", item_lst)
        item_lst = [item.strip() for item in item_lst]

        for word in item_lst:
            inverted_index_dict[word].append(index)

    inverted_index = InvertedIndex(inverted_index_dict)

    return inverted_index


class StoragePolicy:
    """Abstract Class for describing saving strategy policies.

    Abstract Functions
    ------------------
    - dump  - dumps inverted index data on disk.
    - load  - loads inverted index data from disk.
    """

    @staticmethod
    def dump(word_to_docs_mapping: dict, filepath: str):
        """Abstract function for saving inverted index data on disk"""

    @staticmethod
    def load(filepath: str):
        """Abstract function for loading data from disk"""


class JsonPolicy(StoragePolicy):
    """Class for saving inverted index data on disk in json format.

    Functions
    ---------
    - dump  - dumps inverted index data on disk in json format.
    - load  - loads inverted index data from disk in json format.
    """

    @staticmethod
    def dump(word_to_docs_mapping: dict, filepath: str):
        """Save inverted index data on disk in json format"""

        dirname = os.path.dirname(filepath)

        if not os.path.isdir(dirname) and not dirname == '':
            raise FileNotFoundError(f"Dirpath {filepath} doesn't exist\n")

        InvertedIndex.dict_check(word_to_docs_mapping)

        with open(filepath, 'w') as file:
            json.dump(word_to_docs_mapping, file)

    @staticmethod
    def load(filepath: str):
        """Load inverted index data from disk in json format"""

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filepath} doesn't exist\n")

        with open(filepath, 'r') as file:
            data_dict = json.load(file)

        return InvertedIndex(data_dict)


class StructPolicy(StoragePolicy):
    """Class for saving inverted index data on disk in binary format using struct.

    Functions
    ---------
    - dump  - dumps inverted index data on disk in binary format.
    - load  - loads inverted index data from disk in binary format.
    """

    AS_INT = "i"
    AS_SHORT = "H"
    AS_CHAR = "s"
    AS_BIG_ENDIAN = ">"

    INT_SIZE = struct.calcsize(">i")
    SHORT_SIZE = struct.calcsize(">H")
    CHAR_SIZE = struct.calcsize(">s")

    @classmethod
    def dump(cls, word_to_docs_mapping: dict, filepath: str):
        """Save inverted index data on disk in binary format"""
        dirname = os.path.dirname(filepath)

        if not os.path.isdir(dirname) and not dirname == '':
            raise FileNotFoundError(f"Dirpath {filepath} doesn't exist\n")

        InvertedIndex.dict_check(word_to_docs_mapping)

        with open(filepath, 'wb') as file:
            length_of_dict = len(word_to_docs_mapping)
            file.write(struct.pack(cls.AS_BIG_ENDIAN + cls.AS_INT, length_of_dict))
            for word, indices in word_to_docs_mapping.items():
                word = word.encode()
                file.write(struct.pack(cls.AS_BIG_ENDIAN + cls.AS_SHORT, len(word)))
                file.write(struct.pack(cls.AS_BIG_ENDIAN + str(len(word)) + cls.AS_CHAR, word))
                file.write(struct.pack(cls.AS_BIG_ENDIAN + cls.AS_SHORT, len(indices)))
                for index in indices:
                    file.write(struct.pack(cls.AS_BIG_ENDIAN + cls.AS_INT, index))

    @classmethod
    def load(cls, filepath: str):
        """Load inverted index data from disk in binary format"""

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dirpath {filepath} doesn't exist\n")

        data_dict = defaultdict(list)

        with open(filepath, 'rb') as file:
            length_of_dict = struct.unpack(cls.AS_BIG_ENDIAN + cls.AS_INT, \
                file.read(cls.INT_SIZE))[0]

            for _ in range(length_of_dict):
                word_len = struct.unpack(cls.AS_BIG_ENDIAN + cls.AS_SHORT, \
                    file.read(cls.SHORT_SIZE))[0]
                word = struct.unpack(cls.AS_BIG_ENDIAN + str(word_len) + cls.AS_CHAR, \
                    file.read(word_len * cls.CHAR_SIZE))[0]
                word = word.decode()
                index_len = struct.unpack(cls.AS_BIG_ENDIAN + cls.AS_SHORT, \
                    file.read(cls.SHORT_SIZE))[0]
                indices = []

                for _ in range(index_len):
                    index = struct.unpack(cls.AS_BIG_ENDIAN + cls.AS_INT, \
                        file.read(cls.INT_SIZE))[0]
                    indices.append(index)
                data_dict[word] = indices

        return InvertedIndex(data_dict)


class FileTypeWithEncodign(FileType):
    """Custom FileType class for input and output encoding control"""

    def __init__(self, source, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source_ = source

    def __call__(self, string: str) -> TextIOWrapper:
        """Parameter preprocessing"""

        # print(f'Query args: {string}', file=sys.stderr)

        if string == '-':
            descriptor = TextIOWrapper(sys.stdin.buffer, encoding=self._encoding)
        else:
            if self.source_ == 'from_terminal':
                descriptor = string.strip()
            else:
                try:
                    descriptor = open(string, self._mode, self._bufsize, self._encoding, \
                        self._errors)
                except:
                    raise ValueError(f"Can not open file: {string}")

        return descriptor


class QueryInputIterator:
    """
    Input data iterator
    """

    def __init__(self, source):
        """Iterator init with paticular source"""

        self.source = []

        for query_list in source:
            self.source = list(chain(self.source, query_list))

    def __next__(self):
        """Iterator next method"""

        for subquery in self.source:
            print(f"Current subquery: {subquery}", file=sys.stderr)
            if isinstance(subquery, TextIOWrapper):
                query = next(subquery)
                query = query.strip().split()
                query = [i.strip() for i in query]
                yield query
            else:
                subquery = subquery.strip().split()
                yield subquery

    def __iter__(self):
        """Iterator iter method"""

        return self.__next__()


def callback_query(args: Namespace):
    """Query callback"""

    process_query(args)

def process_query(args: Namespace):
    """Process query subparser args"""

    print(f"Query process args: {args}", file=sys.stderr)

    inverted_index = InvertedIndex.load(args.index, method=args.strategy)
    iterator = QueryInputIterator(args.query_input)

    print(f"Loaded index: {inverted_index}", file=sys.stderr)

    for query in iterator:
        document_ids = inverted_index.query(query)
        document_ids = [str(ind) for ind in document_ids]
        print(','.join(document_ids), file=sys.stdout)

def callback_build(args: Namespace):
    """Build callback"""

    process_build(args)

def process_build(args: Namespace):
    """Build Inverted Index using params"""

    # print(f"Start build process with args: {args}", file=sys.stdout)

    documents = load_documents(args.dataset_filename)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(args.output_filename, method=args.strategy)


def setup_parser() -> ArgumentParser:
    """Create and setup command line arguments parser"""

    parser = ArgumentParser(
        prog="inverted_index",
        description="Inverted Index CLI: lib for loading, \
            storing and processing inverted index mappings",
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=True,
        argument_default="-h",
    )
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
        description="Inverted Index CLI",
    )
    subparsers.required = True

    build_parser = subparsers.add_parser(
        "build",
        help="Inverted Index CLI: build: build inverted index",
        description="Inverted Index CLI: build: build inverted index",
    )
    build_parser.add_argument(
        "-s",
        "--strategy",
        help="dump strategy: dump to json \
            or dump to struct (default: json)",
        choices=["json", "struct"],
        default="json",
    )
    build_parser.add_argument(
        "-d",
        "--dataset",
        help="path to dataset",
        dest="dataset_filename",
        required=True,
    )
    build_parser.add_argument(
        "-o",
        "--output",
        help="output file name (default: inverted.index)",
        default=DEFAULT_OUTPUT_FILENAME,
        dest="output_filename"
    )
    build_parser.set_defaults(callback=callback_build)

    query_parser = subparsers.add_parser(
        "query",
        help="Inverted Index CLI: query: search for query result in inverted index",
        description="Inverted Index CLI: query: search for query result in inverted index",
    )
    query_file = query_parser.add_mutually_exclusive_group(required=False)
    query_file.add_argument(
        "--query-file-utf8",
        dest="query_input",
        type=FileTypeWithEncodign('from_file', encoding="utf-8"),
        default=None,
        help="query file to get queries for inverted index",
    )
    query_file.add_argument(
        "--query-file-cp1251",
        dest="query_input",
        type=FileTypeWithEncodign('from_file', 'r', encoding="cp1251"),
        default=None,
        help="query file to get queries for inverted index",
    )
    query_file.add_argument(
        "--query",
        dest="query_input",
        type=FileTypeWithEncodign('from_terminal', encoding="utf-8"),
        default=None,
        nargs='+',
        action='append',
        help="query file to get queries for inverted index",
    )
    query_parser.add_argument(
        "-i",
        "--index",
        dest="index",
        default="inverted.index",
        help="Inverted Index CLI file path",
    )
    query_parser.add_argument(
        "-s",
        "--strategy",
        help="load strategy: load from json \
            or load from struct (default: struct)",
        choices=["json", "struct"],
        default="struct",
    )
    query_parser.set_defaults(callback=callback_query)

    return parser

def parse_arguments(parser: ArgumentParser) -> list:
    """Parse arguments with created parser"""

    args = parser.parse_args()

    return args

def main():
    """Function for acting as a command line script"""

    parser = setup_parser()
    args = parse_arguments(parser)
    args.callback(args)


if __name__ == "__main__":
    main()
