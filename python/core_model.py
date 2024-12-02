from instructions import Instruction, IInstruction

# Models core internal state
class CoreState():
    def __init__(self):
        self.register_file = [0 for _ in range(32)]
        
        self.pc = 0

    def reset(self):
        self.register_file = [0 for _ in range(32)]
        
        self.pc = 0

    def __eq__(self, another_state):
        for i in range(32):
            if(int(self.register_file[i]) != int(another_state.register_file[i])):
                return False
        
        if int(self.pc) != int(another_state.pc):
            return False
        
        return True
    
    def to_int(self):
        for i in range(32):
            self.register_file[i] = int(self.register_file[i])
        
        self.pc = int(self.pc)

def diff_state(state_a : CoreState, state_b : CoreState):
    return_string = ""

    for i in range(32):
        if state_a.register_file[i] != state_b.register_file[i]:
            return_string += f"Register file [{i}]: {state_a.register_file[i]} != {state_b.register_file[i]}\n"
    
    if state_a.pc != state_b.pc:
            return_string += f"Pointer counter: {state_a.pc} != {state_b.pc}"
    
    return return_string

class Memory():
    def __init__(self):
        self.memory = {}
    
    def reset(self):
        self.memory = {}

    def read(self, address):
        if address in self.memory.keys():
            return self.memory[address]
        else:
            # TODO: Fix memory values
            return address

    def write(self, address, data):
        self.memory[address] = data

# Models behavior of processor core
class CoreModel():
    def __init__(self):
        self.state = CoreState()
        self.memory = Memory()
    
    def reset(self):
        self.state.reset()
        self.memory.reset()
    
    def execute(self, instruction : Instruction):
        # TODO: In binary number library, add a function for sign extending based on the number of bits
        if instruction.type in ["I", "IM", "IJ", "IE", "S"]:
            # Sign extension of immediate
            sign_bit = instruction.imm & 0x800
            
            if sign_bit & 0x800:
                imm = instruction.imm | 0xFFFFF000
            else:
                imm = instruction.imm

        if instruction.type in ["B"]:
            # Sign extension of immediate
            sign_bit = instruction.imm & 0x1000
            
            if sign_bit & 0x1000:
                imm = instruction.imm | 0xFFFFE000
            else:
                imm = instruction.imm

        if instruction.type in ["UA", "UL"]:
            imm = instruction.imm
        
        if instruction.type in ["J"]:
            # Sign extension of immediate
            sign_bit = instruction.imm & 0x10000
            
            if sign_bit & 0x10000:
                imm = instruction.imm | 0xFFFE0000
            else:
                imm = instruction.imm

        # Execute basd on opcode
        match instruction.opcode:
            # Register operations
            case 0b0110011:
                match instruction.func3:
                    case 0x0:
                        match instruction.func7:
                            case 0X00:
                                self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] + self.state.register_file[instruction.rs2]
                            case 0X20:
                                self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] - self.state.register_file[instruction.rs2]
                            case default:
                                raise Exception
                    case 0x4:
                        match instruction.func7:
                            case 0X00:
                                self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] ^ self.state.register_file[instruction.rs2]
                            case default:
                                raise Exception
                    case 0x6:
                        match instruction.func7:
                            case 0X00:
                                self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] | self.state.register_file[instruction.rs2]
                            case default:
                                raise Exception
                    case 0x7:
                        match instruction.func7:
                            case 0X00:
                                self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] & self.state.register_file[instruction.rs2]
                            case default:
                                raise Exception
                    case 0x1:
                        match instruction.func7:
                            case 0X00:
                                self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] << self.state.register_file[instruction.rs2]
                            case default:
                                raise Exception
                    case 0x5:
                        match instruction.func7:
                            case 0X00:
                                self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] >> self.state.register_file[instruction.rs2]
                            # TODO: MSB-extend
                            case 0X20:
                                self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] >> self.state.register_file[instruction.rs2]
                            case default:
                                raise Exception
                    case 0x2:
                        match instruction.func7:
                            case 0X00:
                                self.state.register_file[instruction.rd] = 1 if self.state.register_file[instruction.rs1] < self.state.register_file[instruction.rs2] else 0
                            case default:
                                raise Exception
                    case 0x3:
                        match instruction.func7:
                            # TODO: Zero extends
                            case 0X00:
                                self.state.register_file[instruction.rd] = 1 if self.state.register_file[instruction.rs1] < self.state.register_file[instruction.rs2] else 0
                            case default:
                                raise Exception

                # Increments pointer counter
                self.state.pc = self.state.pc + 1

            # Immediate operations
            case 0b0010011:               
                match instruction.func3:
                    case 0x0:
                        self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] + imm
                    case 0x4:
                        self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] ^ imm
                    case 0x6:
                        self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] | imm
                    case 0x7:
                        self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] & imm
                    case 0x1:
                        if instruction.imm <= 31:
                            self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] << imm
                        else:
                            raise Exception
                    case 0x5:
                        match instruction.imm >> 5:
                            case 0x00:
                                self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] >> imm
                            case 0x20:
                                # TODO: Fix MSB-extends
                                self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] >> imm
                            case _:
                                raise Exception
                    case 0x2:
                        self.state.register_file[instruction.rd] = 1 if self.state.register_file[instruction.rs1] < imm else 0
                    case 0x3:
                        # TODO: Zero extends
                        self.state.register_file[instruction.rd] = 1 if self.state.register_file[instruction.rs1] < imm else 0

                # Increments pointer counter
                self.state.pc = self.state.pc + 1

            # Immediate operations - Load
            case 0b0000011:
                match instruction.func3:
                    case 0x0:
                        self.state.register_file[instruction.rd] = self.memory.read((self.state.register_file[instruction.rs1] + imm)) & 0xFF
                    case 0x1:
                        self.state.register_file[instruction.rd] = self.memory.read((self.state.register_file[instruction.rs1] + imm)) & 0xFFFF
                    case 0x2:
                        self.state.register_file[instruction.rd] = self.memory.read((self.state.register_file[instruction.rs1] + imm)) & 0xFFFFFFFF
                    case 0x4:
                        # TODO: Fix zero extend
                        self.state.register_file[instruction.rd] = self.memory.read((self.state.register_file[instruction.rs1] + imm)) & 0xFF
                    case 0x5:
                        # TODO: Fix zero extend
                        self.state.register_file[instruction.rd] = self.memory.read((self.state.register_file[instruction.rs1] + imm)) & 0xFFFF
                
                # Increments pointer counter
                self.state.pc = self.state.pc + 1
            
            # Store operations
            case 0b0100011:
                match instruction.func3:
                    case 0x0:
                        self.memory.write(self.state.register_file[instruction.rs1] + imm, self.state.register_file[instruction.rs2] & 0xFF)
                    case 0x1:
                        self.memory.write(self.state.register_file[instruction.rs1] + imm, self.state.register_file[instruction.rs2] & 0xFFFF)
                    case 0x2:
                        self.memory.write(self.state.register_file[instruction.rs1] + imm, self.state.register_file[instruction.rs2] & 0xFFFFFFFF)
                    case _:
                        raise Exception

                # Increments pointer counter
                self.state.pc = self.state.pc + 1

            # Branch operations
            case 0b1100011:
                branch = False

                match instruction.func3:
                    case 0x0:
                        if self.state.register_file[instruction.rs1] == self.state.register_file[instruction.rs2]: branch = True
                    case 0x1:
                        if self.state.register_file[instruction.rs1] != self.state.register_file[instruction.rs2]: branch = True
                    case 0x4:
                        if self.state.register_file[instruction.rs1] < self.state.register_file[instruction.rs2]: branch = True
                    case 0x5:
                        if self.state.register_file[instruction.rs1] >= self.state.register_file[instruction.rs2]: branch = True
                    case 0x6:
                        # TODO: Fix zero extend
                        if self.state.register_file[instruction.rs1] < self.state.register_file[instruction.rs2]: branch = True
                    case 0x7:
                        # TODO: Fix zero extend
                        if self.state.register_file[instruction.rs1] >= self.state.register_file[instruction.rs2]: branch = True
                    case _:
                        raise Exception
                
                if branch:
                    self.state.pc += imm
                else:
                    self.state.pc += 1
            
            # Jump
            case 0b1101111:
                self.state.register_file[instruction.rd] = self.state.pc + 4

                self.state.pc += imm

            # Jump Reg
            case 0b1100111:
                match instruction.func3:
                    case 0x0:
                        self.state.register_file[instruction.rd] = self.state.pc + 4

                        self.state.pc = self.state.register_file[instruction.rs1] + imm

                    case _:
                        raise Exception

            # Load Upper imm
            case 0b0110111:
                self.state.register_file[instruction.rd] = (imm << 12)

                self.state.pc += 1

            # Add Upper imm
            case 0b0010111:
                self.state.register_file[instruction.rd] = self.state.pc + (imm << 12)

                self.state.pc += 1