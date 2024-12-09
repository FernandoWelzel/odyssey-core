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
localparam READ_MEM   = 3;
localparam WRITE_MEM  = 4;
localparam SEND_VALUE = 5;

reg [2:0] c_state, n_state;

// Internal variables
reg [BLOCK_SIZE-1:0] tag_comp;
reg [TAG_WIDTH*BLOCK_SIZE-1:0] tag_memory_reg;
reg [TAG_WIDTH*BLOCK_SIZE-1:0] tag_memory_reg_new;
reg cache_miss_reg;
reg [BLOCK_SIZE-1:0] valid_line_reg;
reg [BLOCK_SIZE-1:0] valid_line_reg_new;
reg valid_reg;
reg [BLOCK_WIDTH-1:0] data_reg;
reg [ADDR_WIDTH-1:0] HADDR_reg;
reg [1:0] HTRANS_reg;

// SSRAM variables
wire [BLOCK_WIDTH-1:0] dout;
reg wre;
reg [LOG2_BLOCK_SIZE-1:0] ad;
reg [BLOCK_WIDTH-1:0] di;

reg [LOG2_BLOCK_SIZE-1:0] write_ad;
reg [LOG2_BLOCK_SIZE-1:0] next_write_ad;

// Combinatorial logic
always @(*) begin
    wre = 1'b0;

    // State transition logic
    case (c_state)
        INIT: begin
            valid_reg = 1'b0;
            
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

            next_write_ad = write_ad;
        end
        CACHE_MISS: begin
            valid_reg = 1'b0;

            // Make a request for the block transfer from the bus
            HADDR_reg = addr;
            HTRANS_reg = 1'b1;
            
            if (HREADY) begin
                n_state = WRITE_MEM;
            end
            else begin
                n_state = CACHE_MISS;
            end

            next_write_ad = write_ad + 1;
        end
        CACHE_HIT: begin
            n_state = SEND_VALUE;

            next_write_ad = write_ad;
        end
        READ_MEM: begin
            valid_reg = 1'b0;
            
            // Write in the internal memory
            wre = 1'b0;
            
            // Goes back directly
            n_state = WRITE_MEM;

            next_write_ad = write_ad;
        end
        WRITE_MEM: begin
            valid_reg = 1'b0;
            
            // Write in the internal memory
            wre = 1'b1;
            
            // Goes back directly
            n_state = SEND_VALUE;

            next_write_ad = write_ad;
        end
        SEND_VALUE: begin
            valid_reg = 1'b1;            
            wre = 1'b0;
            
            if (req) begin
                n_state = SEND_VALUE;
            end
            else begin
                n_state = INIT;
            end

            next_write_ad = write_ad;
        end
        default: begin
            valid_reg = 1'b0;
            
            n_state = INIT;

            next_write_ad = write_ad;
        end
    endcase
end

// Generating parametric connections
// TODO: Check all the connection
generate
    genvar i;

    // Tag comparison logic
    for (i=0; i<BLOCK_SIZE; i=i+1) begin
        assign tag_comp[i] = (tag_memory_reg[TAG_WIDTH*(i+1)-1:TAG_WIDTH*i] == addr[ADDR_WIDTH-1:ADDR_WIDTH-TAG_WIDTH-1]) && valid_line_reg[i];
    end

    // Generating tag memory replacement
    for(i=0; i<BLOCK_SIZE; i++) begin
        assign tag_memory_reg_new[TAG_WIDTH*(i+1)-1:TAG_WIDTH*i] = (i == ad && wre) ? addr[ADDR_WIDTH-1:ADDR_WIDTH-TAG_WIDTH-1] : tag_memory_reg[TAG_WIDTH*(i+1)-1:TAG_WIDTH*i];
        assign valid_line_reg_new[i] = (i == ad && wre);
    end

    // Generating new data connection
    for(i=0; i<BLOCK_WIDTH_WORDS; i++) begin
        assign di[WORD_WIDTH*(i+1)-1:WORD_WIDTH*i] = (i == addr[LOG2_BLOCK_WIDTH_WORDS-1:0]) ? HRDATA : dout[WORD_WIDTH*(i+1)-1:WORD_WIDTH*i];
    end
endgenerate

reg [LOG2_BLOCK_WIDTH_WORDS-1:0] final_addr;

// Procedural logic
always @(*) begin
    // Compute final address
    final_addr = addr[LOG2_BLOCK_WIDTH_WORDS-1:0];

    // Extract data using a case statement
    // TODO: Fix this fixed size for variable
    case (final_addr)
        0: data_reg = dout[WORD_WIDTH*1-1:WORD_WIDTH*0];
        1: data_reg = dout[WORD_WIDTH*2-1:WORD_WIDTH*1];
        2: data_reg = dout[WORD_WIDTH*3-1:WORD_WIDTH*2];
        3: data_reg = dout[WORD_WIDTH*4-1:WORD_WIDTH*3];
        4: data_reg = dout[WORD_WIDTH*5-1:WORD_WIDTH*4];
        5: data_reg = dout[WORD_WIDTH*6-1:WORD_WIDTH*5];
        6: data_reg = dout[WORD_WIDTH*7-1:WORD_WIDTH*6];
        7: data_reg = dout[WORD_WIDTH*8-1:WORD_WIDTH*7];
        default: data_reg = {WORD_WIDTH{1'b0}}; // Default to zero if address is out of range
    endcase

    // Cache miss logic
    cache_miss_reg = ~|tag_comp;
end

assign data = data_reg;

// Internal registers to output
assign valid = valid_reg;

assign HADDR = HADDR_reg;
assign HTRANS = HTRANS_reg;

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
    integer i;

    if(rst) begin
        // Reseting variables
        tag_memory_reg <= 0;
        ad <= 0;
        write_ad <= 0;

        // Initializing valid line to zero
        // Obs.: All first access will result in a miss
        valid_line_reg <= 0;

        c_state <= INIT;
    end
    else begin
        if(c_state == WRITE_MEM || c_state == READ_MEM || c_state == CACHE_MISS) begin
            ad <= next_write_ad;
        end
        else begin
            for(i = 0; i < BLOCK_SIZE; i=i+1) begin
                if(tag_comp[i] && valid_line_reg[i]) begin
                    ad <= i;
                end
            end
        end

        c_state <= n_state;
        tag_memory_reg <= tag_memory_reg_new;

        valid_line_reg <= valid_line_reg_new;

        write_ad <= next_write_ad;
    end
end

// Assign constant expressions
// TODO: Adjust to the size of the variables
assign HWRITE = 1'b0; 
assign HBURST = 3'b000; // Single transfer mode
assign HMASTLOCK = 1'b0; // No locked transfers
assign HPROT = 4'b0000; // Only do opcode fetch
assign HSIZE = 3'b101; // Size of transfer is only 8-word
assign HNONSEC = 1'b0; // Only non secured transfers
assign HEXCL = 1'b0; // Not exclusive transfers
assign HMASTER = 1'b0; // Master identifier zero for instruction cache
assign HWDATA = 32'h00000000; // Will never write to a subordinate 
assign HWSTRB = 4'h0; // All lanes contain valid data 
assign HWRITE = 1'b0; // Will never write to a subordinate

endmodule