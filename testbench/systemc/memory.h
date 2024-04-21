#include <map>

#ifndef MEMORY_TB_H
#define MEMORY_TB_H

struct Memory : sc_module {
    // Logical signals
    sc_in<bool> clk;
    sc_in<bool> rst;
    sc_in<bool> wen;

    sc_out<sc_uint<32>> data_r;
    sc_in <sc_uint<32>> data_w;
    sc_in <sc_uint<32>> addr;

    // Internal state variables 
    std::map<int, int> addressMap;

    void stimulus();

    SC_CTOR(Memory) {
        SC_METHOD(stimulus);
        sensitive << clk.pos();
    }
};

#endif
