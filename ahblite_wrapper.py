from wrapper import Wrapper

class AHBLite_wrapper(Wrapper):
    def __init__(self,component,path,info):
        Wrapper.__init__(self,component,path,info)
        self.name+="_AHBlite_wrapper"

    def generateWrapper(self):
        Wrapper.generateWrapper(self)

    def module_Signals(self):
        ver=""
        #AHB-Lite signals
        ver+="\n//AHB-Lite signals\n"
        ver+="//Global signals\n\tinput  wire        HCLK,\n\tinput  wire        HRESETn,\n"
        ver+="//Master signals\n\tinput  wire [23:14] HADDR,\n\tinput  wire [2:0] HBURST,\n\tinput  wire        HMASTLOCK,\n\tinput  wire [3:0]  HPROT,\n\tinput  wire [2:0]  HSIZE,\n\tinput  wire [1:0]  HTRANS,\n\tinput  wire [31:0] HWDATA,\n\tinput  wire        HWRITE,\n"
        ver+="//Slave signals\n\toutput wire [31:0] HRDATA,\n\toutput wire        HREADYOUT,\n\toutput wire        HRESP,\n"
        ver+="//Decoder signal\n\tinput  wire        HSEL,\n"
        ver+="//Multiplexer Signal\n\tinput wire         HREADY,\n"

        return ver
    
    def map_Signals(self):
        ver=""
        ver+="assign  rd_enable  = HSEL & (~HWRITE);\nassign  wr_enable = HSEL & HWRITE;\n"
        ver+="assign HRESP = 1'b0;\nassign HREADYOUT = 1'b1;\n"

        return ver

    def module_regs(self):
        return Wrapper.module_regs(self)
    
    def registers_wires(self):
        return Wrapper.registers_wires(self)

    def IO_assignments(self):
        ver=""
        #output always blocks
        ver+="\n//Write"
        for i in range(len(self.regs)):
            if self.regs[i]['access']==0:
                    name=self.regs[i]['name']
                    size=self.regs[i]['size']
                    offeset=int(self.regs[i]['offset'])
                    ver+=("\n//Register: %s\n" %name)
                    ver+=("wire %s_select = wr_enable & (HADDR[23:14] == 10'd%d);\n" %(name, offeset))
                    ver+="always @(posedge HCLK or negedge HRESETn)\nbegin\n\tif (~HRESETn)\n"
                    ver+=("\t\t%s <= %d'h0;\n" %(name,size))
                    ver+=("\telse if (%s_select)\n" %name)
                    ver+=("\t\t%s <= HWDATA;\nend\n" %name)

        #input assignment
        ver+="\n//Read\n"
        ver+="assign HRDATA = \n"
        for i in range(len(self.regs)):
            name=self.regs[i]['name']
            size=self.regs[i]['size']
            offeset=int(self.regs[i]['offset'])
            ver+=("\t(HADDR[23:14] == 10'd%d) ? {%d'd0,%s} :\n"%(offeset, (32-size),name))
        ver+="\t32'hDEADBEEF;\n"

        return ver

    def instantion(self,instname,HCLK,HRESETn,HADDR,HBURST,HMASTLOCK,HPROT,HSIZE,HTRANS,HWDATA,HWRITE,HRDATA,HREADYOUT,HRESP,HSEL,HREADY):
        
        self.clk=HCLK
        self.reset=HRESETn
        
        ver=""
        
        #IP registers wires
        ver+=self.ip_registers_wires()

        #IP irqs wires
        ver+=self.ip_irqs_wires()

        #wrapper instantiation
        ver+=("%s %s( " %(self.name,instname))
        #IP interface signals instantiation
        ver+=self.ip_registers_signals()
        #bus signals instantiation
        ver+=(".HCLK(%s), .HRESETn(%s), .HADDR(%s), .HBURST(%s), .HMASTLOCK(%s), .HPROT(%s), .HSIZE(%s), .HTRANS(%s), .HWDATA(%s), .HWRITE(%s), .HRDATA(%s), .HREADYOUT(%s), .HRESP(%s), .HSEL(%s), .HREADY(%s)" %(HCLK,HRESETn,HADDR,HBURST,HMASTLOCK,HPROT,HSIZE,HTRANS,HWDATA,HWRITE,HRDATA,HREADYOUT,HRESP,HSEL,HREADY))
        ver+=");\n"

        #Actual IP instantiation
        ver+=self.ip_instantiation()

        return ver

    def ip_registers_wires(self):
        return Wrapper.ip_registers_wires(self)

    def ip_registers_signals(self):
        return Wrapper.ip_registers_signals(self)

    def ip_irqs_wires(self):
        return Wrapper.ip_irqs_wires(self)

    def ip_irqs_signals(self):
        return Wrapper.ip_irqs_signals(self)

    def ip_instantiation(self):
        return Wrapper.ip_instantiation(self)

    
