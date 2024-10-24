COMP=iverilog
DISPLAY=gtkwave
SYNTH_TOOL=yosys
RISCV_ASSEMBLER=/opt/riscv/bin/riscv64-unknown-linux-gnu-as
RISCV_OBJCOPY=/opt/riscv/bin/riscv64-unknown-linux-gnu-objcopy
CXX=g++

CXX_FLAGS=-g -Wall -pedantic -Wno-long-long -Werror

SYSTEMC=/opt/systemc
SYSTEMC_FLAGS=-lsystemc -lstdc++ -lm

COMP_FLAGS=-g2012 -I ./src

SOURCES=src/alu.v src/core.v src/decode.v src/fetch.v src/lsu.v src/register_file.v testbench/systemverilog/inst_cache_driver.sv
SOURCES_SYNTH=synth/synth.v
SYNTH_LIBRARY=/home/welzelf/Documents/Packages/yosys/yosys/examples/cmos/cmos_cells.v
SYNTH_SCRIPT=synth/synth.ys
SYNTH_TARGET=synth/synth.v
TOP=testbench/systemverilog/tb.sv
VCD_FILE=tb.vcd
WAVE_SCRIPT=tb.gtkw
TEST_ASSEMBLY=testbench/verilator/test2.asm
TEST_OBJECT=testbench/verilator/test.o
TEST_BINARY=testbench/verilator/test

EXE=tb

compile: 
	$(COMP) $(COMP_FLAGS) $(SOURCES) $(TOP) -o $(EXE)

execute: compile
	./$(EXE)

$(TEST_BINARY): $(TEST_ASSEMBLY) 
	$(RISCV_ASSEMBLER) $(TEST_ASSEMBLY) -o  $(TEST_OBJECT)
	$(RISCV_OBJCOPY) -O binary $(TEST_OBJECT) $(TEST_BINARY)

$(SYNTH_TARGET): $(SOURCES)
	$(SYNTH_TOOL) $(SYNTH_SCRIPT)

synth: $(SYNTH_TARGET)

synth_sim: synth $(TEST_BINARY)
	$(COMP) $(COMP_FLAGS) $(SOURCES_SYNTH) $(SYNTH_LIBRARY) $(TOP) -o $(EXE) -D SYNTH

binary: $(TEST_BINARY)

wave: execute
	$(DISPLAY) $(VCD_FILE) $(WAVE_SCRIPT)

cache_test:
	iverilog -g2012 testbench/systemverilog/cache_test.sv src/cache.v testbench/systemverilog/bus_driver.sv vendor/gowin_ram16s.v vendor/prim_sim.v -o tb

execute_cache_test: cache_test
	./tb

clean:
	rm -f $(EXE) $(SYNTH_TARGET) $(VCD_FILE) $(TEST_OBJECT) $(TEST_BINARY)
