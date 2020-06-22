from .testbench import Testbench, asserteq
import os
import random
from math import ceil
from .uart_sim import UARTSim

assert os.getcwd().replace("/", "").endswith("sim_build")

MEMORY_DEPTH = 16
CLK_FREQ = 25000000
UART_BAUD = 921600
DROP_CLKS = 25000000
CLKS_PER_BYTE = 10 * int(ceil(float(CLK_FREQ) / UART_BAUD))

"""
    Converts a 4-bit instruction and a 32-bit data word into 5 8-bit packets
"""
def create_instruction(inst, data):
    return [
        inst,
        (data & 0xff000000) >> 24,
        (data & 0x00ff0000) >> 16,
        (data & 0x0000ff00) >> 8,
        (data & 0x000000ff) >> 0
    ]

"""
    Converts 5 8-bit packets into a 4-bit instruction and 32-bit data word
"""
def parse_instruction(byte_list):
    data = int("".join(["{0:08b}".format(x) for x in byte_list[1:]]), 2)
    return byte_list[0] & 0x0f, data


def test_wbdbgbus():
    tb = Testbench("wbdbgbus_testharness.sv", "test_wbdbgbus",
                   params={"MEMORY_DEPTH": MEMORY_DEPTH, "CLK_FREQ": CLK_FREQ,
                           "UART_BAUD": UART_BAUD, "DROP_CLKS": DROP_CLKS})
    dut = tb.dut

    uart = UARTSim(tb.write_port("i_rx"), tb.read_port("o_tx"), CLK_FREQ, UART_BAUD)

    tb.add_tick_callback(uart.update)

    tb.tick()

    print("Write & readback test")
    values = [random.randint(0, 2**32 - 1) for _ in range(MEMORY_DEPTH)]

    print("Write")
    for i in range(len(values)):
        data = values[i]
        addr = i

        # Set address
        uart.send_all(create_instruction(0b0011, addr))
        tb.tick(12 * CLKS_PER_BYTE)
        dat = uart.get_recv_data(5)
        resp = parse_instruction(dat)
        asserteq(resp[0], 0b0011)

        # Write data
        uart.send_all(create_instruction(0b0010, data))
        tb.tick(12 * CLKS_PER_BYTE)
        resp = parse_instruction(uart.get_recv_data(5))
        asserteq(resp[0], 0b0010)

    print("Readback")
    for i in range(len(values)):
        data = values[i]
        addr = i

        # Set address
        uart.send_all(create_instruction(0b0011, addr))
        tb.tick(12 * CLKS_PER_BYTE)
        resp = parse_instruction(uart.get_recv_data(5))
        asserteq(resp[0], 0b0011)

        # Read data
        uart.send_all(create_instruction(0b0001, 0))
        tb.tick(12 * CLKS_PER_BYTE)
        resp = parse_instruction(uart.get_recv_data(5))
        asserteq(resp[0], 0b0001)
        asserteq(resp[1], data)

    print("Auto-increment test")
    values = [random.randint(0, 2**32 - 1) for _ in range(MEMORY_DEPTH)]

    # Set address
    uart.send_all(create_instruction(0b0111, 0))
    tb.tick(15 * CLKS_PER_BYTE)
    resp = parse_instruction(uart.get_recv_data(5))
    asserteq(resp[0], 0b0011)

    print("Auto-increment Write")
    for i in range(len(values)):
        data = values[i]

        # Write data
        uart.send_all(create_instruction(0b0010, data))
        tb.tick(12 * CLKS_PER_BYTE)
        resp = parse_instruction(uart.get_recv_data(5))
        asserteq(resp[0], 0b0010)

    print("Manual Readback")
    for i in range(len(values)):
        data = values[i]
        addr = i

        # Set address
        uart.send_all(create_instruction(0b0011, addr))
        tb.tick(12 * CLKS_PER_BYTE)
        resp = parse_instruction(uart.get_recv_data(5))
        asserteq(resp[0], 0b0011)

        # Read data
        uart.send_all(create_instruction(0b0001, 0))
        tb.tick(12 * CLKS_PER_BYTE)
        resp = parse_instruction(uart.get_recv_data(5))
        asserteq(resp[0], 0b0001)
        asserteq(resp[1], data)

    # Set address
    uart.send_all(create_instruction(0b0111, 0))
    tb.tick(15 * CLKS_PER_BYTE)
    resp = parse_instruction(uart.get_recv_data(5))
    asserteq(resp[0], 0b0011)

    print("Auto-increment Readback")
    for i in range(len(values)):
        data = values[i]
        addr = i 

        # Read data
        uart.send_all(create_instruction(0b0001, 0))
        tb.tick(12 * CLKS_PER_BYTE)
        resp = parse_instruction(uart.get_recv_data(5))
        asserteq(resp[0], 0b0001)
        asserteq(resp[1], data)

    print("Bus error test")
    dut.i_force_error = 1

    uart.send_all(create_instruction(0b0001, 0))
    tb.tick(12 * CLKS_PER_BYTE)
    resp = parse_instruction(uart.get_recv_data(5))
    asserteq(resp[0], 0b0100)

    dut.i_force_error = 0
    uart.send_all(create_instruction(0b0001, 0))
    tb.tick(12 * CLKS_PER_BYTE)
    resp = parse_instruction(uart.get_recv_data(5))
    asserteq(resp[0], 0b0001)

    print("Stall test")
    dut.i_force_stall = 1

    uart.send_all(create_instruction(0b0001, 0))
    tb.tick(12 * CLKS_PER_BYTE)
    asserteq(uart.get_recv_len(), 0)
    dut.i_force_stall = 0
    tb.tick(12 * CLKS_PER_BYTE)
    resp = parse_instruction(uart.get_recv_data(5))
    asserteq(resp[0], 0b0001)

    uart.send_all(create_instruction(0b0001, 0))
    tb.tick(12 * CLKS_PER_BYTE)
    resp = parse_instruction(uart.get_recv_data(5))
    asserteq(resp[0], 0b0001)


    print("Buffered instruction test")
    dut.i_force_stall = 1

    for i in range(8):
        uart.send_all(create_instruction(0b0001 if i % 2 == 0 else 0b0011, 0))
        tb.tick(12 * CLKS_PER_BYTE)
        asserteq(uart.get_recv_len(), 0)

    dut.i_force_stall = 0

    # Ensure order remains consistent
    for i in range(8):
        tb.tick(6 * CLKS_PER_BYTE)
        resp = parse_instruction(uart.get_recv_data(5))
        asserteq(resp[0], 0b0001 if i % 2 == 0 else 0b0011)

    print("Buffered write & readback test")
    # Write then readback known data
    dut.i_force_stall = 1

    uart.send_all(create_instruction(0b0111, 0))
    tb.tick(15 * CLKS_PER_BYTE)

    for i in range(8):
        data = values[i]

        # Write data
        uart.send_all(create_instruction(0b0010, data))
        tb.tick(12 * CLKS_PER_BYTE)

    uart.send_all(create_instruction(0b0111, 0))
    tb.tick(15 * CLKS_PER_BYTE)

    for i in range(8):
        uart.send_all(create_instruction(0b0001, 0))
        tb.tick(12 * CLKS_PER_BYTE)
        asserteq(uart.get_recv_len(), 5)

    dut.i_force_stall = 0

    tb.tick(100 * CLKS_PER_BYTE)

    # Ensure order remains same
    resp = parse_instruction(uart.get_recv_data(5))
    asserteq(resp[0], 0b0011)

    for i in range(8):
        resp = parse_instruction(uart.get_recv_data(5))
        asserteq(resp[0], 0b0010)

    resp = parse_instruction(uart.get_recv_data(5))
    asserteq(resp[0], 0b0011)

    for i in range(8):
        resp = parse_instruction(uart.get_recv_data(5))
        asserteq(resp[0], 0b0001)
        asserteq(resp[1], values[i])


test_wbdbgbus()
