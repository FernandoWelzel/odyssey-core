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
    output wire compute_req,
    input  wire compute_valid,
    input  wire branch_flag,
    
    // ALU interface
    output wire [DATA_WIDTH-1:0] pc,
    input  wire [DATA_WIDTH-1:0] new_pc,

    // Global control
    input  wire clk,
    input  wire rst
);

// State machine variables
localparam S_RESET = 0;
localparam S_INST_REQ = 1;
localparam S_INST_VALID = 2;
localparam S_COMPUTE_REQ = 3;
localparam S_COMPUTE_VALID = 4;
localparam S_UPDATE_PC = 5;

reg [2:0] c_state, n_state;

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
        S_RESET: begin
            inst_req_reg = 1'b0;

            n_state = S_INST_REQ;
        end
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
                n_state = S_UPDATE_PC;
            end
        end
        S_UPDATE_PC: begin
            n_state = S_INST_REQ;
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

		c_state <= S_RESET;
    end
    else begin
        if(c_state == S_UPDATE_PC) begin
            if (branch_flag) begin
                inst_addr_reg <= new_pc;
            end
            else begin
                inst_addr_reg <= inst_addr_reg + 1;
            end
        end
        if(c_state == S_INST_VALID) begin
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

assign pc = inst_addr;

endmodule
