from . import dvcp_handler as dvcp
from . import dgp_handler as dgp
import parameters
from datetime import datetime
import select

connected_appliances = {}


def thread(dnn_models, connection, ip, data_set):
    update_connected_appliances(ip)

    ready = select.select([connection], [], [])
    while True:
        try:
            if ready[0]:
                data = connection.recv(4096)
                if len(data) == 0:
                    continue
                version = data[parameters.VERSION_LOCATION] >> 4
                protocol = data[parameters.PROTOCOL_LOCATION] - (data[parameters.PROTOCOL_LOCATION] >> 4 << 4)
                flags = data[parameters.FLAGS_LOCATION] >> 4

                if version != 1:
                    print("Incompatible BCP version " + str(version))
                    # return

                first_byte = data[parameters.VERSION_LOCATION].to_bytes(1, byteorder='little')

                # ---------------------SP---------------------
                if protocol == parameters.SP_PROTOCOL:

                    if flags == parameters.SP_REQUEST_FLAG:
                        # shift the flags left by 4
                        res_flags = 1 << 4
                        second_byte = res_flags.to_bytes(1, byteorder='little')
                        third_fourth_byte = parameters.HEADER_SIZE.to_bytes(2, byteorder='little')

                        res_string = first_byte + second_byte + third_fourth_byte
                        connection.send(res_string)
                    elif flags != parameters.SP_RESPONSE_FLAG:
                        print("Unrecognized flag for SP - " + str(flags))
                        # return

                # ---------------------IDP---------------------
                elif protocol == parameters.IDP_PROTOCOL:
                    # Initial detector request
                    print("Unsupported protocol - IDP")

                # ---------------------DVCP---------------------
                elif protocol == parameters.DVCP_PROTOCOL:
                    sample_string = data[parameters.LENGTH_LOCATION + parameters.LENGTH_SIZE:]
                    # DET packet
                    if flags == parameters.DVCP_DET_FLAG:
                        # DVCP

                        rtr_string = dvcp.det(data_set, dnn_models, sample_string)

                        # shift the flags left by 4
                        res_flags = 1 << 4
                        second_byte = res_flags.to_bytes(1, byteorder='little')
                        third_fourth_byte = (parameters.HEADER_SIZE + parameters.BYTE_SIZE).to_bytes(2, byteorder='little')

                        res_string = first_byte + second_byte + third_fourth_byte + rtr_string
                        connection.send(res_string)
                    elif flags == parameters.DVCP_ACK_FLAG:
                        # ACK Packet
                        dvcp.ack(data_set, dnn_models, sample_string)
                    else:
                        print("Unrecognized flag for DVCP - " + str(flags))
                        # return

                # ---------------------DGP---------------------
                elif protocol == parameters.DGP_PROTOCOL:
                    if flags == parameters.DGP_REG_FLAG:
                        encoded_mal_type = data[parameters.LENGTH_LOCATION + parameters.LENGTH_SIZE]
                        rtr_string = dgp.reg(dnn_models, data_set, encoded_mal_type)

                        # shift the flags left by 4
                        res_flags = parameters.DGP_DEV_FLAG << 4
                        second_byte = res_flags.to_bytes(1, byteorder='little')
                        third_fourth_byte = (
                                parameters.HEADER_SIZE +
                                parameters.DETECTOR_NUMBER_OF_FLOAT_VALUES * parameters.FLOAT_SIZE * parameters.BYTE_SIZE)\
                            .to_bytes(2, byteorder='little')

                        res_string = first_byte + second_byte + third_fourth_byte + rtr_string
                        connection.send(res_string)
                    elif flags != parameters.DGP_DEV_FLAG:
                        print("Unrecognized flag for BGP - " + str(flags))
                        # return

                # ---------------------UNRECOGNIZED---------------------
                else:
                    print("Unrecognized protocol " + str(protocol))
                    # return

                # connection.close()

        except Exception as ex:
            print(ex)
            return


def update_connected_appliances(ip):
    global connected_appliances
    connected_appliances[ip] = datetime.now()
