from cocotb.triggers import Join, Combine
from pyuvm import *
import random
import cocotb
import pyuvm
import sys
from pathlib import Path

sys.path.append(str(Path("..").resolve()))

from instructions import Instruction, RInstruction, IInstruction, create_instruction
from core_utils import CoreBfm
from core_model import CoreState, CoreModel, diff_state

# Sequence classes
class InstSeqItem(uvm_sequence_item):

    def __init__(self, name, instruction : Instruction):
        super().__init__(name)
        self.instruction = instruction

    def randomize(self):
        self.instruction.rd = random.randint(0, 32)
        self.instruction.rs1 = random.randint(0, 32)
        self.instruction.rs2 = random.randint(0, 32)
        self.instruction.func3 = random.randint(0, 8)
        self.instruction.func7 = random.randint(0, 128)
        
        self.instruction.update_inst()

class RandomRSeq(uvm_sequence):
    async def body(self): 
        for _ in range(10):
            new_instruction = RInstruction(0, 0, 0, 0, 0, 0)
            cmd_tr = InstSeqItem("cmd_tr", new_instruction)
            cmd_tr.randomize()
            await self.start_item(cmd_tr)
            cmd_tr.randomize()
            await self.finish_item(cmd_tr)

class RAllSeq(uvm_sequence):
    async def body(self):
        instruction_vector = [
            # ADD 3, 1, 2
            RInstruction(0b0110011, 0b00011, 0b00001, 0b00010, 0x0, 0x00),

            # SUB 3, 1, 2
            RInstruction(0b0110011, 0b00011, 0b00001, 0b00010, 0x0, 0x20),

            # XOR 3, 1, 2
            RInstruction(0b0110011, 0b00011, 0b00001, 0b00010, 0x4, 0x00),

            # OR 3, 1, 2
            RInstruction(0b0110011, 0b00011, 0b00001, 0b00010, 0x6, 0x00),

            # AND 3, 1, 2
            RInstruction(0b0110011, 0b00011, 0b00001, 0b00010, 0x7, 0x00),

            # SLL 3, 1, 2
            RInstruction(0b0110011, 0b00011, 0b00001, 0b00010, 0x1, 0x00),

            # SRL 3, 1, 2
            RInstruction(0b0110011, 0b00011, 0b00001, 0b00010, 0x5, 0x00),

            # # SRA 3, 1, 2
            RInstruction(0b0110011, 0b00011, 0b00001, 0b00010, 0x5, 0x20),

            # # SLT 3, 1, 2
            RInstruction(0b0110011, 0b00011, 0b00001, 0b00010, 0x2, 0x00),

            # # SLTU 3, 1, 2
            RInstruction(0b0110011, 0b00011, 0b00001, 0b00010, 0x3, 0x00)
        ]

        for instruction in instruction_vector:
            cmd_tr = InstSeqItem("cmd_tr", instruction)
            await self.start_item(cmd_tr)
            await self.finish_item(cmd_tr)

# Main sequence
class SimpleSeq(uvm_sequence):
    async def body(self):
        instruction_vector = [
            # ADDI 1, 0, 1
            IInstruction(0b0010011, 0b00001, 0b00000, 0b00001, 0x0),

            # ADD 2, 1, 2
            RInstruction(0b0110011, 0b00010, 0b00001, 0b00010, 0x0, 0x00),

            # ADDI 3, 2, 1
            IInstruction(0b0010011, 0b00011, 0b00010, 0b00001, 0x0),

            # ADD 2, 1, 2
            RInstruction(0b0110011, 0b00010, 0b00001, 0b00010, 0x0, 0x00),

            # ADDI 1, 0, 1
            IInstruction(0b0010011, 0b00001, 0b00000, 0b00001, 0x0),

            # ADD 2, 1, 2
            RInstruction(0b0110011, 0b00010, 0b00001, 0b00010, 0x0, 0x00),

            # ADDI 1, 0, 1
            IInstruction(0b0010011, 0b00001, 0b00000, 0b00001, 0x0),

            # ADD 2, 1, 2
            RInstruction(0b0110011, 0b00010, 0b00001, 0b00010, 0x0, 0x00)
        ]

        for instruction in instruction_vector:
            cmd_tr = InstSeqItem("cmd_tr", instruction)
            await self.start_item(cmd_tr)
            await self.finish_item(cmd_tr)

# Class to execute sequence with a Sequencer DB
class TestAllSeq(uvm_sequence):
    async def body(self):
        seqr = ConfigDB().get(None, "", "SEQR")
        random = SimpleSeq("random")
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
        await self.launch_tb()
        while True:
            current_instruction = await self.seq_item_port.get_next_item()
            await self.bfm.send_instruction(current_instruction)
            result = await self.bfm.get_result()
            self.ap.write(result)
            self.seq_item_port.item_done()

class Scoreboard(uvm_component):
    def build_phase(self):
        self.cmd_fifo = uvm_tlm_analysis_fifo("cmd_fifo", self)
        self.result_fifo = uvm_tlm_analysis_fifo("result_fifo", self)
        self.cmd_get_port = uvm_get_port("cmd_get_port", self)
        self.result_get_port = uvm_get_port("result_get_port", self)
        self.cmd_export = self.cmd_fifo.analysis_export
        self.result_export = self.result_fifo.analysis_export
        
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

            # TODO: Fix this problem
            if ignore_first:
                ignore_first = False
            else:
                if not cmd_success:
                    self.logger.critical(f"result had no command")
                else:
                    # Update processor model state
                    self.model.execute(create_instruction(instruction))

                    predicted_state = self.model.state

                    if predicted_state == actual_state:
                        self.logger.info(f"PASSED")
                    else:
                        self.logger.error(f"FAILED : Predicted != Actual")

                        # Print difference between states
                        diff_state(predicted_state, actual_state)

                        passed = False
            
        assert passed

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

    def connect_phase(self):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.cmd_mon.ap.connect(self.scoreboard.cmd_export)
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
        await self.test_all.start()
        self.drop_objection()