### data preprocessing & svm classiication
### made by Kaho Kato
#######################################################################################
import os, glob
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import pandas as pd
from csv_file_not_extension import CsvFile
from sklearn.preprocessing import StandardScaler
from scipy.fftpack import fft
from scipy import signal
from sklearn.metrics import confusion_matrix, accuracy_score, auc, roc_curve
from sklearn import svm, model_selection
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib
import matplotlib.pyplot as plt

# parameter setting
N = 64 # set data size for FFT (Recommend: 2 to the power of X)
N_Origin = 256 ## data size you got

PARAMETER_Num = 35 ## the number of features
HANDDATA_Num = 4 ## each person has four data (L1, L2, R1, R2)
Health_Num = 28 # the number of health people
SAVE_PATH_True = "./Health"  ## Health data's directory
SAVE_PATH_False = "./Patient"  ## Patient data's directory

window = signal.windows.hanning(N)  ## select window function (Recommend: hanning)
parameter = "all" ### set arbitrary name
From, To = 5, 34 ## select feature, if you want to use only partial feature


def plot_roc_curve(fpr, tpr):
    if not (os.path.exists("./analysis_data")): os.makedirs("./analysis_data")
    plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic (LOO)')
    plt.legend(loc="lower right")
    plt.savefig('./analysis data/LOO-'+ parameter +'png')  ##画像として保存
    plt.show()


def write_result(score, tp, fp, tn, fn, roc_auc):
    if not (os.path.exists("./accudata_txt")): os.makedirs("./accudata_txt")
    f = open('./accudata_txt/LOO-' + parameter + '.txt', 'w')  ## select file path
    data_list = [str(float(Decimal(score * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))), ", ",
                 str(float(Decimal(tp / (fn + tp) * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))),
                 ", ",
                 str(float(Decimal(tn / (tn + fp) * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))),
                 ", ", str(float(Decimal(roc_auc * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)))]
    f.writelines(data_list)
    f.close()


if __name__ == '__main__':
    csv = CsvFile()
    X, x, y, file_list, human_label, human_div, human_all = [], [], [], [], [], [], []
    file_list.append(glob.glob(SAVE_PATH_True + "/*.csv")) ## add health data's path to list
    file_list.append(glob.glob(SAVE_PATH_False + "/*.csv")) ## add patient data's path to list

    ##############PREPROCESSING############################
    for type in range(len(file_list)): ## "type==0" means health data, and "type==1" means patient data
        data = [0] * int(N_Origin / N)
        for data_num, file in enumerate(file_list[type]):
            data_origin = csv.read(file) ## read data
            ## the first 100 frames are excluded if can. only 256 frames are extracted. if not, the 256 frames from the end are extracted
            data[data_num % HANDDATA_Num] = data_origin[100:100+N_Origin, :] if len(data_origin)>(100+N_Origin) else data_origin[len(data_origin) - N_Origin:len(data_origin), :]
            if np.isnan(data[data_num % HANDDATA_Num]).any(): ## check NAN
                print(file)
                data[data_num % HANDDATA_Num] = pd.DataFrame(data[data_num % HANDDATA_Num]).fillna(method='ffill').to_numpy() ## if NAN exists, it is filled by the previous one
            if (data_num % HANDDATA_Num) == HANDDATA_Num - 1: ## process every four data(L1, L2, R1, R2)
                human = int(os.path.basename(file)[:7]) ## get a person's number from file name
                for i in range(int(N_Origin/N)): # 256 frames are divided by four, and the process is done every 64 frames
                    for loop in range(HANDDATA_Num): ## four times (L1,L2,R1,R2)
                        div_data = data[loop][i*N:(i+1)*N, :].T ## div_data = [L1's first 64 frames, L2's first 64 frames, R1's first 64 frames, … R2's last 64 frames]
                        for sensor_num in range(PARAMETER_Num):
                            # if sensor_num < From or sensor_num > To: ## if you want to use only partial feature, you can exclude here freely.
                            #     continue
                            # if loop == 0 and i == 0: print(sensor_num) #display sensor number
                            data_window = signal.detrend(div_data[sensor_num], type="constant") * window ## remove trend(constant) & apply window function
                            F_window = np.abs(fft(data_window)/(N/2)) * 1/(sum(window)/N) ## do FFT & get the absolute value (adjust the amplitude value)
                            x.append(F_window[:int(N/2)])  ## MinMax Normalization & get the low frequency part
                x = np.array(x).flatten()
                X.append(x)  ## add x(frequency data) to list. the data consists of 32 frequency components * four (L1,L2,R1,R2) * four (divide number) * X features = 512*X dimensions
                y.append(int(type % 2))  ## add answer to list
                human_all.append(int(human)) ## make human list
                x = []
    print(human_all)
    print(np.shape(X))
    sc = StandardScaler()
    X = sc.fit_transform(np.abs(np.array(X)).T).T ##StandardScaler使用時
    joblib.dump(sc, './sc_parameter.pkl', compress=True)
    X = np.array(X)
    y = np.array(y)

    ##############LEARNING#########################
    loo = model_selection.LeaveOneOut()
    svc = OneVsRestClassifier(svm.SVC(C=100, kernel='rbf', gamma=0.0001, probability=True))
    expected, predicted, decision = [], [], []
    for train, test in loo.split(X):  ## select train and test data
        svc.fit(X[train], y[train])
        joblib.dump(svc, './svm_data.pkl', compress=True)  # save learning data
        expected.extend(y[test])  ## add truth label
        predicted.extend(svc.predict(X[test]))  ## add predicted label
        decision.extend(svc.decision_function(X[test]))  ## calculate probability
    fpr, tpr, thresholds = roc_curve(expected, decision)
    roc_auc = auc(fpr, tpr)
    # plot_roc_curve(fpr,tpr) ## plot roc curve graph
    matrix = confusion_matrix(expected, predicted)  # make confusion_matrix
    tn, fp, fn, tp = matrix.flatten()
    score = accuracy_score(expected, predicted)  # get accuracy score
    # write_result(score, tp, fp, tn, fn, roc_auc) ## write a result to *.txt

    ### classification result ###
    print("Accuracy　", float(Decimal(score * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)), "%")
    print(matrix)
    print("Sensibility ", float(Decimal(tp / (fn + tp) * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)),
          "%, Specificity ", float(Decimal(tn / (tn + fp) * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)),
          "%, AUC ", float(Decimal(roc_auc).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)))
    #############################

