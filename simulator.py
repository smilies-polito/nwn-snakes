from MycoplasmaChromosome import mycoplasma_chromosome
from wrapping import *

test_module = mycoplasma_chromosome("test")
print(test_module)

test_module.draw(str(0) + "_" + test_module.name + "_")

for i in range(1, 4):
    test_module.fire()
    test_module.draw(str(i) + "_" + test_module.name + "_")