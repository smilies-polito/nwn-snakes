from wrapping import *

class net1(Module):
    def __init__(self, name):
        super().__init__(name)

    def build_net_structure(self) -> PetriNet:
        super(self.__class__, self).build_net_structure()
        upper_net = PetriNet('upper_net', timescale=2)
        lower_net_a = PetriNet('lower_net_a', timescale=1)
        lower_net_b = PetriNet('lower_net_b', timescale=1)

        # rete "inferiore" a
        lower_net_a.add_place(Place("p1", []))
        lower_net_a.add_place(Place("p2", []))
        lower_net_a.add_place(Place("p3", []))
        lower_net_a.add_place(Place("p4", []))

        # transizioni rete a
        lower_net_a.add_transition(Transition('t1'))
        lower_net_a.add_input('p1', 't1', Value(dot))
        lower_net_a.add_output('p1', 't1', Value(dot))
        lower_net_a.add_output('p2', 't1', MultiArc([Value(dot), Value(dot)]))

        lower_net_a.add_transition(Transition('t2'))
        lower_net_a.add_input('p2', 't2', Value(dot))

        lower_net_a.add_transition(Transition('t3'))
        lower_net_a.add_input('p2', 't3', Value(dot))

        # rete "inferiore" b
        lower_net_b.add_place(Place("p1", []))
        lower_net_b.add_place(Place("p2", []))
        lower_net_b.add_place(Place("p3", []))

        # transizioni rete b
        lower_net_b.add_transition(Transition("t1"))
        lower_net_b.add_output("p2", "t1", Value(dot))
        lower_net_b.add_output("p3", "t1", Value(dot))

        lower_net_b.add_transition(Transition("t2"))
        lower_net_b.add_input("p3", "t2", Value(dot))

        # rete superiore
        upper_net.add_place(Place("p1", [lower_net_a]))
        upper_net.add_place(Place("p2", [lower_net_b]))

        # transizioni rete superiore
        #TODO: automatically add Expression("type(x) != PetriNet") for each transition if net contains net tokens
        #upper_net.add_transition(Transition("t_from_left", Expression("str(x) == x")))
        upper_net.add_transition(Transition("t_from_left", Expression("type(x) != PetriNet")))
        upper_net.add_input("p1", "t_from_left", Variable("x"))
        upper_net.add_output("p2", "t_from_left", Expression("x"), notify=[lower_net_b])

        upper_net.add_transition(Transition("t_from_right", Expression("(type(x) != PetriNet) and (x == \"tk\")")))
        upper_net.add_input("p2", "t_from_right", Variable("x"))
        upper_net.add_output("p1", "t_from_right", Variable("x"), notify=[lower_net_a])

        # transizioni che coinvolgono la rete superiore
        lower_net_a.add_output("p3", "t2", Value(dot), notify=[upper_net.place("p1")])
        lower_net_a.add_output("p4", "t3", Value(dot), notify=[upper_net.place("p1")])
        lower_net_b.add_input("p1", "t1", Value(dot), notify=[upper_net.place("p2")])
        lower_net_b.add_output("p1", "t2", Value(dot), notify=[upper_net.place("p2")])

        return upper_net

#TODO controllare transizioni
class simple_bacterial_consortium(Module):
    def __init__(self, name):
        super().__init__(name)

    def build_net_structure(self) -> PetriNet:
        super(self.__class__, self).build_net_structure()
        upper_net = PetriNet('upper_net', timescale=1)
        controller_lower_net = PetriNet('controller_lower_net', timescale=1)
        target_lower_net = PetriNet('target_lower_net', timescale=1)

        # rete "inferiore" controller
        controller_lower_net.add_place(Place("lac1", []))
        controller_lower_net.add_place(Place("_3oc6hsl", []))
        controller_lower_net.add_place(Place("mRNA", []))
        controller_lower_net.add_place(Place("_3oc6hsl_gene", [BlackToken()]))

        # rete "inferiore" target
        target_lower_net.add_place(Place("_3oc6hsl", []))
        target_lower_net.add_place(Place("gfp", []))
        target_lower_net.add_place(Place("mRNA", []))

        # transizioni rete controller
        controller_lower_net.add_transition(Transition('x'))
        controller_lower_net.add_input('mRNA', 'x', Value(dot))
        # output più giù perché fa notify su rete specificata in seguito

        controller_lower_net.add_transition(Transition('y'))
        controller_lower_net.add_input('mRNA', 'y', Value(dot))

        controller_lower_net.add_transition(Transition('z', guard=Expression('True')))
        controller_lower_net.add_input('_3oc6hsl_gene', 'z', Value(dot))
        controller_lower_net.add_output('_3oc6hsl_gene', 'z', Value(dot))
        controller_lower_net.add_output('mRNA', 'z', Value(dot))
        # controller_lower_net.add_output('mRNA', 'z', MultiArc([Value(dot), Value(dot)]))

        # transizioni rete target
        target_lower_net.add_transition(Transition('u'))
        target_lower_net.add_output('mRNA', 'u', Value(dot))

        target_lower_net.add_transition(Transition('t'))
        target_lower_net.add_input('mRNA', 't', Value(dot))

        # rete superiore
        controller_cell = Place("controller_cell", [controller_lower_net])
        target_cell = Place("target_cell", [target_lower_net])
        upper_net.add_place(controller_cell)
        upper_net.add_place(target_cell)

        # transizione di una rete inferiore sincronizzata con posto della rete superiore
        # target_lower_net.add_output('iptg', 't', Value(dot), notify=[upper_net.place("target_cell")])
        controller_lower_net.add_input('lac1', 'y', Value(dot), notify=[upper_net.place("controller_cell")])
        controller_lower_net.add_output('_3oc6hsl', 'x', Value(dot), notify=[upper_net.place('controller_cell')])
        target_lower_net.add_input('_3oc6hsl', 'u', Value(dot), notify=[upper_net.place("target_cell")])
        target_lower_net.add_output('gfp', 't', Value(dot), notify=[upper_net.place("target_cell")])

        # transizione di una rete superiore sincronizzata con rete inferiore
        # upper_net.add_transition(Transition('start'))
        # upper_net.add_output('controller_cell', 'start', Variable('x'), notify=[controller_lower_net])

        upper_net.add_transition(Transition('diffusion_l', Expression("str(x) == x")))
        upper_net.add_input('controller_cell', 'diffusion_l', Variable('x'))
        upper_net.add_output('target_cell', 'diffusion_l', Variable('x'), notify=[target_lower_net])

        upper_net.add_transition(Transition('diffusion_r', Expression("str(x) == x")))
        upper_net.add_input('target_cell', 'diffusion_r', Variable('x'))
        upper_net.add_output('controller_cell', 'diffusion_r', Variable('x'), notify=[controller_lower_net])

        # upper_net.add_transition(Transition('diobbestia', Expression('type(x) == int')))
        # upper_net.add_input('controller_cell', 'diobbestia', Variable('x'))
        # upper_net.add_output('target_cell', 'diobbestia', Expression('x'))

        # upper_net.add_transition(Transition('transustanziazione', Expression('type(x) == str')))
        # upper_net.add_input('target_cell', 'transustanziazione', Variable('x'))
        # upper_net.add_output('controller_cell', 'transustanziazione', Expression('x'))
        print("modes: ", len(controller_lower_net.transition("z").modes()))

        return upper_net