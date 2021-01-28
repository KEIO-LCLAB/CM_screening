### data preprocessing & svm classiication
### made by Kaho Kato
#######################################################################################
import os, glob
import numpy as np
import pandas as pd
from csv_file_not_extension import CsvFile
from scipy.fftpack import fft
from scipy import signal
from sklearn.externals import joblib
import data_check

# parameter setting
N = 64 # set data size for FFT (Recommend: 2 to the power of X)
N_Origin = 256 ## data size you got

PARAMETER_Num = 35 ## the number of parameters
HANDDATA_Num = 4 ## each person has four data (L1, L2, R1, R2)
Classification_Result = ["not CM", "CM"]
DATA_PATH = "./TestData"  ## directory for test
model_path = "./svm_data.pkl"
scaler_path = "./sc_parameter.pkl"

window = signal.windows.hanning(N)  ## select window function (Recommend: hanning)
From, To = 5, 34 ## select parameter, if you want to use only partial parameter


def call_model():
    svm_model = joblib.load(model_path)
    sc = joblib.load(scaler_path)
    return svm_model, sc


if __name__ == '__main__':
    csv = CsvFile()
    svm_model, sc = call_model()
    data_check.identify_data_check(csv)
    file_list = glob.glob(DATA_PATH+ "/*.csv") ## add health data's path to list
    ##############PREPROCESSING############################
    data = [0] * int(N_Origin / N)
    for data_num, file in enumerate(file_list):
        X, x, = [], []
        data_origin = csv.read(file) ## read data
        ## the first 100 frames are excluded if can. only 256 frames are extracted. if not, the 256 frames from the end are extracted
        data[data_num % HANDDATA_Num] = data_origin[100:100+N_Origin, :] if len(data_origin)>(100+N_Origin) else data_origin[len(data_origin) - N_Origin:len(data_origin), :]
        if np.isnan(data[data_num % HANDDATA_Num]).any(): ## check NAN
            print(file)
            data[data_num % HANDDATA_Num] = pd.DataFrame(data[data_num % HANDDATA_Num]).fillna(method='ffill').to_numpy() ## if NAN exists, it is filled by the previous one
        if (data_num % HANDDATA_Num) == HANDDATA_Num - 1: ## process every four data(L1, L2, R1, R2)
            for i in range(int(N_Origin/N)): # 256 frames are divided by four, and the process is done every 64 frames
                for loop in range(HANDDATA_Num): ## four times (L1,L2,R1,R2)
                    div_data = data[loop][i*N:(i+1)*N, :].T ## div_data = [L1's first 64 frames, L2's first 64 frames, R1's first 64 frames, … R2's last 64 frames]
                    for sensor_num in range(PARAMETER_Num):
                        if sensor_num < From or sensor_num > To: ## if you want to use only partial feature, you can exclude here freely
                            continue
                        # if loop == 0 and i == 0: print(sensor_num) #display sensor number
                        data_window = signal.detrend(div_data[sensor_num], type="constant") * window ## remove trend(constant) & apply window function
                        F_window = np.abs(fft(data_window)/(N/2)) * 1/(sum(window)/N) ## do FFT & get the absolute value (adjust the amplitude value)
                        x.append(F_window[:int(N/2)])  ## MinMax Normalization & get the low frequency part
            x = np.array(x).flatten()
            X.append(x)  ## add x(frequency data) to list. the data consists of 32 frequency components * four (L1,L2,R1,R2) * four (divide number) * X features = 512*X dimensions
            X = sc.fit_transform(np.abs(np.array(X)).T).T  ##StandardScaler使用時
            X = np.array(X)
            ##############CLASSIFICATION#########################
            predicted = svm_model.predict(X)
            print("#########Classification Result#########")
            print(os.path.basename(file)[:8] + " is estimated " + Classification_Result[int(predicted)])

