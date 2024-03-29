from keras.models import Sequential
from keras.layers import Dense
import keras.metrics as km
import numpy as np
from tensorflow import keras
from os import path
import threading
import os
import time
from Grizzly import parameters as props
import shutil

# Disable GPU otimization
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


class DNN:

    def __init__(self, out_dir, key, data_set=None):
        self.file_name = out_dir + '/' + key
        self.batch_size = 80
        self.key = key
        self.data_set = data_set
        self.lock = threading.Lock()
        self.model = None
        self.queue = []
        self.retraining_thread = threading.Thread(target=self.retraining_worker)
        self.continue_retraining = True

    def define_model(self):
        hidden_nodes = int(self.data_set.number_of_features / 2)
        # create and fit the DNN network
        model = Sequential()
        model.add(Dense(hidden_nodes, input_dim=self.data_set.get_number_of_features(), activation='relu'))
        model.add(Dense(60, activation='relu'))
        model.add(Dense(50, activation='relu'))
        model.add(Dense(40, activation='relu'))
        model.add(Dense(30, activation='relu'))
        model.add(Dense(20, activation='relu'))
        model.add(Dense(10, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer='adam',
                      metrics=["accuracy", km.TruePositives(), km.FalsePositives(), km.TrueNegatives(),
                               km.FalseNegatives()])
        return model

    def train_dnn(self):

        print("Starting dnn training for " + str(self.key))

        self.model = self.define_model()

        # create training and testing x and y datasets from the kFolds
        training_x, training_y = self.data_set.dnn_instances_x[self.key], self.data_set.dnn_instances_y[self.key]

        # begin training the models
        self.model.fit(np.array(training_x), np.array(training_y), batch_size=self.batch_size, epochs=100, verbose=2)

        # test_x, test_y = self.data_set.dnn_test_instances_x[self.key], self.data_set.dnn_test_instances_y[self.key]
        # results = self.model.evaluate(np.array(test_x), np.array(test_y), batch_size=self.batch_size, verbose=2)
        # for r in results:
        #     print(str(r) + ' ')
        self.save_dnn()
        print("Finished dnn training for " + str(self.key))

        self.retraining_thread.start()

    def save_dnn(self):
        if path.exists(self.file_name):
            if path.isfile(self.file_name):
                os.remove(self.file_name)
            elif path.isdir(self.file_name):
                shutil.rmtree(self.file_name)

        self.model.save(self.file_name)

    def load_dnn(self):
        while True:
            if not path.exists(self.file_name):
                self.file_name = input("The entered file does not exist. Please re-enter a file name\n")
            else:
                break

        self.model = keras.models.load_model(self.file_name)

        self.retraining_thread.start()

    def classify(self, value):

        if self.model:
            self.lock.acquire()
            out = self.model.predict(np.array([value]))[0][0]
            if out > 0.5:
                classification = 1
            else:
                classification = 0
            # classification = int( > 0.5)
            self.lock.release()

            return classification
        else:
            print("No DNN available")
            os.exit(-1)

    def retrain_dnn(self,):
        model = self.define_model()
        x = np.array(self.queue)[:, :-1]
        y = np.array(self.queue[:, -1])
        model.fit(x, y, self.batch_size, epochs=100, verbose=0)
        self.lock.acquire()
        self.model = model
        self.lock.release()

    def retraining_worker(self):
        last_retrain = time.time()
        while self.continue_retraining:
            current_time = time.time()
            if current_time - last_retrain > props.RETRAINING_INTERVAL:
                self.retrain_dnn()
                last_retrain = time.time()

    def close(self):
        self.continue_retraining = False
        self.save_dnn()
