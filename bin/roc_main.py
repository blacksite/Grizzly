from bin.panda import DetectorSet
from bin.grizzly import DNN
import bin.server.bcp_server as handler
import socket
from bin.common.dataset import DataSet
import os
import logging
import time
import threading
from _thread import *
from os import walk
import queue
import parameters as props
import pandas
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
from sklearn.metrics import auc

dnn_models = {}
data_set = DataSet()
HOST, BPORT = props.IP_ADDRESS_VALIDATOR, 1891
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, BPORT))
queue = queue.Queue()

# Ask user if they want to generate and save detectors
dnn_out_directory = 'dnn'
ais_out_directory = '../ais'
data_directory = 'data'
# data_directory = '../tests/dataset'


def dnn_init(train_ais):
    global dnn_models
    global dnn_out_directory
    global data_set

    data_set_init(train_ais, False)
    directories = []
    files = []
    dirnames = []
    for (dirpath, dirnames, files) in walk(dnn_out_directory):
        directories.extend(dirnames)
        break

    if len(files) > 0:
        for f in files:
            key = f
            dnn_models[key] = DNN(dnn_out_directory, f)
            dnn_models[key].load_dnn()
        return
    elif len(dirnames) > 0:
        for d in dirnames:
            key = d
            dnn_models[key] = DNN(dnn_out_directory, d)
            dnn_models[key].load_dnn()
        return




def data_set_init(traing_ais, train_dnn):
    global data_set
    global data_directory
    global ais_out_directory

    filename = ''
    if os.path.isdir(data_directory):

        directories = []
        files = []
        for (dirpath, dirnames, files) in walk(data_directory):
            directories.extend(dirnames)
            break

        if len(files) == 0:
            print('No dataset set files found')
            os._exit(-1)
        else:
            filename = data_directory + '/' + files[0]

            for i in range(1, len(files)):
                filename += ',' + data_directory + '/' + files[i]

    else:
        print('No dataset directory found')
        os._exit(-1)

    # create ais directory if it doesn't exist
    if not os.path.isdir(ais_out_directory):
        try:
            os.mkdir(ais_out_directory)
        except OSError:
            print("Creation of AIS directory failed")
            os._exit(-1)

    w_minmax = open(ais_out_directory + "/min_max.csv", "w")

    data_set.read_from_file(w_minmax, filename, traing_ais, train_dnn)


def detectors_init():
    global dnn_models
    global data_set
    global ais_out_directory

    writer = open(ais_out_directory + "/detectors.csv", "w")
    DetectorSet(data_set, dnn_models, writer)


def start_server():
    global server
    global data_set

    server.listen(5)

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = server.accept()

        # lock acquired by client
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(handler.thread, (dnn_models, c, addr[0], data_set,))


def stop_servers():
    global server
    global dnn_models

    for key, dnn in dnn_models.items():
        dnn.save_dnn()
    os._exit(0)


if __name__ == "__main__":

    start = time.time()

    # initialize dnns
    dnn_init(False)

    dataset = []
    filename = 'data/2021-12-28-collected-test.csv'

    dataframe = pandas.read_csv(filename, engine='python')
    dataframe.fillna(0)

    # if 'Day4' in f:
    # del dataframe['Index']
    del dataframe['Flow ID']
    del dataframe['Src IP']
    del dataframe['Src Port']
    del dataframe['Dst IP']
    dataset.extend(dataframe.values)

    dataset = np.array(dataset)

    x = dataset[:, 3:-1]
    x.astype('float32')
    y = dataset[:, -1]

    # Normalize X features
    scalar = MinMaxScaler()
    scalar.fit(x)

    # Transform y vector into a matrix
    encoder = LabelEncoder()
    encoder.fit(y)
    y_encoded = encoder.transform(y)

    x_normalized = scalar.transform(x)

    local_instances_x = {}
    local_instances_y = {}

    for i in range(len(y)):
        if y[i] not in local_instances_x:
            local_instances_x[y[i]] = []
            local_instances_y[y[i]] = []
        local_instances_x[y[i]].append(x_normalized[i])
        if y[i] == 'Benign':
            local_instances_y[y[i]].append(0)
        else:
            local_instances_y[y[i]].append(1)

    for key, dnn in dnn_models.items():
        local_instances_x[key].extend(local_instances_x['Benign'])
        local_instances_y[key].extend(local_instances_y['Benign'])

        X_test = np.array(local_instances_x[key])
        y_test = np.array(local_instances_y[key])


        y_pred_keras = dnn.model.predict(X_test).ravel()

        fpr_keras, tpr_keras, thresholds_keras = roc_curve(y_test, y_pred_keras, pos_label=1)
        auc_keras = auc(fpr_keras, tpr_keras)

        plt.figure(1)
        plt.plot([0, 1], [0, 1], 'k--')
        plt.plot(fpr_keras, tpr_keras, label='Keras (area = {:.3f})'.format(auc_keras))
        plt.xlabel('False positive rate')
        plt.ylabel('True positive rate')
        plt.title('ROC curve')
        plt.legend(loc='best')
        plt.show()

    stop = input("Press ENTER to stop the program")
