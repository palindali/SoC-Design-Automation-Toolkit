from bus import Bus
from apb_wrapper import APB_wrapper

class APB(Bus):
    
    PCLK = None
    PRESENTn = None
    PADDR = None
    PSEL = None
    PENABLE = None
    PWRITE = None
    PWDATA = None
    PREADY = None
    PRDATA = None
    PSLVERR = None


    def __init__(self, busInfo, master, components, info,filepath, ip_count):
        Bus.__init__(self, busInfo, master, components, info,filepath, ip_count)
        self.PCLK = ("PCLK%d" %self.busInfo['bus_id'])
        self.PRESENTn = ("PRESETn%d" %self.busInfo['bus_id'])
        self.PADDR = ("PADDR%d" %self.busInfo['bus_id'])
        self.PSEL = ("PSEL%d" %self.busInfo['bus_id'])
        self.PENABLE = ("PENABLE%d" %self.busInfo['bus_id'])
        self.PWRITE = ("PWRITE%d" %self.busInfo['bus_id'])
        self.PWDATA = ("PWDATA%d" %self.busInfo['bus_id'])
        self.PREADY = ("PREADY%d" %self.busInfo['bus_id'])
        self.PRDATA = ("PRDATA%d" %self.busInfo['bus_id'])
        self.PSLVERR = ("PSLVERR%d" %self.busInfo['bus_id'])

    def signals(self):
        ver=("\n//APB bridge (id_bus=%d) signals\n" %self.busInfo['bus_id'])
        ver+=("//Bridge Signals\n")
        ver+=("wire [31:0] %s, %s, %s;\n" %(self.PADDR, self.PWDATA, self.PRDATA))
        ver+=("wire %s, %s, %s, %s, %s, %s;\n" %(self.PCLK, self.PRESENTn, self.PENABLE, self.PWRITE, self.PREADY, self.PSLVERR))
        
        for i in range(self.slavesNum):
            ver+=("\n//APB Slave %d signals\n" %i)
            ver+=("wire %s_%d, %s_%d, %s_%d;\n" %(self.PSEL, i, self.PREADY, i, self.PSLVERR, i))
            ver+=("wire [31:0] %s_%d;\n " %(self.PRDATA,i))
        
        return ver

    def instantiation(self):
        
        ver=""

        #Slaves instantiation
        for i in range(self.slavesNum):
            ip_name= self.components[i]['component_type']
            ver+=("\n//%s Instantiation\n" %ip_name)

            wrapper= APB_wrapper(self.components[i],self.filepath,self.info)
            wrapper.generateWrapper()
            ver+=wrapper.instantion(("uut%d" %(self.components[i]["component_id"])),self.PCLK,"",self.PRESENTn,("%s_%d" %(self.PSEL, i)),self.PADDR, self.PENABLE, self.PWRITE, self.PWDATA,("%s_%d" %(self.PRDATA, i)),("%s_%d" %(self.PREADY, i)), ("%s_%d" %(self.PSLVERR, i)))
            
        return ver

    def globalSignal(self):
        return ""

    def generate_subsystems(self):
        self.generate_ahblite_to_apb()

    '''def generate_APB_Bridge(self, fromBus):
        if fromBus == "AHB_lite":
            self.generate_ahblite_to_apb()'''

    def generate_APB_DefaultSlave(self):
        pass

    def generate_ahblite_to_apb(self):
        
        id=self.busInfo['bus_id']

        f= open(self.filepath+("/ahblite_to_apb%d.v" %id),"w+")
        
        ver=self.info+"\n\n"
        ver+="// Simple AHB to APB bridge\n\n"
        
        #defining states of FSM
        ver+="`define IDLE    3'b000\n`define ACCESS  3'b001\n`define SETUP   3'b010\n`define OKAY    3'b011\n`define ERR1    3'b100\n`define ERR2    3'b101\n"
        #defining the module
        ver+=("module ahblite_to_apb%d(" %id)
        
        #AHB-lite signals
        ver+="\tinput  wire HCLK,    // Clock\n\tinput  wire HRESETn, //Reset\n"
        ver+="\tinput  wire         HSEL, //Device select\n\tinput  wire  [23:0] HADDR,   // Address\n\tinput  wire         HMASTLOCK,  // Master lock\n\tinput  wire  [1:0]  HTRANS,  // Transfer control\n\tinput  wire  [2:0]  HSIZE,   // Transfer size\n\tinput  wire         HWRITE,  // Write control\n"
        ver+="\tinput  wire  [6:0]  HPROT,   // Protection information\n\tinput  wire         HREADY,  // Transfer phase done\n\tinput  wire  [31:0] HWDATA,  // Write data\n\toutput wire         HREADYOUT, // Device ready\n\toutput wire  [31:0] HRDATA,\n\toutput wire         HRESP,\n\n"
        
        #APB signals
        ver+="\toutput wire  [11:0] PADDR,\n\toutput wire         PENABLE,\n\toutput wire         PWRITE,\n\toutput wire  [3:0]  PSTRB,\n\toutput wire  [31:0] PWDATA,\n\n"
        
        for i in range(self.slavesNum):
            ver+=("\toutput wire         PSEL%d,\n" %i)

        ver+"\n"
        for i in range(self.slavesNum):
            ver+=("\tinput wire [31:0]   PRDATA%d,\n" %i)
        
        ver+="\n"
        for i in range(self.slavesNum):
            ver+=("\tinput wire         PREADY%d,\n" %i)

        ver+="\n"
        for i in range(self.slavesNum):
            if i== self.slavesNum-1:
                ver+=("\tinput wire         PSLVERR%d);\n" %i)
            else:
                ver+=("\tinput wire         PSLVERR%d,\n" %i)

        #registers needed
        ver+="reg  [11:2] AddrReg; // Address sample register\nreg   [2:0] SelReg; // One-hot PSEL output register\nreg         WrReg; // Write control sample register\nreg   [2:0] StateReg;// State for finite state machine\nwire        ApbSelect; //APB bridge is selected\nwire        ApbTranEnd; // Transfer is completed on APB\nwire        AhbTranEnd; //Transfer is completed on AHB\n"
        ver+=("reg   [%d:0] NextPSel; //Next state of One-Hoy PSEL\n" %(self.slavesNum-1))
        ver+="reg   [2:0] NextState; // Next state for finite state machine\nreg  [31:0] RDataReg;\nwire  [31:0]  muxPRDATA;  // Slave multiplexer signal\nwire          muxPREADY;\nwire          muxPSLVERR;\n"

        #Main code start
        ver+="// Start of main code\n"
        ver+="// Generate APB bridge select\n"
        ver+="assign    ApbSelect = HSEL & HTRANS[1] & HREADY;\n"
        ver+="// Generate APB transfer ended\n"
        ver+="assign    ApbTranEnd = (StateReg==SETUP) & muxPREADY;\n"
        ver+="// Generate AHB transfer ended\n"
        ver+="assign    AhbTranEnd = (StateReg==OKAY) | (StateReg==ERR2);\n"

        #Generate next state of PSEL at each AHB transfer
        ver+"// Generate next state of PSEL at each AHB transfer\n"
        ver+="always @(ApbSelect or HADDR)\nbegin\n"
        ver+="if (ApbSelect)\n\tbegin\n"
        ver+="\tcase (HADDR[23:12]) // Binary to one-hot encoding for device select\n"
        for i in range(self.slavesNum):
            ver+=("\t12’h%s : NextPSel = %d’b%s%d;\n" %(self.components[i]['base'][4:][:3],self.slavesNum,"0"*(self.slavesNum-i-1),10**i))
        ver+=("\tdefault: NextPSel = %d’b%s;\n" %(self.slavesNum, "0"*self.slavesNum))
        ver+="\tendcase\n\tend\n"
        ver+=("else\n\tNextPSel = %d’b%s;\nend\n" %(self.slavesNum, "0"*self.slavesNum))

        #Registering PSEL output
        ver+="// Registering PSEL output\nalways @(posedge HCLK or negedge HRESETn)\nbegin\nif (~HRESETn)\n"
        ver+="\tSelReg <= 3’b000;\nelse if (HREADY|ApbTranEnd)\n\tSelReg <= NextPSel; // Set if bridge is selected\nend                   // Clear at end of APB transfer\n"
        
        #Sample control signals
        ver+="// Sample control signals\nalways @(posedge HCLK or negedge HRESETn)\nbegin\nif (~HRESETn)\n\tbegin\n\tAddrReg <= {10{1’b0}};\n\tWrReg   <= 1’b0;\n\n\tend\nelse if (ApbSelect) // Only change at beginning of each APB transfer\n\tbegin\n\tAddrReg <= HADDR[11:2]; // Note that lowest two bits are not used\n\tWrReg   <= HWRITE;\n\n\tend\nend\n"
        
        #Generate next state for FSM
        ver+="// Generate next state for FSM\n"
        ver+="always @(StateReg or muxPREADY or muxPSLVERR or ApbSelect)\nbegin\ncase (StateReg)\n"
        ver+=" IDLE : NextState = {1’b0, ApbSelect}; // Change to state-1 when selected\n"
        ver+=" ACCESS : NextState = 3’b010;            // Change to state-2\n"
        ver+=" SETUP : begin\n          if (muxPREADY & muxPSLVERR) // Error received - Generate two cycle\n                                // Error response on AHB by\n            NextState = ERR1; // Changing to state-4 and 5\n          else if (muxPREADY & ~muxPSLVERR) // Okay received\n            NextState = OKAY; // Generate okay response in state 3\n          else // Slave not ready\n            NextState = SETUP; // Unchange\n          end\n"
        ver+="  OKAY : NextState = {1’b0, ApbSelect}; // Terminate transfer\n"
        ver+="// Change to state-1 if selected\n  ERR1 : NextState = 3’b101;   // Goto 2nd cycle of error response\n"
        ver+="  ERR2 : NextState = {1’b0, ApbSelect}; // 2nd Cycle of Error response\n"
        ver+="default : // Not used\n// Change to state-1 if selected\n          NextState = {1’b0, ApbSelect}; // Change to state-1 when selected\n"
        ver+="endcase\nend\n"

        #Registering state machine
        ver+="// Registering state machine\nalways @(posedge HCLK or negedge HRESETn)\nbegin\nif (~HRESETn)\n\tStateReg <= 3’b000;\nelse\n\tStateReg <= NextState;\nend\n"

        #Slave Mux
        ver+="// Slave Multiplexer\n"
        ver+="assign muxPRDATA = "
        for i in range(self.slavesNum):
            if i == self.slavesNum-1:
                ver+=("({32{SelReg[%d]}} & PRDATA%d) ;\n" %(i,i))
            else:
                ver+=("({32{SelReg[%d]}} & PRDATA%d) |\n" %(i,i))

        ver+="assign muxPREADY = "
        for i in range(self.slavesNum):
            if i == self.slavesNum-1:
                ver+=("(SelReg[%d] & PREADY%d) ;\n" %(i,i))
            else:
                ver+=("(SelReg[%d] & PREADY%d) |\n" %(i,i))

        ver+="assign muxPSLVERR = "
        for i in range(self.slavesNum):
            if i == self.slavesNum-1:
                ver+=("(SelReg[%d] & PSLVERR%d) ;\n" %(i,i))
            else:
                ver+=("(SelReg[%d] & PSLVERR%d) |\n" %(i,i))
        
        #Sample PRDATA
        ver+="// Sample PRDATA\nalways @(posedge HCLK or negedge HRESETn)\nbegin\nif (~HRESETn)\n\tRDataReg <= {32{1’b0}};\nelse if (ApbTranEnd|AhbTranEnd)\n\tRDataReg <= muxPRDATA;\nend\n"
        

        ver+="// Connect outputs to top level\n"
        ver+="assign PADDR  = {AddrReg[11:2], 2’b00}; // from sample register\n"
        ver+="assign PWRITE = WrReg;    // from sample register\n"
        ver+="assign PWDATA = HWDATA;  // No need to register (HWDATA is in data phase)\n"
        ver+="// PSEL for each APB slave\n"

        for i in range(self.slavesNum):
            ver+=("assign PSEL%d  = SelReg[%d];\n" %(i,i))
        ver+="assign PENABLE= (StateReg == SETUP); // PENABLE to all AHB slaves\n"
        ver+="assign HREADYOUT = (StateReg == IDLE)|(StateReg == OKAY)|(StateReg==ERR2);\n"
        ver+="assign HRDATA = RDataReg;\n"
        ver+="endmodule\n"
        
        f.write(ver)
        f.close()




