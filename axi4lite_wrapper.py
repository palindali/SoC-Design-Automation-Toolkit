from wrapper import Wrapper

class AXI4Lite_Wrapper(Wrapper):
    def __init__(self,component,path,info):
        Wrapper.__init__(self,component,path,info)
        self.name+="_AXI4lite_wrapper"

    def generateWrapper(self):
        Wrapper.generateWrapper(self)

    def module_Signals(self):
        ver=""
        #AXI4-Lite signals
        ver+="\n//AXI4-Lite signals\n"
        ver+="//Global signals\n\tinput  wire        ACLK,\n\tinput  wire        ARESETn,\n"
        ver+="//Write Address channel\n\tinput  wire [23:14] AWADDR,\n\tinput  wire [2:0] AWPROT,\n\tinput  wire        AWVALID,\n\toutput  wire        AWREADY,\n"
        ver+="//Write Data channel\n\tinput  wire [31:0] WDATA,\n\tinput  wire [3:0] WSTRB,\n\tinput  wire        WVALID,\n\toutput  wire        WREADY,\n"
        ver+="//Write Response channel\n\toutput  wire [1:0] BRESP,\n\toutput  wire        BVALID,\n\tinput  wire        BREADY,\n"
        ver+="//Read Address channel\n\tinput  wire [23:14] ARADDR,\n\tinput  wire [2:0] ARPROT,\n\tinput  wire        ARVALID,\n\toutput  wire        ARREADY,\n"
        ver+="//Read Data channel\n\toutput  wire [31:0] RDATA,\n\toutput  wire        RRESP,\n\toutput  wire        RVALID,\n\tinput  wire        RREADY,\n"
        
        return ver

    def map_Signals(self):
        ver=""
        ver+="assign AWREADY=1'b1;\n"
        ver+="assign WREADY=1'b1;\n"
        ver+="assign BVALID = WVALID & WREADY;\n"
        
        ver+="assign ARREADY= 1'b1;\n"
        ver+="assign RVALID= ARVALID & ARREADY;\n"

        ver+="assign  rd_enable  = ARVALID & ARREADY;\nassign  wr_enable = WVALID & WREADY;\n"
        
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
                    ver+=("wire %s_select = wr_enable & (AWADDR[23:14] == 10'd%d);\n" %(name, offeset))
                    ver+="always @(posedge ACLK or negedge ARESETn)\nbegin\n\tif (~ARESETn)\n"
                    ver+=("\t\t%s <= %d'h0;\n" %(name,size))
                    ver+=("\telse if (%s_select)\n" %name)
                    ver+=("\t\t%s <= WDATA;\nend\n" %name)

        #input assignment
        ver+="\n//Read\n"
        ver+="assign RDATA = \n"
        for i in range(len(self.regs)):
            name=self.regs[i]['name']
            size=self.regs[i]['size']
            offeset=int(self.regs[i]['offset'])
            ver+=("\t(ARADDR[23:14] == 10'd%d) ? {%d'd0,%s} :\n"%(offeset, (32-size),name))
        ver+="\t32'hDEADBEEF;\n"

        return ver

    def instantion(self,instname,ACLK,ARESETn,AWADDR,AWVALID,AWREADY,AWPROT,WVALID,WREADY,WDATA,WSTRB,BVALID,BREADY,BRESP,ARVALID,ARREADY,ARADDR,ARPROT,RVALID,RREADY,RDATA,RRESP):
    
    self.clk=ACLK
    self.reset=ARESETn
    
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
    ver+=(".ACLK(%s), .ARESETn(%s), .AWADDR(%s), .AWVALID(%s), .AWREADY(%s), .AWPROT(%s), .WVALID(%s), .WREADY(%s), .WDATA(%s), .WSTRB(%s), .BVALID(%s), .BREADY(%s), .BRESP(%s), .ARVALID(%s), .ARREADY(%s), .ARADDR(%s), .ARPROT(%s), .RVALID(%s), .RREADY(%s), .RDATA(%s), .RRESP(%s)" %(ACLK,ARESETn,AWADDR,AWVALID,AWREADY,AWPROT,WVALID,WREADY,WDATA,WSTRB,BVALID,BREADY,BRESP,ARVALID,ARREADY,ARADDR,ARPROT,RVALID,RREADY,RDATA,RRESP))
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