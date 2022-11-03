import parameters as props
import random
import struct
import uuid

class sample:

    def __init__(self):
        self.uuid = uuid.uuid4().int.to_bytes(16, byteorder='little')

        self.src_ip = (127).to_bytes(1, byteorder='little') + \
                      (0).to_bytes(1, byteorder='little') + \
                      (0).to_bytes(1, byteorder='little') + \
                      (1).to_bytes(1, byteorder='little')

        self.dst_ip = (192).to_bytes(1, byteorder='little') + \
                      (168).to_bytes(1, byteorder='little') + \
                      (0).to_bytes(1, byteorder='little') + \
                      (1).to_bytes(1, byteorder='little')

        self.src_port = (14567).to_bytes(2, byteorder='little')
        self.dst_port = (80).to_bytes(2, byteorder='little')
        self.protocol = (6).to_bytes(1, byteorder='little')

        self.value = []
        self.generate_sample_values()

    def generate_sample_values(self):
        for x in range(props.SAMPLE_NUMBER_OF_FLOAT_VALUES):
            self.value.append(random.random())

    def get_data(self):
        res_string = self.uuid + self.src_ip + self.dst_ip + self.src_port + self.dst_port + self.protocol

        for v in self.value:
            res_string += float_to_bytes(v)

        return res_string


def float_to_bytes(f):
    return bytearray(struct.pack('<f', f))
