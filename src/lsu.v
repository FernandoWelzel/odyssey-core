// Processor load and store unit
module lsu #(
    parameter DATA_WIDTH = 32,
    parameter BYTE_DATA_WIDTH = 4
)
(
    // Decode interface
    input  wire mem_req,
    input  wire mem_we,
    output wire mem_valid,

    input  wire [DATA_WIDTH-1:0] mem_addr,
    output wire [DATA_WIDTH-1:0] result_data,

    output wire [DATA_WIDTH-1:0] mem_rdata,    
    input  wire [DATA_WIDTH-1:0] mem_wdata,

    // Data cache interface
    output wire data_req,
    output wire [DATA_WIDTH-1:0] data_addr,
    input  wire data_valid,
    input  wire [DATA_WIDTH-1:0] rdata,
    output wire [DATA_WIDTH-1:0] wdata,
    output wire data_we,
    output wire [BYTE_DATA_WIDTH-1:0] byte_enable,

    // Global signals
    output wire clk,
    output wire rst
);

endmodule