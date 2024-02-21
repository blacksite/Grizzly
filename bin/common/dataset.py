from os import path
import os
import pandas
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import threading
from sklearn.preprocessing import LabelEncoder
import np_utils
import random
import math
import statistics as stats
import joblib
import pickle


class DataSet:

    def __init__(self):
        self.lock = threading.Lock()
        self.data_set = []
        self.ais_instances_x = []
        self.ais_instances_y = []
        self.dnn_instances_x = {}
        self.dnn_instances_y = {}
        self.dnn_test_instances_x = {}
        self.dnn_test_instances_y = {}
        self.number_of_features = 76
        self.number_of_classes = 0
        self.mean_mad = []
        self.min_max = {}
        self.classes = []
        self.scalar = None
        self.max_samples = 20000
        self.scalar_filename = 'dataset/scalar.gz'
        self.classes_filename = 'dataset/classes.gz'
        self.num_classes_filename = 'dataset/num_classes.gz'
        self.dnn_instances_x_filename = 'dataset/instances_x.gz'
        self.dnn_instances_y_filename = 'dataset/instances_y.gz'
        self.min_max_filename = 'dataset/min_max.gz'

    def read_from_file(self, w, filename, train_ais, train_dnn):
        models = False
        samples = False
        if not train_ais and not train_dnn:
            models = self.load_models()
            samples = True
        elif train_ais or train_dnn:
            models = True
            samples = self.load_samples()

        if not models or not samples:
            print("Loading dataset set started")

            if filename:
                # load the dataset
                dataset = []
                files = []
                if ',' in filename:
                    files = filename.split(',')
                else:
                    files.append(filename)

                for f in files:
                    while True:
                        if not path.exists(f):
                            f = input(f + " does not exist. Please re-enter another file name:\n")
                        else:
                            break
                    dataframe = pandas.read_csv(f, engine='python')
                    dataframe.fillna(0)

                    # if 'Day4' in f:
                    # del dataframe['Index']
                    del dataframe['Flow ID']
                    del dataframe['Src IP']
                    del dataframe['Src Port']
                    del dataframe['Dst IP']
                    dataset.extend(dataframe.values)

                self.data_set = np.array(dataset)
                print('Loading dataset set finished')
                self.partition(w, train_ais, train_dnn)

    def partition(self, w, train_ais, train_dnn):
        #   1. convert all string labels to int
        #   2. for each label, create a new dictionary key
        #   3. add all individual instances to dictionary
        #   4. for each label, partition instances into folds
        #   5. convert all malciious instances to labels of 1
        #   6. extend the folds dictionary with individual partitions

        print('Data set partitioning started')

        x = self.data_set[:, 3:-1]
        x.astype('float32')
        y = self.data_set[:, -1]
        # for d in self.data_set:
        #     # if "LOIC-UDP".lower() not in d[-1].lower() and "Infiltration".lower() not in d[-1].lower() and "Bot".lower()\
        #     #         not in d[-1].lower() and 'Benign'.lower() not in d[-1].lower():
        #     x.append(np.array(self.replace_nan_inf(d[3:-1])))
        #     y.append(d[-1])
        #     if "Flow Duration" in d[3:-1]:
        #         print(str(d[3:-1]))

        self.data_set = None
        # self.add_benign_samples_from_file(x, y)

        # Convert X and Y into numpy arrays
        # x = np.array(x, dtype='f8')
        # y = np.array(y)

        # Normalize X features
        self.scalar = MinMaxScaler()
        self.scalar.fit(x)

        # Transform y vector into a matrix
        encoder = LabelEncoder()
        encoder.fit(y)
        self.classes = encoder.classes_
        y_encoded = encoder.transform(y)

        self.number_of_classes = len(encoder.classes_)
        self.save_models()

        if train_ais or train_dnn:
            x_normalized = self.scalar.transform(x)

            if train_ais:
                # Print the min vector and max vector to be read in by Panda
                w.write(str(self.scalar.data_min_[0]))
                for i in range(1, len(self.scalar.data_min_)):
                    w.write(',' + str(self.scalar.data_min_[i]))
                w.write('\n')

                w.write(str(self.scalar.data_max_[0]))
                for i in range(1, len(self.scalar.data_max_)):
                    w.write(',' + str(self.scalar.data_max_[i]))
                w.write('\n')

                w.flush()
                w.close()

            local_instances_x = {}
            local_instances_y = {}

            for i in range(len(y)):
                if y[i] not in local_instances_x:
                    local_instances_x[y[i]] = []
                    local_instances_y[y[i]] = []
                local_instances_x[y[i]].append(x_normalized[i])
                local_instances_y[y[i]].append(y_encoded[i])

            if train_ais:
                self.generate_min_max_list(local_instances_x)

            # take only 10% of each type for the ais validation samples,
            # not to be less than 1000
            # not to exceed 10000 samples
            # num_ben = local_instances_x['Benign']
            # for key, samples in local_instances_x.items():
            #     size = len(samples)
            #     labels = local_instances_y[key]
            #     cutoff = min(int(num_ben/2), len(local_instances_x[key]))
            #
            #     self.ais_instances_x.extend(samples[:cutoff])
            #     self.ais_instances_y.extend(labels[:cutoff])

            # Partition dataset for dnn training,
            # not to be less than 1000
            # not to exceed 100000 samples
            num_ben = len(local_instances_x['Benign'])
            for key, samples in local_instances_x.items():
                if key != 'Benign':  # and key != 'FTP-BruteForce':
                    if key not in self.dnn_instances_x:
                        self.dnn_instances_x[key] = []
                        self.dnn_instances_y[key] = []

                    cutoff = min(num_ben, self.max_samples)

                    # for the given malicious key, determine how many instances I need per fold
                    for i in range(cutoff):
                        # Get a random index to pop from the sample list
                        index = random.randrange(len(samples))

                        # Add the random sample to the current partition
                        self.dnn_instances_x[key].append(samples.pop(index))
                        self.dnn_instances_y[key].append(1)

                        # Get a random index to pop from the sample list
                        # index = random.randrange(len(local_instances_x['Benign']))

                        # Add the random sample to the current partition
                        # self.dnn_instances_x[key].append(local_instances_x['Benign'].pop(index))
                        # self.dnn_instances_y[key].append(0)
                    self.dnn_instances_x[key].extend(local_instances_x['Benign'][:cutoff])
                    self.dnn_instances_y[key].extend(([0] * cutoff))

                    # self.dnn_test_instances_x[key] = []
                    # self.dnn_test_instances_x[key].extend(samples[:cutoff])
                    # ben_samples = local_instances_x['Benign'][cutoff:(cutoff*2)]
                    # self.dnn_test_instances_x[key].extend(ben_samples)
                    # self.dnn_test_instances_y[key] = []
                    # self.dnn_test_instances_y[key].extend(([1] * cutoff))
                    # self.dnn_test_instances_y[key].extend(([0] * len(ben_samples)))

            self.save_samples()

    def generate_min_max_list(self, local_instances_x):

        num_mal = 0
        for key, value in local_instances_x.items():
            if key != 'Benign':
                temp = []
                num_mal = num_mal + len(value)

                i = 0
                for idx in zip(*value):
                    max_val = stats.median(idx)
                    series = pandas.Series(idx)
                    min_val = series.mad()

                    temp.append((min_val, max_val))

                    i += 1
                self.min_max[key] = temp

        return num_mal

    def get_number_of_features(self):
        return self.number_of_features

    def replace_nan_inf(self, x):
        for i in range(len(x)):
            val = float(x[i])

            if math.isinf(val) or math.isnan(val):
                x[i] = 0.0
                # print(val)
            else:
                x[i] = val
        return x

    def get_classes(self):
        return self.classes

    def get_min_max_features_by_type(self, key):
        return self.min_max[key]

    def save_models(self):
        if path.exists(self.scalar_filename):
            os.remove(self.scalar_filename)
        joblib.dump(self.scalar, self.scalar_filename)

        if path.exists(self.classes_filename):
            os.remove(self.classes_filename)
        with open(self.classes_filename, 'wb') as filehandle:
            pickle.dump(self.classes, filehandle)

        if path.exists(self.num_classes_filename):
            os.remove(self.num_classes_filename)
        with open(self.num_classes_filename, 'wb') as filehandle:
            pickle.dump(self.number_of_classes, filehandle)

    def load_models(self):
        print('Loading models')

        if not path.exists(self.scalar_filename) or not path.exists(self.classes_filename) or not path.exists(self.num_classes_filename):
            return False

        self.scalar = joblib.load(self.scalar_filename)
        with open(self.classes_filename, 'rb') as filehandle:
            self.classes = pickle.load(filehandle)
        with open(self.num_classes_filename, 'rb') as filehandle:
            self.number_of_classes = pickle.load(filehandle)
        return True

    def save_samples(self):
        if path.exists(self.dnn_instances_x_filename):
            os.remove(self.dnn_instances_x_filename)
        with open(self.dnn_instances_x_filename, 'wb') as filehandle:
            pickle.dump(self.dnn_instances_x, filehandle)

        if path.exists(self.dnn_instances_y_filename):
            os.remove(self.dnn_instances_y_filename)
        with open(self.dnn_instances_y_filename, 'wb') as filehandle:
            pickle.dump(self.dnn_instances_y, filehandle)

        if path.exists(self.min_max_filename):
            os.remove(self.min_max_filename)
        with open(self.min_max_filename, 'wb') as filehandle:
            pickle.dump(self.min_max, filehandle)

    def load_samples(self):
        print('Loading samples')
        if not path.exists(self.dnn_instances_x_filename) or not path.exists(self.dnn_instances_y_filename):
            return False

        with open(self.min_max_filename, 'rb') as filehandle:
            self.min_max = pickle.load(filehandle)
        with open(self.classes_filename, 'rb') as filehandle:
            self.classes = pickle.load(filehandle)
        with open(self.num_classes_filename, 'rb') as filehandle:
            self.number_of_classes = pickle.load(filehandle)
        with open(self.dnn_instances_x_filename, 'rb') as filehandle:
            self.dnn_instances_x = pickle.load(filehandle)
        with open(self.dnn_instances_y_filename, 'rb') as filehandle:
            self.dnn_instances_y = pickle.load(filehandle)
        return True
