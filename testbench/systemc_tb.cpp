#include <systemc.h>

SC_MODULE(Testbench) {
    sc_clock clk;
    sc_signal<bool> rst;
    sc_signal<sc_uint<32>> instruction;

    void stimulus() {
        // Stimulus generation goes here
        int a = 0;
    }

    void monitor() {
        // Monitoring code goes here
        int b = 0;
    }

    SC_CTOR(Testbench) : clk("clk", 10, SC_NS) {
        SC_THREAD(stimulus);
        sensitive << clk.posedge_event();

        SC_METHOD(monitor);
        sensitive << clk.posedge_event();
    }
};

int sc_main(int argc, char *argv[]) {
    Testbench testbench("testbench");
    sc_start();
    return 0;
}