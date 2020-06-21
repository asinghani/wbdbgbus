`default_nettype none

`ifndef INTERNAL_TEST

`include "wbdbgbus/uart_rx.sv"
`include "wbdbgbus/uart_tx.sv"
`include "wbdbgbus/wbdbgbusmaster.sv"

`else

`include "uart_rx.sv"
`include "uart_tx.sv"
`include "wbdbgbusmaster.sv"

`endif

module wbdbgbus #(
    parameter CLK_FREQ = 25000000,
    parameter UART_BAUD = 9600,

    // Time before dropping an unfinished instruction
    parameter DROP_CLKS = 2500000 // 0.1s at 25Mhz
)
(
    // UART
    output wire o_tx,
    input wire i_rx,

    // Wishbone
    output wire o_wb_cyc,
    output wire o_wb_stb,
    output wire o_wb_we,
    output wire [31:0] o_wb_addr,
    output wire [31:0] o_wb_data,
    input wire i_wb_ack,
    input wire i_wb_err,
    input wire i_wb_stall,
    input wire [31:0] i_wb_data,

    // Interrupts
    input wire i_interrupt_1,
    input wire i_interrupt_2,
    input wire i_interrupt_3,
    input wire i_interrupt_4,

    input wire i_clk
);

localparam RESP_INT_1 = 4'b1000;
localparam RESP_INT_2 = 4'b1001;
localparam RESP_INT_3 = 4'b1010;
localparam RESP_INT_4 = 4'b1011;


// UART
wire [7:0] uart_rx_data;
wire uart_rx_valid;

reg [7:0] uart_tx_data;
wire uart_tx_ready;
reg uart_tx_valid = 0;

uart_rx #(
    .CLK_FREQ(CLK_FREQ),
    .BAUD(UART_BAUD)
) uart_rx (
    .o_data(uart_rx_data),
    .o_valid(uart_rx_valid),

    .i_in(i_rx),
    .i_clk(i_clk)
);

uart_tx #(
    .CLK_FREQ(CLK_FREQ),
    .BAUD(UART_BAUD)
) uart_tx (
    .o_ready(uart_tx_ready),
    .o_out(o_tx),

    .i_data(uart_tx_data),
    .i_valid(uart_tx_valid),
    .i_clk(i_clk)
);

// Wishbone Master
// TODO add FIFO on cmd and resp
reg cmd_reset = 0;
reg cmd_valid = 0;
wire cmd_ready;
reg [35:0] cmd_data;

wire resp_valid;
wire [35:0] resp_data;

wbdbgbusmaster wbdbgbusmaster (
    .i_cmd_reset(cmd_reset),
    .i_cmd_valid(cmd_valid),
    .o_cmd_ready(cmd_ready),
    .i_cmd_data(cmd_data),

    .o_resp_valid(resp_valid),
    .o_resp_data(resp_data),

    .o_wb_cyc(o_wb_cyc),
    .o_wb_stb(o_wb_stb),
    .o_wb_we(o_wb_we),
    .o_wb_addr(o_wb_addr),
    .o_wb_data(o_wb_data),
    .i_wb_ack(i_wb_ack),
    .i_wb_err(i_wb_err),
    .i_wb_stall(i_wb_stall),
    .i_wb_data(i_wb_data),

    .i_clk(i_clk)
);

reg [39:0] transmit_data = 0;
reg [2:0] transmit_state = 0; // 0 = no tx, 1-5 = bytes

// Interrupt handling
reg interrupt_1_last = 0;
reg interrupt_2_last = 0;
reg interrupt_3_last = 0;
reg interrupt_4_last = 0;

wire interrupt_1_rising = i_interrupt_1 && ~interrupt_1_last;
wire interrupt_2_rising = i_interrupt_2 && ~interrupt_2_last;
wire interrupt_3_rising = i_interrupt_3 && ~interrupt_3_last;
wire interrupt_4_rising = i_interrupt_4 && ~interrupt_4_last;

wire any_interrupt = (interrupt_1_rising || interrupt_2_rising ||
                      interrupt_3_rising || interrupt_4_rising);

always_ff @(posedge i_clk) begin
    interrupt_1_last <= i_interrupt_1;
    interrupt_2_last <= i_interrupt_2;
    interrupt_3_last <= i_interrupt_3;
    interrupt_4_last <= i_interrupt_4;
end

// Transmit output from debug bus & handle interrupts
always_ff @(posedge i_clk) begin
    uart_tx_valid <= 0;

    if (transmit_state == 0) begin
        if (resp_valid) begin
            transmit_data <= {4'b0000, resp_data};
            transmit_state <= 1;
        end
        else if (any_interrupt) begin
            if (interrupt_1_rising) begin
                transmit_data <= {4'b0000, RESP_INT_1, 32'b0};
                transmit_state <= 1;
            end
            else if (interrupt_2_rising) begin
                transmit_data <= {4'b0000, RESP_INT_2, 32'b0};
                transmit_state <= 1;
            end
            else if (interrupt_3_rising) begin
                transmit_data <= {4'b0000, RESP_INT_3, 32'b0};
                transmit_state <= 1;
            end
            else if (interrupt_4_rising) begin
                transmit_data <= {4'b0000, RESP_INT_4, 32'b0};
                transmit_state <= 1;
            end
        end
    end
    else begin
        if (uart_tx_ready && ~uart_tx_valid) begin
            case (transmit_state)
                1: uart_tx_data <= transmit_data[39:32];
                2: uart_tx_data <= transmit_data[31:24];
                3: uart_tx_data <= transmit_data[23:16];
                4: uart_tx_data <= transmit_data[15:8];
                5: uart_tx_data <= transmit_data[7:0];
                default: uart_tx_data <= 0;
            endcase

            uart_tx_valid <= 1;

            transmit_state <= transmit_state + 1;

            if (transmit_state == 5) begin
                transmit_state <= 0;
            end
        end
    end
end

reg [39:0] recieve_data = 0;
reg [2:0] recieve_state = 0; // 0-4 = bytes, 5 = stalled

// Countdown to dropping un-finished data
/* verilator lint_off WIDTH */
reg [$clog2(DROP_CLKS):0] drop_timer = DROP_CLKS;
/* verilator lint_on WIDTH */

// Recieve commands and forward to debug bus
always_ff @(posedge i_clk) begin
    cmd_valid <= 0;
    cmd_reset <= 0;

    if (recieve_state < 5) begin
        if (uart_rx_valid) begin
            case (recieve_state)
                0: recieve_data[39:32] <= uart_rx_data;
                1: recieve_data[31:24] <= uart_rx_data;
                2: recieve_data[23:16] <= uart_rx_data;
                3: recieve_data[15:8] <= uart_rx_data;
                4: recieve_data[7:0] <= uart_rx_data;
            endcase

            recieve_state <= recieve_state + 1;
            /* verilator lint_off WIDTH */
            drop_timer <= DROP_CLKS;
            /* verilator lint_on WIDTH */

            if (recieve_state == 4) begin
                // Reset
                if (recieve_data[35:32] == 4'b1111) begin
                    cmd_reset <= 1;
                    recieve_state <= 0;
                end
                else if (cmd_ready) begin
                    cmd_valid <= 1;
                    cmd_data <= {recieve_data[35:8], uart_rx_data};
                    recieve_state <= 0;
                end
            end
        end
        else if (recieve_state > 0) begin
            drop_timer <= drop_timer - 1;

            if (drop_timer == 1) begin
                recieve_state <= 0;
            end
        end
    end
    else begin
        if (cmd_ready) begin
            cmd_valid <= 1;
            cmd_data <= recieve_data[35:0];
            recieve_state <= 0;
        end
    end
end

endmodule
