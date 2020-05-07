#from bus import Bus
from ahblite import AHBlite
from apb import APB
import shutil

class SoC:
    busesObj=[]
    path=""
    info=""
    jsonObj={}
    
    # number of buses and components
    nbuses= None
    ncomponents = None
    
    #list of buses and list of compnents
    socBuses= None
    socComponents = None

    #dictionaries with key=bus_id and value=list of slaves/masters connected to bus_id
    busSlaves= {}
    busMasters= {}

    #Dictionary fwith key = bus_id and value= number of peripherials
    ip_count={}

    def __init__(self,jsonObj,path):
        
        self.jsonObj=jsonObj
        self.path=path

        self.info=self.getInfo(jsonObj)
       
        self.nbuses=len(jsonObj['soc']['buses'])
        self.ncomponents = len(jsonObj['soc']['components'])
        self.socBuses= jsonObj['soc']['buses']
        self.socComponents = jsonObj['soc']['components']

        self.getSlavesMasters()
        self.createBusObjects()


    def getInfo(self, jsondata):
        info = ("//Design: %s \n" %jsondata['design'])
        info+= ("//License: %d \n" %jsondata['license'])
        info+= ("//Version: %s \n" %jsondata['version'])
        info+= ("//Designer: %s \n" %jsondata['designer']['username'])
        info+= ("//Date: %d / %d / %d \n" % (jsondata['creation_date']['day'] , jsondata['creation_date']['month'] ,jsondata['creation_date']['year']))
        return info

    def getSlavesMasters(self):
        
        for i in range(self.ncomponents):
            #connection 1
            if self.socComponents[i]['connection_1']['connection_type'] == "SLAVE":
                self.busSlaves.setdefault(self.socComponents[i]['connection_1']['bus_id'], []).append(self.socComponents[i])
            elif self.socComponents[i]['connection_1']['connection_type'] == "MASTER":
                self.busMasters.setdefault(self.socComponents[i]['connection_1']['bus_id'], []).append(self.socComponents[i])
            
            #if there is a second connection
            if 'connection_2' in self.socComponents[i]:
                if self.socComponents[i]['connection_2']['connection_type'] == "SLAVE":
                    self.busSlaves.setdefault(self.socComponents[i]['connection_2']['bus_id'], []).append(self.socComponents[i])
                elif self.socComponents[i]['connection_2']['connection_type'] == "MASTER":
                    self.busMasters.setdefault(self.socComponents[i]['connection_2']['bus_id'], []).append(self.socComponents[i])
        
        for i in range(self.nbuses):
            self.ip_count[self.socBuses[i]['bus_id']] = len(self.busSlaves[self.socBuses[i]['bus_id']])
        
        print("\n\nIP COUNTS\n\n")
        print(self.ip_count)

        '''
        print("\n\n masters of buses\n")
        print(self.busMasters)
        print("\n\n")
        print("\n\n slaves of buses\n")
        print(self.busSlaves)
        print("\n\n")'''
    
    def createBusObjects(self):
        for i in range(self.nbuses):
            if self.socBuses[i]['bus_standard']== "AHB_lite":
                tempBus = AHBlite(self.socBuses[i], self.busMasters[self.socBuses[i]['bus_id']], self.busSlaves[self.socBuses[i]['bus_id']], self.info,self.path,self.ip_count)
                self.busesObj.append(tempBus)
                #print("\n\n")
                #self.busesObj[i].printBus()
                #print("\n\n")
            elif self.socBuses[i]['bus_standard']== "APB":
                temp=APB(self.socBuses[i], self.busMasters[self.socBuses[i]['bus_id']], self.busSlaves[self.socBuses[i]['bus_id']], self.info,self.path,self.ip_count)
                self.busesObj.append(temp)
    
    def generateVerilog(self):
        out= open(self.path+("/%s.v" %self.jsonObj['module_name']),"w+")
        ver = self.info+ "\n\n" + self.declareModule()
        
        for i in range(self.nbuses):
            ver+=self.busesObj[i].signals()

        for i in range(self.nbuses):
            ver+=self.busesObj[i].instantiation()
        
        for i in range(self.nbuses):
            self.busesObj[i].generate_subsystems()

        ver+="\nendmodule\n"

        out.write(ver)

        self.generate_components_modules()
        
    def declareModule(self):
        code= "`timescale 1ns/1ns\n\n"
        code+=("module %s(" %self.jsonObj['module_name'])

        #get global signals of components
        code+=self.components_globalSignals()

        gl=[]
        #get global signals of each bus
        for i in range(self.nbuses):
            gl.append(self.busesObj[i].globalSignal())

        for i in range(len(gl)):
            code+=gl[i]
            if i==len(gl)-1:
                code+=");\n"
            elif gl[i+1] != "":
                code+=",\n"
            '''if i==self.nbuses-1:
                code+=self.busesObj[i].globalSignal() + ");\n"
            else:
                code+=self.busesObj[i].globalSignal() + ",\n" '''     
        
        return code

    def components_globalSignals(self):
        ver=""
        for i in range(self.ncomponents):
            id=self.socComponents[i]['component_id']
            if self.socComponents[i]['component_type']=="ADC12":
                ver+=""
            elif self.socComponents[i]['component_type']=="gpio":
                ver+=("input wire [7:0] pin_in_%d,\noutput reg [7:0] pin_out_%d, pin_ddr_%d,\n" %(id, id, id))
            elif self.socComponents[i]['component_type']=="i2c_master":
                ver+=("input wire scl_i_%d, sda_i_%d,\noutput wire scl_o_%d, scl_oen_o_%d, sda_o_%d, sda_oen_o_%d,\n" %(id, id, id, id, id, id))
            elif self.socComponents[i]['component_type']=="spi":
                ver+=("input wire spi_miso_%d,\noutput wire spi_mosi_%d, spi_sck_%d,\n" %(id, id, id))
            elif self.socComponents[i]['component_type']=="timer0":
                ver+=("input wire timer_clk_%d,\noutput wire [2:0] timer_clk_sel_%d,\n" %(id, id))
            elif self.socComponents[i]['component_type']=="uart":
                ver+=("input uart_rx_%d,\noutput uart_tx_%d,\n" %(id, id))
        
        return ver 

    def generate_components_modules(self):
        for i in range(self.ncomponents):
            comp = self.socComponents[i]['component_type']
            if comp == 'SLAVE1':
                src="/Users/Home/Desktop/Mayada/Thesis/generator/components/slave_1.v"
                
                shutil.copy(src, self.path)

            elif comp== 'SLAVE2':
                src="/Users/Home/Desktop/Mayada/Thesis/generator/components/slave_2.v"
              
                shutil.copy(src, self.path)
            elif comp== 'SLAVE3':
                src="/Users/Home/Desktop/Mayada/Thesis/generator/components/slave_3.v"
             
                shutil.copy(src, self.path)
            elif comp=="gpio":
                src="/Users/Home/Desktop/Mayada/Thesis/generator/components/gpio.v"
            
                shutil.copy(src, self.path)
            elif comp=="i2c_master":
                src="/Users/Home/Desktop/Mayada/Thesis/generator/components/i2c_master.v"
      
                shutil.copy(src, self.path)

                src2="/Users/Home/Desktop/Mayada/Thesis/generator/components/i2c_master_defines.v"
            
                shutil.copy(src2, self.path)

                src3="/Users/Home/Desktop/Mayada/Thesis/generator/components/i2c_master_byte_ctrl.v"
            
                shutil.copy(src3, self.path)

                src4="/Users/Home/Desktop/Mayada/Thesis/generator/components/i2c_master_bit_ctrl.v"
           
                shutil.copy(src4, self.path)

                
            elif comp=="spi":
                src="/Users/Home/Desktop/Mayada/Thesis/generator/components/spi.v"
          
                shutil.copy(src, self.path)

                src2="/Users/Home/Desktop/Mayada/Thesis/generator/components/spi_transceiver.v"
         
                shutil.copy(src2, self.path)

            elif comp=="timer0":
                src="/Users/Home/Desktop/Mayada/Thesis/generator/components/timer0.v"
     
                shutil.copy(src, self.path)

                src2="/Users/Home/Desktop/Mayada/Thesis/generator/components/timescale.v"
     
                shutil.copy(src2, self.path)


            elif comp=="uart":
                src="/Users/Home/Desktop/Mayada/Thesis/generator/components/uart.v"
        
                shutil.copy(src, self.path)

                src2="/Users/Home/Desktop/Mayada/Thesis/generator/components/uart_transceiver.v"
          
                shutil.copy(src2, self.path)

            elif comp=="Master":
                src="/Users/Home/Desktop/Mayada/Thesis/generator/components/Master.v"
                shutil.copy(src, self.path)
            
            
        

    
    