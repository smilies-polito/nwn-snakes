from wrapping import *

class bacterial_consortium(Module):
    def __init__(self, name):
        super().__init__(name)

    def build_net_structure(self) -> PetriNet:
        super(self.__class__, self).build_net_structure()
        upper_net = PetriNet('upper_net', timescale=2)
        controller_net = PetriNet('controller_net', timescale=1)
        target_net = PetriNet('target_net', timescale=1)

        # rete controller_net
        controller_net.add_place(Place("_3OC6HSL_gene", []))
        controller_net.add_place(Place("_3OC6HSL_mRNA", []))
        controller_net.add_place(Place("_3OC6HSL_protein", []))
        controller_net.add_place(Place("Lac1_protein", []))

        # transizioni rete controller_net
        controller_net.add_transition(Transition('_3OC6HSL_inhibition'))
        controller_net.add_transition(Transition('_3OC6HSL_transcription_baseline'))
        controller_net.add_transition(Transition('_3OC6HSL_translation'))

        # rete target_net
        target_net.add_place(Place("GFP_gene", []))
        target_net.add_place(Place("GFP_mRNA", []))
        target_net.add_place(Place("GFP_protein", []))
        target_net.add_place(Place("_3OC6HSL_protein", []))

        # transizioni rete target_net
        target_net.add_transition(Transition("GFP_transcription_inducible"))
        target_net.add_transition(Transition("GFP_translation"))

        # rete superiore
        upper_net.add_place(Place("controller_compartment", [controller_net]))
        upper_net.add_place(Place("target_compartment", [target_net]))

        # transizioni rete superiore
        #TODO: automatically add Expression("type(x) != PetriNet") for each transition if net contains net tokens
        upper_net.add_transition(Transition("diffusion_from_controller", Expression("str(x) == x"))) #"not isinstance(x, PetriNet)"
        upper_net.add_input("controller_compartment", "diffusion_from_controller", Variable("x"), notify=[controller_net])
        upper_net.add_output("target_compartment", "diffusion_from_controller", Variable("x"), notify=[target_net])

        upper_net.add_transition(Transition("diffusion_from_target", Expression("str(x) == x")))
        upper_net.add_input("target_compartment", "diffusion_from_target", Variable("x"), notify=[target_net])
        upper_net.add_output("controller_compartment", "diffusion_from_target", Variable("x"), notify=[controller_net])

        # transizioni che coinvolgono la rete superiore
        controller_net.add_input('Lac1_protein', '_3OC6HSL_inhibition', Value(dot), notify=[upper_net.place("controller_compartment")])
        controller_net.add_input('_3OC6HSL_mRNA', '_3OC6HSL_inhibition', Value(dot))

        controller_net.add_input('_3OC6HSL_gene', '_3OC6HSL_transcription_baseline', Value(dot))
        controller_net.add_output('_3OC6HSL_gene', '_3OC6HSL_transcription_baseline', Value(dot))
        controller_net.add_output('_3OC6HSL_mRNA', '_3OC6HSL_transcription_baseline', Value(dot))

        controller_net.add_output('_3OC6HSL_protein', '_3OC6HSL_translation', Value(dot), notify=[upper_net.place("controller_compartment")])
        controller_net.add_input('_3OC6HSL_mRNA', '_3OC6HSL_translation', Value(dot))

        target_net.add_input("_3OC6HSL_protein", "GFP_transcription_inducible", Value(dot), notify=[upper_net.place("target_compartment")])
        target_net.add_input("GFP_gene", "GFP_transcription_inducible", Value(dot))
        target_net.add_output("GFP_gene", "GFP_transcription_inducible", Value(dot))
        target_net.add_output("GFP_mRNA", "GFP_transcription_inducible", Value(dot))

        target_net.add_input("GFP_mRNA", "GFP_translation", Value(dot))
        target_net.add_output("GFP_protein", "GFP_translation", Value(dot))

        return upper_net