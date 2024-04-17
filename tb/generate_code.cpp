#include <iostream>
#include <fstream>
#include <string>

typedef enum instruction_t {
    ADD, SUB, XOR, OR, AND, SLL, SRL, SRA, SLT, SLTU,
    SB, SH, SW
} instruction_t ;

// Returns the integer value of a instruction in for riscv 32 bit 
// FIX: Only works for R instructions
unsigned int instruction(instruction_t type, int rd, int rs1, int rs2, int imm) {
    unsigned int result = 0x0;
    
    unsigned int opcode = 0x00;

    unsigned int funct3 = 0x0;
    unsigned int funct7 = 0x0;
    
    switch (type)
    {
    case ADD:        
        opcode = 0x33;

        funct3 = 0x0;
        funct7 = 0x0;

        break;

    case SUB:
        opcode = 0x33;

        funct3 = 0x0;
        funct7 = 0x20;

        break;
    
    case XOR:
        opcode = 0x33;

        funct3 = 0x04;
        funct7 = 0x00;

        break;

    case OR:
        opcode = 0x33;

        funct3 = 0x06;
        funct7 = 0x00;

        break;

    case AND:
        opcode = 0x33;

        funct3 = 0x07;
        funct7 = 0x00;

        break;

    case SLL:
        opcode = 0x33;

        funct3 = 0x01;
        funct7 = 0x00;

        break;

    case SRL:
        opcode = 0x33;

        funct3 = 0x05;
        funct7 = 0x00;

        break;

    case SRA:
        opcode = 0x33;

        funct3 = 0x05;
        funct7 = 0x20;

        break;

    case SLT:
        opcode = 0x33;

        funct3 = 0x02;
        funct7 = 0x00;

        break;

    case SLTU:
        opcode = 0x33;

        funct3 = 0x03;
        funct7 = 0x00;

        break;

    case SB:
        opcode = 0x23;

        funct3 = 0x00;
        break;

    case SH:
        opcode = 0x23;

        funct3 = 0x01;
        break;

    case SW:
        opcode = 0x23;

        funct3 = 0x02;
        break;
    }

    // Updating result based on the shift of all values
    result = ((imm >> 5) << 25) + (funct7 << 25) + (rs2 << 20) + (rs1 << 15) + (funct3 << 12) + (rd << 7) + ((imm % 32) << 7) + opcode;

    return result;
}

int main(int argc, char const *argv[])
{
    // Open a binary file in write mode
    std::ofstream outFile("generated_bytecode.riscv", std::ios::binary);

    if (!outFile) {
        std::cerr << "Error opening file for writing!" << std::endl;
        return 1;
    }

    unsigned int inst1 = instruction(ADD, 0, 0, 0, 0);
    std::string inst1_str = std::to_string(inst1);
    outFile << inst1_str << std::endl;

    unsigned int inst2 = instruction(SW, 0, 0, 0, 0);
    std::string inst2_str = std::to_string(inst2);
    outFile << inst2_str << std::endl;

    // Check if writing was successful
    if (!outFile.good()) {
        std::cerr << "Error occurred while writing to file!" << std::endl;
        return 1;
    }

    // Close the file
    outFile.close();

    std::cout << "Data has been written to file successfully." << std::endl;

    return 0;
}

