from cocotb.triggers import Join, Combine
from pyuvm import *
import random
import cocotb
from cocotb.triggers import FallingEdge
import pyuvm
import sys
from pathlib import Path

sys.path.append(str(Path("..").resolve()))

from instructions import Instruction, RInstruction, IInstruction, SInstruction, BInstruction, JInstruction, UInstruction
from instructions import  create_instruction, create_random_instruction
from core_utils import CoreBfm
from core_model import CoreState, CoreModel, diff_state

import numpy as np

# Global variables
result_list = []

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

class Coverage(uvm_subscriber):
    def end_of_elaboration_phase(self):
        dtype = [('condition', bool), ('instruction', object)]
        self.cvg = []

    def write(self, value):
        self.cvg.append(value)

    def report_phase(self):
        try:
            disable_errors = ConfigDB().get(
                self, "", "DISABLE_COVERAGE_ERRORS")
        except UVMConfigItemNotFound:
            disable_errors = False
        if not disable_errors:
            # Initialize counters for each instruction type
            instructions_count = [0, 0, 0, 0, 0, 0]       # Total counts: R, I, S, B, J, U
            instructions_true_count = [0, 0, 0, 0, 0, 0]  # True counts: R, I, S, B, J, U

            # Define a function to get the index based on the instruction type
            def get_instruction_index(instruction):
                if isinstance(instruction, RInstruction):
                    return 0  # R type
                elif isinstance(instruction, IInstruction):
                    return 1  # I type
                elif isinstance(instruction, SInstruction):
                    return 2  # S type
                elif isinstance(instruction, BInstruction):
                    return 3  # B type
                elif isinstance(instruction, JInstruction):
                    return 4  # J type
                elif isinstance(instruction, UInstruction):
                    return 5  # U type
                else:
                    return None

            # Count instructions and update counters
            for condition, instruction in self.cvg:
                index = get_instruction_index(instruction)
                if index is not None:
                    instructions_count[index] += 1
                    if condition:
                        instructions_true_count[index] += 1

            # Log coverage report
            self.logger.info("Coverage report (passed/total):")
            self.logger.info(f"    R - {instructions_true_count[0]}/{instructions_count[0]}")
            self.logger.info(f"    I - {instructions_true_count[1]}/{instructions_count[1]}")
            self.logger.info(f"    S - {instructions_true_count[2]}/{instructions_count[2]}")
            self.logger.info(f"    B - {instructions_true_count[3]}/{instructions_count[3]}")
            self.logger.info(f"    J - {instructions_true_count[4]}/{instructions_count[4]}")
            self.logger.info(f"    U - {instructions_true_count[5]}/{instructions_count[5]}")

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
        ignore_first = True

        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False
        while self.result_get_port.can_get() and self.cmd_get_port.can_get():
            _, actual_state = self.result_get_port.try_get()

            cmd_success, instruction = self.cmd_get_port.try_get()

            if not cmd_success:
                self.logger.critical(f"result had no command")
            elif not instruction == 0:
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

                    # Print difference between states
                    # self.logger.debug(f"FAILED (preditecte/actual): {diff_state(predicted_state, actual_state)}")

                # Writing metrics for coverage
                self.ap.write((passed, python_inst))

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