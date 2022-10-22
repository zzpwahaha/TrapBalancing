

from base64 import decode, encode
import enum


output_str = 'Sending bytes: 18 2 0 0 72 85 85 85 84 119 144 227\
Sending bytes: 18 2 0 0 72 85 85 128 4 119 144 227\
Sending bytes: 18 2 0 1 74 170 170 149 84 131 211 142'

outputs = output_str.split('Sending bytes: ')
outputs = list(filter(None, outputs))
for output in outputs:
    output = output.split(' ')[3:]


    dac = int(output[0]) // 64
    chan = int(output[0]) % 64

    byte64 = 0
    for idx, o in enumerate(output[1:][::-1]):
        byte64 += int(o) << (8*idx)
    print(bin((byte64>>28) & 0xFFFFFFFFF))
    freq = ((byte64>>28) & 0xFFFFFFFFF) / 223696213.33333333333333333333333
    amp = ((byte64>>12) & 0xFFFF) / 655.35
    print(bin((byte64>>12) & 0xFFFF))
    phase = ((byte64) & 0xFFF) / 4096 * 360
    print(f"DAC_{dac:d}, channel_{chan:d}, byte={hex(byte64):s}, freq={freq:.6f}, amp={amp:.6f}, phase={phase:.6f}")


# print(output_str.encode('utf-8'))