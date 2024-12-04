# odyssey-core

Simple RISCV 32 bit processor implemented in the Tang Nano 9K FPGA board. Currently does not implement fault-tollerant methods.

# Requirements

The following software and their version used in the project.

- Icarus Verilog - 13.0
- GTKWave - 3.3.118
- Gowin Software Suite - 1.9.9.03 (Education)
- Cocotb (python package)
- Pyuvm (python package)

# Testbench

The verification environment implements a UVM-based system in Python using Cocotb and Pyuvm. It's contained in the *python* folder and can be run using the following commands:

```sh
cd python
make sim
```

A simple report will be generated in which you will be able to see the result of 100 random instructions executed by the core. A 50000 instruction with random instructions was done as of December/2024, which didn't find any bugs.

# Synthesis

The logical synthesis of the core is implemented using the GowinSynthesis util that can be accessed thought the Gowin IDE. To do so, simply launch the IDE (assuming it is in the system path):

```sh
gw_ide
```

After that, open the project *odyssey-core.gprj* and run the synthesis.

## Resource Utilization

As of December/2024, these are the results for the resources used in the Tang 9K board:

| Resource             | Usage                          | Utilization |
|----------------------|--------------------------------|-------------|
| Logic                | 1846 (1782 LUT, 64 ALU) / 8640 | 22%         |
| Register             | 1131 / 6693                    | 17%         |
| -- Register as Latch | 0 / 6693                       | 0%          |
| -- Register as FF    | 1131 / 6693                    | 17%         |
| BSRAM                | 0 / 26                         | 0%          |
