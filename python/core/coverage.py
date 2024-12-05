import os
import numpy as np

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
            sim_num = os.getenv("SIM_NUM")

            # Initialize counters for each instruction type
            instructions_count = {
                "R"  : { "ADD" : 0, "SUB" : 0, "XOR" : 0, "OR" : 0, "AND" : 0, "SLL" : 0, "SRL" : 0, "SRA" : 0, "SLT" : 0, "SLTU" : 0 },
                "I"  : { "ADDI" : 0, "XORI" : 0, "ORI" : 0, "ANDI" : 0, "SLLI" : 0, "SRLI/SRLA" : 0, "SRAI" : 0, "SLTI" : 0, "SLTIU" : 0 },
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
                "I"  : { "ADDI" : 0, "XORI" : 0, "ORI" : 0, "ANDI" : 0, "SLLI" : 0, "SRLI/SRLA" : 0, "SRAI" : 0, "SLTI" : 0, "SLTIU" : 0 },
                "IM" : { "LB" : 0, "LH" : 0, "LW" : 0, "LBU" : 0, "LHU" : 0 },
                "S"  : { "SB" : 0, "SH" : 0, "SW" : 0 },
                "B"  : { "BEQ" : 0, "BNE" : 0, "BLT" : 0, "BGE" : 0, "BLTU" : 0, "BGEU" : 0 },
                "J"  : { "JAL" : 0 },
                "IJ" : { "JALR" : 0 },
                "UL" : { "LUI" : 0 },
                "UA" : { "AUIPC" : 0 },
                "IE" : { "ECALL" : 0, "EBREAK" : 0}
            }

            total_instruction_true_count = 0
            total_instruction_count = 0

            complete_error_log = ""

            # Count instructions and update counters
            for condition, instruction, error_log in self.cvg:
                instructions_count[instruction.type][instruction.name] += 1

                if condition:
                    instructions_true_count[instruction.type][instruction.name] += 1
                else:
                    complete_error_log += f"{error_log}\n\n"
            
            # Print error log to output file
            with open(f"results/error_{sim_num}.txt", "w") as f:
                f.write(complete_error_log)

                self.logger.info(f"Written errors to file 'results/errors_{sim_num}.txt'")

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
                    
                    total_instruction_true_count += instructions_true_count[inst_type][name]
                    total_instruction_count += instructions_count[inst_type][name]
                
                # Print line division
                formated_list.append(SEPARATING_LINE)
            
            # Added total report
            formated_list.append([
                "TOTAL",
                "-",
                total_instruction_true_count,
                total_instruction_count,
                total_instruction_true_count/total_instruction_count*100 if total_instruction_count != 0 else 0
            ])

            # Log coverage report with padded strings
            # TODO: Fix line bigger than 200 characters
            self.logger.info(f"Coverage report (passed/total): {total_instruction_true_count}/{total_instruction_count} = {total_instruction_true_count/total_instruction_count*100 if total_instruction_count != 0 else 0} %")

            # Prepare table
            table = tabulate(formated_list, headers=["Inst", "FMT", "Correct", "Total", "Ratio (%)"], tablefmt="simple")

            # Write the table to a text file
            with open(f"results/coverage_{sim_num}.txt", "w") as f:
                f.write(table)

                self.logger.info(f"Written complete coverage results to file 'results/coverage_{sim_num}.txt'")
            
            # Save list of results as numpy list 
            np.save(f"results/coverage_{sim_num}_count.npy", np.array(instructions_count))
            np.save(f"results/coverage_{sim_num}_true_count.npy", np.array(instructions_true_count))
