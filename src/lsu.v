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

    input  wire [DATA_WIDTH-1:0] mem_wdata,

    input  wire [BYTE_DATA_WIDTH-1:0] mem_byte_enable,

    // Data cache interface
    output wire data_req,
    output wire [DATA_WIDTH-1:0] data_addr,
    input  wire data_valid,
    input  wire [DATA_WIDTH-1:0] rdata,
    output wire [DATA_WIDTH-1:0] wdata,
    output wire data_we,
    output wire [BYTE_DATA_WIDTH-1:0] byte_enable,

    // Global interfaces
    input  wire clk,
    input  wire rst
);

// State machine variables
localparam S_WAIT = 0;
localparam S_MEM_REQ = 1;
localparam S_DATA_VALID = 2;

reg [1:0] c_state, n_state;

reg [DATA_WIDTH-1:0] data_addr_reg;

assign data_req = mem_req;
assign data_we = mem_we;
assign data_addr = data_addr_reg;
assign byte_enable = mem_byte_enable;
assign wdata = mem_wdata;

assign mem_valid = data_valid;

// Byte enable connection
generate;
    genvar i;

    for (i=0; i<BYTE_DATA_WIDTH; ++i) begin
        assign result_data[(i+1)*8-1:i*8] = rdata[(i+1)*8-1:i*8] & {8{mem_byte_enable[i]}};
    end
endgenerate

// Combinatorial
always @(*) begin
	case (c_state)
        S_WAIT: begin
            if(mem_req) begin
                n_state <= S_MEM_REQ;
            end
            else begin
                n_state <= S_WAIT;
            end
        end
        S_MEM_REQ: begin
            if(data_valid) begin
                n_state <= S_DATA_VALID;
            end
            else begin
                n_state <= S_MEM_REQ;
            end
        end
        S_DATA_VALID: begin
            if(mem_req) begin
                n_state <= S_MEM_REQ;
            end
            else begin
                n_state <= S_WAIT;
            end
        end
        default: begin
            n_state <= S_WAIT;
        end
    endcase
end

always @(posedge clk) begin
    if(rst) begin
		c_state <= S_WAIT;
    end
    else begin
        if(c_state == S_WAIT) begin
            data_addr_reg <= mem_addr;
        end

		c_state <= n_state;
    end
end

endmodule
