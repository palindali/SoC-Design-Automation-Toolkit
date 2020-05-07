from bus import Bus
from ahblite_wrapper import AHBLite_wrapper

class AHBlite(Bus):

    def __init__(self, busInfo, master, components, info,filepath, ip_count):
        Bus.__init__(self,busInfo, master, components, info,filepath, ip_count)

    def globalSignal(self):
        return "input HCLK, HRESETn"

    def signals(self):
        #master signals
        ver="\n//master signals\n"
        ver+="wire [31:0] HADDR, HWDATA;\n"
        ver+="wire HWRITE, HMASTCLOCK;\n"
        ver+="wire [1:0] HTRANS;\n"
        ver+="wire [2:0] HSIZE, HBURST;\n"
        ver+="wire [3:0] HPROT;\n"

        #slave signals
        for i in range(self.slavesNum):
            ver+=("\n//AHB-lite slave %d signals\n" %(i))
            ver+=("wire [31:0] HRDATA_%d;\n" %(i))
            ver+=("wire HREADYOUT_%d, HRESP_%d;\n" %(i, i))
        
        #default slave signals
        ver+=("\n//default slave signals\n")
        ver+=("wire [31:0] HRDATA_DF;\n")
        ver+=("wire HREADYOUT_DF, HRESP_DF;\n")

        #decoder signals
        ver+="\n//decoder signals\n"
        ver+="wire "
        for i in range(self.slavesNum):
            ver+=("HSEL_%d, " %(i))
        ver+="HSEL_DF;\n"

        #mux signals
        ver+="\n//mux signals\n"
        ver+="wire [31:0] HRDATA;\n"
        ver+="wire HREADY, HRESP;\n"

        return ver

    def instantiation(self):
        
        #Master instantiation
        ver="\n//Master Instantiation\n"
        #ver+=("%s uut(HRDATA, HREADY, HRESP, HCLK, HRESETn, HWRITE, HMASTCLOCK, HADDR, HWDATA, HPROT, HSIZE, HBURST, HTRANS);\n" %self.master[0]['component_type'])
        ver+=self.AHBlite_MasterInst(self.master[0],"HREADY","HRESP","HRESETn","HCLK","HRDATA","HADDR","HWRITE","HSIZE","HBURST","HPROT","HTRANS","HMASTCLOCK","HWDATA")

        #Decoder instantiation
        ver+="\n//Decoder instantiation\n"
        ver+="decoder_AHBlite dec(HADDR, "
        for i in range(self.slavesNum):
            ver+=("HSEL_%d, "%(i))
        ver+="HSEL_DF);\n"

        #Multiplexer instantiation
        ver+="\n//Multipleser instantiation\n"
        ver+="multiplexer_AHBlite mux( HRDATA, HREADY, HRESP, "
        for i in range(self.slavesNum):
            ver+=("HRDATA_%d, " %(i))
        ver+="HRDATA_DF, HCLK, HRESETn, "
        for i in range(self.slavesNum):
            ver+=("HREADYOUT_%d, " %(i))
        ver+="HREADYOUT_DF, "
        for i in range(self.slavesNum):
            ver+=("HRESP_%d, " %(i))
        ver+="HRESP_DF, "
        for i in range(self.slavesNum):
            ver+=("HSEL_%d, " %(i))
        ver+="HSEL_DF);\n"

        #Slaves instantiations
        for i in range(self.slavesNum):
            ver+=("\n//Slave %d Instantiation\n" %i)
            #ver+=("%s uut%d(HRDATA_%d, HREADYOUT_%d, HRESP_%d, HWRITE, HMASTCLOCK, HSEL_%d, HREADY, HADDR, HWDATA, HPROT, HSIZE, HBURST, HTRANS);\n" %(self.components[i]['component_type'],x,x,x,x,x))
            ver+=self.AHBlite_SlaveInst(self.components[i],("uut%d" %self.components[i]['component_id']),("HSEL_%d" %i), "HADDR","HWRITE","HSIZE","HBURST","HPROT","HTRANS","HMASTCLOCK","HREADY","HWDATA","HRESETn","HCLK",("HREADYOUT_%d" %i),("HRESP_%d" %i),("HRDATA_%d" %i))
        ver+="\n//Default Slave Instantiation\n"
        ver+="slave_default uutDF(HRDATA_DF, HREADYOUT_DF, HRESP_DF, HWRITE, HMASTCLOCK, HSEL_DF, HREADY, HRESETn, HADDR, HWDATA, HPROT, HSIZE, HBURST, HTRANS);\n" 

        return ver

    def generate_subsystems(self):
        self.Generate_AHBlite_DefaultSlave()
        self.Generate_AHBlite_Decoder()
        self.Generate_AHBlie_Mux()

    def Generate_AHBlite_DefaultSlave(self):
        f= open(self.filepath + "/salve_default.v","w+")
        st=self.info
        st+="\n\nmodule slave_default(output reg [31:0] HRDATA,\n"
        st+="output reg [0:0] HREADYOUT, HRESP,\n"
        st+="input HWRITE,HMASTCLOCK,HSEL,HREADY,reset,\n"
        st+="input [31:0] HADDR, HWDATA,\n"
        st+="input [3:0] HPROT,\n"
        st+="input [2:0] HSIZE,HBURST,\n"
        st+="input [1:0] HTRANS);\n"
        st+="always@(posedge(HMASTCLOCK) or posedge(reset))begin\n"
        st+="if(reset==1)\n"
        st+="   HRESP<=1;\n"
        st+="else if(HSEL & HREADY) begin\n"
        st+="   HREADYOUT<=0;\n"
        st+="	HRESP<=1;\n"
        st+="	HRDATA	<=32'hFFFFFFFF;\n"
        st+="end\n"
        st+="else if(HRESP & (~HREADY))begin\n"
        st+="   HREADYOUT<=1;\n"
        st+="   HRESP<=1;\n"
        st+="end\n"
        st+="else if(HRESP & HREADY)\n"
        st+="   HRESP<=0;\n"
        st+="else begin\n"
        st+="   HREADYOUT<=1;\n"
        st+="   HRESP<=0;\n"
        st+="end\nend\nendmodule"
        
        f.write(st)
    
    def Generate_AHBlie_Mux(self):
        f= open(self.filepath+"/multiplexer_AHBlite.v","w+")
        
        ver=self.info+"\n\n"
        ver+="module multiplexer_AHBlite(\noutput reg [31:0] HRDATA,\noutput reg [0:0] HREADY, HRESP,\n"
        
        ver+="input [31:0] "
        for i in range(self.slavesNum):
            ver+=("HRDATA_%d, " %(i))
        ver+="HRDATA_DF,\n"
        
        ver+="input HCLK, HRESETn, "
        
        for i in range(self.slavesNum):
            ver+=("HREADYOUT_%d, " %(i))
        ver+="HREADYOUT_DF, "
        
        for i in range(self.slavesNum):
            ver+=("HRESP_%d, " %(i))
        ver+="HRESP_DF, \n"
        
        ver+="input "
        for i in range(self.slavesNum):
            ver+=("HSEL_%d, " %(i))
        ver+="HSEL_DF);\n\n"

        ver+="reg [0:0] "
        for i in range(self.slavesNum):
            ver+=("HSEL_%dn, " %(i))
        ver+="HSEL_DFn;\n\n"

        ver+="always @ (posedge(HCLK), posedge(HRESETn))\n"
        ver+="begin\n\tif(HRESETn==1) begin\n"
        for i in range(self.slavesNum):
            ver+=("\t\tHSEL_%dn<=0;\n" %(i))
        ver+="\t\tHSEL_DFn<=0;\n"
        ver+="end\n"
        ver+="\telse begin\n"
        ver+="\t\tif(HREADY)begin\n"
        for i in range(self.slavesNum):
            ver+=("\t\t\tHSEL_%dn<=HSEL_%d;\n" %(i,i))
        ver+="\t\t\tHSEL_DFn<=HSEL_DF;\n"
        ver+="\t\tend\n\tend\nend\n"
        ver+="always @(*)\nbegin\n\t"
        for i in range(self.slavesNum):
            ver+=("if(HSEL_%dn)\tbegin\n\t\tHRDATA<=HRDATA_%d;\n\t\tHREADY<=HREADYOUT_%d;\n\t\tHRESP<=HRESP_%d;\n\tend\n" %(i,i,i,i))
            ver+="\telse "
        ver+="if(HSEL_DFn)begin\n\t\tHRDATA<=HRDATA_DF;\n\t\tHREADY<=HREADYOUT_DF;\n\t\tHRESP<=HRESP_DF;\n\tend\n"
        ver+="\telse if(HRESETn)begin\n\t\tHREADY<=1;\n\tend\n\telse begin\n\t\tHREADY<=1;\n\tend\n"
        ver+="end\nendmodule"

        f.write(ver)

    def Generate_AHBlite_Decoder(self):
        f= open(self.filepath+"/decoder_AHBlite.v","w+")
        ver=self.info+"\n\n"
        ver+="module decoder_AHBlite( input [31:0] HADDR,\n"
        ver+="output reg [0:0] "
        for i in range(self.slavesNum):
            ver+=("HSEL_%d, " %(i))
        ver+= "HSEL_DF);\n"
        ver+="wire [7:0] Base_Addr;\nassign Base_Addr= HADDR[31:24];\n"
        ver+="always@(Base_Addr)begin\n"
        for i in range(self.slavesNum):
            ver+=("\tHSEL_%d<=0;\n" %(i))
        ver+="\tHSEL_DF<=0;\n"
        ver+="\tcase (Base_Addr)\n"
        for i in range (self.slavesNum):
            ver+=("\t\t8'h%s:\n\t\t\tHSEL_%d<=1;\n" %(self.components[i]['base'][2:][:2],i))
        ver+="\t\tdefault:\n\t\t\tHSEL_DF<=1;\n"
        ver+="\t\tendcase\n\tend\nendmodule"

        f.write(ver)
        f.close()


    def AHBlite_SlaveInst(self, component, instName, HSEL,HADDR,HWRITE,HSIZE,HBURST,HPROT,HTRANS,HMASTLOCK,HREADY,HWDATA,HRESETn,HCLK,HREADYOUT,HRESP,HRDATA):
        ver=""
        
        #Dummy slaves
        if component['component_type']== 'SLAVE1':
            ver+=("slave_1 %s ( .HRDATA(%s), .HREADYOUT(%s), .HRESP(%s), .HWRITE(%s), .HMASTCLOCK(%s), .HSEL(%s), .HREADY(%s), .HADDR(%s), .HWDATA(%s), .HPROT(%s), .HSIZE(%s), .HBURST(%s), .HTRANS(%s));\n" %(instName, HRDATA, HREADYOUT, HRESP, HWRITE, HMASTLOCK, HSEL, HREADY, HADDR, HWDATA, HPROT, HSIZE, HBURST, HTRANS))
        elif component['component_type']== 'SLAVE2':
            ver+=("slave_2 %s ( .HRDATA(%s), .HREADYOUT(%s), .HRESP(%s), .HWRITE(%s), .HMASTCLOCK(%s), .HSEL(%s), .HREADY(%s), .HADDR(%s), .HWDATA(%s), .HPROT(%s), .HSIZE(%s), .HBURST(%s), .HTRANS(%s));\n" %(instName, HRDATA, HREADYOUT, HRESP, HWRITE, HMASTLOCK, HSEL, HREADY, HADDR, HWDATA, HPROT, HSIZE, HBURST, HTRANS))
        elif component['component_type']== 'SLAVE3':
            ver+=("slave_3 %s ( .HRDATA(%s), .HREADYOUT(%s), .HRESP(%s), .HWRITE(%s), .HMASTCLOCK(%s), .HSEL(%s), .HREADY(%s), .HADDR(%s), .HWDATA(%s), .HPROT(%s), .HSIZE(%s), .HBURST(%s), .HTRANS(%s));\n" %(instName, HRDATA, HREADYOUT, HRESP, HWRITE, HMASTLOCK, HSEL, HREADY, HADDR, HWDATA, HPROT, HSIZE, HBURST, HTRANS))
        
        #APB bridge
        elif component['component_type']== 'ahblite_to_apb':
            ahblite_id=self.busInfo['bus_id']
            apb_id=None

            if ahblite_id==component['connection_1']['bus_id']:
                apb_id=component['connection_2']['bus_id']
            elif ahblite_id==component['connection_2']['bus_id']:
                apb_id=component['connection_1']['bus_id']
            ips=self.ip_count[apb_id]
            
            #Module instantioation
            ver+=("ahblite_to_apb %s " %instName)

            #AHBLite signals
            ver+=("(.HCLK(%s), .HRESETn(%s), .HMASTLOCK(%s), .HSEL(%s), .HADDR(%s), .HTRANS(%s), .HSIZE(%s), .HWRITE(%s), .HPROT(%s), .HREADY(%s), .HWDATA(%s), .HREADYOUT(%s), .HRDATA(%s), .HRESP(%s), " %(HCLK, HRESETn, HMASTLOCK, HSEL, HADDR, HTRANS, HSIZE, HWRITE, HPROT, HREADY, HWDATA, HREADYOUT, HRDATA, HRESP))
            #APB signals
            ver+=(".PADDR(PADDR%d), .PENABLE(PENABLE%d), .PWRITE(PWRITE%d), .PWDATA(PWDATA%d), " %(apb_id, apb_id, apb_id, apb_id))
            
            for i in range(ips):
                if i==ips-1:
                    ver+=(".PSEL%d(PSEL%d_%d), .PRDATA%d(PRDATA%d_%d), .PSLVERR%d(PSLVERR%d_%d));\n" %(i, apb_id, i, i, apb_id, i, i, apb_id,i))
                else:
                    ver+=(".PSEL%d(PSEL%d_%d), .PRDATA%d(PRDATA%d_%d), .PSLVERR%d(PSLVERR%d_%d), " %(i, apb_id, i, i, apb_id, i, i, apb_id,i))

        #IPs need wrappers
        else:
            wrapper = AHBLite_wrapper(component,self.filepath,self.info)
            wrapper.generateWrapper()
            ver+=wrapper.instantion(instName,"HCLK","HRESETn",HADDR,HBURST,HMASTLOCK,HPROT,HSIZE,HTRANS,HWDATA,HWRITE,HRDATA,HREADYOUT,HRESP,HSEL,HREADY)
        return ver
    
    def AHBlite_MasterInst(self, master, HREADY, HRESP, HRESETn, HCLK, HRDATA, HADDR, HWRITE, HSIZE, HBURST, HPROT, HTRANS, HMASTLOCK, HWDATA):
        ver=""
        if master['component_type']=="CPU":
            ver+=("Master master%d ( .HRDATA(%s), .HREADY(%s), .HRESP(%s), .clk(%s), .reset(%s), .HWRITE(%s), .HMASTCLOCK(%s), .HADDR(%s), .HWDATA(%s), .HPROT(%s), .HSIZE(%s), .HBURST(%s), .HTRANS(%s));\n" %(master['component_id'], HRDATA, HREADY, HRESP, HCLK, HRESETn, HWRITE, HMASTLOCK, HADDR, HWDATA, HPROT, HSIZE, HBURST, HTRANS))
        
        return ver

    
