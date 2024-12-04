CWD=$(shell pwd)
SIM ?= icarus
# EXTRA_ARGS += -Wall --trace --trace-structs
# EXTRA_ARGS += -Wall
TOPLEVEL_LANG ?= verilog
ifeq ($(TOPLEVEL_LANG),verilog)
	VERILOG_SOURCES = $(CWD)/core_testbench.v $(CWD)/../src/alu.v $(CWD)/../src/core.v $(CWD)/../src/decode.v $(CWD)/../src/fetch.v $(CWD)/../src/lsu.v $(CWD)/../src/register_file.v
	VERILOG_INCLUDE_DIRS = $(CWD)/../src
else
    $(error "A valid value (verilog) was not provided for TOPLEVEL_LANG=$(TOPLEVEL_LANG)")
endif
ifeq ($(SIM), verilator)
    # Enable processing of #delay statements
    COMPILE_ARGS += --timing
endif
MODULE := core_testbench
TOPLEVEL = core_testbench
GHDL_ARGS := --ieee=synopsys
COCOTB_HDL_TIMEUNIT = 1us
COCOTB_HDL_TIMEPRECISION = 1us
include $(shell cocotb-config --makefiles)/Makefile.sim
include ./checkclean.mk

# Define the total number of simulations
NUM_SIMULATIONS := 500

# Default target
all: launch

results_dir:
	@mkdir -p results

# Target to launch simulations
launch: results_dir
	@for i in $(shell seq 1 $$(($(NUM_SIMULATIONS)-1))); do \
		SIM_NUM=$$i $(MAKE) sim SIM_NUM=$$i; \
	done