from bin.panda import DetectorSet
from bin.grizzly import DNN
import bin.server.server_worker as handler
import socket
import sys
from common.dataset import DataSet
import os
import logging
import time
import threading
from _thread import *
from os import walk
import queue
import parameters as props


dnn_models = {}
data_set = DataSet()
HOST, BPORT = props.LOCALHOST, 1891
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, BPORT))
queue = queue.Queue()

# Ask user if they want to generate and save detectors
dnn_out_directory = '../bin/dnn'
ais_out_directory = '../ais'
data_directory = '../../blacksite/data'


def dnn_init():
    global dnn_models
    global dnn_out_directory
    global data_set

    if os.path.isdir(dnn_out_directory):

        directories = []
        files = []
        for (dirpath, dirnames, files) in walk(dnn_out_directory):
            directories.extend(dirnames)
            break

        if len(files) > 0:
            for f in files:
                dnn_models[f] = DNN(dnn_out_directory, f)
                dnn_models[f].load_dnn(dnn_out_directory + '/' + f)
            return

    option = input("No valid DNNs found. Generate new DNNs: (y/n)")
    if option == 'y':
        if not os.path.isdir(dnn_out_directory):
            try:
                os.mkdir(dnn_out_directory)
            except OSError:
                print("Creation of DNN directory failed")
                sys.exit(-1)
        data_set_init()

        for key, value in data_set.instances_x.items():

            try:
                dnn_models[key] = DNN(dnn_out_directory, key, data_set)
                dnn_models[key].train_dnn()

            except Exception as e:
                logging.error(e)
                sys.exit(-1)
    else:
        sys.exit(-1)


def data_set_init():
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
            print('No data set files found')
            sys.exit(-1)
        elif len(files) == 1:
            filename = data_directory + '/' + files[0]
        else:
            for f in files:
                filename = filename + data_directory + '/' + f + ','
    else:
        print('No data directory found')
        sys.exit(-1)
    #
    # # filename = '../data/Day1.csv,../data/Day2.csv,../data/Day3.csv,../data/Day4.csv,../data/Day5.csv,' \
    # #            '../data/Day6.csv,../data/Day7.csv,../data/Day8.csv,../data/Day9.csv,../data/Day10.csv'
    # # filename = '../data/Day2.csv,../data/Day3.csv,../data/Day4.csv,../data/Day5.csv'
    # # filename = '../data/Day3.csv,../data/Day4.csv'
    # filename = '../data/test.csv'

    # create ais directory if it doesn't exist
    if not os.path.isdir(ais_out_directory):
        try:
            os.mkdir(ais_out_directory)
        except OSError:
            print("Creation of AIS directory failed")
            sys.exit(-1)

    w_minmax = open(ais_out_directory + "/min_max.csv", "w")

    data_set.read_from_file(w_minmax, filename)


def detectors_init(option):
    global dnn_models
    global data_set
    global ais_out_directory

    if option == 'y':
        if len(data_set.classes) <= 0:
            data_set_init()

        for key, value in data_set.instances_x.items():
            writer = open(ais_out_directory + "/" + key + ".csv", "w")
            DetectorSet(key, data_set, dnn_models[key], writer)


def start_server():
    global server

    server.listen(5)

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = server.accept()

        # lock acquired by client
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(handler.thread, (dnn_models, data_set, c, addr[0], queue,))


def stop_servers():
    global server
    global dnn_models

    server.close()
    for key, dnn in dnn_models.items():
        dnn.close()
    sys.exit(0)


if __name__ == "__main__":

    start = time.time()

    # Ask user if they want to generate and save detectors
    generate_detectors_option = input("Generate detectors: (y/n)")

    # initialize dnns
    dnn_init()
    if generate_detectors_option:
        detectors_init(generate_detectors_option)

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
