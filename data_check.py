### check data shape & extract available data
### made by Kaho Kato & Masaru Watanabe
####################################################################
from csv_file_not_extension import CsvFile
import os, glob
import numpy as np


DATA_PATH = "./10s-test-data" ## data path
TESTDATA_PATH = "./classification-data" ## test data path
handlist = ["L1", "L2", "R1", "R2"]
finishflag = [0] * 4


def export_index(index, df0):
    begin_index, finish_index, before_row = -1, 0, 0
    for i in range(index, len(df0)):
        csv_row = np.array(df0)[i][-1]
        print(str(csv_row))
        if csv_row == 1 and i < len(df0) - 1:
            if begin_index == -1:
                begin_index = i
                print("find start point")
            before_row = csv_row
        elif csv_row == 1 and before_row == 1 and i == len(df0) - 1:
            finish_index = len(df0)
            break
        elif csv_row == 0 and before_row == 1:
            print("find finish point")
            finish_index = i
            break
        elif csv_row == 0 and finish_index == 0 and i == len(df0) - 1:
            print("not find")
            return "less data size"
        elif str(csv_row) != "0" and str(csv_row) != "1":
            print("data error")
            return "data error"
    if finish_index - begin_index >= 256 and begin_index != -1:
            return np.array(df0)[begin_index:finish_index]
    return export_index(finish_index, df0)


def identify_data_check(csv):
    dir_list = glob.glob(TESTDATA_PATH + "/*")
    if not (os.path.exists("./TestData")): os.makedirs("./TestData")
    global finishflag
    for directory in dir_list:
        file_list = glob.glob(directory + "/*.csv")  ## get & select data every user
        for file in file_list:
            file_hand = os.path.basename(file)[8:10]
            if file_hand in handlist and finishflag[handlist.index(file_hand)] == 0:
                print(file)
                data_frame = export_index(0, csv.read(file))  ## check data length
                if type(data_frame) != str:  ## if data length is too short, the data cannot use classification
                    df = data_frame[:, 2:22]  ## get only 35 parameters' time series data
                    df = np.append(df, data_frame[:, 37:52], axis=1)
                    csv.write("./TestData/" + os.path.basename(file)[:10], df)
                    print("\x1b[42m" + "SAVE" + "\x1b[0m " + file)
                    finishflag[handlist.index(file_hand)] = 1
                else:
                    print("\x1b[41m" + "Miss" + "\x1b[0m " + file)
                    continue
            if 0 not in finishflag:
                finishflag = [0] * 4
                break


def make_classification_data_check(csv):
    global finishflag
    data = os.listdir(DATA_PATH)
    files_dir = [f for f in data if os.path.isdir(os.path.join(DATA_PATH, f))]
    for item in files_dir:
        directory_list = glob.glob(DATA_PATH + "/" + item + "/*")  ## get data list
        if not (os.path.exists("./" + item)): os.makedirs("./" + item)
        for directory in directory_list:
            file_list = glob.glob(directory + "/*.csv")  ## get & select data every user
            for file in file_list:
                file_hand = os.path.basename(file)[8:10]
                if file_hand in handlist and finishflag[handlist.index(file_hand)] == 0:
                    print(file)
                    data_frame = export_index(0, csv.read(file)) ## check data length
                    if type(data_frame) != str: ## if data length is too short, the data cannot use classification
                        df = data_frame[:, 2:22] ## get only 35 parameters' time series data
                        df = np.append(df, data_frame[:, 37:52], axis=1)
                        csv.write("./" + item + "/" + os.path.basename(file)[:10], df)
                        print("\x1b[42m" + "SAVE" + "\x1b[0m " + file)
                        finishflag[handlist.index(file_hand)] = 1
                    else:
                        print("\x1b[41m" + "Miss" + "\x1b[0m " + file)
                        continue
                if 0 not in finishflag:
                    finishflag = [0] * 4
                    break