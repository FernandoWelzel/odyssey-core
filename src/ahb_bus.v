// AHB bus - Interconnects processor with BSRAM and APB bridge
module ahb_bus #(
    parameter N_MANAGERS = 2,
    parameter N_SUBORDINATES = 2,

    parameter INIT_SUBORDINATE_ADDRS = {32'h00000000, 32'h00080000},
    parameter END_SUBORDINATE_ADDRS = {32'h0007FFFF, 32'h000FFFFF},
    
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
)(
    // Manager interfaces
    output wire [N_MANAGERS*ADDR_WIDTH-1:0] m_HADDR,
    output wire [N_MANAGERS*HBURST_WIDTH-1:0] m_HBURST,
    output wire [N_MANAGERS-1:0] m_HMASTLOCK,
    output wire [N_MANAGERS*HPROT_WIDTH-1:0] m_HPROT,
    output wire [N_MANAGERS*3-1:0] m_HSIZE,
    output wire [N_MANAGERS-1:0] m_HNONSEC,
    output wire [N_MANAGERS-1:0] m_HEXCL,
    output wire [N_MANAGERS*HMASTER_WIDTH-1:0] m_HMASTER,
    output wire [N_MANAGERS*2-1:0] m_HTRANS,
    output wire [N_MANAGERS*WORD_WIDTH-1:0] m_HWDATA,
    output wire [N_MANAGERS*WORD_WIDTH/8-1:0] m_HWSTRB,
    output wire [N_MANAGERS-1:0] m_HWRITE,    
    input  wire [N_MANAGERS*WORD_WIDTH-1:0] m_HRDATA,
    input  wire [N_MANAGERS-1:0] m_HREADY,
    input  wire [N_MANAGERS-1:0] m_HRESP,
    input  wire [N_MANAGERS-1:0] m_HEXOKAY,

    // Subordinate interfaces
    output wire [N_SUBORDINATES-1:0] s_HRESETn,
    output wire [N_SUBORDINATES-1:0] s_HCLK,
    output wire [N_SUBORDINATES-1:0] s_HSELx,
    output wire [N_SUBORDINATES*WORD_WIDTH-1:0] s_HADDR,
    output wire [N_SUBORDINATES-1:0] s_HWRITE,
    output wire [N_SUBORDINATES*2-1:0] s_HTRANS,
    output wire [N_SUBORDINATES*3-1:0] s_HSIZE,
    output wire [N_SUBORDINATES*3-1:0] s_HBURST,
    output wire [N_SUBORDINATES*4-1:0] s_HPROT,
    output wire [N_SUBORDINATES-1:0] s_HMASTLOCK,
    output wire [N_SUBORDINATES-1:0] s_HREADY,
    output wire [N_SUBORDINATES*WORD_WIDTH-1:0] s_HWDATA,
    input  wire [N_SUBORDINATES-1:0] s_HREADYOUT,
    input  wire [N_SUBORDINATES-1:0] s_HRESP,
    input  wire [N_SUBORDINATES*WORD_WIDTH-1:0] s_HRDATA
);


// State registers - One hot encoded of current manager priority
reg [N_MANAGERS-1:0] c_state, n_state;

// Internal registers
reg [ADDR_WIDTH-1:0] c_HADDR;
reg [HBURST_WIDTH-1:0] c_HBURST;
reg c_HMASTLOCK;
reg [HPROT_WIDTH-1:0] c_HPROT;
reg [2:0] c_HSIZE;
reg c_HNONSEC;
reg c_HEXCL;
reg [HMASTER_WIDTH-1:0] c_HMASTER;
reg [1:0] c_HTRANS;
reg [WORD_WIDTH-1:0] c_HWDATA;
reg [WORD_WIDTH/8-1:0] c_HWSTRB;
reg c_HWRITE;    
reg [WORD_WIDTH-1:0] c_HRDATA;
reg c_HREADY;
reg c_HRESP;
reg c_HEXOKAY;

// Generating connection to current manager
always @(*) begin
    c_HADDR = m_HADDR[c_state*ADDR_WIDTH-1:(c_state-1)*ADDR_WIDTH];
    c_HBURST = m_HBURST[c_state*HBURST_WIDTH-1:(c_state-1)*HBURST_WIDTH];
    c_HMASTLOCK = m_HMASTLOCK[c_state-1] ;
    c_HPROT = m_HPROT[c_state*HPROT_WIDTH-1:(c_state-1)*HPROT_WIDTH];
    c_HSIZE = m_HSIZE[c_state*3-1:(c_state-1)*3];
    c_HNONSEC = m_HNONSEC[c_state-1] ;
    c_HEXCL = m_HEXCL[c_state-1] ;
    c_HMASTER = m_HMASTER[c_state*HMASTER_WIDTH-1:(c_state-1)*HMASTER_WIDTH];
    c_HTRANS = m_HTRANS[c_state*2-1:(c_state-1)*2];
    c_HWDATA = m_HWDATA[c_state*WORD_WIDTH-1:(c_state-1)*WORD_WIDTH];
    c_HWSTRB = m_HWSTRB[c_state*WORD_WIDTH/8-1:(c_state-1)*WORD_WIDTH/8];
    c_HWRITE = m_HWRITE[c_state-1] ;
    c_HRDATA = m_HRDATA[c_state*WORD_WIDTH-1:(c_state-1)*WORD_WIDTH];
    c_HREADY = m_HREADY[c_state-1];
    c_HRESP = m_HRESP[c_state-1];
    c_HEXOKAY = m_HEXOKAY[c_state-1];
end

// Generating connections between current manager and subordinates
generate;
    genvar i;

    for (i=0; i<N_SUBORDINATES; ++i) begin
        // Will only be valid if in the correct address
        assign HSELx[i] = (c_HADDR >= INIT_SUBORDINATE_ADDRS[i] && c_HADDR <= END_SUBORDINATE_ADDRS[i]);
    
        // Connections for all subordinates
        assign s_HADDR[i*WORD_WIDTH-1:(i-1)*WORD_WIDTH] = c_HADDR;
        assign s_HBURST[i*3-1:(i-1)*3] = c_HBURST;
        assign s_HMASTLOCK[i] = c_HMASTLOCK;
        assign s_HPROT[i*4-1:(i-1)*4] = c_HPROT; 
        assign s_HSIZE[i*3-1:(i-1)*3] = c_HSIZE;
        // assign  = c_HNONSEC;
        // assign  = c_HEXCL;
        // assign  = c_HMASTER;
        assign s_HTRANS[i] = c_HTRANS;
        assign s_HWDATA[i*WORD_WIDTH-1:(i-1)*WORD_WIDTH] = c_HWDATA;
        // assign  = c_HWSTRB;
        assign s_HWRITE[i] = c_HWRITE;
        assign s_HRDATA[i*WORD_WIDTH-1:(i-1)*WORD_WIDTH] = c_HRDATA; 
        assign s_HREADY[i] = c_HREADY;
        assign s_HRESP[i] = c_HRESP; 
        // assign  = c_HEXOKAY;
    end
endgenerate

// State change logic
always @(*) begin
    // Stay in the same stage if there is a request
    // from the manager with priority at the moment
    if(c_state && m_HTRANS) begin
        n_state = c_state;
    end
    else begin
        // Wraps state arround if in the last state
        if(c_state == N_MANAGERS) begin
            n_state = 1;
        end
        else begin
            n_state = c_state + 1;
        end
    end
end

// Sequential state variables
always @(posedge clk) begin
    if(rst) begin
        // Initialiazes state to the first manager
        c_state <= 1;
    end
    else begin
        c_state <= n_state;
    end
end

endmodule