SRC_SOC=$(shell pwd)/../../src/soc
SRC_VENDOR=$(shell pwd)/../../src/vendor
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

ifeq ($(TOPLEVEL_LANG),verilog)
	VERILOG_SOURCES = ./testbench.v $(SRC_SOC)/cache.v $(SRC_VENDOR)/gowin_ram16s.v $(SRC_VENDOR)/prim_sim.v
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
