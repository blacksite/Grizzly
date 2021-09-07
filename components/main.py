from components.panda import DetectorSet
from components.grizzly import DNN
import components.server as st
import socket
import sys
from cache.dataset import DataSet
import os
import logging
import time
import threading
from _thread import *
from os import walk
import queue
from components.grizzly_retraining_worker import RetrainDNNs


dnn_models = {}
data_set = None
HOST, CPORT, RPORT = "localhost", 2021, 2022
classification_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
classification_server.bind((HOST, CPORT))
regeneration_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
regeneration_server.bind((HOST, RPORT))
queue = queue.Queue()
retraining_thread = RetrainDNNs(dnn_models, queue)

# Ask user if they want to generate and save detectors
out_directory = '../out'


def dnn_init(option):
    global dnn_models
    global out_directory
    global data_set

    if option == 'y':
        data_set_init()

        for key, value in data_set.instances_x.items():

            try:
                dnn_models[key] = DNN(key, data_set)
                dnn_models[key].train_dnn()

            except Exception as e:
                logging.error(e)
                sys.exit(-1)
    else:
        directories = []
        for (dirpath, dirnames, filenames) in walk(out_directory):
            directories.extend(dirnames)
            break

        for dir in directories:
            key = dir
            dnn_models[key] = DNN(key)
            dnn_models[key].load_dnn(out_directory + '/' + dir)


def data_set_init():
    global data_set
    global out_directory

    data_set = DataSet()

    try:
        os.mkdir(out_directory)
    except OSError:
        print("Creation of the directory failed")
    else:
        print("Successfully created the directory")

    # filename = '../data/Day1.csv,../data/Day2.csv,../data/Day3.csv,../data/Day4.csv,../data/Day5.csv,' \
    #            '../data/Day6.csv,../data/Day7.csv,../data/Day8.csv,../data/Day9.csv,../data/Day10.csv'
    # filename = '../data/Day2.csv,../data/Day3.csv,../data/Day4.csv,../data/Day5.csv'
    # filename = '../data/Day3.csv,../data/Day4.csv'
    filename = '../data/test.csv'
    w_minmax = open(out_directory + "/min_max.csv", "w")

    data_set.read_from_file(w_minmax, filename)


def detectors_init(option):
    global dnn_models
    global data_set
    global out_directory

    if option == 'y':
        if not data_set:
            data_set_init()

        for key, value in data_set.instances_x.items():
            writer = open(out_directory + "/" + key + ".csv", "w")
            DetectorSet(key, data_set, dnn_models[key], writer)


def start_classification_server():
    global classification_server

    classification_server.listen(5)

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = classification_server.accept()

        # lock acquired by client
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(st.classification_thread, (dnn_models, data_set, c, queue,))


def stop_servers():
    global classification_server
    global regeneration_server
    global retraining_thread

    classification_server.close()
    regeneration_server.close()
    retraining_thread.stop()
    retraining_thread.join()


def start_regeneration_server():
    global RPORT
    global regeneration_server

    print('Starting regeneration server on port ' + str(RPORT))

    regeneration_server.listen(5)

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = regeneration_server.accept()

        # lock acquired by client
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(st.regeneration_thread, (dnn_models, data_set, c,))


if __name__ == "__main__":

    start = time.time()

    # Ask user if they want to generate and save detectors
    train_dnn_option = input("Would you like to train a the dnn (y/n)")
    # save_detectors_option = input("Would you like to save generated detectors (y/n): ")
    start_server_option = input("Would you like to start the server (y/n)")

    dnn_init(train_dnn_option)
    # detectors_init(save_detectors_option)

    end = time.time() - start
    print('Total runtime: ' + str(end) + 's')

    # Start the classification server
    if start_server_option == 'y' or start_server_option == 'Y':
        print('Starting classification server on port ' + str(CPORT))
        x = threading.Thread(target=start_classification_server)
        x.start()

        print('Starting regeneration server on port ' + str(RPORT))
        # Start the regeneration server
        y = threading.Thread(target=start_regeneration_server)
        y.start()

        print('Starting retraining thread')
        # Start the retraining thread
        retraining_thread.start()

    while True:
        shutdown = input('Please enter \"exit\" to exit the program: ')

        if shutdown == 'exit':
            stop_servers()
            break
