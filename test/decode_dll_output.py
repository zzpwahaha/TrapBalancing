from base64 import decode, encode
import enum



#Chimera
output_str = 'Sending bytes: 18 2 0 0 72 85 85 85 84 119 144 227\
Sending bytes: 18 2 0 1 74 170 170 170 164 131 211 142\
Sending bytes: 18 2 0 2 77 0 0 0 4 135 248 0\
Sending bytes: 18 2 0 3 79 85 85 85 84 138 14 56\
Sending bytes: 18 2 0 4 81 170 170 170 164 142 22 56\
Sending bytes: 18 2 0 5 84 0 0 0 4 148 64 0\
Sending bytes: 18 2 0 6 86 85 85 85 84 160 139 142\
Sending bytes: 18 2 0 7 88 170 170 170 164 166 184 227\
Sending bytes: 18 2 0 8 91 0 0 0 4 170 200 0\
Sending bytes: 18 2 0 64 72 85 85 85 84 78 160 227\
Sending bytes: 18 2 0 65 74 170 170 170 164 95 3 142\
Sending bytes: 18 2 0 66 77 0 0 0 4 99 24 0\
Sending bytes: 18 2 0 67 79 85 85 85 84 105 62 56\
Sending bytes: 18 2 0 68 81 170 170 170 164 115 118 56\
Sending bytes: 18 2 0 69 84 0 0 0 4 123 160 0\
Sending bytes: 18 2 0 70 86 85 85 85 84 140 27 142\
Sending bytes: 18 2 0 71 88 170 170 170 164 148 72 227\
Sending bytes: 18 2 0 72 91 0 0 0 4 158 120 0'

# Python DLL using float
# output_str = 'Sending bytes: 18 2 0 0 72 85 85 128 4 119 144 227\
# Sending bytes: 18 2 0 1 74 170 170 149 84 131 211 142\
# Sending bytes: 18 2 0 2 77 0 0 21 84 135 248 0\
# Sending bytes: 18 2 0 3 79 85 85 42 164 138 14 56\
# Sending bytes: 18 2 0 4 81 170 170 170 164 142 22 56\
# Sending bytes: 18 2 0 5 84 0 0 42 164 148 64 0\
# Sending bytes: 18 2 0 6 86 85 85 64 4 160 139 142\
# Sending bytes: 18 2 0 7 88 170 170 192 4 166 184 227\
# Sending bytes: 18 2 0 8 90 255 255 213 84 170 200 0\
# Sending bytes: 18 2 0 64 72 85 85 128 4 78 160 227\
# Sending bytes: 18 2 0 65 74 170 170 149 84 95 3 142\
# Sending bytes: 18 2 0 66 77 0 0 21 84 99 24 0\
# Sending bytes: 18 2 0 67 79 85 85 42 164 105 62 56\
# Sending bytes: 18 2 0 68 81 170 170 170 164 115 118 56\
# Sending bytes: 18 2 0 69 84 0 0 42 164 123 160 0\
# Sending bytes: 18 2 0 70 86 85 85 64 4 140 27 142\
# Sending bytes: 18 2 0 71 88 170 170 192 4 148 72 227\
# Sending bytes: 18 2 0 72 90 255 255 213 84 158 120 0'

def decoder(output_str):
    outputs = output_str.split('Sending bytes: ')
    outputs = list(filter(None, outputs))
    for output in outputs:
        output = output.split(' ')[3:]


        dac = int(output[0]) // 64
        chan = int(output[0]) % 64

        byte64 = 0
        for idx, o in enumerate(output[1:][::-1]):
            byte64 += int(o) << (8*idx)
        print("FTW bit", bin((byte64>>28) & 0xFFFFFFFFF))
        freq = ((byte64>>28) & 0xFFFFFFFFF) / 223696213.33333333333333333333333
        amp = ((byte64>>12) & 0xFFFF) / 655.35
        print("ATW bit", bin((byte64>>12) & 0xFFFF))
        phase = ((byte64) & 0xFFF) / 4096 * 360
        print("PTW bit",bin((byte64) & 0xFFF))
        print(f"DAC_{dac:d}, channel_{chan:d}, byte={hex(byte64):s}, freq={freq:.6f}, amp={amp:.6f}, phase={phase:.6f}")


# print(output_str.encode('utf-8'))

if __name__ == '__main__':
    decoder(output_str=output_str)
