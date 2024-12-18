// Processor core
module core #(
    parameter DATA_WIDTH = 32,
    parameter BYTE_DATA_WIDTH = 4,
    parameter LOG2_REGISTERS = 5,
    parameter ALU_CONTROL_BITS = 3
)
(
    // Instruction cache interface
    output wire inst_req,
    output wire [DATA_WIDTH-1:0] inst_addr,

    input  wire inst_valid,
    input  wire [DATA_WIDTH-1:0] inst_data,

    // Data cache interface
    output wire data_req,
    input  wire data_valid,
    output wire data_we,
    output wire [BYTE_DATA_WIDTH-1:0] byte_enable,

    output wire [DATA_WIDTH-1:0] data_addr,
    input  wire [DATA_WIDTH-1:0] rdata,
    output wire [DATA_WIDTH-1:0] wdata,

    // Global interfaces
    input  wire clk,
    input  wire rst
);

// Decode unit interface
reg [DATA_WIDTH-1:0] pc;
reg [DATA_WIDTH-1:0] new_pc;
reg compute_req;
reg compute_valid;
reg branch_flag;

// LSU interface
reg mem_req;
reg mem_we;
reg mem_valid;
reg [BYTE_DATA_WIDTH-1:0] mem_byte_enable;
reg [DATA_WIDTH-1:0] mem_addr;
reg [DATA_WIDTH-1:0] result_data;
reg [DATA_WIDTH-1:0] mem_wdata;

// Register file interface
reg [LOG2_REGISTERS-1:0] addr_rd;
reg [LOG2_REGISTERS-1:0] addr_rs1;
reg [LOG2_REGISTERS-1:0] addr_rs2;

reg [1:0] rd_select;
reg [DATA_WIDTH-1:0] direct_store;
reg rf_enable;

// ALU interface
reg less_comp;
reg equal_comp;

reg [ALU_CONTROL_BITS-1:0] alu_control;
reg signed_flag;
reg [DATA_WIDTH-1:0] data_rs1;
reg [DATA_WIDTH-1:0] data_rs2;
reg [DATA_WIDTH-1:0] data_rd;
reg [DATA_WIDTH-1:0] imm;
reg [DATA_WIDTH-1:0] a;
reg [DATA_WIDTH-1:0] b;
reg [DATA_WIDTH-1:0] q;
reg select_imm;
reg select_pc;

// Fetch to decode
reg [DATA_WIDTH-1:0] inst;

// Fetch instantiation
fetch fetch_u (
    .inst_req(inst_req),
    .inst_addr(inst_addr),
    .inst_valid(inst_valid),
    .inst_data(inst_data),
    .inst(inst),
    .compute_req(compute_req),
    .compute_valid(compute_valid),
    .pc(pc),
    .new_pc(new_pc),
    .branch_flag(branch_flag),
    .clk(clk),
    .rst(rst)
);

// Decode instantiation
decode decode_u (
    .inst(inst),
    .compute_req(compute_req),
    .compute_valid(compute_valid),
    .branch_flag(branch_flag),
    .new_pc(new_pc),
    .mem_req(mem_req),
    .mem_we(mem_we),
    .mem_valid(mem_valid),
    .mem_byte_enable(mem_byte_enable),
    .addr_rd(addr_rd),
    .addr_rs1(addr_rs1),
    .addr_rs2(addr_rs2),
    .rd_select(rd_select),
    .rf_enable(rf_enable),
    .direct_store(direct_store),
    .less_comp(less_comp),
    .equal_comp(equal_comp),
    .alu_control(alu_control),
    .signed_flag(signed_flag),
    .imm(imm),
    .select_imm(select_imm),
    .select_pc(select_pc),
    .q(q),
    .clk(clk),
    .rst(rst)
);

// ALU instantiation
alu alu_u (
    .a(a),
    .b(b),
    .q(q),
    .signed_flag(signed_flag),
    .less_comp(less_comp),
    .equal_comp(equal_comp),
    .alu_control(alu_control)
);

// Register file instantiation
register_file register_file_u (
    .addr_rs1(addr_rs1),
    .addr_rs2(addr_rs2),
    .addr_rd(addr_rd),
    .data_rd(data_rd),
    .data_rs1(data_rs1),
    .data_rs2(data_rs2),
    .rf_enable(rf_enable),
    .clk(clk),
    .rst(rst)
);

// LSU instantiation
lsu lsu_u (
    .mem_req(mem_req),
    .mem_we(mem_we),
    .mem_valid(mem_valid),
    .mem_addr(mem_addr),
    .result_data(result_data),
    .mem_wdata(mem_wdata),
    .mem_byte_enable(mem_byte_enable),
    .data_req(data_req),
    .data_addr(data_addr),
    .data_valid(data_valid),
    .rdata(rdata),
    .wdata(wdata),
    .data_we(data_we),
    .byte_enable(byte_enable),
    .clk(clk),
    .rst(rst)
);

assign a = (select_pc) ? pc : data_rs1;
assign b = (select_imm) ? imm : data_rs2;

assign mem_addr = q;

// TODO: Fix
assign data_rd = (rd_select == 2'b00) ? q : ((rd_select == 2'b01) ? direct_store : result_data); 

endmodule
