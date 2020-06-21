from .testbench import Testbench, asserteq
import os
import random
from .uart_sim import UARTSim

assert os.getcwd().replace("/", "").endswith("sim_build")

CLK_FREQ = 250000
BAUD = 9600
CLKS_PER_BAUD = int(CLK_FREQ / BAUD)

def test_uart_rx():
    tb = Testbench("uart_rx.sv", "test_uart_rx", params={"CLK_FREQ": CLK_FREQ, "BAUD": BAUD})
    dut = tb.dut

    uart = UARTSim(tb.write_port("i_in"), None, CLK_FREQ, BAUD)
    tb.add_tick_callback(uart.update)

    dut.i_in = 1
    tb.tick()

    num_bytes = 20
    data = [random.randint(0, 255) for i in range(num_bytes)]

    # Queue back-to-back transmissions
    for byte in data:
        uart.send(byte)

    for i in range(CLKS_PER_BAUD * 11 * num_bytes):
        tb.tick()

        if dut.o_valid == 1:
            asserteq(dut.o_data, data[0])
            data = data[1:]

    asserteq(len(data), 0)

test_uart_rx()
