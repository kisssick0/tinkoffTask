num_of_bits = 8
radix = 2


def str_to_bin(word: str) -> str:
    bin_word = ''
    for letter in word:
        bin_letter = bin(ord(letter))[2:]
        while len(bin_letter) < num_of_bits:
            bin_letter = '0' + bin_letter
        bin_word += bin_letter
    return bin_word


def uleb8_to_bin(number: int) -> str:
    bin_number = bin(number)[2:]
    while len(bin_number) % 7 != 0:
        bin_number = '0' + bin_number
    for b in range(7, len(bin_number), 7):
        bin_number = bin_number[:b] + '1' + bin_number[b:]
    bin_number = '0' + bin_number
    return bin_number


def byte_to_bin(number: int) -> str:
    bin_number = bin(number)[2:]
    while len(bin_number) % num_of_bits != 0:
        bin_number = '0' + bin_number
    return bin_number


def props_to_bin(props: dict) -> dict:              # ДОДЕЛАТЬ
    pass


def cmd_body_to_bin(cmd_body: dict, cmd: int) -> dict:
    match cmd:
        case 1:     # WHOISHERE
            dvc = {
                'dev_name': str_to_bin(cmd_body['dev_name']),
                'dev_props': props_to_bin(cmd_body['dev_props'])
            }
            return dvc
        case 2:     # IAMHERE
            dvc = {
                'dev_name': str_to_bin(cmd_body['dev_name'])
            }
            return dvc
        case 3 | 4:     # GETSTATUS or STATUS
            dvc = {}
            return dvc
        case 5:     # SETSTATUS
            dvc = {'on_or_off': byte_to_bin(cmd_body['on_or_off'])}
            return dvc


def payload_to_bin(payload: dict) -> dict:
    bin_payload = {
            'src': uleb8_to_bin(payload['src']),
            'dst': uleb8_to_bin(payload['dst']),
            'serial': uleb8_to_bin(payload['serial']),
            'dev_type': byte_to_bin(payload['dev_type']),
            'cmd': byte_to_bin(payload['cmd']),
            'cmd_body': cmd_body_to_bin(payload['cmd_body'], payload['cmd'])
        }
    return bin_payload


def count_payload_length_in_bytes(payload: dict) -> int:
    length_in_bits = 0
    for key in payload.keys():
        if isinstance(payload[key], str):
            length_in_bits += len(payload[key])
        elif isinstance(payload[key], dict):
            length_in_bits += count_payload_length_in_bytes(payload[key])
        else:
            raise TypeError
    length_in_bytes = length_in_bits // 8
    return length_in_bytes


def packet_to_bin(dct: dict) -> dict:
    bin_dct = {'length': '',
               'payload': payload_to_bin(dct['payload']),
               'crc8': byte_to_bin(dct['crc8'])}
    bin_dct['length'] = byte_to_bin(count_payload_length_in_bytes(bin_dct['payload']))
    return bin_dct