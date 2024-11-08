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

# Base instruction class
class Instruction():
    def __init__(self, type : str):
        # Initializes opcode
        if type in type_dictionary:
            self.opcode = type_dictionary[type]
        else:
            raise Exception
        
        self.type = type
        self.inst = 0

    def __str__(self) -> str:
        return f"{'0x{0:08X}'.format(self.inst)}"
    
    def update_inst():
        ...

    def randomize():
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
    
    def randomize(self):
        self.rs1 = random.randint(0, 31)
        self.rs2 = random.randint(0, 31)
    
        self.func3 = random.choice([0x0, 0x1, 0x4, 0x5, 0x6, 0x7])
    
        self.imm = random.randint(0, 4095)
        
        self.update_inst()

# TODO: Make all other instructions types

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
   
    # Ilegal instruction
    if instruction == None:
        raise Exception

    return instruction

# Create completly random instruction
def create_random_instruction():
    # Random instruction type
    match random.choice(["R", "I", "S", "B", "J", "U"]):
        case "R":
            instruction = RInstruction(0, 0, 0, 0, 0)
        
        case "I":
            # TODO: Enable other instructions
            # sub_type = random.choice(["I", "IM", "IJ", "IE"])
            sub_type = random.choice(["I", "IM"])
            sub_type_opcode = type_dictionary[sub_type]

            instruction = IInstruction(sub_type_opcode, 0, 0, 0, 0)
        
        # TODO: Create the code for remaining instructions
        case "S":
            instruction = SInstruction(0, 0, 0, 0)
        
        case "B":
            instruction = BInstruction(0, 0, 0, 0)
        
        case "J":
            # TODO: Substitute instruction
            instruction = RInstruction(0, 0, 0, 0, 0)
        
        case "U":
            # TODO: Substitute instruction
            instruction = RInstruction(0, 0, 0, 0, 0)
    
    # Randomize internal values
    instruction.randomize()

    # Returns a copy of the instance
    return copy.deepcopy(instruction)