import csv
import json
import os
import pickle
import sys
import xml.etree.ElementTree as eTree
from abc import ABCMeta, abstractmethod


class Converter(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def read(self, path):
        raise NotImplementedError

    @abstractmethod
    def write(self, path, obj):
        raise NotImplementedError


class MyCsv(Converter):
    def read(self, path):
        file = open(path)
        obj = list(csv.DictReader(file))
        file.close()
        return obj

    def write(self, path, obj):
        headers = obj[0].keys()
        file = open(path, 'w')
        writer = csv.DictWriter(file, headers)
        writer.writeheader()
        writer.writerows(obj)
        file.close()


class MyXml(Converter):
    def read(self, path):
        file = open(path)
        tree = eTree.parse(file)
        file.close()
        root = tree.getroot()
        return [{child.tag: child.text for child in user} for user in root]

    def write(self, path, obj):
        temp = []
        for key in obj[0]:
            temp.append(f'\t<{key}>{{{key}}}</{key}>\n')
        string = '<person>\n' + ''.join(temp) + '</person>\n'
        result = []
        for item in obj:
            result.append(string.format(**item))
        result_str = ''.join(result)
        result_str = f'<root>\n{result_str}</root>'
        file = open(path, 'w')
        file.write(result_str)
        file.close()


class MyJson(Converter):
    def read(self, path):
        file = open(path)
        obj = json.load(file)
        file.close()
        return obj

    def write(self, path, obj):
        file = open(path, 'w')
        file.write(json.dumps(obj, indent=4))
        file.close()


class MyPickle(Converter):
    def read(self, path):
        file = open(path, 'rb')
        obj = pickle.load(file)
        file.close()
        return obj

    def write(self, path, obj):
        file = open(path, 'wb')
        pickle.dump(obj, file)
        file.close()


def check_file():
    in_file, out_file = None, None
    if len(sys.argv) > 1:
        in_file = sys.argv[1]
        if len(sys.argv) == 3:
            out_file = sys.argv[2]
    else:
        raise SystemExit('Для работы утилиты нужны 1 либо 2 аргумента')
    return in_file, out_file


def check_ext(file, _ext):
    file_ext = None
    try:
        file_ext = file.rsplit('.', 1)[1]
    except IndexError:
        print(f'Нет расширения у {file}')
    if file_ext and file_ext not in _ext:
        print(f'Неверное расширения у {file}')
        file_ext = None
    return file_ext


if __name__ == "__main__":
    ext = {'csv': MyCsv(), 'json': MyJson(), 'xml': MyXml(), 'bin': MyPickle()}
    input_file, output_file = check_file()
    input_ext = check_ext(input_file, ext.keys()) if input_file else None
    output_ext = check_ext(output_file, ext.keys()) if output_file else None
    if input_ext is None:
        raise SystemExit('Не верный аргумент входного файла')
    if not os.path.exists(input_file):
        raise SystemExit('Входного файла по этому пути не существует')
    py_obj = ext[input_ext].read(input_file)
    if output_ext is None:
        print(py_obj)
    else:
        ext[output_ext].write(output_file, py_obj)
