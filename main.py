import base64
import requests
from encoder import *
from decoder import *


num_of_bits = 8
radix = 2


def create_packet(payload: dict, crc8: int) -> dict:
    dct = {
        'length': '',  # byte
        'payload': payload,  # bytes
        'crc8': crc8,  # byte
    }
    return dct


def create_payload(src: str, dst: str, serial: int, dev_type: int, cmd: int, cmd_body: dict) -> dict:
    dct = {
            'src': src,  # адрес отправителя
            'dst': dst,  # адрес получателя
            'serial': serial,  # порядковый номер
            'dev_type': dev_type,  # тип устройства
            'cmd': cmd,  # команда протокола
            'cmd_body': cmd_body,  # формат зависит от команды
        }
    return dct


def create_cmd_body(dev_name: str, dev_props) -> dict:
    dct = {
        'dev_name': dev_name,
        'dev_props': dev_props,
    }
    return dct


crc_table = []


def calculate_table_crc8():
    generator = 29
    for dividend in range(256):
        curr_byte = dividend
        for bit in range(8):
            if curr_byte & 128 != 0:
                curr_byte = curr_byte << 1
                curr_byte ^= generator
            else:
                curr_byte = curr_byte << 1
        crc_table.append(curr_byte)


def calculate_crc8(byte_string: str) -> str:
    print(byte_string)
    crc = '00000000'
    data = ''
    for byte in range(len(byte_string) // 8):
        print(byte)
        for b in range(8):
            print(byte_string[byte*8+b])
            print(crc)
            if byte_string[byte*8+b] == '0':
                if crc[b] == '0':
                    data += '0'
                elif crc[b] == '1':
                    data += '1'
            elif byte_string[byte*8+b] == '1':
                if crc[b] == '0':
                    data += '1'
                elif crc[b] == '1':
                    data += '0'
        crc = bin(crc_table[int(data, 2)])[2:]
        data = ''
    return crc


def timer(timestamp: int):
    dct = {
        'timestamp': timestamp
    }
    return dct


cmds = {
    'WHOISHERE': 1,
    'IAMHERE': 2,
    'GETSTATUS': 3,
    'STATUS': 4,
    'SETSTATUS': 5,
    'TICK': 6,
}

dev_type = {
    'SmartHub': 1,
    'EnvSensor': 2,
    'Switch': 3,
    'Lamp': 4,
    'Socket': 5,
    'Clock': 6
}

URL = 'http://localhost:9998'
HUB_ADDRESS = 'ef0'
BROADCAST_ADDRESS = '3fff'

print(decode_packet('BgUBEwUEAQ8'))


if __name__ == '__main__':
    calculate_table_crc8()
    pyld = create_payload(src=HUB_ADDRESS,
                   dst=BROADCAST_ADDRESS,
                   serial=1, dev_type=dev_type['SmartHub'],
                   cmd=cmds['WHOISHERE'],
                   cmd_body=timer(1688984021000),)
    #pack = create_packet(13, pyld, 138)
    #resp = requests.post(url=URL, data=pack)

