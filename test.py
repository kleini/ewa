import struct

can_frame_fmt = "=IB3x8s"

def build_can_frame(can_id, data):
       can_dlc = len(data)
       data = data.ljust(8, b'\x00')
       return struct.pack(can_frame_fmt, can_id, can_dlc, data)

key = build_can_frame(1489, b'\x01\x02\x03')

print(key)
