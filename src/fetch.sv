// Processor fetch unit
module fetch #(
    parameter DATA_WIDTH = 32,
    parameter IMM_SMALL_LENGHT = 
)
(
    output logic [DATA_WIDTH-1:0] address,
    input  logic [DATA_WIDTH-1:0] intruction,

    output logic [11:0]

    input  logic clk,
    input  logic rst
);

// Variable declaration
logic [DATA_WIDTH-1:0] pc;
logic [DATA_WIDTH-1:0] c_intruction;

// Main loop 
always @(posedge clk) begin
    if(rst) begin
        pc <= 0;
        c_intruction <= 0;
    end
    else begin
        c_intruction <= instruction;
    end
end

endmodule