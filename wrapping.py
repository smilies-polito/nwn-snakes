import collections
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
import random
import pandas as pd
from snakes.nets import *
import snakes.plugins
snakes.plugins.load("gv", "snakes.nets", "nets")
from nets import *
import numpy as np


class AdvEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_name_value(cls):
        return list(map(lambda c: (c.name, c.value), cls))


class Level(AdvEnum):
    INFO = 20
    DEBUG = 10
    NOTSET = 0

class HierarchyTree(): #create a tree that just stores references to all the nets that are around
    def __init__(self, net):
        self.root: PetriNet = net
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def create_hierarchy_tree(self, root):
        tree = HierarchyTree(root)
        for place in root.place():
            for token in place.tokens:
                if isinstance(token, PetriNet):
                    tree.add_child(self.create_hierarchy_tree(token))
        return tree

    def __repr__(self):
        s = "hierarchy tree:\n"
        s.join("net: " + self.root.name)
        for place in self.root.place():
            pass

class DeepDict(defaultdict):
    def __call__(self):
        return DeepDict(self.default_factory)

class Module(ABC):
    """
    The base class of each module

    ...

    Attributes
    ----------

    Methods
    -------

    """
    level = Level.NOTSET

    def __init__(self, name: str = ""):
        self.name = name
        self._clock = 0
        self._net = self.build_net_structure()
        self._net.globals.declare("from snakes.nets import *; import snakes.plugins; snakes.plugins.load('gv', 'snakes.nets', 'nets')")
        self._net_timescales = self.collect_timescales()
        self._transitions = self.collect_transitions()
        self._marking_count = self.get_marking_count()
        self._watch = None #TODO places to watch

    @abstractmethod
    def build_net_structure(self) -> PetriNet:
        pass

    def set_marking(self, marking):
        self._set_marking(self._net, marking)

    def _set_marking(self, node, marking):
        if type(node) == PetriNet:
            node.set_marking(marking[node.name])
            for p in node.place():
                self._set_marking(p, marking)
            return
        elif type(node) == Place:
            for tk in node.tokens:
                self._set_marking(tk, marking)
            return
        return

    def add_marking(self, marking):
        self._add_marking(self._net, marking)

    def _add_marking(self, node, marking):
        if type(node) == PetriNet:
            node.add_marking(marking[node.name])
            for p in node.place():
                self._add_marking(p, marking)
            return
        elif type(node) == Place:
            for tk in node.tokens:
                self._add_marking(tk, marking)
            return
        return

    def get_marking(self):
        return self._get_marking(self._net, defaultdict())

    def _get_marking(self, node, marking):
        if type(node) == PetriNet:
            marking[node.name] = node.get_marking()
            for p in node.place():
                self._get_marking(p, marking)
            return marking
        elif type(node) == Place:
            for tk in node.tokens:
                marking = self._get_marking(tk, marking)
            return marking
        return marking

    def get_marking_count(self):
        return self._get_marking_count(self._net, {}, "")

    def _get_marking_count(self, node, marking, net_name) -> {}:
        if type(node) == PetriNet:
            marking[node.name] = {}
            for p in node.place():
                marking = self._get_marking_count(p, marking, node.name)
            return marking
        elif type(node) == Place:
            #if len(node.tokens) > 0:
            marking[net_name][node.name] = dict(collections.Counter(node.tokens))
            for tk in node.tokens:
                marking = self._get_marking_count(tk, marking, net_name)
            return marking
        #elif isinstance(node, Token):
        #    s += str(node) + " "
        return marking

    def print_marking_count(self, i, output_path = "."):
        marking = self.get_marking_count()
        for d in marking.keys():
            out = os.path.join(output_path, "marking_" + d + " .csv")
            header = not os.path.exists(out)
            with open(out, 'a') as f:
                pd.DataFrame.from_dict({i: marking[d]}).stack().unstack(level=[0]).to_csv(f, header=header)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self._str(self._net, "Module " + self.name + ":\n", 0)

    def _str(self, node, s, i):
        if type(node) == PetriNet:
            s += "N " + node.name + "\n"
            for p in node.place():
                s = self._str(p, s, i+1)
            return s
        elif type(node) == Place:
            s += "\t" * (i+1) + "P " + node.name
            if len(node.tokens) > 0:
                s += "\n" + "\t" * (i+2) + "T "
            for tk in node.tokens:
                s = self._str(tk, s, i+2)
            return s + "\n"
        elif isinstance(node, Token):
            s += str(node) + " "
        return s

    def collect_timescales(self) -> {}:
        return self._collect_timescales(self._net, {})

    def _collect_timescales(self, node, timescales):
        if type(node) == PetriNet:
            timescales[node.name] = node.timescale
            for p in node.place():
                timescales = self._collect_timescales(p, timescales)
            return timescales
        elif type(node) == Place:
            for tk in node.tokens:
                timescales = self._collect_timescales(tk, timescales)
            return timescales
        return timescales

    def collect_transitions(self):
        return self._collect_transitions(self._net, defaultdict(dict))

    def _collect_transitions(self, node, transitions):
        if type(node) == PetriNet:
            for t in node.transition():
                transitions[node.name][t.name] = t
            for p in node.place():
                transitions = self._collect_transitions(p, transitions)
            return transitions
        elif type(node) == Place:
            for tk in node.tokens:
                transitions = self._collect_transitions(tk, transitions)
            return transitions
        return transitions

    # TODO parametrizzare la percentuale di transizioni pescate per modello
    def fire(self, step, prob=0.6):
        print("step", step)
        to_fire = []
        for node in self._transitions.keys():
            if(step % self._net_timescales[node] == 0):
                # filtro solo le transizioni abilitate a scattare (per cui ci sono token sufficienti nel posto di origine)
                transitions = [ t for t in self._transitions[node].values() if len(t.modes()) > 0 ]
                # faccio scattare ogni transizione abilitate con una probabilità del 60%
                probs = np.random.choice([False, True], size=len(transitions), p=[1-prob, prob])
                for i, t in enumerate(transitions):
                    if probs[i] == True:
                        to_fire.append(t)
        random.shuffle(to_fire)
        for t in to_fire:
            try:
                t.fire(random.choice(t.modes()))
                print("\t-- transition", t.name, "fired")
            except Exception as e:
                # if here: one of the previous transitions selected during this same simulation step
                # consumed a token that was needed by this transition to fire
                pass
                #print(e)
        #TODO spostare qua l'aggiornamento del count marking

    #TODO aggiungere filtro sui token da plottare (impostabile dall'esterno, es. main della simulazione)
    def draw(self, path):
        self._draw(self._net, path)

    def _draw(self, node, path):
        if type(node) == PetriNet:
            node.draw(path + node.name + ".png")
            for p in node.place():
                self._draw(p, path)
            return
        elif type(node) == Place:
            for tk in node.tokens:
                self._draw(tk, path)
            return
        return
