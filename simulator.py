from bacterial_consortium import bacterial_consortium
from wrapping import *

class Simulator():
    def __init__(self, m, steps, output = None):
        self._module = m
        self._steps = steps
        self.output = output if output is not None else sys.stdout

    def set_module(self, m: Module):
        self._module = m

    def set_steps(self, steps):
        self._steps = steps

    def execute(self): #TODO livello di output (quiet, verbose, debug), tipi di output (csv e/o img)
        for i in range(0, self._steps):
            self._module.fire()

    def execute_step_by_step(self):
        pass

test_module = bacterial_consortium("test")
#print(test_module)
marking = test_module.get_marking()
# TODO ritornare una mappa custom con "=" ridefinito per fare un append e sostituire l'append di set_marking nel wrapper?
# TODO sarebbe comodo poter indirizzare con la sintassi "." invece che quadre e stringhe
marking['upper_net']['controller_cell'] = [BlackToken()]*3
test_module.set_marking(marking)

print(marking)


test_module.draw(str(0) + "_" + test_module.name + "_")

for i in range(1, 2):
    test_module.fire()
    test_module.draw(str(i) + "_" + test_module.name + "_")

#simulator = Simulator(bacterial_consortium, 3)
#simulator.execute()


