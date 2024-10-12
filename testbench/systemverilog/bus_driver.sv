// TODO: Check value of parameters
module bus_driver #(
    // Size of cache
    parameter WORD_WIDTH = 32,
    parameter BLOCK_WIDTH = 256,
    parameter BLOCK_WIDTH_WORDS = 8,
    parameter BLOCK_SIZE = 32,

    // Address division
    parameter LOG2_BLOCK_WIDTH_WORDS = 3,
    parameter LOG2_BLOCK_SIZE = 5,
    parameter TAG_WIDTH = 22,
    parameter ADDR_WIDTH = 32,
 
    parameter HBURST_WIDTH = 1,
    parameter HPROT_WIDTH = 1,
    parameter HMASTER_WIDTH = 1
)
(
    // AHB bus interface
    input  wire [ADDR_WIDTH-1:0] HADDR,
    input  wire [HBURST_WIDTH-1:0] HBURST,
    input  wire HMASTLOCK,
    input  wire [HPROT_WIDTH-1:0] HPROT,
    input  wire [2:0] HSIZE,
    input  wire HNONSEC,
    input  wire HEXCL,
    input  wire [HMASTER_WIDTH-1:0] HMASTER,
    input  wire [1:0] HTRANS,
    input  wire [WORD_WIDTH-1:0] HWDATA,
    input  wire [WORD_WIDTH/8-1:0] HWSTRB,
    input  wire HWRITE,
    
    output wire [WORD_WIDTH-1:0] HRDATA,
    output wire HREADY,
    output wire HRESP,
    output wire HEXOKAY,
    
	// Global control
    input  wire HCLK,
    input  wire HRESETn,

    input  wire clk,
    input  wire rst
);

reg [BLOCK_WIDTH-1:0] data_reg;
reg hready_reg;

// Sequential logic
always @(posedge clk) begin
    if(rst) begin
        // Reseting variables
        data_reg <= 0;
        hready_reg <= 0;
    end
    else begin
        // For simplicity of simulation, makes the
        // data read to be equal to the address
        data_reg <= {BLOCK_WIDTH_WORDS{HADDR}};

        hready_reg <= 1;
    end
end

assign HREADY = hready_reg;
assign HRDATA = data_reg;

endmodule