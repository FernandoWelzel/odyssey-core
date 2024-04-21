#include <fstream>
#include <iostream>

#include <systemc.h>

#include "memory.h"
#include "core_wrapper.h"

int sc_main(int, char *[]) {
    // Openning start message file
    std::string start_message_path = "../ressources/start_message.txt";
    std::ifstream startMessageFile(start_message_path);
    if (!startMessageFile.is_open()) {
        std::cerr << "Error opening file: " << start_message_path << std::endl;
        return 1;
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
    std::ifstream assemblyFile(assembly_path, ios::binary);

    // Check for assembly file options
    if(!assemblyFile.is_open()) {
        std::cerr << "Error opening file: " << assembly_path << std::endl;
    }

    // Signal declaration
    sc_signal<bool> clk;
    sc_signal<bool> rst;

    // Data memory interface declaration
    sc_signal<sc_uint<32>> inst_r;
    sc_signal<sc_uint<32>> inst_w;
    sc_signal<sc_uint<32>> inst_a;
    sc_signal<bool> inst_wen;
 
    // Data memory interface declaration
    sc_signal<sc_uint<32>> data_r;
    sc_signal<sc_uint<32>> data_w;
    sc_signal<sc_uint<32>> data_a;
    sc_signal<bool> data_wen;

    // Instantiating suplementary modules
    Memory data_memory("data_memory");
    Memory instruction_memory("instruction_memory");

    // Instantiating main verification module
    CoreWrapper core_wrapper("core_wrapper"); 

    // Port binding
    data_memory(clk, rst, data_wen, data_r, data_w, data_a);
    instruction_memory(clk, rst, inst_wen, inst_r, inst_w, inst_a);
    core_wrapper(clk, rst, inst_r, inst_w, inst_a, inst_wen, data_r, data_w, data_a, data_wen);

    // Writting instrucion memory from assembly file
    int instruction_variable;
    int current_address = 0;

    while(assemblyFile.read(reinterpret_cast<char*>(&instruction_variable), sizeof(int))) {
        instruction_memory.addressMap[current_address] = instruction_variable;
        
        // Increases current address
        current_address++;
    }

    assemblyFile.close();
 
    // Toggling clock
    sc_start(0, SC_NS);
    
    for(int i = 0; i < 5; i++){
        clk.write(1);
        sc_start( 10, SC_NS );
        clk.write(0);
        sc_start( 10, SC_NS );
    }
    
    return 0;
}