// Processor register file
module register_file #(
    parameter DATA_WIDTH = 32,
    parameter REGISTERS = 32,
    parameter LOG2_REGISTERS = 5
)
(
    // Data interface
    input  wire [LOG2_REGISTERS-1:0] addr_rs1,
    input  wire [LOG2_REGISTERS-1:0] addr_rs2,
    input  wire [LOG2_REGISTERS-1:0] addr_rd,

    input  wire [DATA_WIDTH-1:0] data_rd,
    output wire [DATA_WIDTH-1:0] data_rs1,
    output wire [DATA_WIDTH-1:0] data_rs2,

    input  wire clk,
    input  wire rst
);

// Internal variable declaration
reg [REGISTERS*DATA_WIDTH-1:0] registers;
reg [REGISTERS*DATA_WIDTH-1:0] registers_new;

// Connecting registers to new values
generate;
    genvar i;

    for (i = 0; i<REGISTERS; i=i+1) begin
        if(i == 0) begin
            assign registers_new[DATA_WIDTH-1:0] = 0;
        end
        else begin
            assign registers_new[DATA_WIDTH*(i+1)-1:DATA_WIDTH*i] = (addr_rd == i) ? data_rd : registers[DATA_WIDTH*(i+1)-1:DATA_WIDTH*i];
        end
    end
endgenerate

// Update of registers
always @(posedge clk) begin
    if(rst) begin
        registers <= 0;
    end
    else begin
        registers <= registers_new;
    end
end

endmodule
