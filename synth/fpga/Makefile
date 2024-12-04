# Variables
SRC_DIR = ../../src
VERILOG_FILES = $(wildcard $(SRC_DIR)/*.v)
OUTPUT_DIR = build

# Targets
synth: $(VERILOG_FILES)
	@echo "Synthesizing files..."; \
	GowinSynthesis -i $(VERILOG_FILES); \

clean:
	@echo "Cleaning synthesis output..."
	@rm -rf $(OUTPUT_DIR)/*.*

.PHONY: synth clean
