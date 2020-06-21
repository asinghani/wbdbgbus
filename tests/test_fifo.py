from .testbench import Testbench, asserteq
import os
import random

assert os.getcwd().replace("/", "").endswith("sim_build")

WIDTH = 8
DEPTH = 16

def test_fifo():
    tb = Testbench("wbdbgbus_fifo.sv", "test_fifo",
                   params={"WIDTH": WIDTH, "DEPTH": DEPTH})
    dut = tb.dut

    tb.tick(2)

    for i in range(5):
        print("Full depth write & readback test")
        data = [random.randint(0, 2**WIDTH - 1) for i in range(DEPTH)]

        asserteq(dut.o_empty, 1)
        for x in data:
            dut.i_wr_en = 1
            dut.i_wr_data = x
            asserteq(dut.o_full, 0)
            tb.tick()
            asserteq(dut.o_empty, 0)

        asserteq(dut.o_full, 1)
        dut.i_wr_en = 0
        tb.tick()

        # Readback
        for x in data:
            dut.i_rd_en = 1
            asserteq(dut.o_empty, 0)
            tb.tick()
            asserteq(dut.o_rd_data, x)
            asserteq(dut.o_full, 0)

        asserteq(dut.o_empty, 1)
        dut.i_rd_en = 0
        tb.tick()


        print("Write & reset test")
        data = [random.randint(0, 2**WIDTH - 1) for i in range(DEPTH)]

        # Write junk data
        asserteq(dut.o_empty, 1)
        for x in range(5):
            dut.i_wr_en = 1
            dut.i_wr_data = x
            asserteq(dut.o_full, 0)
            tb.tick()
            asserteq(dut.o_empty, 0)

        # Reset
        dut.i_wr_en = 0
        dut.i_rst = 1
        tb.tick()
        dut.i_rst = 0
        tb.tick()

        # Write real data
        asserteq(dut.o_empty, 1)
        for x in data:
            dut.i_wr_en = 1
            dut.i_wr_data = x
            asserteq(dut.o_full, 0)
            tb.tick()
            asserteq(dut.o_empty, 0)

        asserteq(dut.o_full, 1)
        dut.i_wr_en = 0
        tb.tick()

        # Readback
        for x in data:
            dut.i_rd_en = 1
            asserteq(dut.o_empty, 0)
            tb.tick()
            asserteq(dut.o_rd_data, x)
            asserteq(dut.o_full, 0)

        asserteq(dut.o_empty, 1)
        dut.i_rd_en = 0
        tb.tick()

        print("Partial depth write & readback test")
        data = [random.randint(0, 2**WIDTH - 1) for i in range(DEPTH // 3)]

        asserteq(dut.o_empty, 1)
        for x in data:
            dut.i_wr_en = 1
            dut.i_wr_data = x
            asserteq(dut.o_full, 0)
            tb.tick()
            asserteq(dut.o_empty, 0)

        dut.i_wr_en = 0
        tb.tick()

        # Readback
        for x in data:
            dut.i_rd_en = 1
            asserteq(dut.o_empty, 0)
            tb.tick()
            asserteq(dut.o_rd_data, x)
            asserteq(dut.o_full, 0)

        asserteq(dut.o_empty, 1)
        dut.i_rd_en = 0
        tb.tick()






test_fifo()
