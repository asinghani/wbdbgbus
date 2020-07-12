`default_nettype none

`ifdef INTERNAL_TEST

`include "wbdbgbus.sv"

`endif

// A simple test harness which connects the wbdbgbus to a memory bank for
// verification of wbdbgbus functionality. Includes optional stall and
// interrupt connections

module wbdbgbus_testharness #(
    parameter CLK_FREQ = 25000000,
    parameter UART_BAUD = 115200,
    parameter DROP_CLKS = 2500000,
    parameter MEMORY_DEPTH = 128
) (
    output wire o_tx,
    input wire i_rx,

    input wire i_force_stall,
    input wire i_force_error,
    input wire i_interrupt,

    input wire i_clk
);

wire wb_cyc, wb_stb, wb_we;
reg wb_ack, wb_err;
wire [31:0] wb_addr;
wire [31:0] wb_wdata;
reg [31:0] wb_rdata;

/* verilator lint_off PINMISSING */
wbdbgbus #(
    .CLK_FREQ(CLK_FREQ),
    .UART_BAUD(UART_BAUD),
    .DROP_CLKS(DROP_CLKS)
) wbdbgbus (
    .o_tx(o_tx),
    .i_rx(i_rx),

    .o_wb_cyc(wb_cyc),
    .o_wb_stb(wb_stb),
    .o_wb_we(wb_we),
    .o_wb_addr(wb_addr),
    .o_wb_data(wb_wdata),
    .i_wb_ack(wb_ack),
    .i_wb_err(wb_err),
    .i_wb_stall(i_force_stall),
    .i_wb_data(wb_rdata),

    .i_interrupt_1(i_interrupt),

    .i_clk(i_clk),
);
/* verilator lint_on PINMISSING */

reg [31:0] ram[0:(MEMORY_DEPTH - 1)];

always_ff @(posedge i_clk) begin
    wb_ack <= 0;
    wb_err <= 0;
    wb_rdata <= 0;

    if (wb_cyc && wb_stb && ~i_force_stall) begin
        if (wb_we) begin
            if (i_force_error) begin
                wb_err <= 1;
            end
            else if (wb_addr < MEMORY_DEPTH) begin
                ram[wb_addr] <= wb_wdata;
                wb_ack <= 1;
            end
            else begin
                wb_ack <= 1;
            end
        end
        else begin
            if (i_force_error) begin
                wb_err <= 1;
            end
            else if (wb_addr < MEMORY_DEPTH) begin
                wb_rdata <= ram[wb_addr];
                wb_ack <= 1;
            end
            else begin
                wb_ack <= 1;
            end
        end
    end
end

endmodule
