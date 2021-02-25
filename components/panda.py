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
                  self.data_set.number_of_features, self.dnn, self.data_set.mean_mad,
                  number_of_detectors=self.number_of_detectors)

        for d in self.model.detector_objects:
            self.writer.write(str(d.value[0]))
            for i in range(1, len(d.value)):
                self.writer.write(',' + str(d.value[i]))
            self.writer.write('\n')

        self.writer.flush()
        self.writer.close()

        self.model.teardown()

        del self.model
