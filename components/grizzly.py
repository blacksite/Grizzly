from keras.models import Sequential
from keras.layers import Dense
import keras.metrics as km
import numpy as np
from tensorflow import keras
from os import path
import threading
from cache.dataset import DataSet


# Disable GPU otimization
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class DNN:

    def __init__(self, type, data_set):
        self.file_name = "../out/" + type + '.dnn'
        self.batch_size = 80
        self.type = type
        self.data_set = data_set
        self.lock = threading.Lock()

        self.model = self.define_model()
        self.train_dnn()

    def define_model(self):
        hidden_nodes = int(self.data_set.number_of_features / 2)
        # create and fit the DNN network
        model = Sequential()
        model.add(Dense(hidden_nodes, input_dim=self.data_set.number_of_features, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer='adam',
                      metrics=["accuracy", km.TruePositives(), km.FalsePositives(), km.TrueNegatives(),
                               km.FalseNegatives()])
        return model

    def train_dnn(self):

        print("Starting dnn training for " +str(self.type))

        # create training and testing x and y datasets from the kFolds
        training_x, training_y = self.data_set.instances_x[self.type], self.data_set.instances_y[self.type]

        # begin training the models
        self.model.fit(np.array(training_x), np.array(training_y), self.batch_size, epochs=100, verbose=0)

        self.save_dnn()
        print("Finished dnn training for " + str(self.type))

    def save_dnn(self):
        self.model.save(self.file_name)

    def load_dnn(self, filename):
        while True:
            if not path.exists(filename):
                filename = input("The entered file does not exist. Please re-enter a file name\n")
            else:
                break

        self.model = keras.models.load_model(filename)

    def classify(self, value):

        if self.model:
                self.lock.acquire()
                classification = self.model.predict_classes(np.array([value]))[0][0]
                self.lock.release()

                return classification
        else:
            print("No DNN available")
            exit(-1)
