from bacterial_consortium import bacterial_consortium
from example_modules import *
from simulator import *

#test_module = net1("test")
test_module = bacterial_consortium("bacterial_consortium")
#print(test_module)
#TODO nella classe Module prevedere un meccanismo per l'enumerazione dei posti (con accesso solo a quelli
# della rete superiore?) e aggiornamento del marking nei posti degli altri livelli connessi da "canali"
marking = test_module.get_marking()
marking['controller_net']['Lac1_protein'].add([BlackToken()]*50)
marking['upper_net']['controller_compartment'].add(["Lac1_protein" for i in range(50)])
#marking['controller_net']['_3OC6HSL_mRNA'].add([BlackToken()]*100)
marking['controller_net']['_3OC6HSL_gene'].add([BlackToken()]*1)
marking['target_net']['GFP_gene'].add([BlackToken()]*1)
#marking['target_net']['_3OC6HSL_protein'].add([BlackToken()]*10)
#marking['upper_net']['target_compartment'].add(["_3OC6HSL_protein" for i in range(10)])
#test_module.set_marking(marking)

output_path = os.path.join(".", test_module.name + "_results")
s = Simulator(m=test_module, steps=100, output_path=output_path, draw_nets=False)
#for esperimenti
s.execute(marking)
s.make_charts()
