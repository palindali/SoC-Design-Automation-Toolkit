class Wrapper:
    name=None
    description=None
    regs=None
    path=None
    info=None
    ip_type=None
    ip_id=None
    clk=None
    reset=None
    irqs=None

    def __init__(self,component,path, info):
        self.name=component['component_type']
        self.description=component['description']
        self.regs=component['regs']
        self.path=path
        self.info=info
        self.ip_type=component['component_type']
        self.ip_id=component['component_id']
        self.irqs=component['irqs']
        

    def generateWrapper(self):
        f= open(self.path+("/%s.v" %self.name),"w+")
        
        ver=""
        ver += self.info
        ver+= "\n\n"
        
        #declare module name
        ver+=("module %s( \n" %self.name)
        
        #declare module bus signals
        ver+=self.module_Signals()
        
        #declare module registers
        ver+=self.module_regs()
        
        #map bus signals
        ver+= self.map_Signals()
        
        #register and wire
        ver+= self.registers_wires()
        
        #read and write assignments
        ver+= self.IO_assignments()
        
        ver+="endmodule"

        f.write(ver)

        f.close()
    
    def module_Signals(self):
        pass
    
    def map_Signals(self):
        pass

    def module_regs(self):
        ver=""

        #registers
        ver+="\n//IP signals\n"
        for i in range(len(self.regs)):
            name=self.regs[i]['name']
            size=self.regs[i]['size']
            io= "input" if self.regs[i]['access']==1 else "output"

            #registers with fields
            if 'fields' in self.regs[i]:
                for j in range(len(self.regs[i]['fields'])):
                    field_name=self.regs[i]['fields'][j]['name']
                    field_size=self.regs[i]['fields'][j]['size']
                    ver+=("\t%s [%d:0] %s_%s" %(io, field_size-1, name, field_name))
                    if i== len(self.regs)-1 and j==len(self.regs[i]['fields'])-1 :
                        ver+=");\n\n"
                    else:
                        ver+=",\n"
            #registers without fields
            else:
                ver+=("\t%s [%d:0] %s" %(io, size-1, name))        
                if i== len(self.regs)-1:
                    ver+=");\n\n"
                else:
                    ver+=",\n"

        return ver
    
    def registers_wires(self):
        ver=""
        #output registers
        for i in range(len(self.regs)):
            if self.regs[i]['access']==0:
                #register
                name=self.regs[i]['name']
                size=self.regs[i]['size']
                ver+=("\n//Register: %s\n" %name)
                ver+=("reg [%d:0] %s;\n" %(size-1,name))

                #its fields
                if 'fields' in self.regs[i]:
                    for j in range(len(self.regs[i]['fields'])):
                        field_name=self.regs[i]['fields'][j]['name']
                        field_size=self.regs[i]['fields'][j]['size']
                        field_offset=int(self.regs[i]['fields'][j]['offset'])
                        ver+=("assign %s_%s = %s [%d:%d];\n" %(name, field_name, name, field_offset+field_size-1,field_offset))
        #input wires
        for i in range(len(self.regs)):
            if self.regs[i]['access']==1:
                if 'fields' in self.regs[i]:
                    #register
                    name=self.regs[i]['name']
                    size=self.regs[i]['size']
                    ver+=("\n//Register: %s\n" %name)
                    ver+=("wire [%d:0] %s;\n" %(size-1,name))
                    for j in range(len(self.regs[i]['fields'])):
                        #its fields
                        field_name=self.regs[i]['fields'][j]['name']
                        field_size=self.regs[i]['fields'][j]['size']
                        field_offset=int(self.regs[i]['fields'][j]['offset'])
                        ver+=("assign %s_%s = %s [%d:%d];\n" %(name, field_name, name, field_offset+field_size-1,field_offset))
                    
        return ver

    def IO_assignments(self):
        pass

    def instantion(self):
        pass

    def ip_registers_wires(self):
        id=self.ip_id
        ver=""
        ver+="//IP and Wrapper interface\n"

        for i in range(len(self.regs)):
            name=self.regs[i]['name']
            size=self.regs[i]['size']
            #registers with fields
            if 'fields' in self.regs[i]:
                for j in range(len(self.regs[i]['fields'])):
                    field_name=self.regs[i]['fields'][j]['name']
                    field_size=self.regs[i]['fields'][j]['size']
                    ver+=("wire [%d:0] %s_%s_%d;\n" %(field_size-1, name, field_name,id))
            #registers without fields
            else:
                ver+=("wire [%d:0] %s_%d;\n" %(size-1, name,id))    

        return ver

    def ip_registers_signals(self):
        id=self.ip_id
        
        ver=""

        for i in range(len(self.regs)):
            name=self.regs[i]['name']
            size=self.regs[i]['size']
            #registers with fields
            if 'fields' in self.regs[i]:
                for j in range(len(self.regs[i]['fields'])):
                    field_name=self.regs[i]['fields'][j]['name']
                    field_size=self.regs[i]['fields'][j]['size']
                    ver+=(".%s_%s(%s_%s_%d), " %(name, field_name,name, field_name,id))
            #registers without fields
            else:
                ver+=(".%s(%s_%d), " %(name,name,id))  

        return ver

    def ip_irqs_wires(self):
        ver=""
        ver+=("//%s irqs wire\n" %self.ip_type)
        for i in range(len(self.irqs)):
            ver+=("wire %s_%d;\n" %(self.irqs[i]['reg'], self.ip_id))

        return ver

    def ip_irqs_signals(self):
        ver=""
        for i in range(len(self.irqs)):
            ver+=(".%s(%s_%d), " %(self.irqs[i]['reg'],self.irqs[i]['reg'], self.ip_id))
        
        return ver
    
    def ip_instantiation(self):
        id= self.ip_id
        
        ver=""
        #ip module instantiation
        ver+=("%s %s_%d (" %(self.ip_type, self.ip_type, self.ip_id))
        
        #registers signals
        ver+=self.ip_registers_signals()

        #irqs signals
        ver+=self.ip_irqs_signals()

        #clk, reset and IO pins signals
        if self.ip_type=="ADC12":
            ver+=("")
        elif self.ip_type=="gpio":
            ver+=(".sys_clk(%s), .sys_rst(%s), .pin_in(pin_in_%d), .pin_out(pin_out_%d), .pin_ddr(pin_ddr_%d)" %(self.clk, self.reset, id, id, id))
        elif self.ip_type=="i2c_master":
            ver+=(".scl_i(scl_i_%d), .scl_o(scl_o_%d), .scl_oen_o(scl_oen_o_%d), .sda_i(sda_i_%d), .sda_o(sda_o_%d), .sda_oen_o(sda_oen_o_%d)" %(id, id, id, id, id, id))
        elif self.ip_type=="spi":
            ver+=(".spi_miso(spi_miso_%d), .spi_mosi(spi_mosi_%d), .spi_sck(spi_sck_%d)" %(id, id, id))
        elif self.ip_type=="timer0":
            ver+=(".timer_clk(timer_clk_%d), .timer_clk_sel(timer_clk_sel_%d)" %(id, id))
        elif self.ip_type=="uart":
            ver+=(".uart_rx(uart_rx_%d), .uart_tx(uart_tx_%d)" %(id, id))

        ver+=");\n"
        return ver


    

