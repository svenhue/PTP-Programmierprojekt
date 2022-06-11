from pickle import FALSE
from opcua import Server, ua, uamethod
from opcua.common.manage_nodes import create_method
from simulation import MController

  
server = Server()

    # opcua server setup
url = "opc.tcp://localhost:4841/"
server.set_endpoint(url)
server.set_security_IDs(["Anonymous", "Basic256Sha256", "Admin"])
server.allow_remote_admin("allow")
uri = "localhost/ptp_programmierprojekt"
namespace = server.register_namespace(uri)
objects = server.get_objects_node()
server.start()
print("Server started at {}".format(url))


anlage = objects.add_object("ns=1;i=1", "Machine")
anlage_status = anlage.add_variable("ns=1;i=12", "machine_status", False)

komponente_1 = objects.add_object("ns=1;i=2", "komponente_1")
komponente_1_status = komponente_1.add_variable("ns=1;i=21", "komponente_1_status", False)
lichtschranke_l1 = komponente_1.add_variable("ns=1;i=23", "lichtschranke_l1", False)
initiator_1 = komponente_1.add_variable("ns=1;i=24", "initiator_1", False)
lichtschranke_l2 = komponente_1.add_variable("ns=1;i=25", "lichtschranke_l2", False)


fließband_1 = objects.add_object("ns=1;i=3", "fließband_1")
fließband_1_status = fließband_1.add_variable("ns=1;i=34", "fließband_1_status", False)

fließband_2 = objects.add_object("ns=1;i=31", "fließband_2")
fließband_2_puffer = fließband_2.add_variable("ns=1;i=32", "fließband_2_puffer", False)
fließband_2_status = fließband_2.add_variable("ns=1;i=33", "fließband_2_status", False)

fahrstuhldockingstation = objects.add_object("ns=1;i=4", "fahrstuhldockingstation")
fahrstuhldockingstation_status = fahrstuhldockingstation.add_variable("ns=1;i=42", "fahrstuhldockingstation_status", False)
lichtschranke_l3 = fahrstuhldockingstation.add_variable("ns=1;i=41", "lichtschranke_l3", False)

hochregallager = objects.add_object("ns=1;i=5", "hochregallager")
roboter = hochregallager.add_variable("ns=1;i=51", "roboter", False)
freie_roboter = hochregallager.add_variable("ns=1;i=52", "freie_roboter", 6)
freie_lagerplaetze = hochregallager.add_variable("ns=1;i=53", "freie_lagerplaetze", 20000)

werkstueck = objects.add_object("ns=1;i=6", "werkstueck")
werkstueck_status = werkstueck.add_variable("ns=1;i=61", "werkstueck_status",  False)
werkstueck_typ = werkstueck.add_variable("ns=1;i=62", "werkstueck_typ",  False)
werkstueck_position = werkstueck.add_variable("ns=1;i=65", "werkstueck_position", False)

task = objects.add_object("ns=1;i=8", "task")
task_status = task.add_variable("ns=1;i=81", "task_status", False)
task_starttime = task.add_variable("ns=1;i=82", "task_starttime", False)
task_stoptime = task.add_variable("ns=1;i=83", "task_stoptime", False)
current_task = task.add_variable("ns=1;i=84", "current_task", False)
    
programm = objects.add_object("ns=1;i=7", "Programm")
program_name = programm.add_variable("ns=1;i=71", "Programm", True)



class DataObserver():
    
    def update(self, args):
        for key, value in args.items():
            print(key, value)
            output = globals()[key]
            output.set_value(value)
        pass


          
            
machine_controller = MController()
obs = DataObserver()
controller = machine_controller.setup(obs, globals())

    # ua args for method "change_machine_state"
statusUA = ua.Argument()
statusUA.Name = "StatusUA"
statusUA.DataType = ua.NodeId(ua.ObjectIds.Boolean)
statusUA.ArrayDimensions = []
statusUA.Description = ua.LocalizedText("Status change")
statusoutput = ua.Argument()
statusoutput.Name = "StatusOutputUA"
statusoutput.DataType = ua.NodeId(ua.ObjectIds.Boolean)
statusoutput.ArrayDimensions = []
statusoutput.Description = ua.LocalizedText("Status change output")

taskUA = ua.Argument()
taskUA.Name = "TaskUA"
taskUA.DataType = ua.NodeId(ua.ObjectIds.String)
taskUA.ArrayDimensions = []
taskUA.Description = ua.LocalizedText("task execution")

taskUAinstruction = ua.Argument()
taskUAinstruction.Name = "TaskUAInstruction"
taskUAinstruction.DataType = ua.NodeId(ua.ObjectIds.Integer)
taskUAinstruction.ArrayDimensions = []
taskUAinstruction.Description = ua.LocalizedText("task execution")

taskoutput = ua.Argument()
taskoutput.Name = "TaskOutputUA"
taskoutput.DataType = ua.NodeId(ua.ObjectIds.String)
taskoutput.ArrayDimensions = []
taskoutput.Description = ua.LocalizedText("task execution result")

programUA = ua.Argument()
programUA.Name = "ProgramUA"
programUA.DataType = ua.NodeId(ua.ObjectIds.String)
programUA.ArrayDimensions = []
programUA.Description = ua.LocalizedText("Program")

programoutputUA = ua.Argument()
programoutputUA.Name = "ProgramUA"
programoutputUA.DataType = ua.NodeId(ua.ObjectIds.String)
programoutputUA.ArrayDimensions = []
programoutputUA.Description = ua.LocalizedText("Program")

    #Callable ua methods
@uamethod
def change_machine_status(status):
    if status == True:
        controller.startmachine()
        return status
 
    elif status == False:
        controller.stopmachine()
        return status

@uamethod
def startprogram(parent, name):
    program = controller.runprogram(name)
    return program

      #Register methods in namespace
anlage.add_method(1, "change machine status", change_machine_status, [statusUA], [statusoutput])
anlage.add_method(1, "run program", startprogram, [programUA], [programoutputUA])
   
