#include <fstream>
#include <iostream>

#include <systemc.h>

#include "core_wrapper.h"

void CoreWrapper::entry() {
    // Setting pointer counter to first instruction
    pointer_counter = 0x00000000;

    return;
}

void CoreWrapper::stimulus() {
    // Printing values in the each variable
    std::cout << "Instruction read: " << inst_r.read() << std::endl;
    std::cout << "Instruction write: " << inst_w.read() << std::endl;
    std::cout << "Instruction address: " << inst_a.read() << std::endl;
    
    // Reading from first instruction 
    inst_wen.write(true);
    inst_a.write(pointer_counter);

    // Incrementing instruction pointer
    pointer_counter++;

    return;
}
