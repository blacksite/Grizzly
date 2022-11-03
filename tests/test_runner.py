from tests.test_socket import socket
from tests.test_sample import sample
import bin.server.bcp_server as sw
import parameters as props
import bin.main as main
import pandas
import os
from os import walk
from os import path
import numpy as np
# import unittest
from sklearn.preprocessing import LabelEncoder


def main_tests():
    try:

        main.dnn_init(False)

        data_directory = 'data'

        filename = ''
        if os.path.isdir(data_directory):

            directories = []
            files = []
            for (dirpath, dirnames, files) in walk(data_directory):
                directories.extend(dirnames)
                break

            if len(files) == 0:
                print('No dataset set files found')
                os._exit(-1)
            else:
                filename = data_directory + '/' + files[0]

                for i in range(1, len(files)):
                    filename += ',' + data_directory + '/' + files[i]

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

        dataset = np.array(dataset)
        x = dataset[:, 3:-1]
        x.astype('float32')
        y = dataset[:, -1]

        x_normalized = main.data_set.scalar.transform(x)
        # Transform y vector into a matrix
        encoder = LabelEncoder()
        encoder.fit(y)
        y_encoded = encoder.transform(y)

        classifications = {}

        for key, model in main.dnn_models.items():
            if key not in classifications:
                classifications[key] = []
            for samp in x_normalized:
                out = model.classify(samp)
                classifications[key].append(out)

        print('Done')

        # main.data_set_init()
        print("Main test - success")

        return True
    except Exception as e:
        print(e)
        return False


def status_req_test():
    try:
        first_byte = (props.DEFAULT_VERSION << 4 | props.SP_PROTOCOL).to_bytes(1, byteorder='little')

        res_flags = props.SP_REQUEST_FLAG << 4
        second_byte = res_flags.to_bytes(1, byteorder='little')
        third_fourth_byte = props.HEADER_SIZE.to_bytes(2, byteorder='little')

        data = first_byte + second_byte + third_fourth_byte
        c = socket(data)

        sw.thread(main.dnn_models, c, '127.0.0.1', main.data_set)
        print("SP Request test - success")

        return True
    except Exception as e:
        print(e)
        return False


def status_res_test():
    try:
        first_byte = (props.DEFAULT_VERSION << 4 | props.SP_PROTOCOL).to_bytes(1, byteorder='little')

        res_flags = props.SP_RESPONSE_FLAG << 4
        second_byte = res_flags.to_bytes(1, byteorder='little')
        third_fourth_byte = props.HEADER_SIZE.to_bytes(2, byteorder='little')

        data = first_byte + second_byte + third_fourth_byte
        c = socket(data)

        sw.thread(main.dnn_models, c, '127.0.0.1', main.data_set)
        print("SP Response test - success")

        return True
    except Exception as e:
        print(e)
        return False


def dvcp_det_test():
    try:
        first_byte = (props.DEFAULT_VERSION << 4 | props.DVCP_PROTOCOL).to_bytes(1, byteorder='little')

        res_flags = props.DVCP_DET_FLAG
        second_byte = res_flags.to_bytes(1, byteorder='little')
        third_fourth_byte = props.HEADER_SIZE.to_bytes(2, byteorder='little')

        data = first_byte + second_byte + third_fourth_byte + sample().get_data()

        c = socket(data)

        sw.thread(main.dnn_models, c, '127.0.0.1', main.data_set)
        print("DVCP Detection test - success")

        return True
    except Exception as e:
        print(e)
        return False


def dvcp_ack_test():
    try:
        first_byte = (props.DEFAULT_VERSION << 4 | props.DVCP_PROTOCOL).to_bytes(1, byteorder='little')

        res_flags = props.DVCP_ACK_FLAG << 4
        second_byte = res_flags.to_bytes(1, byteorder='little')
        third_fourth_byte = props.HEADER_SIZE.to_bytes(2, byteorder='little')

        data = \
            first_byte + \
            second_byte + \
            third_fourth_byte + \
            sample().get_data() + \
            (1).to_bytes(1, byteorder='little') + \
            (1).to_bytes(1, byteorder='little')

        c = socket(data)

        sw.thread(main.dnn_models, c, '127.0.0.1', main.data_set)
        print("DVCP Acknowledgement test - success")

        return True
    except Exception as e:
        print(e)
        return False


def dgp_reg_test():
    try:
        first_byte = (props.DEFAULT_VERSION << 4 | props.DGP_PROTOCOL).to_bytes(1, byteorder='little')

        res_flags = props.DGP_REG_FLAG << 4
        second_byte = res_flags.to_bytes(1, byteorder='little')
        third_fourth_byte = props.HEADER_SIZE.to_bytes(2, byteorder='little')

        data = first_byte + second_byte + third_fourth_byte + (1).to_bytes(1, byteorder='little')

        c = socket(data)

        sw.thread(main.dnn_models, c, '127.0.0.1', main.data_set)
        print("DGP Regeneration test - success")

        return True
    except Exception as e:
        print(e)
        return False


def dgp_dev_test():
    try:
        first_byte = (props.DEFAULT_VERSION << 4 | props.DGP_PROTOCOL).to_bytes(1, byteorder='little')

        res_flags = props.DGP_DEV_FLAG << 4
        second_byte = res_flags.to_bytes(1, byteorder='little')
        third_fourth_byte = props.HEADER_SIZE.to_bytes(2, byteorder='little')

        data = first_byte + second_byte + third_fourth_byte

        c = socket(data)

        sw.thread(main.dnn_models, c, '127.0.0.1', main.data_set)
        print("DGP Detector Values test - success")

        return True
    except Exception as e:
        print(e)
        return False


# class TestServerFunction(unittest.TestCase):
#     def test_main(self):
#         self.assert_(main_tests())
#
#     def test_sp_req(self):
#         self.assert_(status_req_test())
#
#     def test_sp_res(self):
#         self.assert_(status_res_test())
#
#     def test_dvcp_det(self):
#         self.assert_(dvcp_det_test())
#
#     def test_dvcp_ack(self):
#         self.assert_(dvcp_ack_test())
#
#     def test_dgp_reg(self):
#         self.assert_(dgp_reg_test())
#
#     def test_dgp_dev(self):
#         self.assert_(dgp_dev_test())


if __name__ == '__main__':
    assert main_tests()
    # assert status_req_test()
    # assert status_res_test()
    # assert dvcp_det_test()
    # assert dvcp_ack_test()
    # assert dgp_reg_test()
    # assert dgp_dev_test()

