from panda import DetectorSet
from grizzly import DNN
import server.bcp_server as handler
import socket
from common.dataset import DataSet
import os
import logging
import time
import threading
from _thread import *
from os import walk
import queue
from Grizzly import parameters as props


dnn_models = {}
data_set = DataSet()
HOST, BPORT = props.LOCALHOST, 1865
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

    option = input("Generate new DNNs: (y/n)")

    if option == 'n':
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

    elif option == 'y':
        data_set_init(train_ais, True)
        if not os.path.isdir(dnn_out_directory):
            try:
                os.mkdir(dnn_out_directory)
            except OSError:
                print("Creation of DNN directory failed")
                os._exit(-1)

        for key, value in data_set.dnn_instances_x.items():

            try:
                dnn_models[key] = DNN(dnn_out_directory, key, data_set)
                dnn_models[key].train_dnn()

            except Exception as e:
                logging.error(e)
                os._exit(-1)
    else:
        os._exit(-1)


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
    #
    # # filename = '../dataset/Day1.csv,../dataset/Day2.csv,../dataset/Day3.csv,../dataset/Day4.csv,../dataset/Day5.csv,' \
    # #            '../dataset/Day6.csv,../dataset/Day7.csv,../dataset/Day8.csv,../dataset/Day9.csv,../dataset/Day10.csv'
    # # filename = '../dataset/Day2.csv,../dataset/Day3.csv,../dataset/Day4.csv,../dataset/Day5.csv'
    # # filename = '../dataset/Day3.csv,../dataset/Day4.csv'
    # filename = '../dataset/test.csv'

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

    # Ask user if they want to generate and save detectors
    generate_detectors_option = input("Generate detectors: (y/n)")

    # initialize dnns

    if generate_detectors_option == 'y':
        dnn_init(True)
        detectors_init()
    else:
        dnn_init(False)

    end = time.time() - start
    print('Total runtime: ' + str(end) + 's')

    # Start the classification server

    print('Starting server on port ' + str(BPORT))
    x = threading.Thread(target=start_server)
    x.start()

    while True:
        shutdown = input('Please enter \"exit\" to exit the program: ')

        if shutdown == 'exit':
            stop_servers()
            break
