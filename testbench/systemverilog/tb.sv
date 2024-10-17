// Simple testbench
module testbench #(
    parameter DATA_WIDTH = 32,
    parameter REGISTERS = 32,

    parameter PERIOD = 10 
)();

// Signal declaration
logic clk;
logic rst;

logic [DATA_WIDTH-1:0] inst_address;
logic [DATA_WIDTH-1:0] inst;
logic [0:DATA_WIDTH-1] inst_inversed;
logic inst_csn;

logic [DATA_WIDTH-1:0] data_address;
logic [DATA_WIDTH-1:0] r_data;
logic [DATA_WIDTH-1:0] w_data;

// Instantiating main component
`ifdef SYNTH
    core core_i (
`else
    core core_i (
`endif
    .inst_req(inst_req),
    .inst_addr(inst_addr),
    .inst_valid(inst_valid),
    .inst_data(inst_data),
    .data_req(data_req),
    .data_addr(data_addr),
    .data_valid(data_valid),
    .rdata(rdata),
    .wdata(wdata),
    .inst_we(inst_we),
    .byte_enable(byte_enable),
    .clk(clk),
    .rst(rst)
);

// Toggling clock
initial begin
    forever begin
        #(PERIOD/2) clk <= ~clk;
    end
end

// File handle
int file_handle;

assign inst_inversed = inst;

string line;
int FILE, code;

// Function to read instruction from file considering byte order
function automatic bit [31:0] read_int_from_file();
    bit [7:0] temp_byte;
    int i;

    // Read the bytes into a temporary variable
    for (i = 0; i < 4; i++) begin
        if (!$fread(temp_byte, FILE)) begin
            return 0;
        end

        inst[i*8 +: 8] = temp_byte;
    end

    return 1;
endfunction

// Open the binary file for reading
initial begin
    // Open the file in binary mode for reading
    FILE = $fopen("testbench/verilator/test", "rb");

    if (FILE == 0) begin
        $display("Error opening file");
        $finish;
    end
end

int status;

initial begin
    // Initialize signals
    clk <= 0;
    rst <= 0;

    // Wait testbench
    while(read_int_from_file()) begin
        // Put value into data
        $display("%h", inst);

        #PERIOD;

      	// $display("RD = %0d, RS1 = %0d, RS2 = %0d", core_i.rd, core_i.rs1, core_i.rs2);
      	// $display("DATA[RD] = %0d, DATA[RS1] = %0d, DATA[RS2] = %0d", core_i.register_file[core_i.rd], core_i.register_file[core_i.rs1], core_i.register_file[core_i.rs2]);
    end

    $display("Simulation passing!");

    $finish;
end

// Declare a file to dump the waveform data
initial begin
    $dumpfile("testbench.vcd");
    $dumpvars(0, testbench); // Dump all signals in the module
end

endmodule
