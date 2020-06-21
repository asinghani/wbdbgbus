# Wishbone UART-Based Debug Bridge

## Motivation

This repo provides a drop-in debug master for a [Wishbone B4](https://cdn.opencores.org/downloads/wbspec_b4.pdf) bus (pipelined mode) that can be accessed over UART from a program running on a host machine or in a testbench harness.

## Connection Interface

The module that must be integrated into a design to connect this debug bus interface is the `wbdbgbus` module. Following are the parameters and connections required to integrate this module:
```verilog
// Configuration parameters
parameter CLK_FREQ // Clock frequency, used for UART
parameter UART_BAUD // UART baud rate
parameter DROP_CLKS // Number of clocks before dropping an unfinished command
```

```verilog
// Module Connections

// UART
output o_tx
input i_rx

// Wishbone
output o_wb_cyc
output o_wb_stb
output o_wb_we
output [31:0] o_wb_addr
output [31:0] o_wb_data
input i_wb_ack
input i_wb_err
input i_wb_stall
input [31:0] i_wb_data

// Interrupts
input i_interrupt_1
input i_interrupt_2
input i_interrupt_3
input i_interrupt_4

// Clock
input i_clk
```

## Interacting with the bus

A host machine may interact with the bus through a fairly simple protocol. 

To read a single word from the bus:
1. Send a "Set Address" instruction with the address to read
2. Wait for an "Address Acknowledge" response
3. Send a "Read Request" instruction
4. Wait for the "Read Response" response, which will contain the data that has been read

To read multiple sequential words from the bus:
1. Send a "Set Address (Auto-Increment)" instruction with the base address to read from
2. Wait for an "Address Acknowledge" response
3. Send a "Read Request" instruction
4. Wait for the "Read Response" response, which will contain the data that has been read
5. Repeat steps 3 and 4 for each consecutive address to read from. The address will automatically increment by 1 after each read.

To write a single word to the bus:
1. Send a "Set Address" instruction with the address to write to
2. Wait for an "Address Acknowledge" response
3. Send a "Write Request" instruction with the data to write
4. Wait for the "Write Acknowledge" response

To write multiple sequential words to the bus:
1. Send a "Set Address" instruction with the base address to write to
2. Wait for an "Address Acknowledge" response
3. Send a "Write Request" instruction with the data to write
4. Wait for the "Write Acknowledge" response
5. Repeat steps 3 and 4 for each consecutive address to write to. The address will automatically increment by 1 after each read.

To reset a hung bus:
1. Send a "Bus Reset" instruction. This will automatically bypass any other instructions or stalls and immediately reset the bus master.
2. Wait for a "Bus Reset Acknowledge" response. If one is not received, a power-cycle may be required.

### Instruction Format

A simple 36-bit-wide binary data format is defined, consisting of a 4-bit opcode and 32-bits of data. When passing the data over a UART connection, it is converted into 5 bytes, with the first byte including 4-bits of don't-care and a 4-bit opcode, and the remaining 4 bytes containing the 32-bit data in big-endian format.

The command opcodes (binary) are defined as follows:
* `0001` - Read Request
* `0010` - Write Request (Data = data to write)
* `0011` - Set Address (Data = address to set)
* `0111` - Set Address w/ Auto-Increment (Data = base address to set)
* `1111` - Bus Reset

The response opcodes (binary) are defined as follows:
* `0001` - Read Response (Data = data read)
* `0010` - Write Acknowledge
* `0011` - Address Acknowledge
* `0100` - Bus Error
* `0101` - Bus Reset Acknowledge
* `1000` - Interrupt 1 Triggered
* `1001` - Interrupt 2 Triggered
* `1010` - Interrupt 3 Triggered
* `1011` - Interrupt 4 Triggered

## Planned Features

* [ ] Host-side interface library
* [ ] Testbench interface wrappers
* [ ] FIFO instruction buffering
* [ ] UART flow control

## Contributing

Please file an issue if any bugs or missing features are found. Pull requests are always welcome.

## License

[MIT](https://choosealicense.com/licenses/mit/)
