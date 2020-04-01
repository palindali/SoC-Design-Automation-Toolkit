//Design: Example Design 
//License: 1 
//Version: 2.0 
//Designer:  
//Date: 8 / 12 / 2019 


module multiplexer(
output reg [31:0] HRDATA,
output reg [0:0] HREADY, HRESP,
input [31:0] HRDATA_1, HRDATA_2, HRDATA_3, HRDATA_DF,
input HCLK, HRESETn, HREADYOUT_1, HREADYOUT_2, HREADYOUT_3, HREADYOUT_DF, HRESP_1, HRESP_2, HRESP_3, HRESP_DF, 
input HSEL_1, HSEL_2, HSEL_3, HSEL_DF);

reg [0:0] HSEL_1n, HSEL_2n, HSEL_3n, HSEL_DFn;

always @ (posedge(HCLK), posedge(HRESETn))
begin
	if(HRESETn==1) begin
		HSEL_1n<=0;
		HSEL_2n<=0;
		HSEL_3n<=0;
		HSEL_DFn<=0;
end
	else begin
		if(HREADY)begin
			HSEL_1n<=HSEL_1;
			HSEL_2n<=HSEL_2;
			HSEL_3n<=HSEL_3;
			HSEL_DFn<=HSEL_DF;
		end
	end
end
always @(*)
begin
	if(HSEL_1n)	begin
		HRDATA<=HRDATA_1;
		HREADY<=HREADYOUT_1;
		HRESP<=HRESP_1;
	end
	else if(HSEL_2n)	begin
		HRDATA<=HRDATA_2;
		HREADY<=HREADYOUT_2;
		HRESP<=HRESP_2;
	end
	else if(HSEL_3n)	begin
		HRDATA<=HRDATA_3;
		HREADY<=HREADYOUT_3;
		HRESP<=HRESP_3;
	end
	else if(HSEL_DFn)begin
		HRDATA<=HRDATA_DF;
		HREADY<=HREADYOUT_DF;
		HRESP<=HRESP_DF;
	end
	else if(HRESETn)begin
		HREADY<=1;
	end
	else begin
		HREADY<=1;
	end
end
endmodule