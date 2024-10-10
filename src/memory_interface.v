// TODO: Check value of parameters
module memory_interface #(
    parameter ADDR_WIDTH = 32,
    parameter HBURST_WIDTH = 1,
    parameter HPROT_WIDTH = 1,
    parameter HMASTER_WIDTH = 1,
    parameter WORD_WIDTH = 32
)
(
    // AHB bus interface
    input  logic [ADDR_WIDTH-1:0] HADDR,
    input  logic [HBURST_WIDTH-1:0] HBURST,
    input  logic HMASTLOCK,
    input  logic [HPROT_WIDTH-1:0] HPROT,
    input  logic [2:0] HSIZE,
    input  logic HNONSEC,
    input  logic HEXCL,
    input  logic [HMASTER_WIDTH-1:0] HMASTER,
    input  logic [1:0] HTRANS,
    input  logic [WORDS_WIDTH-1:0] HWDATA,
    input  logic [WORDS_WIDTH/8-1:0] HWSTRB,
    input  logic HWSTRB,
    input  logic HWDATA,
    input  logic HWRITE,
    
    output logic [WORDS_WIDTH-1:0] HRDATA,
    output logic HREADY,
    output logic HRESP,
    output logic HEXOKAY,

    // BSRAM interface (TANG 9k - Single Port 16K BSRAM)
    input  logic [WORDS_WIDTH-1:0] DO,
    output logic [WORDS_WIDTH-1:0] DI,
    output logic [14:0] AD,
    output logic CE,
    output logic CLK,
    output logic RESET,
    output logic OCE,
    output logic [2:0] BLKSEL,

	// Global control
    input  logic HCLK,
    input  logic HRESETn,
);
    