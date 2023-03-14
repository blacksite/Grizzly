
from common.models import NeuralNetworkNSA
import numpy as np


class DetectorSet:

    def __init__(self, data_set, validator, writer):
        self.validator = validator
        self.data_set = data_set
        self.writer = writer
        self.number_of_detectors = 50

        self.model = None

        self.train_detectors()

    # def define_model(self):
        #model = NeuralNetworkNSA()

        #return model

    def train_detectors(self):
        self.writer.write(str(self.number_of_detectors) + '\n')

        for mal_type in range(1, len(self.data_set.classes)):
            key = self.data_set.classes[mal_type]
            training_x, training_y = self.data_set.dnn_instances_x[key], self.data_set.dnn_instances_y[key]

            self.model = NeuralNetworkNSA(mal_type)
            self.model.fit(np.array(training_x, dtype='f4'), np.array(training_y, dtype='i4'),
                           self.data_set, self.validator, self.number_of_detectors)

            self.writer.write(str(self.model.best_r_value) + '\n')
            for d in self.model.detector_objects:
                value = d.get_value()
                self.writer.write(str(value[0][0]) + ',' + str(value[0][1]))
                for i in range(1, len(value)):
                    self.writer.write(',' + str(value[i][0]) + ',' + str(value[i][1]))
                self.writer.write(',' + str(d.TYPE))
                self.writer.write('\n')
            self.model.teardown()

        self.writer.flush()
        self.writer.close()


