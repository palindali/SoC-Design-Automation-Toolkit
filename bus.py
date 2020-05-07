class Bus:
    busInfo ={}
    master={}
    components = {}
    info=str()
    slavesNum = None
    filepath=""
    ip_count={}

    def __init__(self, busInfo, master, components, info,filepath,ip_count):
        self.busInfo=busInfo
        self.master=master
        self.components=components
        self.info=info
        self.slavesNum=len(self.components)
        self.filepath=filepath
        self.ip_count=ip_count

    def globalSignal(self):
        pass

    def signals(self):
        pass

    def instantiation(self):
        pass

    def generate_subsystems(self):
        pass
    
    


    def printBus(self):
        print("\n",self.info,"\n")
        print("\n",self.busInfo,"\n")
        print("\n",self.master,"\n")
        print("\n",self.components,"\n")