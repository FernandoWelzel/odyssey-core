from instructions import Instruction

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

# Models behavior of processor core
class CoreModel():
    def __init__(self):
        self.state = CoreState()
    
    def execute(self, instruction : Instruction):

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
                        self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] + instruction.imm
                    case 0x4:
                        self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] ^ instruction.imm
                    case 0x6:
                        self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] | instruction.imm
                    case 0x7:
                        self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] & instruction.imm
                    case 0x1:
                        # TODO: Exception for immediate value
                        self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] << (instruction.imm & 0b11111)
                    case 0x5:
                        # TODO: Exception for immediate value and msb-extend
                        self.state.register_file[instruction.rd] = self.state.register_file[instruction.rs1] >> (instruction.imm & 0b11111)
                    case 0x2:
                        self.state.register_file[instruction.rd] = 1 if self.state.register_file[instruction.rs1] < instruction.imm else 0
                    case 0x3:
                        # TODO: Fix zero-extend
                        self.state.register_file[instruction.rd] = 1 if self.state.register_file[instruction.rs1] < instruction.imm else 0
                
                # Increments pointer counter
                self.state.pc = self.state.pc + 1
