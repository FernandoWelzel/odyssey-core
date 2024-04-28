#include <iostream>

#include "memory.hpp"

Memory::Memory() {

}

Memory::~Memory() {

}

// Update method to the memory - Executed each clock cycle
int Memory::update(int csn, int wen, int address, int data) {
    // Updating memory
    if(!csn) {
        // Switches according to memory action
        if(wen) {
            return data_map[address];
        }
        else {
            // Writes data to memory
            data_map[address] = data;
        }
    }

    // Returning default
    return 0;
}

// Instruction to immediatly write into memory
void Memory::write(int address, int data) {
    data_map[address] = data;
}