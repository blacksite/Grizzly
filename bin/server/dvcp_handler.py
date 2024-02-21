import parameters as props
import struct
import pymongo
import numpy as np
import ssl
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

sample = {}
UUID_STR = 'DetUUID'
SRC_IP_STR = 'SrcIP'
DST_IP_STR = 'DstIP'
SRC_PORT_STR = 'SrcPort'
DST_PORT_STR = 'DstPort'
PROTOCOL_STR = 'Protocol'
VALUES_STR = 'VALUES'
TYPE = 'Type'
MY_CLIENT = pymongo.MongoClient("mongodb+srv://mcarby991:"+os.environ['MONGODB_SECRET']+"@cluster0.z7en3rk.mongodb.net/?retryWrites=true&w=majority")
MY_DB = MY_CLIENT["blacksite"]
MY_COL = MY_DB["samples"]


def det(data_set, dnn_models, sample_string):
    global sample
    try:
        # print('Det')
        parse_sample(sample_string)
        sample2 = sample
        classes = data_set.get_classes()
        key = classes[sample2[TYPE]]
        classification = dnn_models[key].classify(sample2[VALUES_STR])
        classification = 0
        for key, value in dnn_models.items():
            out = value.classify(sample2[VALUES_STR])
            if out == 1:
                classification = 1
                break

        # send_validated_sample_to_sys_admin(data_set)
        if classification == 1:
            send_validated_sample_to_sys_admin(data_set)
            return (1).to_bytes(1, 'little')

        return (0).to_bytes(1, 'little')
    except Exception as e:
        print(e)
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


def send_validated_sample_to_sys_admin(data_set):
    global MY_COL
    global sample

    # print('send')
    src_ip = str(sample[SRC_IP_STR][0]) + "." + str(sample[SRC_IP_STR][1]) + "." + str(sample[SRC_IP_STR][2]) + "." + str(sample[SRC_IP_STR][3])
    src_port = str(int.from_bytes(sample[SRC_PORT_STR], "little"))
    dst_ip = str(sample[DST_IP_STR][0]) + "." + str(sample[DST_IP_STR][1]) + "." + str(sample[DST_IP_STR][2]) + "." + str(sample[DST_IP_STR][3])
    dst_port = str(int.from_bytes(sample[DST_PORT_STR], "little"))
    try:
        protocol = str(int.from_bytes(sample[PROTOCOL_STR],'little'))
    except:
        protocol = str(sample[PROTOCOL_STR])

    mydict = {}
    mydict["FlowID"] = src_ip + "-" + dst_ip + "-" +src_port+ "-" +dst_port+ "-" +protocol
    mydict[UUID_STR] = sample[UUID_STR].hex()
    mydict[SRC_IP_STR] = src_ip
    mydict[SRC_PORT_STR] = src_port
    mydict[DST_IP_STR] = dst_ip
    mydict[DST_PORT_STR] = dst_port
    mydict[PROTOCOL_STR] = protocol

    ts = datetime.datetime.now()
    mydict["Timestamp"] = str(ts)

    unnormalized = data_set.scalar.inverse_transform(np.array([sample[VALUES_STR]]))[0]

    mydict["FlowDuration"] = unnormalized[0]
    mydict["TotFwdPkts"] = unnormalized[1]
    mydict["TotBwdPkts"] = unnormalized[2]
    mydict["TotLenFwdPkts"] = unnormalized[3]
    mydict["TotLenBwdPkts"] = unnormalized[4]
    mydict["FwdPktLenMax"] = unnormalized[5]
    mydict["FwdPktLenMin"] = unnormalized[6]
    mydict["FwdPktLenMean"] = unnormalized[7]
    mydict["FwdPktLenStd"] = unnormalized[8]
    mydict["BwdPktLenMax"] = unnormalized[9]
    mydict["BwdPktLenMin"] = unnormalized[10]
    mydict["BwdPktLenMean"] = unnormalized[11]
    mydict["BwdPktLenStd"] = unnormalized[12]
    mydict["FlowBytss"] = unnormalized[13]
    mydict["FlowPktss"] = unnormalized[14]
    mydict["FlowIATMean"] = unnormalized[15]
    mydict["FlowIATStd"] = unnormalized[16]
    mydict["FlowIATMax"] = unnormalized[17]
    mydict["FlowIATMin"] = unnormalized[18]
    mydict["FwdIATTot"] = unnormalized[19]
    mydict["FwdIATMean"] = unnormalized[20]
    mydict["FwdIATStd"] = unnormalized[21]
    mydict["FwdIATMax"] = unnormalized[22]
    mydict["FwdIATMin"] = unnormalized[23]
    mydict["BwdIATTot"] = unnormalized[24]
    mydict["BwdIATMean"] = unnormalized[25]
    mydict["BwdIATStd"] = unnormalized[26]
    mydict["BwdIATMax"] = unnormalized[27]
    mydict["BwdIATMin"] = unnormalized[28]
    mydict["FwdPSHFlags"] = unnormalized[29]
    mydict["BwdPSHFlags"] = unnormalized[30]
    mydict["FwdURGFlags"] = unnormalized[31]
    mydict["BwdURGFlags"] = unnormalized[32]
    mydict["FwdHeaderLen"] = unnormalized[33]
    mydict["BwdHeaderLen"] = unnormalized[34]
    mydict["FwdPktss"] = unnormalized[35]
    mydict["BwdPktss"] = unnormalized[36]
    mydict["PktLenMin"] = unnormalized[37]
    mydict["PktLenMax"] = unnormalized[38]
    mydict["PktLenMean"] = unnormalized[39]
    mydict["PktLenStd"] = unnormalized[40]
    mydict["PktLenVarv"] = unnormalized[41]
    mydict["FINFlagCnt"] = unnormalized[42]
    mydict["SYNFlagCnt"] = unnormalized[43]
    mydict["RSTFlagCnt"] = unnormalized[44]
    mydict["PSHFlagCnt"] = unnormalized[45]
    mydict["ACKFlagCnt"] = unnormalized[46]
    mydict["URGFlagCnt"] = unnormalized[47]
    mydict["CWEFlagCount"] = unnormalized[48]
    mydict["ECEFlagCnt"] = unnormalized[49]
    mydict["DownUpRatio"] = unnormalized[50]
    mydict["PktSizeAvg"] = unnormalized[51]
    mydict["FwdSegSizeAvg"] = unnormalized[52]
    mydict["BwdSegSizeAvg"] = unnormalized[53]
    mydict["FwdBytsbAvg"] = unnormalized[54]
    mydict["FwdPktsbAvg"] = unnormalized[55]
    mydict["FwdBlkRateAvg"] = unnormalized[56]
    mydict["BwdBytsbAvg"] = unnormalized[57]
    mydict["BwdPktsbAvg"] = unnormalized[58]
    mydict["BwdBlkRateAvg"] = unnormalized[59]
    mydict["SubflowFwdPkts"] = unnormalized[60]
    mydict["SubflowFwdByts"] = unnormalized[61]
    mydict["SubflowBwdPkts"] = unnormalized[62]
    mydict["SubflowBwdByts"] = unnormalized[63]
    mydict["InitFwdWinByts"] = unnormalized[64]
    mydict["InitBwdWinByts"] = unnormalized[65]
    mydict["FwdActDataPkts"] = unnormalized[66]
    mydict["FwdSegSizeMin"] = unnormalized[67]
    mydict["ActiveMean"] = unnormalized[68]
    mydict["ActiveStd"] = unnormalized[69]
    mydict["ActiveMax"] = unnormalized[70]
    mydict["ActiveMin"] = unnormalized[71]
    mydict["IdleMean"] = unnormalized[72]
    mydict["IdleStd"] = unnormalized[73]
    mydict["IdleMax"] = unnormalized[74]
    mydict["IdleMin"] = unnormalized[75]

    # MY_COL.insert_one(mydict)

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
    global TYPE

    # print('parse')
    sample = {}

    # Get the detector UUID
    detector_uuid = sample_string[:props.UUID_SIZE]
    sample_string = sample_string[props.UUID_SIZE:]

    detector_type = sample_string[0]
    sample_string = sample_string[1:]

    # Get the src and dest ip addresses
    src_ip = sample_string[:4]
    sample_string = sample_string[4:]
    dst_ip = sample_string[:4]
    sample_string = sample_string[4:]

    # Get the src and dst port numbers
    src_port = sample_string[:2]
    sample_string = sample_string[2:]
    dst_port = sample_string[:2]
    sample_string = sample_string[2:]

    # Get the protocol value
    protocol = sample_string[0]
    sample_string = sample_string[1:]

    # Get the remaining bytes for the sample values
    values = []
    for i in range(props.SAMPLE_NUMBER_OF_FLOAT_VALUES):
        # Convert 4 bytes into a float
        if props.FLOAT_SIZE >= len(sample_string):
            byte_value = sample_string
        else:
            byte_value = sample_string[:props.FLOAT_SIZE]

        converted_value = bytes_to_float(byte_value)

        # Add the float value to the values list
        values.append(converted_value)

        sample_string = sample_string[props.FLOAT_SIZE:]

    sample[UUID_STR] = detector_uuid
    sample[TYPE] = detector_type
    sample[SRC_IP_STR] = src_ip
    sample[DST_IP_STR] = dst_ip
    sample[SRC_PORT_STR] = src_port
    sample[DST_PORT_STR] = dst_port
    sample[PROTOCOL_STR] = protocol.to_bytes(1, 'little')
    sample[VALUES_STR] = values


def bytes_to_float(b):
    return struct.unpack('<f', b)[0]
