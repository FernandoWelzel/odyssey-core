`timescale 1ns/100ps

module cache_test #(
	parameter CLK_PERIOD = 5,
    
    // Size of cache
    parameter WORD_WIDTH = 32,
    parameter BLOCK_WIDTH = 256,
    parameter BLOCK_WIDTH_WORDS = 8,
    parameter BLOCK_SIZE = 32,

    // Address division
    parameter LOG2_BLOCK_WIDTH_WORDS = 3,
    parameter LOG2_BLOCK_SIZE = 5,
    parameter TAG_WIDTH = 22,
    parameter ADDR_WIDTH = 32,
 
    parameter HBURST_WIDTH = 1,
    parameter HPROT_WIDTH = 1,
    parameter HMASTER_WIDTH = 1
)();

// CPU interface
bit req;
bit [ADDR_WIDTH-1:0] addr;
bit valid;
bit [WORD_WIDTH-1:0] data;

// Bus interface
bit [ADDR_WIDTH-1:0] HADDR;
bit [HBURST_WIDTH-1:0] HBURST;
bit HMASTLOCK;
bit [HPROT_WIDTH-1:0] HPROT;
bit [2:0] HSIZE;
bit HNONSEC;
bit HEXCL;
bit [HMASTER_WIDTH-1:0] HMASTER;
bit [1:0] HTRANS;
bit [WORD_WIDTH-1:0] HWDATA;
bit [WORD_WIDTH/8-1:0] HWSTRB;
bit HWRITE;
bit [WORD_WIDTH-1:0] HRDATA;
bit HREADY;
bit HRESP;
bit HEXOKAY;
bit HCLK;
bit HRESETn;

// Global signals
bit clk;
bit rst;

// Clock generation
always #CLK_PERIOD clk <= ~clk;

// DUT instance
cache dut (
    // Microprocessor interface
    .req(req),
    .addr(addr),
    .valid(valid),
    .data(data),
    
    // Bus interface
    .HADDR(HADDR),
    .HBURST(HBURST),
    .HMASTLOCK(HMASTLOCK),
    .HPROT(HPROT),
    .HSIZE(HSIZE),
    .HNONSEC(HNONSEC),
    .HEXCL(HEXCL),
    .HMASTER(HMASTER),
    .HTRANS(HTRANS),
    .HWDATA(HWDATA),
    .HWSTRB(HWSTRB),
    .HWRITE(HWRITE),
    .HRDATA(HRDATA),
    .HREADY(HREADY),
    .HRESP(HRESP),
    .HEXOKAY(HEXOKAY),
    .HCLK(clk),
    .HRESETn(~rst),

    // Global control interface
    .clk(clk),
    .rst(rst)
);

bus_driver driver (
    // Bus interface
    .HADDR(HADDR),
    .HBURST(HBURST),
    .HMASTLOCK(HMASTLOCK),
    .HPROT(HPROT),
    .HSIZE(HSIZE),
    .HNONSEC(HNONSEC),
    .HEXCL(HEXCL),
    .HMASTER(HMASTER),
    .HTRANS(HTRANS),
    .HWDATA(HWDATA),
    .HWSTRB(HWSTRB),
    .HWRITE(HWRITE),
    .HRDATA(HRDATA),
    .HREADY(HREADY),
    .HRESP(HRESP),
    .HEXOKAY(HEXOKAY),
    .HCLK(clk),
    .HRESETn(~rst),

    // Global control interface
    .clk(clk),
    .rst(rst)
);

initial begin
    // Initializing variables
    clk = 1'b0;
    req = 1'b0;

    // Reset sequence
    rst = 1'b1;
    # 10;
    rst = 1'b0;
    # 10;

    // Sequence
    for (int i=0; i<1024; ++i) begin
        req = 1'b1;
        addr = i;

        @(posedge valid);
        
        req = 1'b0;

        #5;
    end

    $finish;
end

// Declare a file to dump the waveform data
initial begin
    $dumpfile("testbench.vcd");
    $dumpvars(0, cache_test); // Dump all signals in the module
end

endmodule
