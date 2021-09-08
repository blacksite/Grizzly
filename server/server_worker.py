import server.dvcp_handler as dvcp
import server.dgp_handler as bgp
import properties
from datetime import datetime

connected_appliances = {}


def thread(dnn_models, connection, ip, data_set=None):
    update_connected_appliances(ip)
    try:
        data = connection.recv(4096)

        version = data[properties.VERSION_LOCATION] >> 4
        protocol = data[properties.PROTOCOL_LOCATION] - (data[properties.PROTOCOL_LOCATION] >> 4 << 4)
        flags = data[properties.FLAGS_LOCATION] >> 4

        if version != 1:
            print("Incompatible BSP version " + str(version))
            return

        first_byte = data[properties.VERSION_LOCATION].to_bytes(1, byteorder='little')

        # ---------------------SP---------------------
        if protocol == properties.SP_PROTOCOL:

            if flags == properties.SP_REQUEST_FLAG:
                # shift the flags left by 4
                res_flags = 1 << 4
                second_byte = res_flags.to_bytes(1, byteorder='little')
                third_fourth_byte = properties.HEADER_SIZE.to_bytes(2, byteorder='little')

                res_string = first_byte + second_byte + third_fourth_byte
                connection.send(res_string)
            elif flags != properties.SP_RESPONSE_FLAG:
                print("Unrecognized flag for SP - " + str(flags))
                return

        # ---------------------IDP---------------------
        elif protocol == properties.IDP_PROTOCOL:
            # Initial detector request
            print("Unsupported protocol - IDP")

        # ---------------------DVCP---------------------
        elif protocol == properties.DVCP_PROTOCOL:
            sample_string = data[properties.LENGTH_LOCATION + properties.LENGTH_SIZE:]
            # DET packet
            if flags == properties.DVCP_DET_FLAG:
                # DVCP

                rtr_string = dvcp.det(dnn_models, sample_string)

                # shift the flags left by 4
                res_flags = 1 << 4
                second_byte = res_flags.to_bytes(1, byteorder='little')
                third_fourth_byte = (properties.HEADER_SIZE + properties.BYTE_SIZE).to_bytes(2, byteorder='little')

                res_string = first_byte + second_byte + third_fourth_byte + rtr_string
                connection.send(res_string)
            elif flags == properties.DVCP_ACK_FLAG:
                # ACK Packet
                dvcp.ack(data_set, dnn_models, sample_string)
            else:
                print("Unrecognized flag for DVCP - " + str(flags))
                return

        # ---------------------DGP---------------------
        elif protocol == properties.DGP_PROTOCOL:
            if flags == properties.DGP_REG_FLAG:
                encoded_mal_type = data[properties.LENGTH_LOCATION + properties.LENGTH_SIZE]
                rtr_string = bgp.reg(dnn_models, data_set, encoded_mal_type)

                # shift the flags left by 4
                res_flags = 1 << 4
                second_byte = res_flags.to_bytes(1, byteorder='little')
                third_fourth_byte = (
                            properties.HEADER_SIZE +
                            properties.DETECTOR_NUMBER_OF_FLOAT_VALUES * properties.FLOAT_SIZE * properties.BYTE_SIZE)\
                    .to_bytes(2, byteorder='little')

                res_string = first_byte + second_byte + third_fourth_byte + rtr_string
                connection.send(res_string)
            elif flags != properties.DGP_DEV_FLAG:
                print("Unrecognized flag for BGP - " + str(flags))
                return

        # ---------------------UNRECOGNIZED---------------------
        else:
            print("Unrecognized protocol " + str(protocol))
            return

        connection.close()

    except Exception as ex:
        print(ex)


def update_connected_appliances(ip):
    global connected_appliances
    connected_appliances[ip] = datetime.now()
