# Host-side Python Library for wbdbgbus

## Installation

To install the library, run `pip3 install .` in the `wbdbgbus` directory. It will install in the form of a python package named `wbdbgbus`.

## Basic Example

This example blinks an LED (through a GPIO peripheral with the LED connected to the least-significant write bit) at address 0x00, and reads the values of registers [0x10, 0x11, 0x12, 0x13].

```python
from wbdbgbus import DebugBus
import time

SERIAL_PORT = "/dev/ttyUSB0"
BAUD = 115200
FIFO_SIZE = 96

led_state = 0

with DebugBus(SERIAL_PORT, BAUD, fifo_size=FIFO_SIZE, timeout=0) as fpga:
    for i in range(60):
        fpga.write(0x00, led_state)
        led_state = 1 - led_state

        # Read 4 contiguous words starting at 0x10
        print(fpga.read(0x10, n=4))
        time.sleep(1)
```

## Context Manager

The `DebugBus` module is fully context manager compliant. If used with the Python `with` statement, it will automatically handle closing the serial port after completion. Alternatively, the `close()` function can be called to manually close the bus's serial port.

## API Reference

### Setup & Teardown

`DebugBus(serial_port, baud, fifo_size, timeout=0)` - Creates and opens a debug bus along with its underlying serial port.

- `serial_port` - The device name of the serial port (i.e. `/dev/ttyUSB0` on Linux or `COM4` on Windows).
- `baud` - The baud rate of the serial port. Should match the rate that the debug bus was synthesized with.
- `fifo_size` - The size of the FIFO within the debug bus. Should match the FIFO size that the debug bus was synthesized with.
- `timeout` - The number of seconds to wait for a response during a `read()` operation before timing out. If 0, there is no timeout (this is the recommended option for most use-cases and it is the default).

`close()` - Closes the underlying serial port.

`reset()` - Forcibly reset the bus. Blocks until the bus-reset is acknowledged.

### Read

`read(address, n=1)` - Read `n` contiguous 32-bit words starting at `address`. Blocks execution until finished or timed out. For reading multiple values from the same address (for peripherals which use a single register as a pipe), use `read_peripheral()`. If `n` = 1, returns a single integer value read from the bus, otherwise returns an array of integer values with length `n`.

- `address` - The base address to read from.
- `n` - The number of values to read starting at the given address.

`read_peripheral(address, n=1)` - Read `n` 32-bit words, all from `address`. Blocks execution until finished or timed out. This should be used for peripherals which use a single register as a pipe. If `n` = 1, returns a single integer value read from the bus, otherwise returns an array of integer values with length `n`.

- `address` - The singular address to read from.
- `n` - The number of values to read from the given address.

### Write

`write(address, data, verify=False)` - Write `data` into contiguous 32-bit words starting at `address`. Blocks execution until finished or timed out. `None` values in the data array will not be written. For writing multiple values to the same address (for peripherals which use a single register as a pipe), use `write_peripheral()`.

- `address` - The base address to write to.
- `data` - The data (an integer or list of integers) to write.
- `verify` - Whether to read-back and verify the data after writing.

`write_peripheral(address, n=1)` - Write all values in `data` to `address`. Blocks execution until finished or timed out. This should be used for peripherals which use a single register as a pipe.

- `address` - The singular address to write to.
- `data` - The data (an integer or list of integers) to write.

### Interrupts

When one of the four interrupts are triggered, the corresponding value in the interrupts array goes high. After reading the interrupt, it must be reset by calling `reset_interrupt()` or by passing `reset=True` to `poll_interrupts`.

`poll_interrupts(reset=False)` - Poll the recieved interrupts. Returns an array of the 4 interrupts.

- `reset` - Whether to reset the interrupts after reading.

`reset_interrupts()` - Reset interrupts regardless of whether they have been polled.
