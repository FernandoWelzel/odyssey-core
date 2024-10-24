// Processor core
module core #(
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
    input  wire clk,
    input  wire rst
);

reg inst_req_reg;
reg [DATA_WIDTH-1:0] inst_addr_reg;

reg data_req_reg;
reg data_we_reg;
reg [BYTE_DATA_WIDTH-1:0] byte_enable_reg;

reg [DATA_WIDTH-1:0] data_addr_reg;
reg [DATA_WIDTH-1:0] wdata_reg;

always @(posedge clk) begin
    if(rst) begin
        inst_req_reg <= 1'b0;
        inst_addr_reg <= 0;
        data_req_reg <= 0;
        data_we_reg <= 0;
        byte_enable_reg <= 0;
        data_addr_reg <= 0;
        wdata_reg <= 0;
    end else begin
        inst_req_reg <= ~inst_req_reg;
        inst_addr_reg <= 0;
        data_req_reg <= 0;
        data_we_reg <= 0;
        byte_enable_reg <= 0;
        data_addr_reg <= 0;
        wdata_reg <= 0;
    end
end

assign inst_req = inst_req_reg;
assign inst_addr = inst_addr_reg;

assign data_req = data_req_reg;
assign data_we = data_we_reg;
assign byte_enable = byte_enable_reg;

assign data_addr = data_addr_reg;
assign wdata = wdata_reg;

endmodule
