######################################################################
#
# DESCRIPTION: Verilator compilation script
#
######################################################################
# Check for sanity to avoid later confusion

ifneq ($(words $(CURDIR)),1)
 $(error Unsupported: GNU Make cannot build in directories containing spaces, build elsewhere: '$(CURDIR)')
endif

######################################################################
# Set up verilator variables
VERILATOR = verilator

# Generate C++
VERILATOR_FLAGS := -cc
# Optimize
VERILATOR_FLAGS += -x-assign fast
# Warn abount lint issues; may not want this on less solid designs
# TODO: Enable this feature
# VERILATOR_FLAGS += -Wall
VERILATOR_FLAGS += -CFLAGS -DVL_TIME_CONTEXT

# Make waveforms
TOP_VERILATOR_FLAGS = $(VERILATOR_FLAGS) --trace

# Assembly script
TEST_BINARY=test
TEST_ASSEMBLY=test.asm
TEST_OBJECT=test.o

RISCV_ASSEMBLER=/opt/riscv/bin/riscv64-unknown-linux-gnu-as
RISCV_OBJCOPY=/opt/riscv/bin/riscv64-unknown-linux-gnu-objcopy

######################################################################
default: run

$(TEST_BINARY): $(TEST_ASSEMBLY) 
	$(RISCV_ASSEMBLER) $(TEST_ASSEMBLY) -o  $(TEST_OBJECT)
	$(RISCV_OBJCOPY) -O binary $(TEST_OBJECT) $(TEST_BINARY)

run: $(TEST_BINARY)
	@echo "-- VERILATE core module ---------------------------------------"
	@echo " Transforming top module in C++..."
	@echo "---------------------------------------------------------------"
	$(VERILATOR) $(TOP_VERILATOR_FLAGS) --exe ../../src/core.sv sim_main.cpp memory.cpp
	
	@echo "-- COMPILE top module and testbench ---------------------------"
	@echo " Compilling top module and C++ testbench using g++..."
	@echo "---------------------------------------------------------------"
	$(MAKE) -j 4 -C obj_dir -f Vcore.mk

	@echo "-- RUNNING testbench ------------------------------------------"
	@echo " Running main testbench and dumping vcd file..."
	@echo "---------------------------------------------------------------"
	@mkdir -p logs
	obj_dir/Vcore +trace

######################################################################
clean:
	-rm -rf obj_dir* logs *.log core
