# odyssey-core

Simple RISCV 32 bit processor implemented in the Tang Nano 9K FPGA board. Currently does not implement fault-tollerant methods.

# Requirements

The following software and their version used in the project.

- Icarus Verilog - 13.0
- GTKWave - 3.3.118
- Yosys - 0.40+7 (git sha1 b827b9862, clang++ 14.0.0-1ubuntu1.1 -fPIC -Os)
- Cocotb (python package)
- Pyuvm (python package)

# Testbench

The verification environment implements a UVM-based system in Python using Cocotb and Pyuvm. It's contained in the *python* folder and can be run using the following commands:

```sh
cd python
make sim
```