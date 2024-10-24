RISCV_CXX=/opt/riscv32/bin/riscv32-unknown-linux-gnu-g++
RISCV_OBJDUMP=/opt/riscv32/bin/riscv32-unknown-linux-gnu-objdump
RISCV_ASSEMBLER=/opt/riscv32/bin/riscv32-unknown-linux-gnu-as
RISCV_OBJCOPY=/opt/riscv32/bin/riscv32-unknown-linux-gnu-objcopy

SOURCES=main.cpp
LINKER_SCRIPT=linker_script.ld
TEST_OBJECT=main.o
FINAL_TEST_OBJECT=final_main.o
TEST_BINARY=main
TEST_ASSEMBLY=main.asm
TEST_EXE=main.elf

all: $(TEST_BINARY)

$(TEST_OBJECT): $(SOURCES)
	$(RISCV_CXX) -march=rv32id -c $(SOURCES) -o $(TEST_OBJECT)

$(TEST_ASSEMBLY): $(TEST_OBJECT) 
	$(RISCV_CXX) -nostdlib -nostartfiles -march=rv32id -T $(LINKER_SCRIPT) $(TEST_OBJECT) -o $(TEST_EXE)
	$(RISCV_OBJDUMP) -d $(TEST_EXE) > $(TEST_ASSEMBLY)

$(TEST_BINARY): $(TEST_ASSEMBLY) 
	$(RISCV_ASSEMBLER) $(TEST_ASSEMBLY) -o $(TEST_OBJECT)

# $(RISCV_OBJCOPY) -O binary $(TEST_OBJECT) $(TEST_BINARY)

clean:
	rm -f $(TEST_ASSEMBLY) $(TEST_OBJECT) $(TEST_EXE) $(TEST_BINARY)