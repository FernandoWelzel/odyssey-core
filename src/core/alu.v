`include "config.v"

// Processor Arithmetic Logical Unit
module alu #(
    parameter DATA_WIDTH = 32,
    parameter ALU_CONTROL_BITS = 3
)
(
    // Data interface
    input  wire [DATA_WIDTH-1:0] a,
    input  wire [DATA_WIDTH-1:0] b,
    output wire [DATA_WIDTH-1:0] q,

    // Comparison interface
    output wire less_comp,
    output wire equal_comp,

    // External control
    input  wire signed_flag,
    input  wire [ALU_CONTROL_BITS-1:0] alu_control
);

// Local variables
reg [DATA_WIDTH-1:0] q_reg;

// Combinational logic
always @(*) begin
    case (alu_control)
        ADD_SUB_OP: begin
            q_reg = a + b;
        end
        XOR_OP: begin
            q_reg = a ^ b;
        end
        OR_OP: begin
            q_reg = a | b;
        end
        AND_OP: begin
            q_reg = a & b;
        end
        LLS_OP: begin
            q_reg = a << b;
        end
        RLS_OP: begin
            q_reg = a >> b;
        end
        default: begin
            q_reg = 0;
        end
    endcase
end

// Comparisons
assign less_comp = a < b;
assign equal_comp = a == b;

// Output connection
assign q = q_reg;

endmodule
