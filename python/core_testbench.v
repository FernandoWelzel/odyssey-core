// A wrapper for the core module - With clock generation
module core_testbench #(
    parameter DATA_WIDTH = 32,
    parameter BYTE_DATA_WIDTH = 4,
    parameter LOG2_REGISTERS = 5,
    parameter ALU_CONTROL_BITS = 3
)
(
    // Instruction cache interface
    output wire inst_req,
    output wire [DATA_WIDTH-1:0] inst_addr,

    input  wire inst_valid,
    input  wire [DATA_WIDTH-1:0] inst_data,

    // Data cache interface
    output wire data_req,
    input  wire data_valid,
    output wire data_we,
    output wire [BYTE_DATA_WIDTH-1:0] byte_enable,

    output wire [DATA_WIDTH-1:0] data_addr,
    input  wire [DATA_WIDTH-1:0] rdata,
    output wire [DATA_WIDTH-1:0] wdata,

    // Global interfaces
    input  wire rst
);

// Generating clock signal
bit clk;

initial clk = 0;
always #5 clk = ~clk;

core #(
    .DATA_WIDTH(DATA_WIDTH),
    .BYTE_DATA_WIDTH(BYTE_DATA_WIDTH),
    .LOG2_REGISTERS(LOG2_REGISTERS),
    .ALU_CONTROL_BITS(ALU_CONTROL_BITS)
) dut (
    .inst_req(inst_req),
    .inst_addr(inst_addr),
    .inst_valid(inst_valid),
    .inst_data(inst_data),
    .data_req(data_req),
    .data_valid(data_valid),
    .data_we(data_we),
    .byte_enable(byte_enable),
    .data_addr(data_addr),
    .rdata(rdata),
    .wdata(wdata),
    .clk(clk),
    .rst(rst)
);

initial begin
    // Open the VCD file for dumping
    $dumpfile("simulation.vcd");
    $dumpvars(0, dut);
end

endmodule