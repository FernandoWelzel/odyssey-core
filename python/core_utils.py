import cocotb
from cocotb.triggers import FallingEdge
from cocotb.queue import QueueEmpty, Queue
from cocotb.log import get_sim_time

import enum
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
        await FallingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await FallingEdge(self.dut.clk)

    async def driver_bfm(self):
        while True:
            await FallingEdge(self.dut.clk)
            request = get_int(self.dut.inst_req)

            if request:
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
                
        # TODO: Fix being the same as result
    async def cmd_mon_bfm(self):
        prev_request = 0
        while True:
            await FallingEdge(self.dut.clk)
            request = get_int(self.dut.inst_req)
            if request == 1 and prev_request == 0:
                self.cmd_mon_queue.put_nowait(self.dut.inst_data.value)

            prev_request = request

    async def result_mon_bfm(self):
        prev_request = 0

        state = CoreState()
        
        while True:
            await FallingEdge(self.dut.clk)
            request = get_int(self.dut.inst_req)

            if request == 0 and prev_request == 1:
                # Getting registers from internal values
                state.register_file = self.dut.dut.register_file_u.registers.value
                state.pc = self.dut.inst_addr

                # Store as int values
                state.to_int()

                self.result_mon_queue.put_nowait(copy.deepcopy(state))

            prev_request = request

    def start_bfm(self):
        cocotb.start_soon(self.driver_bfm())
        cocotb.start_soon(self.cmd_mon_bfm())
        cocotb.start_soon(self.result_mon_bfm())
