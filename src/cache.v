// TODO: Check value of parameters
module cache #(
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
	// Microprocessor interface
    input  wire req,
    input  wire [ADDR_WIDTH-1:0] addr,

    output wire valid,
    output wire [WORD_WIDTH-1:0] data,

    // AHB bus interface
    output wire [ADDR_WIDTH-1:0] HADDR,
    output wire [HBURST_WIDTH-1:0] HBURST,
    output wire HMASTLOCK,
    output wire [HPROT_WIDTH-1:0] HPROT,
    output wire [2:0] HSIZE,
    output wire HNONSEC,
    output wire HEXCL,
    output wire [HMASTER_WIDTH-1:0] HMASTER,
    output wire [1:0] HTRANS,
    output wire [WORD_WIDTH-1:0] HWDATA,
    output wire [WORD_WIDTH/8-1:0] HWSTRB,
    output wire HWRITE,
    
    input  wire [WORD_WIDTH-1:0] HRDATA,
    input  wire HREADY,
    input  wire HRESP,
    input  wire HEXOKAY,
    
	// Global control
    input  wire HCLK,
    input  wire HRESETn,

    input  wire clk,
    input  wire rst
);

// State variables
localparam INIT       = 0;
localparam CACHE_HIT  = 1;
localparam CACHE_MISS = 2;

reg [1:0] c_state, n_state;

// Internal variables
reg [TAG_WIDTH*BLOCK_SIZE-1:0] tag_memory_reg;

wire [BLOCK_SIZE-1:0] tag_comp;

reg cache_miss_reg;

reg valid_reg;

reg [BLOCK_WIDTH-1:0] data_reg;

// Combinatorial logic
always @(*) begin
    // State transition logic
    case (c_state)
        INIT: begin
            valid_reg = 1'b1;
            
            if(req) begin
                if(cache_miss_reg) begin
                    n_state = CACHE_MISS;
                end
                else begin
                    n_state = CACHE_HIT;
                end
            end
            else begin
                n_state = INIT;
            end
        end
        CACHE_MISS: begin
            valid_reg = 1'b0;
            
            // Make a request for the block transfer from the bus
            // TODO: Fix state transition
            n_state = INIT;
        end
        CACHE_HIT: begin
            valid_reg = 1'b1;
            
            // Goes back directly
            n_state = INIT;
        end
        default: begin
            valid_reg = 1'b1;
            
            n_state = INIT;
        end
    endcase
end

reg [BLOCK_SIZE-1:0] addr_selection;

// Generating parametric connections
generate
    genvar i;

    // Tag comparison logic
    for (i=0; i<BLOCK_SIZE; i=i+1) begin
        assign tag_comp[i] = (tag_memory_reg[TAG_WIDTH*(i + 1) - 1 : TAG_WIDTH*i] == addr[ADDR_WIDTH-1:ADDR_WIDTH-TAG_WIDTH-1]);
    end
endgenerate

// SSRAM variables
wire [BLOCK_WIDTH-1:0] dout;
reg wre;
reg [LOG2_BLOCK_SIZE-1:0] ad;
reg [BLOCK_WIDTH-1:0] di;

always @(*) begin
    data_reg = dout[addr];
    
    // Will have a tag miss only with all tags are invalid
    cache_miss_reg = ~| tag_comp; 
end

assign data = data_reg;

// Internal registers to output
assign valid = valid_reg;

// Instantiation of SSRAM based memory
Gowin_RAM16S memory_block (
    .dout(dout), //output [255:0] dout
    .wre(wre),   //input wre
    .ad(ad),     //input [4:0] ad
    .di(di),     //input [255:0] di
    .clk(clk)    //input clk
);

// Sequential logic
always @(posedge clk) begin
    if(rst) begin
        c_state <= INIT;
    end
    else begin
        c_state <= n_state;
    end
end

endmodule