from components.panda import DetectorSet
from components.grizzly import DNN
import sys
from cache.dataset import DataSet
import os
import logging
import time

dnn_models = {}


def start():
    start = time.time()

    # Ask user if they want to generate and save detectors
    save_detectors_option = input("Would you like to save generate detectors (y/n): ")

    out_directory = '../out'
    try:
        os.mkdir(out_directory)
    except OSError:
        print("Creation of the directory failed")
    else:
        print("Successfully created the directory")

    # filename = '../data/Day1.csv,../data/Day2.csv,../data/Day3.csv,../data/Day4.csv,../data/Day5.csv,' \
    #            '../data/Day8.csv,../data/Day9.csv,../data/Day10.csv'
    # filename = '../data/Day2.csv,../data/Day3.csv,../data/Day4.csv,../data/Day5.csv'
    # filename = '../data/Day1.csv'
    filename = '../data/test.csv'
    w_minmax = open(out_directory + "/min_max.csv", "w")

    data_set = DataSet()
    data_set.read_from_file(w_minmax, filename)

    writers = {}

    global dnn_models

    for key, value in data_set.instances_x.items():
        if key != 'Benign':
            writers[key] = open(out_directory + "/" + key + ".csv", "w")

        try:
            dnn_models[key] = DNN(key, data_set)
            if save_detectors_option == 'y' or save_detectors_option == 'Y':
                DetectorSet(key, data_set, dnn_models[key], writers[key])

        except Exception as e:
            logging.error(e)
            # grizzly.save_dnn(save_file)
            sys.exit(-1)

    end = time.time() - start

    print('Total runtime: ' + str(end) + 's')


def open_server():
    print("Socket connection to listen to Panda opened here")


if __name__ == "__main__":
    start()
    open_server()
