from common.detector import Detector
import parameters as props
import struct


def reg(dnn_models, data_set, encoded_mal_type):
    rtr_string = bytearray()

    while True:
        unencoded_mal_type = data_set.classes[encoded_mal_type]
        seed = data_set.min_max[unencoded_mal_type]
        num_features = data_set.number_of_features
        detector = Detector(num_features=num_features, seed=seed)

        classification = dnn_models[unencoded_mal_type].classify(detector.get_mean_value())
        # class_value = classes[classification]
        # self.lock.release()

        # if class_value != 'Benign':
        if classification == 1:
            values = detector.get_value()

            for (v1, v2) in values:
                rtr_string += float_to_bytes(v1) + float_to_bytes(v2)

            break

    return rtr_string


def float_to_bytes(f):
    return bytearray(struct.pack('<f', f))