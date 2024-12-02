import cocotb
from cocotb.triggers import FallingEdge
from cocotb.queue import QueueEmpty, Queue
from cocotb.log import get_sim_time

import logging

from pyuvm import utility_classes

from core_model import CoreModel, CoreState
from instructions import Instruction

import copy

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_int(signal):
    try:
        sig = int(signal.value)
    except ValueError:
        sig = 0
    return sig

class CoreBfm(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.model = CoreModel()
        
        self.driver_queue = Queue(maxsize=1)
        self.cmd_mon_queue = Queue(maxsize=0)
        self.result_mon_queue = Queue(maxsize=0)

        self.request = 0
        self.prev_request = 0

    async def send_instruction(self, instruction : Instruction):
        await self.driver_queue.put(instruction)

    async def get_cmd(self):
        cmd = await self.cmd_mon_queue.get()
        return cmd

    async def get_result(self):
        result = await self.result_mon_queue.get()
        return result

    async def reset(self):
        await FallingEdge(self.dut.clk)
        self.dut.inst_valid.value = 0
        self.dut.inst_data.value = 0
        self.dut.data_valid.value = 0
        self.dut.rdata.value = 0
        self.dut.rst.value = 1
        for _ in range(10):
            await FallingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await FallingEdge(self.dut.clk)

    async def driver_bfm(self):
        while True:
            await FallingEdge(self.dut.clk)
            inst_request = get_int(self.dut.inst_req)
            data_request = get_int(self.dut.data_req)

            # Sends new instruction
            if inst_request:
                try:
                    # Get new instruction
                    current_instruction = self.driver_queue.get_nowait()
                    
                    # Sends instruction to DUT
                    self.dut.inst_data.value = current_instruction.instruction.inst
                    self.dut.inst_valid.value = 1

                except QueueEmpty:
                    pass
            else:
                self.dut.inst_valid.value = 0
            
            # Sends new data or write into memory the result
            if data_request:
                # Sends instruction to DUT
                self.dut.rdata.value = self.dut.data_addr.value
                self.dut.data_valid.value = 1
            else:
                self.dut.data_valid.value = 0
                
    async def cmd_mon_bfm(self):
        self.prev_valid = 0
        while True:
            await FallingEdge(self.dut.clk)
            self.valid = get_int(self.dut.inst_valid)
            if self.valid == 1 and self.prev_valid == 0:
                # print(f"Got monitor at time {get_sim_time()}")
                self.cmd_mon_queue.put_nowait(self.dut.inst_data.value)

            self.prev_valid = self.valid

    async def result_mon_bfm(self):
        count = 0        
        self.inst_addr = 0
        self.prev_inst_addr = 0

        # Initializes state
        state = CoreState()

        while True:
            await FallingEdge(self.dut.clk)
            self.request = get_int(self.dut.inst_req)
            self.inst_addr = get_int(self.dut.inst_addr)

            if self.request == 1 and self.prev_request == 0 and self.inst_addr != self.prev_inst_addr:
                # Getting registers from internal values
                state.register_file = self.dut.dut.register_file_u.registers.value
                state.pc = self.dut.inst_addr

                # Store as int values
                state.to_int()

                self.result_mon_queue.put_nowait(copy.deepcopy(state))

                count = 0
            
            elif count == 1E4:
                raise Exception

            else:
                # Increases count for number of unused clocks
                count += 1
            
            self.prev_request = self.request
            self.prev_inst_addr = self.inst_addr

    def start_bfm(self):
        cocotb.start_soon(self.driver_bfm())
        cocotb.start_soon(self.cmd_mon_bfm())
        cocotb.start_soon(self.result_mon_bfm())
