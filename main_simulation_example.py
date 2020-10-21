from example_modules import *
from simulator import *

test_module = net1("test")
#print(test_module)
#TODO nella classe Module prevedere un meccanismo per l'enumerazione dei posti (con accesso solo a quelli
# della rete superiore?) e aggiornamento del marking nei posti degli altri livelli connessi da "canali"
marking = test_module.get_marking()
marking['lower_net_a']['p1'].add([BlackToken()]*3)
marking['lower_net_b']['e'].add([BlackToken()]*10)
marking['upper_net']['p1'].add(["p1", "p1", "p1", "p2", "p2", "p2", "p2", "p2", "p2", "p2", "p2", "p2"])
marking['upper_net']['p2'].add(["tk"]*10)
test_module.set_marking(marking)

output_path = os.path.join(".", test_module.name + "_results")
s = Simulator(m=test_module, steps=10, output_path=output_path, draw_nets=True)
s.execute()