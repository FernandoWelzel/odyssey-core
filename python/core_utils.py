import cocotb
from cocotb.triggers import FallingEdge
from cocotb.queue import QueueEmpty, Queue

import enum
import logging

from pyuvm import utility_classes

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_int(signal):
    try:
        sig = int(signal.value)
    except ValueError:
        sig = 0
    return sig

class Instruction():
    def __init__(self, opcode : int):
        # TODO: Assert size of opcode
        self.opcode = opcode

class RInstruction(Instruction):
    def __init__(self, opcode : int, rd : int, rs1 : int, rs2 : int, func3 : int, func7 : int):
        super().__init__(opcode)
        
        # TODO: Assert size of each of the variables
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.func3 = func3
        self.func7 = func7

        # Calculate the new instruction
        self.update_inst()
    
    def __str__(self) -> str:
        return f"R type instruction : {'0x{0:08X}'.format(self.inst)}"

    def update_inst(self):
        # TODO: Assert size of new variables
        self.inst = self.opcode + (self.rd << 7) + (self.rs1 << 15) + (self.rs2 << 20) + (self.func3 << 12) + (self.func7 << 25)
    
# TODO: Make all other instructions types

class CoreBfm(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top
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
            address = get_int(self.dut.inst_addr)
            if request:
                try:
                    current_instruction = self.driver_queue.get_nowait()
                    self.dut.inst_data.value = current_instruction.instruction.inst
                    self.dut.inst_valid.value = 1
                except QueueEmpty:
                    pass

    async def cmd_mon_bfm(self):
        # TODO: Fix being the same as result
        prev_request = 0
        while True:
            await FallingEdge(self.dut.clk)
            request = get_int(self.dut.inst_req)
            if request == 1 and prev_request == 0:
                self.cmd_mon_queue.put_nowait(self.dut.inst_addr)
            prev_request = request

    async def result_mon_bfm(self):
        prev_request = 0
        while True:
            await FallingEdge(self.dut.clk)
            request = get_int(self.dut.inst_req)
            if request == 1 and prev_request == 0:
                self.result_mon_queue.put_nowait(self.dut.inst_addr)
            prev_request = request

    def start_bfm(self):
        cocotb.start_soon(self.driver_bfm())
        cocotb.start_soon(self.cmd_mon_bfm())
        cocotb.start_soon(self.result_mon_bfm())
