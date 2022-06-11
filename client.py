
import sys
import opcua
from opcua import Client, ua


class SubHandler():

    def datachange_notification(node, val, data):
        print(node, ":", val)
        pass

def main():

    url = "opc.tcp://localhost:4841/"

    client = Client(url)
    client.set_user("Admin")
    client.set_password("Basic256Sha256")
    client.connect()
    base = client.get_objects_node()


  
    anlage_status = client.get_node("ns=1;i=12")
    komponente_1_status = client.get_node("ns=1;i=21")
    lichtschranke_l1 = client.get_node("ns=1;i=23")
    initiator_1 = client.get_node("ns=1;i=24")
    lichtschranke_l2 = client.get_node("ns=1;i=25")
    fließband_1_status = client.get_node("ns=1;i=34")
    fließband_2_status = client.get_node("ns=1;i=33")
    fließband_2_puffer = client.get_node("ns=1;i=32")
    fahrstuhldockingstation_status = client.get_node("ns=1;i=42")
    lichtschranke_l3 = client.get_node("ns=1;i=41")
    roboter =  client.get_node("ns=1;i=51")
    freie_roboter =  client.get_node("ns=1;i=52")
    freie_lagerplaetze =  client.get_node("ns=1;i=53")
    werkstueck =  client.get_node("ns=1;i=6")
    werkstueck_status = client.get_node('ns=1;i=61')
    werkstueck_typ =  client.get_node("ns=1;i=62")
    werkstueck_position =  client.get_node("ns=1;i=65")


    sub = client.create_subscription(1, SubHandler)

    sub.subscribe_data_change(anlage_status)
    sub.subscribe_data_change(komponente_1_status)
    sub.subscribe_data_change(lichtschranke_l1)
    sub.subscribe_data_change(initiator_1)
    sub.subscribe_data_change(lichtschranke_l2)
    sub.subscribe_data_change(fließband_1_status)
    sub.subscribe_data_change(fließband_2_puffer)
    sub.subscribe_data_change(fließband_2_status)
    sub.subscribe_data_change(fahrstuhldockingstation_status)
    sub.subscribe_data_change(lichtschranke_l3)
    sub.subscribe_data_change(roboter)
    sub.subscribe_data_change(freie_roboter)
    sub.subscribe_data_change(freie_lagerplaetze)
    sub.subscribe_data_change(werkstueck_status)
    sub.subscribe_data_change(werkstueck_typ)
    sub.subscribe_data_change(werkstueck_position)
    method_change_machinestate = client.get_node("ns=1;i=2001")
    method_program = client.get_node("ns=1;i=2007")
    
    base.call_method(method_program, "default")
    
    pass


if __name__ == "__main__":
    main()