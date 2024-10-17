`ifndef _config_vh_
`define _config_vh_

// ALU operations encoding - Equals and less than will always be performed:
localparam ADD_SUB_OP = 0; // Addition/Subtraction
localparam XOR_OP     = 1; // Bitwise XOR
localparam OR_OP      = 2; // Bitwise OR
localparam AND_OP     = 3; // Bitwise AND
localparam LLS_OP     = 4; // Left shift
localparam RLS_OP     = 5; // Right shift

`endif
