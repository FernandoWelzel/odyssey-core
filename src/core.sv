// Core processor module
module core #(
    parameter DATA_WIDTH = 32,
    parameter REGISTERS = 32
)
(
    // Instructions memory bus
    output logic [DATA_WIDTH-1:0] inst_address,
    input  logic [DATA_WIDTH-1:0] r_inst,
    output logic [DATA_WIDTH-1:0] w_inst,
    output logic inst_csn,
    output logic inst_wen,

    // Data memory bus
    output logic [DATA_WIDTH-1:0] data_address,
    input  logic [DATA_WIDTH-1:0] r_data,
    output logic [DATA_WIDTH-1:0] w_data,
    output logic data_csn,
    output logic data_wen,
    
    input  logic clk,
    input  logic rst
);

// Variable declaration
logic [DATA_WIDTH-1:0] register_file [REGISTERS];

logic [6:0] opcode;
logic [2:0] funct3;
logic [6:0] funct7;

logic [4:0] rd, rs1, rs2;

logic [11:0] imm_s;
logic [11:0] imm_i;

logic [11:0] pc_jump;

// Assigments
assign opcode = r_inst[6:0];
assign funct3 = r_inst[14:12];
assign funct7 = r_inst[31:25];

assign rd = r_inst[11:7];
assign rs1 = r_inst[19:15];
assign rs2 = r_inst[24:20];

assign imm_s = {r_inst[31:25], r_inst[11:7]};
assign imm_i = {r_inst[31:20]};

// Main loop 
always @(posedge clk) begin
    if (rst) begin
        // Initializing all registers to zero
        for (int i=0; i<REGISTERS; ++i) begin
            register_file[i] <= 0;
        end

        // Other internal variables
        inst_address <= 0;

        // Instruction memory
        inst_wen = 1'b1;
        inst_csn = 1'b0;
        
        // Data memory
        data_wen = 1'b1;
        data_csn = 1'b1;

        // Pointer counter
        pc_jump <= 0;

    end 
    else begin
        // Calculate instruction
        case (opcode)
            // R instructions
            7'b0110011: begin
                pc_jump <= 1;
                
                case (funct3)
                    // ADD and SUB
                    3'b000: begin
                        case (funct7)
                            // ADD
                            7'b0000000: begin
                                register_file[rd] <= register_file[rs1] + register_file[rs2];
                            end

                            // SUB
                            7'b0100000: begin
                                register_file[rd] <= register_file[rs1] - register_file[rs2];
                            end

                            // Default
                            default: begin
                                register_file[rd] <= register_file[rd];
                            end
                        endcase
                    end

                    // SLL - Shift Left Logical
                    3'b001: begin
                        register_file[rd] <= register_file[rs1] << register_file[rs2];
                    end

                    // SLT - Set Less Than
                    3'b010: begin
                        register_file[rd] <= (register_file[rs1] < register_file[rs2]) ? 1 : 0;
                    end

                    // SLTU - Set Less Than (U)
                    3'b011: begin
                        // TODO: Fix
                        register_file[rd] <= (register_file[rs1] < register_file[rs2]) ? 1 : 0;
                    end
                    
                    // XOR
                    3'b100: begin
                        register_file[rd] <= register_file[rs1] ^ register_file[rs2];
                    end
                    
                    // SRL and SRA
                    3'b101: begin
                        case (funct7)
                            // SRL - Shift Right Logical
                            7'b0000000: begin
                                register_file[rd] <= register_file[rs1] >> register_file[rs2];
                            end

                            // SRA - Shift Right Arithmetic
                            7'b0100000: begin
                                // TODO: Fix
                                register_file[rd] <= register_file[rs1] >> register_file[rs2];
                            end

                            // Default
                            default: begin
                                register_file[rd] <= register_file[rd];
                            end
                        endcase
                    end
                    
                    // OR
                    3'b110: begin
                        register_file[rd] <= register_file[rs1] | register_file[rs2];
                    end
                    
                    // AND
                    3'b111: begin
                        register_file[rd] <= register_file[rs1] & register_file[rs2];
                    end
                endcase
            end

            // I instructions
            7'b0010011: begin
                pc_jump <= 1;

                case (funct3)
                    // ADDI
                    3'b000: begin
                        register_file[rd] <= register_file[rs1] + {20'h00000, imm_i};
                    end

                    // XORI
                    3'b100: begin
                        register_file[rd] <= register_file[rs1] ^ {20'h00000, imm_i};
                    end

                    // OR
                    3'b110: begin
                        register_file[rd] <= register_file[rs1] | {20'h00000, imm_i};
                    end

                    // AND
                    3'b111: begin
                        register_file[rd] <= register_file[rs1] & {20'h00000, imm_i};
                    end
                    
                    // Shift Left Immediate
                    3'b001: begin
                        case (imm_i[11:5])
                            // SLLI
                            7'h00: begin
                                register_file[rd] <= register_file[rs1] << imm_i[4:0];
                            end

                            // Default
                            default: begin
                                register_file[rd] <= register_file[rd];
                            end
                        endcase
                    end
                    
                    // Shift Right Immediate
                    3'b101: begin
                        case (imm_i[11:5])
                            // SRLI
                            7'h00: begin
                                register_file[rd] <= register_file[rs1] >> imm_i[4:0];
                            end

                            // SRAI
                            // TODO: Fix difference with MSB extend
                            7'h20: begin
                                register_file[rd] <= register_file[rs1] >> imm_i[4:0];
                            end

                            // Default
                            default: begin
                                register_file[rd] <= register_file[rd];
                            end
                        endcase
                    end

                    // SLTI
                    3'b010: begin
                        register_file[rd] <= (register_file[rs1] < {20'h00000, imm_i}) ? 1 : 0;
                    end
                
                    // SLTIU
                    3'b011: begin
                        if(imm_i[11]) begin
                            register_file[rd] <= (register_file[rs1] < {20'hFFFFF, imm_i}) ? 1 : 0;
                        end
                        else begin
                            register_file[rd] <= (register_file[rs1] < {20'h00000, imm_i}) ? 1 : 0;
                        end
                    end

                    // Default
                    default: begin
                        register_file[rd] <= register_file[rd];
                    end
                endcase
            end
            
            // S instructions
            7'b0100011: begin
                pc_jump <= 1;

                // Initiating all write values to zero
                w_data <= 0;

                case (funct3)
                    // SB - Store Byte
                    3'b000: begin
                        data_address <= register_file[rs1] + {20'h00000, imm_s};

                        w_data[7:0] <= register_file[rs2][7:0];
                    end
                    // SH - Store Half
                    3'b001: begin
                        data_address <= register_file[rs1] + {20'h00000, imm_s};

                        w_data[15:0] <= register_file[rs2][15:0];
                    end
                    // SW - Store Word
                    3'b010: begin
                        data_address <= register_file[rs1] + {20'h00000, imm_s};

                        w_data <= register_file[rs2];
                    end

                    // Default
                    default: begin
                        register_file[rd] <= register_file[rd];
                    end
                endcase
            end
            
            // B instructions
            7'b1100011: begin
                case (funct3)
                    // BEQ
                    3'b000: begin
                        pc_jump <= (register_file[rs1] == register_file[rs2]) ? imm_i : 1;
                    end

                    // BNE
                    3'b001: begin
                        pc_jump <= (register_file[rs1] != register_file[rs2]) ? imm_i : 1;
                    end

                    // BLT
                    3'b100: begin
                        pc_jump <= (register_file[rs1] < register_file[rs2]) ? imm_i : 1;
                    end

                    // BGE
                    3'b101: begin
                        pc_jump <= (register_file[rs1] >= register_file[rs2]) ? imm_i : 1;
                    end

                    // BLTU
                    // TODO: Fix zero extend
                    3'b110: begin
                        pc_jump <= (register_file[rs1] < register_file[rs2]) ? imm_i : 1;
                    end

                    // BGEU
                    // TODO: Fix zero extend
                    3'b111: begin
                        pc_jump <= (register_file[rs1] >= register_file[rs2]) ? imm_i : 1;
                    end

                    // Default
                    default: begin
                        register_file[rd] <= register_file[rd];
                    end
                endcase
            end
            
        // Default
        default: begin
            pc_jump <= 1;
            
            register_file[rd] <= register_file[rd];
        end
        
        endcase
        
        // Update pointer counter
        inst_address <= inst_address + {20'h00000, pc_jump};
    end
end

endmodule
