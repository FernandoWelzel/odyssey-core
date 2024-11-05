// Processor fetch unit
module fetch #(
    parameter DATA_WIDTH = 32,
    parameter START_ADDR = 32'hFFFFFFFF
)
(
    // Instruction cache interface
    output wire inst_req,
    output wire [DATA_WIDTH-1:0] inst_addr,

    input  wire inst_valid,
    input  wire [DATA_WIDTH-1:0] inst_data,

    // Decode unit interface
    output wire [DATA_WIDTH-1:0] inst,
    output wire compute_req,
    input  wire compute_valid,
    
    // ALU interface
    output wire [DATA_WIDTH-1:0] pc,
    input  wire [DATA_WIDTH-1:0] new_pc,

    // Global control
    input  wire clk,
    input  wire rst
);

// State machine variables
localparam S_INST_REQ = 0;
localparam S_INST_VALID = 1;
localparam S_COMPUTE_REQ = 2;
localparam S_COMPUTE_VALID = 3;

reg [1:0] c_state, n_state;

// Internal variables
reg [DATA_WIDTH-1:0] inst_addr_reg;
reg [DATA_WIDTH-1:0] inst_reg;

reg inst_req_reg;
reg compute_req_reg;
reg compute_req_reg_new;

// Combinatorial
always @(*) begin
    inst_req_reg = 1'b0;
    compute_req_reg_new = 1'b0;

	case (c_state)
        S_INST_REQ: begin
            inst_req_reg = 1'b1;

            if(inst_valid) begin
                n_state = S_INST_VALID;
            end
            else begin
                n_state = S_INST_REQ;
            end
        end
        S_INST_VALID: begin
            if(inst_valid) begin
                n_state = S_INST_VALID;
            end
            else begin
                n_state = S_COMPUTE_REQ;
            end
        end
        S_COMPUTE_REQ: begin
            compute_req_reg_new = 1'b1;

            if(compute_valid) begin
                n_state = S_COMPUTE_VALID;
            end
            else begin
                n_state = S_COMPUTE_REQ;
            end
        end
        S_COMPUTE_VALID: begin
            if(compute_valid) begin
                n_state = S_COMPUTE_VALID;
            end
            else begin
                n_state = S_INST_REQ;
            end
        end
        default: begin
            n_state = S_INST_REQ;
        end
    endcase
end

// Sequential - FSM logic
always @(posedge clk) begin
    if(rst) begin
        // Initialize first memory addr
        inst_addr_reg <= START_ADDR;

		c_state <= S_INST_REQ;
    end
    else begin
        // TODO: Fix to account for jumps in the address    
        if(c_state == S_INST_VALID) begin
            inst_addr_reg <= inst_addr_reg + 1;

            inst_reg <= inst_data;
        end

		c_state <= n_state;

        compute_req_reg <= compute_req_reg_new;
    end
end

// Internal variables to outside connection
assign inst_addr = inst_addr_reg;

assign inst_req = inst_req_reg;

assign inst = inst_reg;

assign compute_req = compute_req_reg;

endmodule
