module testbench #(
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
)
(
    // Cache interface
    input  wire req,
    input  wire [ADDR_WIDTH-1:0] addr,

    output wire valid,
    output wire [WORD_WIDTH-1:0] data,

    // AHB bus interface
    output wire [ADDR_WIDTH-1:0] HADDR,
    output wire [HBURST_WIDTH-1:0] HBURST,
    output wire HMASTLOCK,
    output wire [HPROT_WIDTH-1:0] HPROT,
    output wire [2:0] HSIZE,
    output wire HNONSEC,
    output wire HEXCL,
    output wire [HMASTER_WIDTH-1:0] HMASTER,
    output wire [1:0] HTRANS,
    output wire [WORD_WIDTH-1:0] HWDATA,
    output wire [WORD_WIDTH/8-1:0] HWSTRB,
    output wire HWRITE,
    
    input  wire [WORD_WIDTH-1:0] HRDATA,
    input  wire HREADY,
    input  wire HRESP,
    input  wire HEXOKAY,
    
	// Global control
    input  wire HCLK,
    input  wire HRESETn,

    // Global control
    input rst
);

// Generating clock signal
bit clk;

initial clk = 0;
always #5 clk = ~clk;

// Instantiate the cache module
cache #(
    .WORD_WIDTH(WORD_WIDTH),
    .BLOCK_WIDTH(BLOCK_WIDTH),
    .BLOCK_WIDTH_WORDS(BLOCK_WIDTH_WORDS),
    .BLOCK_SIZE(BLOCK_SIZE),
    .LOG2_BLOCK_WIDTH_WORDS(LOG2_BLOCK_WIDTH_WORDS),
    .LOG2_BLOCK_SIZE(LOG2_BLOCK_SIZE),
    .TAG_WIDTH(TAG_WIDTH),
    .ADDR_WIDTH(ADDR_WIDTH),
    .HBURST_WIDTH(HBURST_WIDTH),
    .HPROT_WIDTH(HPROT_WIDTH),
    .HMASTER_WIDTH(HMASTER_WIDTH)
) dut (
    .req(req),
    .addr(addr),
    .valid(valid),
    .data(data),
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
    .clk(clk),
    .rst(rst)
);

// Simulation variables
initial begin
    // Open the VCD file for waveform dumping
    $dumpfile("simulation.vcd");
    $dumpvars(0, dut);
end

endmodule
