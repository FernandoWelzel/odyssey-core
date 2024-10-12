// Processor 7 segment display driver
module fys_driver (
    output wire [6:0] segments,
    
    input  wire rstn,
    input  wire clk
);

reg [6:0] segments_reg;
reg [31:0] count;

always @(posedge clk) begin
    if(~rstn) begin
        count = 0;
    end
    else begin
        count = count + 1;
    end
end

always @(*) begin
    case (count[26:23])
        4'h0: begin
            segments_reg = 7'b1101000;
        end
        4'h1: begin
            segments_reg = 7'b1011011;
        end
        4'h2: begin
            segments_reg = 7'b1110100;
        end
        4'h3: begin
            segments_reg = 7'b1110001;
        end
        4'h4: begin
            segments_reg = 7'b1000011;
        end
        4'h5: begin
            segments_reg = 7'b0100001;
        end
        4'h6: begin
            segments_reg = 7'b0100000;
        end
        4'h7: begin
            segments_reg = 7'b1111011;
        end
        4'h8: begin
            segments_reg = 7'b1100000;
        end
        4'h9: begin
            segments_reg = 7'b1100011;
        end
        4'hA: begin
            segments_reg = 7'b1100010;
        end
        4'hB: begin
            segments_reg = 7'b0000000;
        end
        4'hC: begin
            segments_reg = 7'b0101100;
        end
        4'hD: begin
            segments_reg = 7'b1010000;
        end
        4'hE: begin
            segments_reg = 7'b0100100;
        end
        4'hF: begin
            segments_reg = 7'b0100110;
        end
    endcase
end

assign segments = segments_reg;

endmodule
