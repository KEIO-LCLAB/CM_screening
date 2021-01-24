#########################################################################################################
# how to use pandas library
# data_frame = pandas.read_csv(full path, header=header line, index_col=index_line,encoding=encoding)
# if you need to read header/index data from csv file, you set header/index line = 0 (or -1/None if not).
#
# data_frame.to_csv(full path, encoding=encoding, header=header line, index=index line)
# if you need to write header/index data to csv file, you set header/index line = -1 (or 0 if not).
#
# data_frame.columns = [list]
# data_frame.index = [list]
# data_frame = data_frame.astype(type)
# data_frame = pd.DataFrame(ndarry)
#########################################################################################################
import pandas as pd
import numpy as np
from copy import deepcopy


def add_header_and_index(data, header=None, index=None):
    if isinstance(data, np.ndarray) or isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = deepcopy(data)
    if header is not None:
        df.columns = header
    if index is not None:
        df.index = index
    return df


class CsvFile(object):
    def __init__(self, delimiter=",", encoding="utf-8"):
        self.delimiter = delimiter
        self.encoding = encoding

    def read(self, file_path, header=False, index=False, is_data_frame=False):
        full_path = file_path + ""
        has_header = 0 if header else None
        has_index = 0 if index else None
        data = pd.read_csv(full_path, header=has_header, index_col=has_index, encoding=self.encoding,
                           float_precision="high")
        if not is_data_frame:
            data = data.values
        return data

    def write(self, file_path, data, header=False, index=False):
        if isinstance(data, np.ndarray) or isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = deepcopy(data)
        full_path = str(file_path) + ".csv"
        has_header = -1 if header else 0
        has_index = -1 if index else 0
        df.to_csv(full_path, encoding=self.encoding, header=has_header, index=has_index)

    def addwrite(self, file_path, data, header=False, index=False):
        if isinstance(data, np.ndarray) or isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = deepcopy(data)
        full_path = str(file_path) + ".csv"
        has_header = -1 if header else 0
        has_index = -1 if index else 0
        df.to_csv(full_path, mode="a",encoding=self.encoding, header=has_header, index=has_index)

def main():
    DATA_ROOT = "./"
    csv = CsvFile()
    csv_data = csv.read(DATA_ROOT + "tmp", header=True, is_data_frame=True)
    # print(csv_data)
    csv_data = add_header_and_index(csv_data, header=list("ABCD"), index=list("abc"))
    csv_data = csv_data.astype(float)
    # print(csv_data)
    csv_ndarray = csv_data.values
    # print(csv_ndarray)
    inv_ndarry = csv_ndarray.T
    csv.write(DATA_ROOT + "inv", inv_ndarry)
    inv_data = pd.DataFrame(inv_ndarry)
    # print(inv_data)
    # csv.write(DATA_ROOT + "inv", inv_data)


if __name__ == '__main__':
    main()
