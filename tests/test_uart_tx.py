from .testbench import Testbench, asserteq
import os
import random
from .uart_sim import UARTSim

assert os.getcwd().replace("/", "").endswith("sim_build")

CLK_FREQ = 250000
BAUD = 9600
CLKS_PER_BAUD = int(CLK_FREQ / BAUD)
CLKS_PER_1_5_BAUD = int(1.5 * CLKS_PER_BAUD)

def test_uart_tx():
    tb = Testbench("wbdbgbus_uart_tx.sv", "test_uart_tx", params={"CLK_FREQ": CLK_FREQ, "BAUD": BAUD})
    dut = tb.dut

    uart = UARTSim(None, tb.read_port("o_out"), CLK_FREQ, BAUD)
    tb.add_tick_callback(uart.update)

    tb.tick()

    for byte in [random.randint(0, 255) for i in range(10)]:
        print("Testing "+str(byte))
        bits = [int(bit) for bit in format(byte, "08b")][::-1]

        while dut.o_ready == 0:
            tb.tick()

        dut.i_data = byte
        dut.i_valid = 1

        tb.tick()

        dut.i_data = 0
        dut.i_valid = 0

        received = False

        for i in range(CLKS_PER_BAUD * 12):
            tb.tick()

            out = uart.get_recv_data()
            if out is not None:
                asserteq(out, byte)
                received = True
                break

        asserteq(received, True, "Did not recieve output byte")


test_uart_tx()
