class Instruction():
    def __init__(self, opcode : int):
        # TODO: Assert size of opcode
        self.opcode = opcode

class RInstruction(Instruction):
    def __init__(self, opcode : int, rd : int, rs1 : int, rs2 : int, func3 : int, func7 : int):
        super().__init__(opcode)
        
        # TODO: Assert size of each of the variables
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.func3 = func3
        self.func7 = func7

        # Calculate the new instruction
        self.update_inst()
    
    def __str__(self) -> str:
        return f"R type instruction : {'0x{0:08X}'.format(self.inst)}"

    def update_inst(self):
        # TODO: Assert size of new variables
        self.inst = self.opcode | (self.rd << 7) | (self.rs1 << 15) | (self.rs2 << 20) | (self.func3 << 12) | (self.func7 << 25)

class IInstruction(Instruction):
    def __init__(self, opcode : int, rd : int, rs1 : int, imm : int, func3 : int):
        super().__init__(opcode)
        
        # TODO: Assert size of each of the variables
        self.rd = rd
        self.rs1 = rs1
        self.imm = imm
        self.func3 = func3

        # Calculate the new instruction
        self.update_inst()
    
    def __str__(self) -> str:
        return f"R type instruction : {'0x{0:08X}'.format(self.inst)}"

    def update_inst(self):
        # TODO: Assert size of new variables
        self.inst = self.opcode | (self.rd << 7) | (self.rs1 << 15) | (self.imm << 20) | (self.func3 << 12)

# TODO: Make all other instructions types

# TODO: Fix this horrible looking code
def create_instruction(instruction_bin):
    instruction = None

    match(instruction_bin & 0b1111111):
        # R instruction
        case 0b0110011:
            instruction = RInstruction(0b0110011, (instruction_bin >> 7) & 0b11111, (instruction_bin >> 15) & 0b11111, (instruction_bin >> 20) & 0b11111, (instruction_bin >> 12) & 0b111, (instruction_bin >> 25) & 0b1111111)
        
        # I instruction
        case 0b0010011:
            instruction = IInstruction(0b0010011, (instruction_bin >> 7) & 0b11111, (instruction_bin >> 15) & 0b11111, (instruction_bin >> 20) & 0b111111111111, (instruction_bin >> 12) & 0b111)
    
    # Ilegal instruction
    if instruction == None:
        raise Exception

    return instruction