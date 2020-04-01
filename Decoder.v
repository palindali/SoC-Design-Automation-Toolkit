//Design: Example Design 
//License: 1 
//Version: 2.0 
//Designer:  
//Date: 8 / 12 / 2019 


module decoder( input [31:0] HADDR,
output reg [0:0] HSEL_1, HSEL_2, HSEL_3, 	HSEL_DF);
wire [3:0] Base_Addr;
assign Base_Addr= HADDR[31:28];
always@(Base_Addr)begin
	HSEL_1<=0;
	HSEL_2<=0;
	HSEL_3<=0;
	HSEL_DF<=0;
	case (Base_Addr)
		4'd1:
			HSEL_1<=1;
		4'd2:
			HSEL_2<=1;
		4'd3:
			HSEL_3<=1;
		default:
			HSEL_DF<=1;
		endcase
end
endmodule