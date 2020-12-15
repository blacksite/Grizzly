from experimental import grizzly, panda
import sys
from cache import dataset, detectors, new_instances, suspicious_instances, validated_instances
from os import path
import os
import logging

SAVE_FILE = None


def start_dataset():
    file_prompt = input('Would you like to use a dataset from a csv file?: y/n\n')
    while True:
        if file_prompt == 'y':
            # filename = input('\nEnter the csv filename\n'
            #                 '**If there are multiple files, separate with a comma (no spaces)**\n')
            filename = 'data/Day1.csv,data/Day2.csv'
            # filename = 'data/Sample.csv'
            dataset.read_from_file(filename)
            break
        elif file_prompt == 'n':
            # grizzly.train_dnn()
            break
        else:
            print('\nInvalid input')
            file_prompt = input('Would you like to use a dataset from a csv file?: y/n\n')


def start_experiment():

    save_file = input("Please enter the file name to save the results\n")

    while True:
        if path.exists("results/" + save_file + ".csv"):
            option = input("That file exists, would you like to overwrite it: y/n\n")
            if option == "y":
                break
            else:
                save_file = input("Please enter the file name to save the results\n")
        else:
            break

    result_directory = '../results/' + save_file
    try:
        os.mkdir(result_directory)
    except OSError:
        print("Creation of the directory failed")
    else:
        print("Successfully created the directory")

    filename = '../data/Day1.csv,../data/Day2.csv,../data/Day3.csv,../data/Day4.csv'
    # filename = '../data/test.csv'
    # filename = '../data/Day1.csv'
    w_dataset = open(result_directory + "/dataset.csv", "w")
    dataset.read_from_file(w_dataset, filename)

    w_dnn = open(result_directory + "/dnn.csv", "w")
    w_dnn.write("{:^30s}".format("Accuracy"))
    for i in range(len(dataset.CLASSES)):
        w_dnn.write(
            ",{:^30s},{:^30s}".format(dataset.CLASSES[i] + "-correct", dataset.CLASSES[i] + "-not-correct"))
    w_dnn.write("\n")
    w_dnn.flush()
    grizzly.set_common(detectors, validated_instances, suspicious_instances, dataset)
    panda.set_common(detectors, new_instances, suspicious_instances, dataset)

    # std_devs = [1]
    # num_detectors = [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
    # writers = {}
    #
    # for s in std_devs:
    #     for n in num_detectors:
    #         writers[s+n] = open(result_directory + "/dnn-detectors-" + str(s) + "-" + str(n) + ".csv", "w")
    #
    #         writers[s+n].write("{:^30s}".format("Accuracy"))
    #         writers[s + n].write(",{:^30s}".format("r-value"))
    #         for c in dataset.CLASSES:
    #             writers[s+n].write(
    #                     ",{:^30s},{:^30s}".format(c + "-correct", c + "-not-correct"))
    #         writers[s+n].write("\n")
    #         writers[s+n].flush()

    for i in range(dataset.KFOLDS):

        try:
                    # if i == 0:
                    #     grizzly.load_dnn("../model/" + save_file + ".dnn")
                    #     grizzly.experimental_train_dnn(w_dnn, i, False)
                    # else:
            grizzly.experimental_train_dnn(w_dnn, i)

            # for s in std_devs:
            #     for n in num_detectors:
            #         panda.evaluate_dnn(writers[s+n], grizzly, i, n, s)
            #             # panda.evaluate_nsa(w_detectors_nsa, i)

        except Exception as e:
            logging.error(e)
            grizzly.save_dnn(save_file)
            sys.exit(-1)


if __name__ == "__main__":
    start_experiment()
