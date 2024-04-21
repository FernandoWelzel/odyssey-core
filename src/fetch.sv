// Processor fetch unit
module fetch #(
    parameter DATA_WIDTH = 32
)
(
    // output logic [DATA_WIDTH-1:0] address,
    input  logic [DATA_WIDTH-1:0] instruction,

    output logic [DATA_WIDTH-1:0] c_instruction,
    // output logic [11:0] name,

    input  logic clk,
    input  logic rst
);

// Variable declaration
// logic [DATA_WIDTH-1:0] pc;
// logic [DATA_WIDTH-1:0] c_instruction;

// Main loop 
always @(posedge clk) begin
    if(rst) begin
        // pc <= 0;
        c_instruction <= 0;
    end
    else begin
        c_instruction <= instruction;
    end
end

endmodule
