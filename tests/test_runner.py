from tests.test_socket import socket
from tests.test_sample import sample
import bin.server.server_worker as sw
import parameters as props
import bin.main as main
# import unittest


def main_tests():
    try:
        main.dnn_init()
        main.data_directory = '../tests/data'
        main.data_set_init()
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
    assert status_req_test()
    assert status_res_test()
    assert dvcp_det_test()
    assert dvcp_ack_test()
    assert dgp_reg_test()
    assert dgp_dev_test()

