import properties as props
import struct

sample = {}
UUID_STR = 'DETECTOR_UUID'
SRC_IP_STR = 'SOURCE_IP'
DST_IP_STR = 'DESTINATION_IP'
SRC_PORT_STR = 'SOURCE_PORT'
DST_PORT_STR = 'DESTINATION_PORT'
PROTOCOL_STR = 'PROTOCOL'
VALUES_STR = 'VALUES'


def det(dnn_models, sample_string):
    global sample

    parse_sample(sample_string)

    for key, model in dnn_models.items():
        classification = model.classify(sample[VALUES_STR])

        if classification == 1:
            send_validated_sample_to_sys_admin()
            return (1).to_bytes(1, 'little')

    return (0).to_bytes(1, 'little')


def ack(data_set, dnn_models, sample_string):
    global sample
    global VALUES_STR

    # Get the sample values
    parse_sample(sample_string)

    # Second to last byte is the malicious type
    encoded_mal_type = int(sample_string[-2])
    unencoded_mal_type = data_set.classes[encoded_mal_type]

    # Last byte is the System Administrators decision
    decision = int(sample_string[-1])

    values = sample[VALUES_STR]
    values.append(decision)

    # Add the sample to the corresponding DNNs queue
    dnn_models[unencoded_mal_type].queue.append(values)


def send_validated_sample_to_sys_admin():

    return 1


def parse_sample(sample_string):
    global sample
    global UUID_STR
    global SRC_IP_STR
    global DST_IP_STR
    global SRC_PORT_STR
    global DST_PORT_STR
    global PROTOCOL_STR
    global VALUES_STR

    sample = {}

    # Get the detector UUID
    start = 0
    end = props.UUID_SIZE
    detector_uuid = sample_string[start:end]

    # Get the src and dest ip addresses
    start = end
    end = end + props.IP_ADDRESS_SIZE
    src_ip = sample_string[start:end]
    start = end
    end = end + props.IP_ADDRESS_SIZE
    dst_ip = sample_string[start:end]

    # Get the src and dst port numbers
    start = end
    end = end + props.TCP_UDP_PORT_SIZE
    src_port = sample_string[start:end]
    start = end
    end = end + props.TCP_UDP_PORT_SIZE
    dst_port = sample_string[start:end]

    # Get the protocol value
    start = end
    protocol = sample_string[start]

    # Get the remaining bytes for the sample values
    start += props.IP_PROTOCOL_SIZE
    values = []
    for i in range(props.SAMPLE_NUMBER_OF_FLOAT_VALUES):
        # Convert 4 bytes into a float
        if start + props.FLOAT_SIZE >= len(sample_string):
            byte_value = sample_string[start:]
        else:
            byte_value = sample_string[start:(start + props.FLOAT_SIZE)]

        converted_value = bytes_to_float(byte_value)

        # Add the float value to the values list
        values.append(converted_value)

        start += props.FLOAT_SIZE

    sample[UUID_STR] = detector_uuid
    sample[SRC_IP_STR] = src_ip
    sample[DST_IP_STR] = dst_ip
    sample[SRC_PORT_STR] = src_port
    sample[DST_PORT_STR] = dst_port
    sample[PROTOCOL_STR] = protocol.to_bytes(1, 'little')
    sample[VALUES_STR] = values


def bytes_to_float(b):
    return struct.unpack('<f', b)[0]
