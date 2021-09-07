from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import threading
from models import NeuralNetworkNSA
import numpy as np


class DetectorSet:

    def __init__(self, type, data_set, dnn, writer):
        self.type = type
        self.dnn = dnn
        self.data_set = data_set
        self.writer = writer
        self.number_of_detectors = 100000

        self.model = self.define_model()

        self.train_detectors()

    def define_model(self):
        model = NeuralNetworkNSA()

        return model

    def train_detectors(self):

        training_x, training_y = self.data_set.instances_x[self.type], self.data_set.instances_y[self.type]

        self.model.fit(np.array(training_x, dtype='f4'), np.array(training_y, dtype='i4'), self.data_set.classes,
                       self.data_set.number_of_features, self.dnn, self.data_set.min_max[self.type],
                       self.number_of_detectors)

        self.writer.write(str(self.model.best_r_value) + '\n')
        for d in self.model.detector_objects:
            value = d.get_value()
            self.writer.write(str(value[0][0]) + ',' + str(value[0][1]))
            for i in range(1, len(value)):
                self.writer.write(',' + str(value[i][0]) + ',' + str(value[i][1]))
            self.writer.write('\n')

        self.writer.flush()
        self.writer.close()

        self.model.teardown()
