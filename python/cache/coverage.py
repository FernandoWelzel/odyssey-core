import os
import numpy as np
from pyuvm import *
from tabulate import tabulate, SEPARATING_LINE

class Coverage(uvm_subscriber):
    def end_of_elaboration_phase(self):
        self.cvg = []  # Store tuples of (condition, instruction, address, error_log)
        self.unique_addresses = set()  # Track unique addresses requested

    def write(self, value):
        """Append each coverage-related transaction."""
        self.cvg.append(value)
        _, _, address, _ = value
        self.unique_addresses.add(address)

    def report_phase(self):
        try:
            disable_errors = ConfigDB().get(self, "", "DISABLE_COVERAGE_ERRORS")
        except UVMConfigItemNotFound:
            disable_errors = False

        if not disable_errors:
            sim_num = os.getenv("SIM_NUM")

            # Initialize instruction counters
            instructions_count = {inst_type: {name: 0 for name in names}
                                  for inst_type, names in {
                                      "R": ["ADD", "SUB", "XOR", "OR", "AND", "SLL", "SRL", "SRA", "SLT", "SLTU"],
                                      "I": ["ADDI", "XORI", "ORI", "ANDI", "SLLI", "SRLI/SRLA", "SRAI", "SLTI", "SLTIU"],
                                      "IM": ["LB", "LH", "LW", "LBU", "LHU"],
                                      "S": ["SB", "SH", "SW"],
                                      "B": ["BEQ", "BNE", "BLT", "BGE", "BLTU", "BGEU"],
                                      "J": ["JAL"],
                                      "IJ": ["JALR"],
                                      "UL": ["LUI"],
                                      "UA": ["AUIPC"],
                                      "IE": ["ECALL", "EBREAK"]
                                  }.items()}

            instructions_true_count = {inst_type: {name: 0 for name in names}
                                        for inst_type, names in instructions_count.items()}

            complete_error_log = ""
            total_instruction_true_count = 0
            total_instruction_count = 0

            # Count instructions and track unique addresses
            for condition, instruction, address, error_log in self.cvg:
                instructions_count[instruction.type][instruction.name] += 1
                if condition:
                    instructions_true_count[instruction.type][instruction.name] += 1
                else:
                    complete_error_log += f"{error_log}\n\n"

            # Write error log to output file
            os.makedirs("results", exist_ok=True)
            with open(f"results/error_{sim_num}.txt", "w") as f:
                f.write(complete_error_log)
                self.logger.info(f"Written errors to file 'results/error_{sim_num}.txt'")

            # Prepare coverage report
            formatted_list = []
            for inst_type in instructions_count.keys():
                for name in instructions_count[inst_type].keys():
                    formatted_list.append([
                        name,
                        inst_type,
                        instructions_true_count[inst_type][name],
                        instructions_count[inst_type][name],
                        instructions_true_count[inst_type][name] / instructions_count[inst_type][name] * 100
                        if instructions_count[inst_type][name] != 0 else 0
                    ])
                    total_instruction_true_count += instructions_true_count[inst_type][name]
                    total_instruction_count += instructions_count[inst_type][name]

                formatted_list.append(SEPARATING_LINE)

            # Add a total coverage summary
            formatted_list.append([
                "TOTAL",
                "-",
                total_instruction_true_count,
                total_instruction_count,
                total_instruction_true_count / total_instruction_count * 100 if total_instruction_count != 0 else 0
            ])

            # Log instruction coverage
            self.logger.info(f"Coverage report: {total_instruction_true_count}/{total_instruction_count} = "
                             f"{total_instruction_true_count / total_instruction_count * 100 if total_instruction_count != 0 else 0} %")

            # Write coverage report as a table
            table = tabulate(formatted_list, headers=["Inst", "FMT", "Correct", "Total", "Ratio (%)"], tablefmt="simple")
            with open(f"results/coverage_{sim_num}.txt", "w") as f:
                f.write(table)
                self.logger.info(f"Written coverage results to 'results/coverage_{sim_num}.txt'")

            # Save additional coverage metrics
            np.save(f"results/coverage_{sim_num}_count.npy", np.array(instructions_count))
            np.save(f"results/coverage_{sim_num}_true_count.npy", np.array(instructions_true_count))

            # Log unique address coverage
            with open(f"results/unique_addresses_{sim_num}.txt", "w") as f:
                f.write(f"Unique Addresses: {len(self.unique_addresses)}\n")
                f.write("\n".join(map(str, sorted(self.unique_addresses))))
                self.logger.info(f"Written unique address coverage to 'results/unique_addresses_{sim_num}.txt'")

