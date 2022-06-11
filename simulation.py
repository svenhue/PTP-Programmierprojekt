from datetime import datetime
import random
import time
import sys
from opcua import Server, ua, uamethod


# simuliert den Warenfluss und löst damit die Sensoren (lichtschranken, initiator Komponente 1) bzw. updated die nodes im namespace
# dies ermöglicht die Nutzung von Transitionen



class MTask():
    
    tasks = {"transportierePaketmitFörderbandFL1": {"time": 1},
             "vermessePaket" : {"time": 1, }, "transitions": {"lichtschranke_l1": True },
             "tranportierePaketmitFörderbandFL2":  {"time": 1,  "transitions": {"lichtschranke_l2": True}},
             "positionierePaketfürRoboterDockingstation":{"time": 1, },"transitions": {"Roboterdockingstation": False, "lichtschranke_l3": True},
             "lagerePaketinHochregallager": {"time": 1, "transitions": {"freie_lagerplaetze": 1, "freie_roboter": 1}}}
    
    def start(self):
        now = datetime.now() 
        self.starttime = now.strftime("%H:%M:%S")
        return self.starttime
        
    def stop(self):
        now = datetime.now()
        self.stoptime = now.strftime("%H:%M:%S")
        return self.stoptime

    def checktransitions(self, opcua_globals):
        
       
        if self.task_data.get("transitions") is not None:
            transitions = self.task_data.get("transitions")
            for key, value in transitions.items():
                subject = opcua_globals[key]
                print('transition:', key, 'value:' , subject.get_value())
                
                if key == "freie_lagerplaetze":
                    if subject.get_value() >= 1:
                        return True
                elif key == "freie_roboter":
                        if subject.get_value() >= 1:
                            return True
                elif subject.get_value() == value:
                    return True
                else:
                    return False
        else: 
            return True
                
    def instruct(self, taskname, instructions):
        task_data = MTask.tasks.get(taskname)
        self.task = taskname
        self.task_data = task_data
        self.instructions = instructions
        return self



class Workpiece():
 
    def __init__(self):
        self.type = ""
        self.position = ""
        pass

    # Sendet die durch eine Aufgabe veränderten Daten (Werkstück, Aufgabe, Maschine) an den DataObserver, der die Notes im Namespace aktualisiert
class DataPublisher():

    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def dispatch(self, args):
        for obs in self._observers:
            obs.update(args)

    def unsubscibe(self, observer):
        self._observers.remove(observer)
    
    # Ein Programm besteht aus x beliebigen Aufgaben, welche in der angegebenen Reihenfolge ausgeführt werden. Zudem können Anweisungen mitgegeben werden
class Program():

    programs = {"default": 
                {"tasks": [
                    {"task": "transportierePaketmitFörderbandFL1"},
                    {"task": "vermessePaket"}, 
                    {"task": "tranportierePaketmitFörderbandFL2"}, 
                    {"task":"positionierePaketfürRoboterDockingstation"}, 
                    {"task": "lagerePaketinHochregallager"}
                     ]}}

    def set(self, name):
        program = Program.programs.get(name)
        self.name = name
        self.program = program
        return self



class Anlage():
    
    def __init__(self):
        self.temp = 20
        pass
    
    def executetask(self, task, workpiece, opcua_globals):

        if task.checktransitions(opcua_globals) == True:
            starttime = task.start()
            time.sleep(task.task_data.get("time"))
            output =  getattr(self, task.task)(task, workpiece)
            stoptime = task.stop()
            output["task_starttime"] = starttime
            output["task_stoptime"] = stoptime
            output["current_task"] = task.task
            return output
        else:       
            output = {"task_status": "transitions not active"} 
            return output

    def transportierePaketmitFörderbandFL1(self, task, workpiece):
        
        output = {'lichtschranke_l1': True}
        
        return output
    
    
    def vermessePaket(self, task, workpiece):
       
        
        moegliche_vermessungen = ["schuhe", "hosen"]
       
        vermessungen = random.choices(moegliche_vermessungen, [0.5,0.5])
        
        output = {'werkstueck_position': 'komponente_1', "werkstueck_typ": vermessungen, "komponente_1_status": "ausgelastet", "lichtschranke_l2": True}
   
        return output

    def tranportierePaketmitFörderbandFL2(self, task, workpiece):
 
        
        output = {'werkstueck_position': "fließband_fl2", "lichtschranke_l3": True}
   
        return output
        
    def positionierePaketfürRoboterDockingstation(self, task, workpiece):
        
        output = {'werkstueck_position': 'fahrstuhldockingstation_status', 'fahrstuhldockingstation_status': 'besetzt'}
        return output
    
    def lagerePaketinHochregallager(self, task, workpiece):
        
        output= {'werkstueck_position': "lager", "freie_lagerplaetze": "", "freie_roboter": "", "roboter": ""}
        return output


class MController():
    
    def instructtaskexecution(self, taskname, instructions):

        task = MTask()
        task = task.instruct(taskname, instructions)
        output = self.machine.executetask(task, self.workpiece, self.opcua_globals)
       
        
        return output

    def setup(self, obs, globals):
        self.opcua_globals = globals
        self.machine = Anlage()
        self.workpiece = Workpiece()
        self.pub = DataPublisher()
        self.pub.subscribe(obs)
        return self
    
    def startmachine(self):
        self.pub.dispatch({"anlage_status" : True})
        pass

    def stopmachine(self):
        self.pub.dispatch({"anlage_status": False})
        pass

    def dispatchoutputs(self, output):
       
        self.pub.dispatch(output)
        pass
    
    def runprogram(self, programname):
        program = Program()
        program = program.set(programname)
        self.taskloop(program)
        pass

    def taskloop(self, program):

        tasklist = program.program.get("tasks")      
        for task  in tasklist:
            output = self.instructtaskexecution(task.get("task"), task.get("instruction"))
            self.dispatchoutputs(output)
   