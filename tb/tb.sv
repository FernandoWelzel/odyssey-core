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

logic [DATA_WIDTH-1:0] data_address;
logic [DATA_WIDTH-1:0] r_data;
logic [DATA_WIDTH-1:0] w_data;

// Instantiating main component
`ifdef SYNTH
    core core_i (
`else
    core #(
        .DATA_WIDTH(DATA_WIDTH),
        .REGISTERS(REGISTERS)
    ) core_i (
`endif
        .clk(clk),
        .rst(rst),
        .inst_address(inst_address),
        .inst(inst),
        .data_address(data_address),
        .r_data(r_data),
        .w_data(w_data)
    );

// Toggling clock
initial begin
    forever begin
        #(PERIOD/2) clk <= ~clk;
    end
end

// File handle
int file_handle;

string line;
int FILE, code;

// Open the binary file for reading
initial begin
    // Open the file in binary mode for reading
    FILE = $fopen("tb/generated_bytecode.riscv", "r");

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

    `ifndef SYNTH
        for (int i=0; i<REGISTERS; ++i) begin
            core_i.register_file[i] <= 1;
        end
    `endif

    // Wait testbench
    while($fgets(line, FILE)) begin
        // Put value into data
        status = $sscanf(line, "%d", inst);

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