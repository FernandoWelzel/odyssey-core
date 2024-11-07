from instructions import Instruction, IInstruction

# Models core internal state
class CoreState():
    def __init__(self):
        self.register_file = [0 for _ in range(32)]
        
        # TODO: Fix PC offset
        self.pc = -1

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
    for i in range(32):
        if state_a.register_file[i] != state_b.register_file[i]:
            print(f"Register file [{i}]: {state_a.register_file[i]} != {state_b.register_file[i]}")
    
    if state_a.pc != state_b.pc:
            print(f"Pointer counter: {state_a.pc} != {state_b.pc}")

class Memory():
    def __init__(self):
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
    
    def execute(self, instruction : Instruction):
        if instruction.type in ["I", "IM"]:
            # Sign extension of immediate
            imm = instruction.imm & 0xFFF
            
            if imm & 0x800:
                imm = imm | 0xFFFFF000

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
            case 0b0100011:
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
                self.register_file[instruction.rd] = (imm << 12)

            # Add Upper imm
            case 0b0010111:
                self.register_file[instruction.rd] = self.state.pc + (imm << 12)
