# odyssey-core

Simple RISCV 32 bit processor.

# Requirements

- Icarus Verilog
- GTKWave
- Yosys

# Running testbench 

```sh
make compile
./tb
gtkwave tb.vcd
```

# Next steps

- [ ] Testbench
    - [ ] Simple testbench with supported instructions
    - [ ] Implement simple riscv assembly compiler
- [ ] Choose the directions to go with project
    - [ ] Use standart riscv flow (compilation and execution) ?
    - [ ] Processor architecture (supported instructions/extensions + cache + general pipeline)
    - [ ] HLS or RTL implementation
        - [ ] If HLS, which software suite for open source?
    - [ ] Technology (is there an open-source alternative ?)
    - [ ] Choose goals (P&R, integration with SoC?)
    - [ ] Choose synthesis tool (Yosys) + Integrate it with HLS?
- [ ] Implement testbench in SystemC
    - [ ] Integrate memory as a SystemC component that reads from a file
