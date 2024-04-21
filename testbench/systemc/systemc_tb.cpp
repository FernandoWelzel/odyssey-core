#include <fstream>
#include <iostream>

#include <systemc.h>

#include "systemc_tb.h"

void Testbench::entry() {
    // Openning start message file
    std::string start_message_path = "../ressources/start_message.txt";
    std::ifstream startMessageFile(start_message_path);
    if (!startMessageFile.is_open()) {
        std::cerr << "Error opening file: " << start_message_path << std::endl;
        return;
    }
    
    // Printing start message
    std::string line;
    while (std::getline(startMessageFile, line)) {
        std::cout << line << std::endl;
    }
    startMessageFile.close();

    // Path to RISCV assembly testfile
    std::string assembly_path = "test";

    // Open file for reading
    this->assemblyFile.open(assembly_path, ios::binary);

    // Check for assembly file options
    if(!this->assemblyFile.is_open()) {
        std::cerr << "Error opening file: " << assembly_path << std::endl;
    }
}

void Testbench::stimulus() {
    // Stimulus generation goes here
    std::cout << "Entered stimulus" << std::endl; 
    
    // Read value from file and put in signal
    if(this->assemblyFile.read(reinterpret_cast<char*>(&instruction_variable), sizeof(int))) {
        std::cout << "Read value: " << instruction_variable << std::endl;
    }
    else {
        std::cout << "Quitting simulation" << std::endl;

        // Quit simulation after reading all instructions
        assemblyFile.close();
        sc_abort();
    };
}

int sc_main(int, char *[]) {
    // Signal declaration
    sc_signal<bool> clk;
    sc_signal<bool> rst;
    sc_signal<sc_uint<32>> instruction;

    // Instantiating testbench
    Testbench testbench("testbench");

    // Port binding
    testbench(clk, rst, instruction);

    // Toggling clock
    sc_start(0, SC_NS);
    
    for(int i = 0; i < 50; i++){
        clk.write(1);
        sc_start( 10, SC_NS );
        clk.write(0);
        sc_start( 10, SC_NS );
    }
    
    return 0;
}