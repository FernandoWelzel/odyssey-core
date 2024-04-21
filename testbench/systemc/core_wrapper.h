#ifndef CORE_WRAPPER_H
#define CORE_WRAPPER_H

struct CoreWrapper : sc_module {
    // Global logic signals
    sc_in<bool> clk;
    sc_in<bool> rst;

    // Instruction memory interface
    sc_in <sc_uint<32>> inst_r;
    sc_out<sc_uint<32>> inst_w;
    sc_out<sc_uint<32>> inst_a;
    sc_out<bool> inst_wen;

    // Data memory interface
    sc_in <sc_uint<32>> data_r;
    sc_out<sc_uint<32>> data_w;
    sc_out<sc_uint<32>> data_a;
    sc_out<bool> data_wen;

    // Internal state variables
    int pointer_counter;

    void entry();
    void stimulus();

    SC_CTOR(CoreWrapper) {
        // Initializing variables
        entry();
        
        // Set method with clock sensitivity
        SC_METHOD(stimulus);
        sensitive << clk.pos();
    }
};

#endif
