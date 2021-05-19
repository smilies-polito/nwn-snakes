import errno

from wrapping import *
import pylab as plt
import pandas as pd

#TODO controlli!
class Simulator():
    def __init__(self, m, steps, firing_prob = 0.6, output_path = ".", draw_nets = False):
        self._module = m
        self._steps = steps
        #self._stimuli = self._read_stimuli(stimuli)
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

    #TODO sistemare il marking iniziale
    def execute(self, initial_marking, stimuli): #TODO livello di output (quiet, verbose, debug), tipi di output (csv e/o img)
        self._module.draw(os.path.join(self._output_path, self._module.name + "_"))
        if initial_marking is not None:
            self._module.set_marking(initial_marking)
        self._markings[0] = self._module.get_marking_count()
        if self._draw_nets:
            self._module.draw(os.path.join(self._output_path, "0_" + self._module.name + "_"))
        self._module.print_marking_count(0, output_path=self._output_path)
        for i in range(self._steps):
            if stimuli[i] is not None:
                self._administer(stimuli[i])
            self._module.fire(i, prob=self._firing_prob)
            if self._draw_nets:
                self._module.draw(os.path.join(self._output_path, str(i+1) + "_" + self._module.name + "_"))
            if self._output_path:
                self._module.print_marking_count(i+1, output_path = self._output_path)
            self._markings[i+1] = self._module.get_marking_count()

    def _administer(self, stimulus):
        self._module.add_marking(stimulus)

    def _read_stimuli(self, filename):
        if filename is None:
            self._stimuli = None
            return
        if not os.path.exists(self._output_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)
        self._stimuli = pd.read_csv(filename)
        print(self._stimuli.head())
        return


    def execute_step_by_step(self):
        pass

    def make_charts(self, exclude=[]):
        custom_cmap = defaultdict()

        tree = lambda: defaultdict(tree)
        d = tree()
        m = self._markings
        for step in list(m.keys()):
            for net in m[step].keys():
                for place in m[step][net].keys():
                    for tk, n in m[step][net][place].items():
                        d[net][place][str(tk)][step] = n
                        if str(tk) not in custom_cmap:
                            custom_cmap[str(tk)] = None

        tk_count = len(custom_cmap)
        cmap = plt.cm.get_cmap('Dark2_r')
        colors = cmap(np.linspace(0, 1, tk_count))
        for i, tk in enumerate(sorted(custom_cmap.keys())):
            custom_cmap[tk] = colors[i]

        for net in d:
            for place in d[net]:
                if any(e in place for e in exclude):
                    continue
                fig, ax = plt.subplots()
                plt.subplots_adjust(right=0.75)
                plt.xlabel("simulation step")
                plt.ylabel("# tokens")
                title = "place " + place + " (" + net + ")"
                plt.title(title)
                ymax = 0
                for i, token in enumerate(d[net][place]):
                    if not "_net" in token:
                        X = d[net][place][token].keys()
                        Y = d[net][place][token].values()
                        ax.plot(X, Y, label=token.lstrip("_"), color=custom_cmap[token])
                        if max(Y) > ymax:
                            ymax = max(Y)

                plt.xlim(xmin = 0)
                plt.ylim(ymin = 0)
                ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
                ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
                ax.xaxis.set_ticks(np.arange(0, self._steps + 1, int(self._steps / 10)))
                ax.yaxis.set_ticks(np.arange(0, ymax + np.ceil(ymax/10), 1 if ymax <= 10 else 5 if ymax <= 50 else 10 if ymax <=100 else 50))
                fig.legend()
                #plt.show()
                plt.savefig(os.path.join(self._output_path, title), bbox_inches="tight")
                plt.close()
        print(f"Simulation results saved to {self._output_path}")