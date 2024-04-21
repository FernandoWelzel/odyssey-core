#ifndef SYSTEMC_TB_H
#define SYSTEMC_TB_H

struct Testbench : sc_module {
    // Logical signals
    sc_in<bool> clk;
    sc_in<bool> rst;
    sc_out<sc_uint<32>> instruction;

    // Internal state variables 
    int instruction_variable;
    std::ifstream assemblyFile;

    void stimulus();
    void entry();

    SC_CTOR(Testbench) {
        // Initializing variables
        entry();

        SC_METHOD(stimulus);
        sensitive << clk.pos();
    }
};

#endif
