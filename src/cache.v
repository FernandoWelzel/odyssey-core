// TODO: Check value of parameters
module cache #(
    parameter WORD_WIDTH = 32,
    parameter WORDS = 128,

    parameter ADDR_WIDTH = 32,
    parameter HBURST_WIDTH = 1,
    parameter HPROT_WIDTH = 1,
    parameter HMASTER_WIDTH = 1,
    parameter WORD_WIDTH = 32
)
(
	// Microprocessor interface

    // AHB bus interface
    output logic [ADDR_WIDTH-1:0] HADDR,
    output logic [HBURST_WIDTH-1:0] HBURST,
    output logic HMASTLOCK,
    output logic [HPROT_WIDTH-1:0] HPROT,
    output logic [2:0] HSIZE,
    output logic HNONSEC,
    output logic HEXCL,
    output logic [HMASTER_WIDTH-1:0] HMASTER,
    output logic [1:0] HTRANS,
    output logic [WORDS_WIDTH-1:0] HWDATA,
    output logic [WORDS_WIDTH/8-1:0] HWSTRB,
    output logic HWSTRB,
    output logic HWDATA,
    output logic HWRITE,
    
    input  logic [WORDS_WIDTH-1:0] HRDATA,
    input  logic HREADY,
    input  logic HRESP,
    input  logic HEXOKAY,
    
	// Global control
    input  logic HCLK,
    input  logic HRESETn,
);

