import struct
frame = struct.pack('i3sii1500s',0, "STR".encode('utf-8'), 1, 0, "9".encode('utf-8'))
frame2 = struct.pack('i3sii1500s',0, "STR".encode('utf-8'), 1, 0, "9".encode('utf-8'))
send = frame + frame2
print(len(send[0:1517]))
a, b, c, d, e = struct.unpack('i3sii1500s', send[0:1516])
print(a)
print(b.decode('utf-8'))
print(c)
print(d)
print(e.decode('utf-8'))