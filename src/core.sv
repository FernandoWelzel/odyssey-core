// Core processor module
module core #(
    parameter DATA_WIDTH = 32,
    parameter REGISTERS = 32
)
(
    // Instructions memory bus
    output logic [DATA_WIDTH-1:0] inst_address,
    input  logic [DATA_WIDTH-1:0] inst,

    // Data memory bus
    output logic [DATA_WIDTH-1:0] data_address,
    input  logic [DATA_WIDTH-1:0] r_data,
    output logic [DATA_WIDTH-1:0] w_data,

    input  logic clk,
    input  logic rst
);

// Variable declaration
logic [DATA_WIDTH-1:0] register_file [REGISTERS];

logic [6:0] opcode;
logic [2:0] funct3;
logic [6:0] funct7;

logic [4:0] rd, rs1, rs2;

logic [11:0] imm;

// Assigments
assign opcode = inst[6:0];
assign funct3 = inst[14:12];
assign funct7 = inst[6:0];

assign rd = inst[11:7];
assign rs1 = inst[19:15];
assign rs2 = inst[24:20];

assign imm = {inst[31:25], inst[11:7]};

// Main loop 
always @(posedge clk) begin
    // Update instruction counter
    // TODO: Correctly update PC
    inst_address <= inst_address + 1;

    // Calculate instruction
    case (opcode)
        // R instructions
        7'b0110011: begin
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
        
        // S instructions
        7'b0100011: begin
            // Initiating all write values to zero
            w_data <= 0;

            case (funct3)
                // SB - Store Byte
                3'b000: begin
                    data_address <= register_file[rs1] + imm;

                    w_data[7:0] <= register_file[rs2][7:0];
                end
                // SH - Store Half
                3'b001: begin
                    data_address <= register_file[rs1] + imm;

                    w_data[15:0] <= register_file[rs2][15:0];
                end
                // SW - Store Word
                3'b010: begin
                    data_address <= register_file[rs1] + imm;

                    w_data <= register_file[rs2];
                end
            endcase
        end
    endcase
end

endmodule