COMP=iverilog

DISPLAY=gtkwave

COMP_FLAGS=-g2012

SYNTH_TOOL=yosys

SOURCES=src/core.sv

SOURCES_SYNTH=synth/synth.v

SYNTH_LIBRARY=/home/welzelf/Documents/Packages/yosys/yosys/examples/cmos/cmos_cells.v

SYNTH_SCRIPT=synth/synth.ys

SYNTH_TARGET=synth/synth.v

TOP=tb/tb.sv

EXE=testbench

VCD_FILE=testbench.vcd

WAVE_SCRIPT=testbench.gtkw

compile: 
	$(COMP) $(COMP_FLAGS) $(SOURCES) $(TOP) -o $(EXE)

execute: compile
	./$(EXE)

$(SYNTH_TARGET): $(SOURCES)
	$(SYNTH_TOOL) $(SYNTH_SCRIPT)

synth: $(SYNTH_TARGET)

synth_sim: synth
	$(COMP) $(COMP_FLAGS) $(SOURCES_SYNTH) $(SYNTH_LIBRARY) $(TOP) -o $(EXE) -D SYNTH

wave: execute
	$(DISPLAY) $(VCD_FILE) $(WAVE_SCRIPT)

clean:
	rm -f $(EXE) $(SYNTH_TARGET) $(VCD_FILE)