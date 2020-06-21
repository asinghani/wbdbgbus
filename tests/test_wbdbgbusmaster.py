from .testbench import Testbench, asserteq
import os
import random

assert os.getcwd().replace("/", "").endswith("sim_build")

def test_read():
    tb = Testbench("wbdbgbusmaster.sv", "test_dbg_read", params={})
    dut = tb.dut

    dut.i_wb_ack = 0
    dut.i_wb_err = 0
    dut.i_wb_stall = 0
    dut.i_cmd_reset = 0

    tb.tick()
    tb.tick()

    print("Testing immediate ack...")
    for x in range(10):
        while dut.o_cmd_ready == 0:
            tb.tick()

        dut.i_cmd_data = 0b0001 << 32
        tb.tick()

        asserteq(dut.o_wb_cyc, 0)
        asserteq(dut.o_wb_stb, 0)

        dut.i_cmd_valid = 1
        tb.tick()
        
        asserteq(dut.o_wb_cyc, 1)
        asserteq(dut.o_wb_stb, 1)
        asserteq(dut.o_wb_addr, 0)
        asserteq(dut.o_cmd_ready, 0)

        dut.i_cmd_valid = 0
        dut.i_wb_data = x
        tb.tick()
        dut.i_wb_ack = 1
        
        asserteq(dut.o_wb_cyc, 1)
        asserteq(dut.o_wb_stb, 0)
        asserteq(dut.o_wb_addr, 0)
        asserteq(dut.o_cmd_ready, 0)

        tb.tick()
        dut.i_wb_ack = 0

        asserteq(dut.o_wb_cyc, 0)
        asserteq(dut.o_wb_stb, 0)
        asserteq(dut.o_resp_valid, 1)
        asserteq(dut.o_resp_data, (0b0001 << 32) | x)

        tb.tick()
        asserteq(dut.o_cmd_ready, 1)


    print("Testing delayed ack...")
    for x in range(10):
        while dut.o_cmd_ready == 0:
            tb.tick()

        dut.i_cmd_data = 0b0001 << 32
        tb.tick()

        asserteq(dut.o_wb_cyc, 0)
        asserteq(dut.o_wb_stb, 0)

        dut.i_cmd_valid = 1
        tb.tick()
        
        asserteq(dut.o_wb_cyc, 1)
        asserteq(dut.o_wb_stb, 1)
        asserteq(dut.o_wb_addr, 0)
        asserteq(dut.o_cmd_ready, 0)

        dut.i_cmd_valid = 0
        dut.i_wb_data = x
        
        for i in range(10):
            tb.tick()
        
            asserteq(dut.o_wb_cyc, 1)
            asserteq(dut.o_wb_stb, 0)
            asserteq(dut.o_wb_addr, 0)
            asserteq(dut.o_cmd_ready, 0)

        dut.i_wb_ack = 1

        tb.tick()
        dut.i_wb_ack = 0

        asserteq(dut.o_wb_cyc, 0)
        asserteq(dut.o_wb_stb, 0)
        asserteq(dut.o_resp_valid, 1)
        asserteq(dut.o_resp_data, (0b0001 << 32) | x)

        tb.tick()
        asserteq(dut.o_cmd_ready, 1)

    print("Testing stalled bus...")
    for x in range(10):
        while dut.o_cmd_ready == 0:
            tb.tick()

        dut.i_cmd_data = 0b0001 << 32
        tb.tick()

        asserteq(dut.o_wb_cyc, 0)
        asserteq(dut.o_wb_stb, 0)

        dut.i_cmd_valid = 1
        tb.tick()
        
        asserteq(dut.o_wb_cyc, 1)
        asserteq(dut.o_wb_stb, 1)
        asserteq(dut.o_wb_addr, 0)
        asserteq(dut.o_cmd_ready, 0)

        dut.i_wb_stall = 1
        dut.i_cmd_valid = 0
        dut.i_wb_data = 42
        
        for i in range(10):
            tb.tick()
        
            asserteq(dut.o_wb_cyc, 1)
            asserteq(dut.o_wb_stb, 1)
            asserteq(dut.o_wb_addr, 0)
            asserteq(dut.o_cmd_ready, 0)

        dut.i_wb_stall = 0
        dut.i_wb_data = x
        dut.i_wb_ack = 1
        tb.tick()
        asserteq(dut.o_wb_cyc, 1)
        asserteq(dut.o_wb_stb, 0)
        asserteq(dut.o_wb_addr, 0)
        asserteq(dut.o_cmd_ready, 0)

        tb.tick()
        dut.i_wb_ack = 0

        asserteq(dut.o_wb_cyc, 0)
        asserteq(dut.o_wb_stb, 0)
        asserteq(dut.o_resp_valid, 1)
        asserteq(dut.o_resp_data, (0b0001 << 32) | x)

        tb.tick()
        asserteq(dut.o_cmd_ready, 1)

def test_addr():
    tb = Testbench("wbdbgbusmaster.sv", "test_dbg_addr", params={})
    dut = tb.dut

    dut.i_wb_ack = 0
    dut.i_wb_err = 0
    dut.i_wb_stall = 0
    dut.i_cmd_reset = 0

    tb.tick()
    tb.tick()

    print("Testing set addr...")
    for _ in range(3):
        addr = random.randint(0, 500)

        while dut.o_cmd_ready == 0:
            tb.tick()

        dut.i_cmd_data = (0b0011 << 32 | addr)
        tb.tick()

        asserteq(dut.o_wb_cyc, 0)
        asserteq(dut.o_wb_stb, 0)

        dut.i_cmd_valid = 1
        tb.tick()
        
        dut.i_cmd_valid = 0
        asserteq(dut.o_resp_valid, 1)
        asserteq(dut.o_resp_data, (0b0011 << 32))

        tb.tick()
        asserteq(dut.o_cmd_ready, 1)

        for x in range(10):
            while dut.o_cmd_ready == 0:
                tb.tick()

            dut.i_cmd_data = 0b0001 << 32
            tb.tick()

            asserteq(dut.o_wb_cyc, 0)
            asserteq(dut.o_wb_stb, 0)

            dut.i_cmd_valid = 1
            tb.tick()
            
            asserteq(dut.o_wb_cyc, 1)
            asserteq(dut.o_wb_stb, 1)
            asserteq(dut.o_wb_addr, addr)
            asserteq(dut.o_cmd_ready, 0)

            dut.i_cmd_valid = 0
            dut.i_wb_data = x
            tb.tick()
            dut.i_wb_ack = 1
            
            asserteq(dut.o_wb_cyc, 1)
            asserteq(dut.o_wb_stb, 0)
            asserteq(dut.o_wb_addr, addr)
            asserteq(dut.o_cmd_ready, 0)

            tb.tick()
            dut.i_wb_ack = 0

            asserteq(dut.o_wb_cyc, 0)
            asserteq(dut.o_wb_stb, 0)
            asserteq(dut.o_resp_valid, 1)
            asserteq(dut.o_resp_data, (0b0001 << 32) | x)

            tb.tick()
            asserteq(dut.o_cmd_ready, 1)

    print("Testing auto-inc addr...")
    for _ in range(3):
        addr = random.randint(0, 500)

        while dut.o_cmd_ready == 0:
            tb.tick()

        dut.i_cmd_data = (0b0111 << 32 | addr)
        tb.tick()

        asserteq(dut.o_wb_cyc, 0)
        asserteq(dut.o_wb_stb, 0)

        dut.i_cmd_valid = 1
        tb.tick()
        
        dut.i_cmd_valid = 0
        asserteq(dut.o_resp_valid, 1)
        asserteq(dut.o_resp_data, (0b0011 << 32))

        tb.tick()
        asserteq(dut.o_cmd_ready, 1)

        for x in range(10):
            while dut.o_cmd_ready == 0:
                tb.tick()

            dut.i_cmd_data = 0b0001 << 32
            tb.tick()

            asserteq(dut.o_wb_cyc, 0)
            asserteq(dut.o_wb_stb, 0)

            dut.i_cmd_valid = 1
            tb.tick()
            
            asserteq(dut.o_wb_cyc, 1)
            asserteq(dut.o_wb_stb, 1)
            asserteq(dut.o_wb_addr, addr + x)
            asserteq(dut.o_cmd_ready, 0)

            dut.i_cmd_valid = 0
            dut.i_wb_data = x
            tb.tick()
            dut.i_wb_ack = 1
            
            asserteq(dut.o_wb_cyc, 1)
            asserteq(dut.o_wb_stb, 0)
            asserteq(dut.o_cmd_ready, 0)

            tb.tick()
            dut.i_wb_ack = 0

            asserteq(dut.o_wb_cyc, 0)
            asserteq(dut.o_wb_stb, 0)
            asserteq(dut.o_resp_valid, 1)
            asserteq(dut.o_resp_data, (0b0001 << 32) | x)

            tb.tick()
            asserteq(dut.o_cmd_ready, 1)


def test_write():
    tb = Testbench("wbdbgbusmaster.sv", "test_dbg_write", params={})
    dut = tb.dut

    dut.i_wb_ack = 0
    dut.i_wb_err = 0
    dut.i_wb_stall = 0
    dut.i_cmd_reset = 0

    tb.tick()
    tb.tick()

    print("Testing immediate ack write...")
    for x in range(10):
        while dut.o_cmd_ready == 0:
            tb.tick()

        dut.i_cmd_data = (0b0010 << 32) | x
        tb.tick()

        asserteq(dut.o_wb_cyc, 0)
        asserteq(dut.o_wb_stb, 0)

        dut.i_cmd_valid = 1
        tb.tick()
        
        asserteq(dut.o_wb_cyc, 1)
        asserteq(dut.o_wb_stb, 1)
        asserteq(dut.o_wb_addr, 0)
        asserteq(dut.o_cmd_ready, 0)

        dut.i_cmd_valid = 0
        tb.tick()
        dut.i_wb_ack = 1
        
        asserteq(dut.o_wb_cyc, 1)
        asserteq(dut.o_wb_stb, 0)
        asserteq(dut.o_wb_addr, 0)
        asserteq(dut.o_wb_data, x)
        asserteq(dut.o_cmd_ready, 0)

        tb.tick()
        dut.i_wb_ack = 0

        asserteq(dut.o_wb_cyc, 0)
        asserteq(dut.o_wb_stb, 0)
        asserteq(dut.o_resp_valid, 1)
        asserteq(dut.o_resp_data, 0b0010 << 32)

        tb.tick()
        asserteq(dut.o_cmd_ready, 1)

test_read()
test_addr()
test_write()
