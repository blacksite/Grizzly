from common.detector import Detector


def classification_thread(dnn_models, data_set, connection, queue):
    try:
        # key_length = int(connection.recv(8))
        # key = connection.recv(key_length).decode("utf-8")
        # detector_id = connection.recv(128).decode("utf-8")
        #
        # sample_value = []
        #
        # for i in range(data_set.number_of_features):
        #     value_length = int(connection.recv(8))
        #     sample_value.append(float(connection.recv(value_length).decode("utf-8")))

        rec_string = connection.recv(4096).decode("utf-8")
        rec_values = rec_string.split(',')
        key = rec_values[0]
        detector_id = rec_values[1]
        sample_value = [float(x) for x in rec_values[2:]]

        classification = dnn_models[key].classify(sample_value)

        if classification == '1':
            connection.send('true'.encode())
        else:
            connection.send('false'.encode())

        connection.close()

        sample_value.append(classification)
        queue.put(sample_value)

    except Exception as ex:
        print(ex)


def regeneration_thread(dnn_models, data_set, connection):
    try:
        type = connection.recv(512).decode("utf-8")

        while True:
            seed = data_set.min_max[type]
            num_features = data_set.number_of_features
            detector = Detector(num_features=num_features, seed=seed)

            classification = dnn_models[type].classify(detector.get_mean_value())
            # class_value = classes[classification]
            # self.lock.release()

            # if class_value != 'Benign':
            if classification == 1:
                value = detector.get_value()

                send_string = str(value[0][0]) + ',' + str(value[0][1])

                for i in range(1,len(value)):
                    send_string += ',' + str(value[i][0]) + ',' + str(value[i][1])

                connection.send(send_string.encode())

                break

        connection.close()
    except Exception as ex:
        print(ex)
