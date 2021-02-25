def server_thread(dnn_models, data_set, connection):
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
    except Exception as ex:
        print(ex)
