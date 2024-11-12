from pyuvm import *

from tabulate import tabulate, SEPARATING_LINE

class Coverage(uvm_subscriber):
    def end_of_elaboration_phase(self):
        dtype = [('condition', bool), ('instruction', object)]
        self.cvg = []

    def write(self, value):
        self.cvg.append(value)

    def report_phase(self):
        try:
            disable_errors = ConfigDB().get(
                self, "", "DISABLE_COVERAGE_ERRORS")
        except UVMConfigItemNotFound:
            disable_errors = False
        if not disable_errors:
            # Initialize counters for each instruction type
            instructions_count = {
                "R"  : { "ADD" : 0, "SUB" : 0, "XOR" : 0, "OR" : 0, "AND" : 0, "SLL" : 0, "SRL" : 0, "SRA" : 0, "SLT" : 0, "SLTU" : 0 },
                "I"  : { "ADDI" : 0, "XORI" : 0, "ORI" : 0, "ANDI" : 0, "SLLI" : 0, "SRLI" : 0, "SRAI" : 0, "SLTI" : 0, "SLTIU" : 0 },
                "IM" : { "LB" : 0, "LH" : 0, "LW" : 0, "LBU" : 0, "LHU" : 0 },
                "S"  : { "SB" : 0, "SH" : 0, "SW" : 0 },
                "B"  : { "BEQ" : 0, "BNE" : 0, "BLT" : 0, "BGE" : 0, "BLTU" : 0, "BGEU" : 0 },
                "J"  : { "JAL" : 0 },
                "IJ" : { "JALR" : 0 },
                "UL" : { "LUI" : 0 },
                "UA" : { "AUIPC" : 0 },
                "IE" : { "ECALL" : 0, "EBREAK" : 0}
            }
            instructions_true_count = {
                "R"  : { "ADD" : 0, "SUB" : 0, "XOR" : 0, "OR" : 0, "AND" : 0, "SLL" : 0, "SRL" : 0, "SRA" : 0, "SLT" : 0, "SLTU" : 0 },
                "I"  : { "ADDI" : 0, "XORI" : 0, "ORI" : 0, "ANDI" : 0, "SLLI" : 0, "SRLI" : 0, "SRAI" : 0, "SLTI" : 0, "SLTIU" : 0 },
                "IM" : { "LB" : 0, "LH" : 0, "LW" : 0, "LBU" : 0, "LHU" : 0 },
                "S"  : { "SB" : 0, "SH" : 0, "SW" : 0 },
                "B"  : { "BEQ" : 0, "BNE" : 0, "BLT" : 0, "BGE" : 0, "BLTU" : 0, "BGEU" : 0 },
                "J"  : { "JAL" : 0 },
                "IJ" : { "JALR" : 0 },
                "UL" : { "LUI" : 0 },
                "UA" : { "AUIPC" : 0 },
                "IE" : { "ECALL" : 0, "EBREAK" : 0}
            }

            # Count instructions and update counters
            for condition, instruction in self.cvg:
                instructions_count[instruction.type][instruction.name] += 1

                if condition:
                    instructions_true_count[instruction.type][instruction.name] += 1
            
            formated_list = []

            # Print log for every instruction type
            for inst_type in instructions_count.keys():
                for name in instructions_count[inst_type].keys():
                    formated_list.append([
                        name,
                        inst_type,
                        instructions_true_count[inst_type][name],
                        instructions_count[inst_type][name],
                        instructions_true_count[inst_type][name]/instructions_count[inst_type][name]*100 if instructions_count[inst_type][name] != 0 else 0
                    ])
                
                # Print line division
                formated_list.append(SEPARATING_LINE)

            # Log coverage report with padded strings
            self.logger.info("Coverage report (passed/total):")
        
            print(tabulate(formated_list, headers=["Inst", "FMT", "Correct", "Total", "Ratio (%)"], tablefmt="grid"))
