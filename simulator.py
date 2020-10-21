from wrapping import *
import pylab as plt
import pandas as pd

#TODO controlli!
class Simulator():
    def __init__(self, m, steps, firing_prob = 0.6, output_path = ".", draw_nets = False):
        self._module = m
        self._steps = steps
        self._firing_prob = firing_prob
        self._output_path = output_path
        self._draw_nets = draw_nets
        self._markings = {}
        if not os.path.exists(self._output_path):
            os.mkdir(self._output_path)

    def set_module(self, m: Module):
        self._module = m

    def set_steps(self, steps):
        self._steps = steps

    def set_output_path(self, output_path):
        self._output_path = output_path

    def set_draw(self, draw):
        self._draw = draw

    def execute(self): #TODO livello di output (quiet, verbose, debug), tipi di output (csv e/o img)
        self._markings[0] = self._module.get_marking_count()
        #if self._draw_nets:
        self._module.draw(os.path.join(self._output_path, "0_" + self._module.name + "_"))
        for i in range(1, self._steps + 1):
            self._module.fire(i, prob=self._firing_prob)
            if self._draw_nets:
                self._module.draw(os.path.join(self._output_path, str(i) + "_" + self._module.name + "_"))
            if self._output_path:
                self._module.print_marking_count(i, output_path = self._output_path)
            self._markings[i] = self._module.get_marking_count()

    def execute_step_by_step(self):
        pass

    def make_charts(self):
        tree = lambda: defaultdict(tree)

        d = tree()
        for step in list(self._markings.keys()):
            for net in self._markings[step].keys():
                for place in self._markings[step][net].keys():
                    for tk, n in self._markings[step][net][place].items():
                        d[net][place][str(tk)][step] = n

        for net in d:
            for place in d[net]:
                fig, ax = plt.subplots()
                ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
                ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
                plt.subplots_adjust(right=0.75)
                plt.xlabel("simulation step")
                plt.ylabel("# tokens")
                title = "place " + place + " (" + net + ")"
                plt.title(title)
                for i, token in enumerate(d[net][place]):
                    X = d[net][place][token].keys()
                    Y = d[net][place][token].values()
                    #plt.plot(X, Y, label=token)
                    ax.plot(X, Y, label=token)
                fig.legend()
                #plt.show()
                plt.savefig(os.path.join(self._output_path, title), bbox_inches="tight")