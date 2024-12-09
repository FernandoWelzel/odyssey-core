from cocotb.triggers import Join, Combine
from pyuvm import *
import pyuvm
import random
import cocotb
from cocotb.triggers import FallingEdge
import sys
from pathlib import Path

sys.path.append(str(Path("../..").resolve()))

from utils import CacheBfm
from coverage import Coverage

# Sequence items for CPU requests and AHB transactions
class CacheSeqItem(uvm_sequence_item):
    def __init__(self, name, addr=None, ahb_transaction=None):
        super().__init__(name)
        self.addr = addr  # For CPU requests
        self.ahb_transaction = ahb_transaction  # For AHB transactions

    def randomize(self):
        self.addr = random.randint(0, 2**32 - 1)

class RandomSeq(uvm_sequence):
    async def body(self):
        seq_item = CacheSeqItem("seq_item")
        seq_item.randomize()
        await self.start_item(seq_item)
        await self.finish_item(seq_item)

# Class to execute sequence with a Sequencer DB
class TestAllSeq(uvm_sequence):
    async def body(self):
        seqr = ConfigDB().get(None, "", "SEQR")
        random = RandomSeq("random")
        await random.start(seqr)

class CacheDriver(uvm_driver):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)

    def start_of_simulation_phase(self):
        self.bfm = CacheBfm()

    async def launch_tb(self):
        await self.bfm.reset()
        self.bfm.start_bfm()

    async def run_phase(self):
        await self.launch_tb()
        while True:
            cache_item = await self.seq_item_port.get_next_item()
            await self.bfm.send_cpu_request(cache_item.addr)
            self.seq_item_port.item_done()

            for _ in range(10):  # Adjust to match the cache timing
                await FallingEdge(cocotb.top.clk)

class CacheScoreboard(uvm_component):
    def build_phase(self):
        self.cmd_fifo = uvm_tlm_analysis_fifo("cmd_fifo", self)
        self.result_fifo = uvm_tlm_analysis_fifo("result_fifo", self)
        self.cmd_get_port = uvm_get_port("cmd_get_port", self)
        self.result_get_port = uvm_get_port("result_get_port", self)
        self.cmd_export = self.cmd_fifo.analysis_export
        self.result_export = self.result_fifo.analysis_export

        # Interface with coverage
        self.ap = uvm_analysis_port("ap", self)

    def connect_phase(self):
        self.result_get_port.connect(self.result_fifo.get_export)
        self.cmd_get_port.connect(self.cmd_fifo.get_export)

    def check_phase(self):
        passed = True
        while self.result_get_port.can_get() and self.cmd_get_port.can_get():
            cmd_success, addr = self.cmd_get_port.try_get()
            result_success, result = self.result_get_port.try_get()

            if not cmd_success or not result_success:
                self.logger.error("Mismatched transactions")
                passed = False
            else:
                # Check response correctness (e.g., cache hit/miss logic)
                if self.check_response(addr, result):
                    self.logger.info(f"Transaction passed for address {addr}")
                else:
                    self.logger.error(f"Transaction failed for address {addr}")
                    passed = False

    def check_response(self, addr, result):
        # Implement cache behavior validation
        return True  # Placeholder

class CacheMonitor(uvm_component):
    def __init__(self, name, parent, method_name):
        super().__init__(name, parent)
        self.method_name = method_name

    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.bfm = CacheBfm()
        self.get_method = getattr(self.bfm, self.method_name)

    async def run_phase(self):
        while True:
            datum = await self.get_method()
            self.ap.write(datum)

class CacheEnv(uvm_env):
    def build_phase(self):
        self.seqr = uvm_sequencer("seqr", self)
        ConfigDB().set(None, "*", "SEQR", self.seqr)
        self.driver = CacheDriver.create("driver", self)
        self.cmd_mon = CacheMonitor("cmd_mon", self, "get_cpu_response")
        self.scoreboard = CacheScoreboard("scoreboard", self)
        self.coverage = Coverage("coverage", self)

    def connect_phase(self):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.cmd_mon.ap.connect(self.scoreboard.cmd_export)
        self.scoreboard.ap.connect(self.coverage.analysis_export)
        self.driver.ap.connect(self.scoreboard.result_export)

@pyuvm.test()
class CacheTest(uvm_test):
    """Test Cache with random CPU requests"""

    def build_phase(self):
        self.env = CacheEnv("env", self)

    async def run_phase(self):
        self.raise_objection()
        
        for _ in range(10):
            self.test_all = TestAllSeq.create("test_all")
            await self.test_all.start()
        
        self.drop_objection()
