#include <fstream>
#include <iostream>

#include <systemc.h>

#include "memory.h"

void Memory::stimulus() {
    // Reading enable value
    bool read_wen = wen.read();

    // Reading or Writting value
    if(read_wen) {
        // Getting address
        sc_uint<32> addr_value = addr.read();

        // Reading from memory
        data_r.write(addressMap[addr_value]);
    }
    else {
        // Writting in memory
        sc_uint<32> write_value = data_w.read();
    }
}
