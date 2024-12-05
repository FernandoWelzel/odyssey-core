import cocotb
from cocotb.triggers import FallingEdge
from cocotb.queue import QueueEmpty, Queue

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

class CacheBfm(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top

        # Queues for communication
        self.cpu_req_queue = Queue(maxsize=1)
        self.cpu_resp_queue = Queue(maxsize=0)
        self.ahb_req_queue = Queue(maxsize=1)
        self.ahb_resp_queue = Queue(maxsize=0)

    async def send_cpu_request(self, addr):
        """Send a CPU request to the cache."""
        await self.cpu_req_queue.put(addr)

    async def get_cpu_response(self):
        """Get a response from the cache for the CPU."""
        response = await self.cpu_resp_queue.get()
        return response

    async def send_ahb_request(self, ahb_transaction):
        """Send an AHB transaction to the cache."""
        await self.ahb_req_queue.put(ahb_transaction)

    async def get_ahb_response(self):
        """Get a response from the AHB interface."""
        response = await self.ahb_resp_queue.get()
        return response

    async def reset(self):
        """Reset the DUT."""
        self.dut.rst.value = 1
        self.dut.HRESETn.value = 0
        for _ in range(10):
            await FallingEdge(self.dut.clk)
        self.dut.rst.value = 0
        self.dut.HRESETn.value = 1
        await FallingEdge(self.dut.clk)

    async def interface_bfm(self):
        """BFM for CPU core interface."""
        while True:
            await FallingEdge(self.dut.clk)
            try:
                addr = self.cpu_req_queue.get_nowait()
                self.dut.req.value = 1
                self.dut.addr.value = addr
            except QueueEmpty:
                self.dut.req.value = 0

            if self.dut.valid.value == 1:
                data = get_int(self.dut.data)
                self.cpu_resp_queue.put_nowait(data)
            
            # Driving AHB interface
            if self.dut.HTRANS.value == 1:
                self.dut.HREADY.value = 1
                self.dut.HRDATA.value = self.dut.HADDR.value
            else:
                self.dut.HREADY.value = 0

    def start_bfm(self):
        """Start the BFMs."""
        cocotb.start_soon(self.interface_bfm())
