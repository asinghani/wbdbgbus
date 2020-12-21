#!/usr/bin/env python3
from wbdbgbus import *
import sys

if len(sys.argv) < 4:
    print("Usage: {} (serial port) (baud) (addr)".format(sys.argv[0]))
    sys.exit(1)

port = sys.argv[1]
baud = int(sys.argv[2])

BIG_ENDIAN = False

with DebugBus(port, baud, fifo_size=1, timeout=0) as fpga:
    addr = sys.argv[3].replace("_", "")

    if addr == "reset":
        fpga.reset()
    else:
        addr = int(addr, 0)
        chars = ""
        for i in range(1000):
            data = fpga.read(addr + (4 * i))[0]
            data = "{:08x}".format(data)
            data = bytes.fromhex(data).decode("ascii")
            if not BIG_ENDIAN:
                data = data[::-1]

            if "\0" in data:
                data = data[:data.find("\0")]
                chars += data
                break
            else:
                chars += data

        print("0x{:08x} = \"{}\"".format(addr, chars))

