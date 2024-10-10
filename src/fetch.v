// Processor fetch unit
module fetch #(
    parameter DATA_WIDTH = 32,
    parameter START_ADDR = 0x80000000 
)
(
    input  logic [DATA_WIDTH-1:0] instruction,
    output logic [DATA_WIDTH-1:0] addr_instruction,

    input  logic clk,
    input  logic rst
);

// Variable declaration
logic [DATA_WIDTH-1:0] pc;
logic [DATA_WIDTH-1:0] c_instruction;

// Sequential
always @(posedge clk) begin
    if(rst) begin
		pc <= START_ADDR;
    end
    else begin
        // Loads current instruction
		c_instruction <= instruction;

		// Updates pc
    end
end

// Combinatorial
always_comb begin
	case (opcode)
	    // R instructions
	    7'b0110011: begin
	        pc_jump <= 1;
		end
	endcase
end

endmodule
