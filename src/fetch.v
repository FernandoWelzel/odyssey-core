// Processor fetch unit
module fetch #(
    parameter DATA_WIDTH = 32,
    parameter START_ADDR = 32'h00000000 
)
(
    // Instruction cache interface
    output wire inst_req,
    output wire [DATA_WIDTH-1:0] inst_addr,

    input  wire inst_valid,
    input  wire [DATA_WIDTH-1:0] inst_data,

    // Decode unit interface
    output wire [DATA_WIDTH-1:0] inst,
    output wire pc_req,
    input  wire pc_valid,
    input  wire stall,
    
    // ALU interface
    output wire [DATA_WIDTH-1:0] pc,
    input  wire [DATA_WIDTH-1:0] new_pc,

    // Global control
    input  wire clk,
    input  wire rst
);

// State machine variables
localparam UPDATE = 0;
localparam WAIT_MEM = 1;
localparam WAIT_PC = 2;

integer c_state, n_state;

// Internal variables
reg [DATA_WIDTH-1:0] inst_addr_reg;
reg [DATA_WIDTH-1:0] inst_reg;
reg inst_req_reg;

// Combinatorial
always @(*) begin
	case (c_state)
        UPDATE: begin
            inst_req_reg = 1'b1;

            if(inst_req) begin
                n_state = WAIT_MEM;
            end
            else if (pc_req) begin
                n_state = WAIT_PC;
            end
            else begin
                n_state = UPDATE;
            end
        end
        WAIT_MEM: begin
            inst_req_reg = 1'b0;

            if(inst_valid) begin
                n_state = UPDATE;
            end
            else begin 
                n_state = WAIT_MEM;
            end
        end
        WAIT_PC: begin
            inst_req_reg = 1'b0;

            if(pc_valid) begin
                n_state = UPDATE;
            end
            else begin 
                n_state = WAIT_PC;
            end
        end
        default: begin
            inst_req_reg = 1'b0;

            n_state = n_state;
        end
    endcase
end

// Sequential - FSM logic
always @(posedge clk) begin
    if(rst) begin
        // Initialize first memory addr
        inst_addr_reg <= START_ADDR;

        inst_reg = 0;

		c_state <= UPDATE;
    end
    else begin
        // TODO: Fix to account for jumps in the address    
        if(c_state == UPDATE) begin
            inst_addr_reg = inst_addr_reg + 1; 

            inst_reg = inst_data;
        end

		c_state <= n_state;
    end
end

// Internal variables to outside connection
assign inst_addr = inst_addr_reg;

assign inst_req = inst_req_reg;

assign inst = inst_reg;

endmodule
