from cocotb.triggers import Join, Combine
from pyuvm import *
import random
import cocotb
import pyuvm
import sys
from pathlib import Path
sys.path.append(str(Path("..").resolve()))
from core_utils import CoreBfm, Instruction, RInstruction

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
        new_instruction = RInstruction(0, 0, 0, 0, 0, 0)
        cmd_tr = InstSeqItem("cmd_tr", new_instruction)
        cmd_tr.randomize()
        await self.start_item(cmd_tr)
        cmd_tr.randomize()
        await self.finish_item(cmd_tr)

class TestAllSeq(uvm_sequence):

    async def body(self):
        seqr = ConfigDB().get(None, "", "SEQR")
        random = RandomRSeq("random")
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

    def connect_phase(self):
        self.result_get_port.connect(self.result_fifo.get_export)

    def check_phase(self):
        passed = True
        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False
        while self.result_get_port.can_get():
            _, actual_result = self.result_get_port.try_get()

            # TODO: Logic to predict next instruction
            predicted_result = 0
            
            if predicted_result == actual_result:
                self.logger.info(f"PASSED: actual_result : {actual_result.value}")
            else:
                self.logger.error(f"FAILED:"
                                    f"= 0x{actual_result.value:08x}"
                                    f"expected 0x{predicted_result:08x}")
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
            self.logger.debug(f"MONITORED {datum.value}")
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
        # self.cmd_mon.ap.connect(self.coverage.analysis_export)
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
