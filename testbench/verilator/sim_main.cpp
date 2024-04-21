// DESCRIPTION: Verilator: --protect-lib example module
//
// This file ONLY is placed under the Creative Commons Public Domain, for
// any use, without warranty, 2019 by Todd Strader.
// SPDX-License-Identifier: CC0-1.0
//======================================================================

// See examples/tracing_c for notes on tracing
#include <fstream>
#include <iostream>
#include <string>

// Include common routines
#include <verilated.h>

#include "Vcore.h"

#include <verilated_vcd_c.h>

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;

    // Construct context to hold simulation time, etc
    const std::unique_ptr<VerilatedContext> contextp{new VerilatedContext};
    contextp->debug(0);
    contextp->randReset(2);
    contextp->commandArgs(argc, argv);

    // Construct the Verilated model
    const std::unique_ptr<Vcore> core{new Vcore{contextp.get(), "CORE"}};

    // Instantiating memories
    std::map<int, int> dataMap;
    std::map<int, int> instMap;

    // Path to RISCV assembly testfile
    std::string assembly_path = "test";

    // Open file for reading
    std::ifstream assemblyFile(assembly_path, ios::binary);

    // Populating instruction memory
    int current_address = 0;
    int instruction_variable = 0;
    
    while(assemblyFile.read(reinterpret_cast<char*>(&instruction_variable), sizeof(int))) {
        instruction_memory.addressMap[current_address] = instruction_variable;
        
        // Increases current address
        current_address++;
    }

    // When tracing, the contents of the secret module will not be seen
#if VM_TRACE
    VerilatedVcdC* tfp = nullptr;
    const char* flag = contextp->commandArgsPlusMatch("trace");
    if (flag && 0 == std::strcmp(flag, "+trace")) {
        contextp->traceEverOn(true);
        VL_PRINTF("Enabling waves into logs/vlt_dump.vcd...\n");
        tfp = new VerilatedVcdC;
        core->trace(tfp, 99);
        Verilated::mkdir("logs");
        tfp->open("logs/vlt_dump.vcd");
    }
#endif
    
    // Initializing variables
    core->clk = 0;

    // Run simulation for 10 clock cycles
    for (int i = 0; i < 10; ++i) {
        // Increase time
        contextp->timeInc(10);
        
        // Toggle clock
        core->clk = !core->clk;

        // Assert clock for 3 clock cycles
        if (i < 6)
            core->rst = 1;
        else
            core->rst = 0;

        // Evaluate the core
        core->eval();

        // Updating memory
        if(core->inst_csn) {
            // Switches according to memory action
            if(inst_wen) {
                
            }
            else {
                
            }
            
        }

        VL_PRINTF("%s\n", print_variable.c_str());

        // Dump variables
#if VM_TRACE
        if (tfp) tfp->dump(contextp->time());
#endif
    }

    // Final model cleanup
    core->final();

    // Close trace if opened
#if VM_TRACE
    if (tfp) {
        tfp->close();
        tfp = nullptr;
    }
#endif

    // Return good completion status
    // Don't use exit() or destructor won't get called
    return 0;
}
