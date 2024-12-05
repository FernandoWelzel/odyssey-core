from cocotb.triggers import Join, Combine
from pyuvm import *
import pyuvm
import random
import cocotb
from cocotb.triggers import FallingEdge
import sys
from pathlib import Path

sys.path.append(str(Path("../..").resolve()))

from instructions import create_instruction, create_random_instruction
from utils import CoreBfm
from model import CoreModel, diff_state
from coverage import Coverage

# Sequence classes
class InstSeqItem(uvm_sequence_item):
    def __init__(self, name, instruction = None):
        super().__init__(name)
        self.instruction = instruction

    def randomize(self):
        self.instruction = create_random_instruction()

class RandomSeq(uvm_sequence):
    async def body(self): 
        cmd_tr = InstSeqItem("cmd_tr")
        cmd_tr.randomize()
        await self.start_item(cmd_tr)
        await self.finish_item(cmd_tr)

# Class to execute sequence with a Sequencer DB
class TestAllSeq(uvm_sequence):
    async def body(self):
        seqr = ConfigDB().get(None, "", "SEQR")
        random = RandomSeq("random")
        await random.start(seqr)

class Driver(uvm_driver):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)

    def start_of_simulation_phase(self):
        self.bfm = CoreBfm()

    async def launch_tb(self):
        await self.bfm.reset()
        self.bfm.start_bfm()

    async def run_phase(self):
        while True:
            await self.launch_tb()
            current_instruction = await self.seq_item_port.get_next_item()
            await self.bfm.send_instruction(current_instruction)
            result = await self.bfm.get_result()
            self.ap.write(result)
            self.seq_item_port.item_done()
            
            # TODO: Fix time period for each instruction
            for _ in range(20):
                await FallingEdge(cocotb.top.clk)

class Scoreboard(uvm_component):
    def build_phase(self):
        self.cmd_fifo = uvm_tlm_analysis_fifo("cmd_fifo", self)
        self.result_fifo = uvm_tlm_analysis_fifo("result_fifo", self)
        self.cmd_get_port = uvm_get_port("cmd_get_port", self)
        self.result_get_port = uvm_get_port("result_get_port", self)
        self.cmd_export = self.cmd_fifo.analysis_export
        self.result_export = self.result_fifo.analysis_export

        # Interface with coverage
        self.ap = uvm_analysis_port("ap", self)

        # Initializing prediction environment
        self.model = CoreModel()

    def connect_phase(self):
        self.result_get_port.connect(self.result_fifo.get_export)
        self.cmd_get_port.connect(self.cmd_fifo.get_export)

    def check_phase(self):
        passed = True
        previous_instruction = 0

        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False
        while self.result_get_port.can_get() and self.cmd_get_port.can_get():
            _, (actual_state, result_time) = self.result_get_port.try_get()

            cmd_success, instruction = self.cmd_get_port.try_get()

            # Initializing error log for each instruction
            error_log = ""

            if not cmd_success:
                self.logger.critical(f"result had no command")
            elif not instruction == 0 and not instruction == previous_instruction:
                python_inst = create_instruction(instruction)

                # TODO: Stop reseting model before each iteration
                self.model.reset()

                # Update processor model state
                self.model.execute(python_inst)

                predicted_state = self.model.state

                if predicted_state == actual_state:
                    passed = True

                else:
                    passed = False
                    
                    # Adding instruction information into error log
                    error_log += f"{'0x{0:08X}'.format(int(instruction))} => {python_inst} - {result_time} ns\n"
                    error_log += diff_state(predicted_state, actual_state)

                # Writing metrics for coverage
                self.ap.write((passed, python_inst, error_log))

            previous_instruction = instruction

class Monitor(uvm_component):
    def __init__(self, name, parent, method_name):
        super().__init__(name, parent)
        self.method_name = method_name

    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.bfm = CoreBfm()
        self.get_method = getattr(self.bfm, self.method_name)

    async def run_phase(self):
        while True:
            datum = await self.get_method()
            self.logger.debug(f"MONITORED {datum.integer}")
            self.ap.write(datum)

class CoreEnv(uvm_env):
    def build_phase(self):
        self.seqr = uvm_sequencer("seqr", self)
        ConfigDB().set(None, "*", "SEQR", self.seqr)
        self.driver = Driver.create("driver", self)
        self.cmd_mon = Monitor("cmd_mon", self, "get_cmd")
        self.scoreboard = Scoreboard("scoreboard", self)
        self.coverage = Coverage("coverage", self)

    def connect_phase(self):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.cmd_mon.ap.connect(self.scoreboard.cmd_export)
        self.scoreboard.ap.connect(self.coverage.analysis_export)
        self.driver.ap.connect(self.scoreboard.result_export)

@pyuvm.test()
class CoreAllTest(uvm_test):
    """Test Core with random instructions"""

    def build_phase(self):
        self.env = CoreEnv("env", self)

    def end_of_elaboration_phase(self):
        self.test_all = TestAllSeq.create("test_all")

    async def run_phase(self):
        self.raise_objection()
    
        for _ in range(100):
            # Apply sequence
            self.test_all = TestAllSeq.create("test_all")
            await self.test_all.start()

        self.drop_objection()