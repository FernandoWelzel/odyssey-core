# TODO: Create Python library to deal with binary conversions
import numpy as np
import random
import copy

# Correspondency of instruction FMT with opcode
type_dictionary = {
    "R"  : 0b0110011,
    "I"  : 0b0010011,
    "IM" : 0b0000011,
    "S"  : 0b0100011,
    "B"  : 0b1100011,
    "J"  : 0b1101111,
    "IJ" : 0b1100111,
    "UL" : 0b0110111,
    "UA" : 0b0010111,
    "IE" : 0b1110011
}

# Correspondance of funct3 and func7 with name
name_dictionary = {
    "R"  : {
        0x0: { 0x00: "ADD", 0x20: "SUB" }, 0x1: { 0x00: "SLL" }, 0x2: { 0x00: "SLT" }, 0x3: { 0x00: "SLTU" },
        0x4: { 0x00: "XOR" }, 0x5: { 0x00: "SRL", 0x20: "SRA" }, 0x6: { 0x00: "OR" }, 0x7: { 0x00: "AND" }
    },
    "I"  : {
        0x0 : "ADDI", 0x1 : "SLLI", 0x2 : "SLTI", 0x3 : "SLTIU", 0x4 : "XORI", 0x5 : "SRLI/SRLA",
        0x6 : "ORI", 0x7 : "ANDI"
    },
    "IM" : {
        0x0 : "LB", 0x1 : "LH", 0x2 : "LW", 0x4 : "LBU", 0x5 : "LHU"
    },
    "S"  : {
        0x0 : "SB", 0x1 : "SH", 0x2 : "SW"
    },
    "B"  : {
        0x0 : "BEQ", 0x1 : "BNE", 0x4 : "BLT", 0x5 : "BGE", 0x6 : "BLTU", 0x7 : "BGEU"
    },
    "J"  : "JAL",
    "IJ" : "JALR",
    "UL" : "LUI",
    "UA" : "AUIPC",
    "IE" : {
        0x0 : "ECALL",
        0x1 : "EBREAK"
    }
}

# Base instruction class
class Instruction():
    def __init__(self, type : str, name : str = None):
        # Initializes opcode
        if type in type_dictionary:
            self.opcode = type_dictionary[type]
        else:
            raise Exception
        
        self.type = type
        self.name = name

        self.inst = 0

    def __str__(self) -> str:
        return f"{self.type} - {self.name} - {'0x{0:08X}'.format(self.inst)}"
    
    def update_inst(self):
        ...

    def randomize(self):
        ...

class RInstruction(Instruction):
    def __init__(self, rd : int, rs1 : int, rs2 : int, func3 : int, func7 : int):
        super().__init__("R")
        
        # TODO: Assert size of each of the variables
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.func3 = func3
        self.func7 = func7

        # Calculate the new instruction
        self.update_inst()
    
    def update_inst(self):
        # TODO: Assert size of new variables
        self.inst = self.opcode | (self.rd << 7) | (self.rs1 << 15) | (self.rs2 << 20) | (self.func3 << 12) | (self.func7 << 25)

        # Get name of instruction
        if self.func3 in name_dictionary["R"].keys():
            if self.func7 in name_dictionary["R"][self.func3].keys():
                self.name = name_dictionary["R"][self.func3][self.func7]
            else:
                raise Exception
        else:
            raise Exception

    def randomize(self):
        self.rd = random.randint(0, 31)
        self.rs1 = random.randint(0, 31)
        self.rs2 = random.randint(0, 31)
        self.func3 = random.randint(0, 7)

        if self.func3 == 0x0 or self.func3 == 0x0:
            self.func7 = random.choice([0x00, 0x20])
        else:
            self.func7 = 0x00
        
        self.update_inst()
        
class IInstruction(Instruction):
    def __init__(self, opcode : int, rd : int, rs1 : int, imm : int, func3 : int):
        match opcode:
            case 0b0010011:
                super().__init__("I")
            case 0b0000011:
                super().__init__("IM")
            case 0b1100111:
                super().__init__("IJ")
            case 0b1110011:
                super().__init__("IE")
            case _:
                raise Exception
        
        # TODO: Assert size of each of the variables
        self.rd = rd
        self.rs1 = rs1
        self.imm = imm
        self.func3 = func3

        # Calculate the new instruction
        self.update_inst()

    def update_inst(self):
        # TODO: Assert size of new variables
        self.inst = self.opcode | (self.rd << 7) | (self.rs1 << 15) | (self.imm << 20) | (self.func3 << 12)

        # Get name of instruction
        match self.type:
            case "I":
                if self.func3 in name_dictionary[self.type].keys():
                    self.name = name_dictionary[self.type][self.func3]
                else:
                    raise Exception
            case "IM":
                if self.func3 in name_dictionary[self.type].keys():
                    self.name = name_dictionary[self.type][self.func3]
                else:
                    raise Exception
            case "IJ":
                self.name = name_dictionary["IJ"]
            case "IE":
                if self.imm in name_dictionary["IE"].keys():
                    self.name = name_dictionary["IE"][self.imm]
                else:
                    raise Exception
            case _:
                raise Exception

    def randomize(self):
        self.rd = random.randint(0, 31)
        self.rs1 = random.randint(0, 31)

        match self.type:
            case "I":
                self.func3 = random.randint(0, 7)
            case "IM":
                self.func3 = random.choice([0x0, 0x1, 0x2, 0x4, 0x5])
            case "IJ":
                self.func3 = 0x0
            case "IE":
                self.func3 = 0x0
            case _:
                raise Exception
        
        if self.type == "I" and self.func3 in [0x1, 0x5]:
            self.imm = random.randint(0, 31)
        elif self.type == "IE":
            self.imm = random.randint(0, 1)
        else:
            self.imm = random.randint(0, 4095)
        
        self.update_inst()

class SInstruction(Instruction):
    def __init__(self, rs1 : int, rs2 : int, imm : int, func3 : int):
        super().__init__("S")
        
        # TODO: Assert size of each of the variables
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.func3 = func3

        # Calculate the new instruction
        self.update_inst()

    def update_inst(self):
        # TODO: Assert size of new variables
        # TODO: Fix horrible looking code        
        bit4_0 = (self.imm & 0b11111)
        bit11_5 = ((self.imm & 0b111111100000) >> 5)
        
        self.inst = self.opcode | (self.rs1 << 15) | (self.rs2 << 20) | (self.func3 << 12)  | (bit4_0 << 7) | (bit11_5 << 25)

        # Get name of instruction
        if self.func3 in name_dictionary["S"].keys():
            self.name = name_dictionary["S"][self.func3]
        else:
            raise Exception
    
    def randomize(self):
        self.rs1 = random.randint(0, 31)
        self.rs2 = random.randint(0, 31)
    
        self.func3 = random.choice([0x0, 0x1, 0x2])
    
        self.imm = random.randint(0, 4095)
        
        self.update_inst()

class BInstruction(Instruction):
    def __init__(self, rs1 : int, rs2 : int, imm : int, func3 : int):
        super().__init__("B")
        
        # TODO: Assert size of each of the variables
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.func3 = func3

        # Calculate the new instruction
        self.update_inst()
    
    def update_inst(self):
        # TODO: Assert size of new variables
        # TODO: Fix horrible looking code
        if (self.imm & 0x400) == 0x400:
            bit11 = 0b1
        else:
            bit11 = 0b0  
        
        if (self.imm & 0x800) == 0x800:
            bit12 = 0b1
        else:
            bit12 = 0b0
        
        bit4_1 = ((self.imm & 0b11110) >> 1)
        bit10_5 = ((self.imm & 0b11111100000) >> 5)
        
        self.inst = self.opcode | (self.rs1 << 15) | (self.rs2 << 20) | (self.func3 << 12)  | (bit11 << 7) | (bit12 << 31) | (bit4_1 << 8) | (bit10_5 << 25)

        # Get name of instruction
        if self.func3 in name_dictionary["B"].keys():
            self.name = name_dictionary["B"][self.func3]
        else:
            raise Exception
    
    def randomize(self):
        self.rs1 = random.randint(0, 31)
        self.rs2 = random.randint(0, 31)
    
        self.func3 = random.choice([0x0, 0x1, 0x4, 0x5, 0x6, 0x7])
    
        self.imm = random.randint(0, 4095)
        
        self.update_inst()

class UInstruction(Instruction):
    def __init__(self, opcode, rd : int, imm : int):
        match opcode:
            case 0b0110111:
                super().__init__("UL")
            case 0b0010111:
                super().__init__("UA")
            case _:
                raise Exception
        
        # TODO: Assert size of each of the variables
        self.rd = rd
        self.imm = imm

        # Calculate the new instruction
        self.update_inst()
    
    def update_inst(self):
        # TODO: Assert size of new variables
        # TODO: Fix horrible looking code
        
        self.inst = self.opcode | (self.rd << 7) | (self.imm << 12)

        # Get name of instruction
        self.name = name_dictionary[self.type]

    def randomize(self):
        self.rd = random.randint(0, 31)
    
        self.imm = random.randint(0, 1048575)
        
        self.update_inst()

class JInstruction(Instruction):
    def __init__(self, rd : int, imm : int):
        super().__init__("J")
        
        # TODO: Assert size of each of the variables
        self.rd = rd
        self.imm = imm

        # Calculate the new instruction
        self.update_inst()
    
    def update_inst(self):
        # TODO: Assert size of new variables
        # TODO: Fix horrible looking code
        if (self.imm & 0x100000) == 0x100000:
            bit20 = 0b1
        else:
            bit20 = 0b0
        
        if (self.imm & 0x800) == 0x800:
            bit11 = 0b1
        else:
            bit11 = 0b0
        
        bit10_1 = ((self.imm & 0b1111111111) >> 1)
        bit19_12 = ((self.imm & 0b11111111) >> 12)
        
        self.inst = self.opcode | (self.rd << 7) | (bit20 << 31) | (bit11 << 19) | (bit10_1 << 20) | (bit19_12 << 12)

        # Get name of instruction
        self.name = name_dictionary[self.type]
    
    def randomize(self):
        self.rd = random.randint(0, 31)
    
        self.imm = random.randint(0, 1048575)
        
        self.update_inst()


# TODO: Fix this horrible looking code
def create_instruction(instruction_bin):
    instruction = None

    match(instruction_bin & 0b1111111):
        # R instruction
        case 0b0110011:
            instruction = RInstruction((instruction_bin >> 7) & 0b11111, (instruction_bin >> 15) & 0b11111, (instruction_bin >> 20) & 0b11111, (instruction_bin >> 12) & 0b111, (instruction_bin >> 25) & 0b1111111)
        
        # I instruction
        case 0b0010011:
            instruction = IInstruction(0b0010011, (instruction_bin >> 7) & 0b11111, (instruction_bin >> 15) & 0b11111, (instruction_bin >> 20) & 0b111111111111, (instruction_bin >> 12) & 0b111)

        # IM instruction
        case 0b0000011:
            instruction = IInstruction(0b0000011, (instruction_bin >> 7) & 0b11111, (instruction_bin >> 15) & 0b11111, (instruction_bin >> 20) & 0b111111111111, (instruction_bin >> 12) & 0b111)

        # IJ instruction
        case 0b1100111:
            instruction = IInstruction(0b1100111, (instruction_bin >> 7) & 0b11111, (instruction_bin >> 15) & 0b11111, (instruction_bin >> 20) & 0b111111111111, (instruction_bin >> 12) & 0b111)

        # IE instruction
        case 0b1110011:
            instruction = IInstruction(0b1110011, (instruction_bin >> 7) & 0b11111, (instruction_bin >> 15) & 0b11111, (instruction_bin >> 20) & 0b111111111111, (instruction_bin >> 12) & 0b111)
        
        # S instruction
        case 0b0100011:
            imm4_0 = (instruction_bin >> 7) & 0b11111
            imm11_5 = (instruction_bin >> 24) & 0b1111111

            imm = (imm4_0) | (imm11_5 << 5)

            instruction = SInstruction((instruction_bin >> 15) & 0b11111, (instruction_bin >> 20) & 0b11111, imm, (instruction_bin >> 12) & 0b111)
            
        # B instruction
        case 0b1100011:
            imm12 = instruction_bin >> 30
            imm11 = (instruction_bin >> 6) & 0b1 
            imm4_1 = (instruction_bin >> 7) & 0b1111
            imm10_5 = (instruction_bin >> 24) & 0b111111

            imm = (imm4_1 << 1) | (imm10_5 << 5) | (imm11 << 11) | (imm12 << 12)

            instruction = BInstruction((instruction_bin >> 15) & 0b11111, (instruction_bin >> 20) & 0b11111, imm, (instruction_bin >> 12) & 0b111)

        # J instruction
        case 0b1101111:
            imm20 = instruction_bin >> 30
            imm10_1 = (instruction_bin >> 20) & 0b1111111111 
            imm11 = (instruction_bin >> 19) & 0b1
            imm19_12 = (instruction_bin >> 11) & 0b11111111

            imm = (imm10_1 << 1) | (imm20 << 20) | (imm11 << 11) | (imm19_12 << 12)

            instruction = JInstruction((instruction_bin >> 7) & 0b11111, imm)

        # U instruction
        case 0b0110111:
            imm = ((instruction_bin & 0xFFFFF000) >> 12)

            instruction = UInstruction(0b0110111, (instruction_bin >> 7) & 0b11111, imm)

        # U instruction
        case 0b0010111:
            imm = ((instruction_bin & 0xFFFFF000) >> 12)

            instruction = UInstruction(0b0010111, (instruction_bin >> 7) & 0b11111, imm)

    # Ilegal instruction
    if instruction == None:
        raise Exception

    return instruction

# Create completly random instruction
def create_random_instruction():
    choice = np.random.choice(["R", "I", "S", "B", "J", "U"], p=[0.5, 0.5, 0, 0, 0, 0])

    # Random instruction type
    match choice:
        case "R":
            instruction = RInstruction(0, 0, 0, 0, 0)
        
        case "I":
            sub_type = np.random.choice(["I", "IM", "IJ", "IE"], p=[0.5, 0.3, 0.1, 0.1])

            sub_type_opcode = type_dictionary[sub_type]

            instruction = IInstruction(sub_type_opcode, 0, 0, 0, 0)

        case "S":
            instruction = SInstruction(0, 0, 0, 0)
        
        case "B":
            instruction = BInstruction(0, 0, 0, 0)
        
        case "J":
            instruction = JInstruction(0, 0)
        
        case "U":
            sub_type = np.random.choice(["UL", "UA"], p=[0.5, 0.5])
            sub_type_opcode = type_dictionary[sub_type]

            instruction = UInstruction(sub_type_opcode, 0, 0)
    
    # Randomize internal values
    instruction.randomize()

    # Returns a copy of the instance
    return copy.deepcopy(instruction)