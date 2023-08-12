import base64

num_of_bits = 8
radix = 2


def bin_to_ascii(bin_part_of_payload: str) -> str:
    str_ascii = ''
    for b in range(0, len(bin_part_of_payload), num_of_bits):
        if int(bin_part_of_payload[b:b + num_of_bits], radix) < 32:
            bin_part_of_payload = bin_part_of_payload[:b] + bin_part_of_payload[b+8:]
        else:
            break
    for b in range(0, len(bin_part_of_payload), num_of_bits):
        if int(bin_part_of_payload[b:b + num_of_bits], radix) < 32:
            break
        str_ascii += chr(int(bin_part_of_payload[b:b + num_of_bits], 2))
    return str_ascii


def decode_uleb128(bin_part_of_payload: str) -> str:
    str_ULEB128 = ''
    for i in range(0, len(bin_part_of_payload), num_of_bits):  # отделяем байты для чтения
        str_ULEB128 += bin_part_of_payload[i:i + num_of_bits]
        if bin_part_of_payload[i] == '0':
            break
    decoded_bytes = []
    for i in range(0, len(str_ULEB128), num_of_bits):  # байты в массив, убирая 1 старший бит
        decoded_bytes.append(str_ULEB128[i + 1:i + num_of_bits])
    decoded_bytes.reverse()  # переписываем байты в массиве в реальном порядке
    decoded_bytes = ''.join(decoded_bytes)
    return decoded_bytes


def bin_to_str_switch_dev_names(bin_part_of_payload: str) -> list:
    dev_names = []
    for b in range(len(bin_part_of_payload) // num_of_bits):
        dev_names.append(bin_to_ascii(bin_part_of_payload))
        bin_part_of_payload = bin_part_of_payload[(len(dev_names[b]) + 1) * num_of_bits:]
        if len(bin_part_of_payload) == 0:
            break
    return dev_names


def decode_triggers(bin_part_of_payload: str) -> list[dict]:
    triggers = []
    while len(bin_part_of_payload) > 0:
        op = bin_part_of_payload[:num_of_bits]
        value = decode_uleb128(bin_part_of_payload[num_of_bits:])
        name = bin_to_ascii(bin_part_of_payload[num_of_bits + (len(value) // 7) * num_of_bits:])
        triggers.append({
            'op': op,
            'value': value,
            'name': name
        })
        bin_part_of_payload = \
            bin_part_of_payload[num_of_bits + (len(value) // 7) * num_of_bits + num_of_bits + len(name)*num_of_bits:]
        # num_of_bits = size(op) + size(value) + 1 byte(\x06) + size(name)
    return triggers


def decode_env_sensor_values(bin_part_of_payload: str) -> list:
    values = []
    while len(bin_part_of_payload) > 0:
        value = decode_uleb128(bin_part_of_payload)
        values.append(int(value, radix))
        bin_part_of_payload = bin_part_of_payload[(len(value)//7) * num_of_bits:]
    return values


def decode_cmd_body(bin_part_of_payload: str, device_type: int, command: int) -> dict:
    cmd_body = {}
    match device_type:
        case 1:     # hub
            if command == 1 or command == 2:        # IAMHERE or WHOISHERE
                cmd_body = {
                    'dev_name': bin_to_ascii(bin_part_of_payload)
                }
        case 2:     # env sensor
            if command == 1 or command == 2:        # IAMHERE or WHOISHERE
                dev_name = bin_to_ascii(bin_part_of_payload)
                bin_part_of_payload = bin_part_of_payload[(len(dev_name) + 1) * num_of_bits:]
                cmd_body = {
                    'dev_name': dev_name,
                    'dev_props': {
                        'dev_sensors': bin_part_of_payload[:num_of_bits],
                        'triggers': decode_triggers(bin_part_of_payload[num_of_bits * 2:])
                    }
                }
            elif command == 4:      # STATUS
                cmd_body = {
                    "values": decode_env_sensor_values(bin_part_of_payload[8:])
                }
        case 3:     # switch
            if command == 1 or command == 2:        # IAMHERE or WHOISHERE
                dev_name = bin_to_ascii(bin_part_of_payload)
                cmd_body = {
                    'dev_name': dev_name,
                    'dev_props': {
                        'dev_names': bin_to_str_switch_dev_names(bin_part_of_payload[(len(dev_name) + 2) * 8:])
                    }
                }
            elif command == 4:      # STATUS
                cmd_body = int(bin_part_of_payload, radix)     # 1/0
        case 4 | 5:     # lamp | socket
            if command == 1 or command == 2:
                cmd_body = {
                    'dev_name': bin_to_ascii(bin_part_of_payload)
                }
            elif command == 4 or command == 5:      # STATUS or SETSTATUS
                cmd_body = int(bin_part_of_payload, radix)     # 1/0
        case 6:     # timer
            if command == 1 or command == 2:        # IAMHERE or WHOISHERE
                cmd_body = {
                    'dev_name': bin_to_ascii(bin_part_of_payload)
                }
            elif command == 6:      # TICK
                cmd_body = {
                    'timestamp': int(decode_uleb128(bin_part_of_payload), radix)
                    # dt = datetime.datetime.fromtimestamp(time_in_millis / 1000.0)
                }
    return cmd_body


def decode_payload(bin_payload: str) -> dict:
    src = decode_uleb128(bin_payload)
    bin_payload = bin_payload[len(src) + len(src) // 7:]
    dst = decode_uleb128(bin_payload)
    bin_payload = bin_payload[len(dst) + len(dst) // 7:]
    serial = decode_uleb128(bin_payload)
    bin_payload = bin_payload[len(serial) + len(serial) // 7:]
    serial = int(serial, radix)
    dev_type = int(bin_payload[:num_of_bits], radix)
    bin_payload = bin_payload[num_of_bits:]
    cmd = int(bin_payload[:num_of_bits], radix)
    bin_payload = bin_payload[num_of_bits:]
    cmd_body = decode_cmd_body(bin_payload, dev_type, cmd)
    payload = {
        'src': src,                 # bin
        'dst': dst,                 # bin
        'serial': serial,           # int
        'dev_type': dev_type,       # int
        'cmd': cmd,                  # int
        'cmd_body': cmd_body
    }
    return payload


def decode_packet(base64_packet: str) -> dict:
    while len(base64_packet) % 4 != 0:
        base64_packet += '='
    decoded_base64_packet = base64.urlsafe_b64decode(base64_packet.encode("ascii"))
    bin_packet = "".join(["{:08b}".format(x) for x in decoded_base64_packet])
    length = int(bin_packet[:num_of_bits], radix)
    packet = {
        'length': length,  # byte
        'payload': decode_payload(bin_packet[num_of_bits:(length+1)*num_of_bits]),  # bytes
        'crc8': bin_packet[(length + 1) * num_of_bits:],  # byte
    }
    return packet