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
    output wire [DATA_WIDTH-1:0] data_addr,
    input  wire data_valid,
    input  wire [DATA_WIDTH-1:0] rdata,
    output wire [DATA_WIDTH-1:0] wdata,
    output wire inst_we,
    output wire [BYTE_DATA_WIDTH-1:0] byte_enable,

    // Global interfaces
    input  wire clk,
    input  wire rst
);

// Fetch interface
reg inst_req_reg;

// Decode unit interface
reg [DATA_WIDTH-1:0] inst;
reg pc_req;
reg pc_valid;
reg stall;

// LSU interface
reg mem_req;
reg mem_we;
reg mem_valid;
reg [BYTE_DATA_WIDTH-1:0] byte_enable_lsu;

// Register file interface
reg [LOG2_REGISTERS-1:0] addr_rd;
reg [LOG2_REGISTERS-1:0] addr_rs1;
reg [LOG2_REGISTERS-1:0] addr_rs2;

reg [1:0] rd_select;
reg [DATA_WIDTH-1:0] direct_store;

// ALU interface
reg less;
reg equal;

reg [ALU_CONTROL_BITS-1:0] alu_control;
reg signed_flag;
reg [DATA_WIDTH-1:0] imm;
reg select_imm;
reg select_pc;

// Fetch instantiation
fetch fetch_u (
    .inst_req(inst_req),
    .inst_addr(inst_addr),
    .inst_valid(inst_valid),
    .inst_data(inst_data),
    .inst(inst),
    .pc_req(pc_req),
    .pc_valid(pc_valid),
    .stall(stall),
    .pc(pc),
    .new_pc(new_pc),
    .clk(clk),
    .rst(rst)
);

// Decode instantiation
decode decode_u (
    .inst(inst),
    .pc_req(pc_req),
    .pc_valid(pc_valid),
    .stall(stall),
    .mem_req(mem_req),
    .mem_we(mem_we),
    .mem_valid(mem_valid),
    .byte_enable(byte_enable),
    .addr_rd(addr_rd),
    .addr_rs1(addr_rs1),
    .addr_rs2(addr_rs2),
    .rd_select(rd_select),
    .direct_store(direct_store),
    .less(less),
    .equal(equal),
    .alu_control(alu_control),
    .signed_flag(signed_flag),
    .imm(imm),
    .select_imm(select_imm),
    .select_pc(select_pc),
    .clk(clk),
    .rst(rst)
);

// ALU instantiation
alu alu_u (
    .a(a),
    .b(b),
    .q(q),
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
    .mem_rdata(mem_rdata),
    .mem_wdata(mem_wdata),
    .data_req(data_req),
    .data_addr(data_addr),
    .data_valid(data_valid),
    .rdata(rdata),
    .wdata(wdata),
    .inst_we(inst_we),
    .byte_enable(byte_enable),
    .clk(clk),
    .rst(rst)
);

assign inst_req = inst_req_reg;

endmodule
