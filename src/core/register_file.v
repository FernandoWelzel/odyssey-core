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

    input  wire rf_enable,

    input  wire clk,
    input  wire rst
);

// Internal variable declaration
reg [DATA_WIDTH-1:0] registers [REGISTERS];
reg [DATA_WIDTH-1:0] registers_new [REGISTERS];

reg [DATA_WIDTH-1:0] data_rs1_reg;
reg [DATA_WIDTH-1:0] data_rs2_reg;

integer j;

// Connecting registers to new values
generate;
    genvar i;

    for (i = 0; i<REGISTERS; i=i+1) begin : G_MUX
        if(i == 0) begin : G_ZERO
            assign registers_new[i] = 0;
        end
        else begin : G_REST
            assign registers_new[i] = (addr_rd == i) ? data_rd : registers[i];
        end
    end    

endgenerate

// Generating output connection
always @(*) begin
    data_rs1_reg = registers[addr_rs1];
    data_rs2_reg = registers[addr_rs2];
end

// Update of registers
always @(posedge clk) begin
    if(rst) begin
        for (j=0; j<REGISTERS; ++j) begin
            registers[j] <= 0;        
        end
    end
    else begin
        for (j=0; j<REGISTERS; ++j) begin
            if(rf_enable) begin
                registers[j] <= registers_new[j];        
            end
            else begin
                registers[j] <= registers[j];        
            end
        end
    end
end

assign data_rs1 = data_rs1_reg;
assign data_rs2 = data_rs2_reg;

endmodule
