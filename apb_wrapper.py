from wrapper import Wrapper

class APB_wrapper(Wrapper):
    
    def __init__(self,component,path,info):
        Wrapper.__init__(self,component,path,info)
        self.name+="_APB_wrapper"

    def generateWrapper(self):
        Wrapper.generateWrapper(self)
  
    def module_Signals(self):
        ver=""
        #APB signals
        ver+="\n//APB signals\n"
        ver+="\tinput  wire        PCLK,\n\tinput  wire        PCLKG,\n\tinput  wire        PRESETn,\n\tinput  wire        PSEL,\n\tinput  wire [11:2] PADDR,\n\tinput  wire        PENABLE,\n\tinput  wire        PWRITE,\n\tinput  wire [31:0] PWDATA,\n\toutput wire [31:0] PRDATA,\n\toutput wire        PREADY,\n\toutput wire        PSLVERR,\n"

        return ver

    def map_Signals(self):
        ver=""
        ver+= "assign  rd_enable  = PSEL & (~PWRITE);\nassign  wr_enable = PSEL & PWRITE & (~PENABLE);\n"
        ver+="assign PREADY = 1'b1;\nassign PSLVERR= 1'b0;\n"
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
                    ver+=("wire %s_select = wr_enable & (PADDR[11:2] == 10'd%d);\n" %(name, offeset))
                    ver+="always @(posedge PCLK or negedge PRESETn)\nbegin\n\tif (~PRESETn)\n"
                    ver+=("\t\t%s <= %d'h0;\n" %(name,size))
                    ver+=("\telse if (%s_select)\n" %name)
                    ver+=("\t\t%s <= PWDATA;\nend\n" %name)

        #input assignment
        ver+="\n//Read\n"
        ver+="assign PRDATA = \n"
        for i in range(len(self.regs)):
            name=self.regs[i]['name']
            size=self.regs[i]['size']
            offeset=int(self.regs[i]['offset'])
            ver+=("\t(PADDR[11:2] == 10'd%d) ? {%d'd0,%s} :\n"%(offeset, (32-size),name))
        ver+="\t32'hDEADBEEF;\n"

        return ver

    def instantion(self, instname,PCLK,PCLKG,PRESETn,PSEL,PADDR,PENABLE,PWRITE,PWDATA,PRDATA,PREADY, PSLVERR):
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
        ver+=(".PCLK(%s), .PCLKG(%s), .PRESETn(%s), .PSEL(%s), .PADDR(%s), .PENABLE(%s), .PWRITE(%s), .PWDATA(%s), .PRDATA(%s), .PREADY(%s), .PSLVERR(%s)" %(PCLK,PCLKG,PRESETn,PSEL,PADDR,PENABLE,PWRITE,PWDATA,PRDATA,PREADY, PSLVERR))

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

    
