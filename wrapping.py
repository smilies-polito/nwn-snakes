from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
import random

from snakes.nets import *
import snakes.plugins
snakes.plugins.load("gv", "snakes.nets", "nets")
from nets import *


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
        self._transitions = self.collect_transitions()
        #self._tree = HierarchyTree(self._net)
        self._watch = None #TODO places to watch
        #print(self._tree)
        #print(self._tree.dump_marking())
        #print(self._transitions)

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

    def get_marking(self) -> {}:
        return self._get_marking(self._net, {})

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


    def __repr__(self):
        return self.name

    def __str__(self):
        return self._str(self._net, "Module " + self.name + ":\n", 0)

    def dump_marking(self): #TODO parametro file di output?
        return self._str(self._net, "Module " + self.name + ":\n", 0)
        #return self._print_hierarchy_tree(self._net, "", 0)

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
    def fire(self):
        for node in self._transitions.keys():
            # filtro solo le transizioni abilitate a scattare (per cui ci sono token sufficienti nel posto di origine)
            transitions = [ t for t in self._transitions[node].values() if len(t.modes()) > 0 ]
            # faccio scattare solo il 60% delle transizioni abilitate
            for t in random.sample(transitions, int(0.6 * len(transitions))):
                try:
                    t.fire(random.choice(t.modes()))
                except:
                    pass

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




