SRC_CORE=$(shell pwd)/../../src/core
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

ifeq ($(TOPLEVEL_LANG),verilog)
	VERILOG_SOURCES = ./testbench.v $(SRC_CORE)/alu.v $(SRC_CORE)/core.v $(SRC_CORE)/decode.v $(SRC_CORE)/fetch.v $(SRC_CORE)/lsu.v $(SRC_CORE)/register_file.v
	VERILOG_INCLUDE_DIRS = $(SRC_CORE)
else
    $(error "A valid value (verilog) was not provided for TOPLEVEL_LANG=$(TOPLEVEL_LANG)")
endif

ifeq ($(SIM), verilator)
    # Enable processing of #delay statements
    COMPILE_ARGS += --timing
endif

MODULE := testbench
TOPLEVEL = testbench
GHDL_ARGS := --ieee=synopsys
COCOTB_HDL_TIMEUNIT = 1us
COCOTB_HDL_TIMEPRECISION = 1us
include $(shell cocotb-config --makefiles)/Makefile.sim
include ./checkclean.mk

# Define the total number of simulations
NUM_SIMULATIONS := 1

# Default target
all: launch

results_dir:
	@mkdir -p results

# TODO: Fix None creation error and results folder creation for sim
# Target to launch simulations
launch: results_dir
	@for i in $(shell seq 1 $$(($(NUM_SIMULATIONS)-1))); do \
		SIM_NUM=$$i $(MAKE) sim SIM_NUM=$$i; \
	done