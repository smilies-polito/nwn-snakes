from wrapping import *


class bacterial_consortium(Module):
    def __init__(self, name):
        super().__init__(name)

    def build_net_structure(self) -> PetriNet:
        super(self.__class__, self).build_net_structure()
        upper_net = PetriNet('upper_net')
        controller_lower_net = PetriNet('controller_lower_net')
        target_lower_net = PetriNet('target_lower_net')

        # rete "inferiore" controller
        lac1 = Place("lac1", [BlackToken()]*10)
        iptg = Place("iptg", [])
        _3oc6hsl = Place("_3oc6hsl", [])
        controller_lower_net.add_place(lac1)
        controller_lower_net.add_place(iptg)
        controller_lower_net.add_place(_3oc6hsl)
        controller_lower_net.add_place(Place("mRNA", [BlackToken()] * 3))

        # rete "inferiore" target
        target_lower_net.add_place(Place("_3oc6hsl", []))
        target_lower_net.add_place(Place("gfp", []))
        target_lower_net.add_place(Place("iptg", []))
        target_lower_net.add_place(Place("mRNA", [BlackToken()] * 3))

        # transizioni rete controller
        controller_lower_net.add_transition(Transition('x'))
        controller_lower_net.add_input('mRNA', 'x', Value(dot))

        controller_lower_net.add_transition(Transition('y'))
        controller_lower_net.add_input('lac1', 'y', Value(dot))
        controller_lower_net.add_input('mRNA', 'y', Value(dot))

        controller_lower_net.add_transition(Transition('z'))
        controller_lower_net.add_input('iptg', 'z', Value(dot))
        controller_lower_net.add_output('mRNA', 'z', Value(dot))

        # transizioni rete target
        target_lower_net.add_transition(Transition('u'))
        target_lower_net.add_input('_3oc6hsl', 'u', Value(dot))
        target_lower_net.add_output('mRNA', 'u', Value(dot))

        target_lower_net.add_transition(Transition('t'))
        target_lower_net.add_input('mRNA', 't', Value(dot))
        target_lower_net.add_output('iptg', 't', Value(dot))
        target_lower_net.add_output('gfp', 't', Value(dot))

        # rete superiore
        controller_cell = Place("controller_cell", [controller_lower_net])
        target_cell = Place("target_cell", [target_lower_net, "_3oc6hsl", "iptg", "gfp"])
        upper_net.add_place(controller_cell)
        upper_net.add_place(target_cell)

        # transizione di una rete inferiore sincronizzata con posto della rete superiore
        controller_lower_net.add_output('_3oc6hsl', 'x', Value(dot), notify=[upper_net.place('controller_cell')])

        # transizione della rete superiore sincronizzata con rete inferiore
        upper_net.add_transition(Transition('start'))
        upper_net.add_output('controller_cell', 'start', Variable('x'), notify=[controller_lower_net])

        upper_net.add_transition(Transition('diffusion_l', Expression('isinstance(x, str)')))
        upper_net.add_input('controller_cell', 'diffusion_l', Variable('x'))
        upper_net.add_output('target_cell', 'diffusion_l', Expression('x'), notify=[target_lower_net])

        upper_net.add_transition(Transition('diffusion_r', Expression('isinstance(x, str)')))
        upper_net.add_input('target_cell', 'diffusion_r', Variable('x'))
        upper_net.add_output('controller_cell', 'diffusion_r', Expression('x'), notify=[controller_lower_net])

        return upper_net