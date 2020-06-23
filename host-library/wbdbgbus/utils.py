CMD_READ_REQ     = 0b0001
CMD_WRITE_REQ    = 0b0010
CMD_SET_ADDR     = 0b0011
CMD_SET_ADDR_INC = 0b0111
CMD_BUS_RESET    = 0b1111

RESP_READ_RESP   = 0b0001
RESP_WRITE_ACK   = 0b0010
RESP_ADDR_ACK    = 0b0011
RESP_BUS_ERROR   = 0b0100
RESP_BUS_RESET   = 0b0101
RESP_INTERRUPT_1 = 0b1000
RESP_INTERRUPT_2 = 0b1001
RESP_INTERRUPT_3 = 0b1010
RESP_INTERRUPT_4 = 0b1011

RESP_INTERRUPT_ALL = [RESP_INTERRUPT_1, RESP_INTERRUPT_2,
                      RESP_INTERRUPT_3, RESP_INTERRUPT_4]

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
