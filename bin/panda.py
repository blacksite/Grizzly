
from common.models import NeuralNetworkNSA
import numpy as np


class DetectorSet:

    def __init__(self, data_set, validator, writer):
        self.validator = validator
        self.data_set = data_set
        self.writer = writer
        self.number_of_detectors = 100

        self.model = self.define_model()

        self.train_detectors()

    def define_model(self):
        model = NeuralNetworkNSA()

        return model

    def train_detectors(self):

        training_x, training_y = self.data_set.ais_instances_x, self.data_set.ais_instances_y

        self.model.fit(np.array(training_x, dtype='f4'), np.array(training_y, dtype='i4'),
                       self.data_set, self.validator, self.number_of_detectors)

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
