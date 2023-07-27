# nwn-snakes
**nwn-snakes** is a customized version of the [snakes](https://github.com/fpom/snakes) library by Franck Pommereau, 
adding support for the [Nets within Nets](https://en.wikipedia.org/wiki/Nets_within_Nets) modelling method.

## Petri Nets and Nets within Nets
**Petri Nets** support the modeling and simulation of distributed systems and processes running in parallel and competing 
for resources.  
High-level Petri Nets extend the basic Petri Nets notation by allowing tokens of different types (e.g. integers, floats, 
strings) and varying degrees of complexity. 

The **Nets within Nets** (NWN) formalism introduces an additional type of token, the *net token*, that embeds another 
Petri Net.
This implies that Petri Nets can be hierarchically organized, and each layer can be described resorting to the same 
formalism (see Fig. XX).  

NWNs models naturally express encapsulation and selective communication, allowing to represent more complex systems, 
such as compartmentalization and semi-permeability of membranes in the biology domain.

## Extensions for NWN implementation
**nwn-snakes** extends the original SNAKES definition of `PetriNet`, `Place`, and `Transition` classes in order to 
implement the NWN formalism, and the communication and synchronization between nets and net tokens.

### `PetriNet` class
The `PetriNet` class includes two new parameters, both optional. 
\begin{itemize}
* The `parent` parameter is of type Place and defaults to `None`. It shall be used when the `PetriNet` object under 
  creation is a token, in order to set a reference to its parent `Place`.
* The `timescale` parameter defaults to `1` and must be an integer greater than or equal to 1. 
  It represents the rate at which time passes for a given `PetriNet` with respect to the base unitary firing step.  
  
Both the `add_input` and `add_output` methods have been extended with an optional parameter `notify`. 
These methods allow the creation of an input and an output arc, respectively. The `notify` parameter, defaulting to 
`None`, accepts a list of `PetriNet` and `Place` objects.  
When a notification list is specified for an input arc, each object in the list is updated with the removal of the tokens 
enabling the transition. For an output arc instead, each object in the notification list is updated by adding the same number 
of tokens output by the transition.  
These extensions implements the *synchronization mechanism* needed to interlock the evolution at two different levels of 
the net.

### `Place` class
The `Place` class has been equipped with a `sync` method -- called by the `fire` method of the `Transition` class -- 
that is parametrized with the `Token`, and the action to be performed (add/remove).

### `Transition` class
The `Transition` class holds two additional lists of nodes -- `Places` or `PetriNets` to be notified as either inputs 
or outputs for the `Transition` itself. When it fires, the nodes to be notified are handled in two different ways, 
depending on whether they are instances of `Places` or `PetriNets`. If a `Place` is to be notified, then a colored 
token with the same name of the input (output) `Place` is removed from (added to) it. If it is a `PetriNet` instead, 
each `Place` in that net bearing the same name of the colored token in input to (output from) the firing `Transition` 
is supplemented with (deprived of) a black token.

### Basic example
The following piece of code builds the network shown in Fig. XX
This net represents a fictitious [contact-dependent (juxtacrine) signalling process](https://en.wikipedia.org/wiki/Juxtacrine_signalling) 
involving two cells &mdash; `Place` *cell_A* and *cell_B* &mdash; that *live* in the top-level `PetriNet` *basic_example_net*. 
At a high abstraction level, *cell_A* produces *A_protein* colored tokens (`str`) that are "signaled" to the adjacent 
*cell_B* which in turn produces *A_receptor_active_protein* colored tokens. The signaling process is modeled through the 
`Transition` *juxtacrine_signaling_A_protein_cell_A_cell_B*

The `Place` named *cell_A* encapsulates the protein production process in the net token *process_A_net* &mdash; a 
colored token of type `PetriNet`&mdash; producing black tokens in the `Place` *A_protein* starting from `Place` *A_gene*.  

In *process_A_net*
* The `Place` *A_gene* is initialized with a black token that enables the `Transition` *A_gene_transcription*, which 
  produces one black token back to *A_gene* and another one in the `Place` *A_mrna*.  
  * This construct represents the *existence* of a gene that gets transcribed but is not depleted in the process.
* A black token in the `Place` *A_mrna* enables the `Transition` *A_mrna_translation*, producing 3 black tokens in the 
  `Place` *A_protein*.
  * At the same time, the parent place *A_cell* gets notified of the production of the black tokens 
    (`notify=[basic_example_net.place('cell_A')]`). Under the hood, this notification results in the 
    production of as many colored tokens (`str` *"A_protein"*) in *A_cell*.
* A protein degradation process is modeled through the `Transition` *A_protein_degradation* that depletes black tokens 
  from *A_protein* place, without an output arc for passing the tokens to a downstream place.
  * The same notification mechanism as before removes the corresponding colored tokens from *A_protein* place. 
```python
# petri nets
process_B_net = PetriNet("process_B_net", timescale=1)
process_A_net = PetriNet("process_A_net", timescale=1)
basic_example_net = PetriNet("basic_example_net", timescale=1)

# process_B_net places
process_B_net.add_place(Place("A_receptor_active_protein"))

# process_B_net transitions
process_B_net.add_transition(Transition("A_receptor_active_protein_degradation"))

# process_A_net places
process_A_net.add_place(Place("A_gene", [BlackToken()]))
process_A_net.add_place(Place("A_mrna"))
process_A_net.add_place(Place("A_protein"))

# process_A_net transitions
process_A_net.add_transition(Transition("A_gene_transcription"))
process_A_net.add_transition(Transition("A_mrna_translation"))
process_A_net.add_transition(Transition("A_protein_degradation"))

# basic_example_net places
basic_example_net.add_place(Place("cell_A", [process_A_net]))
basic_example_net.add_place(Place("cell_B", [process_B_net]))

# basic_example_net transitions
basic_example_net.add_transition(Transition("juxtacrine_signaling_A_protein_cell_A_cell_B", Expression("str(x) == 'A_protein'")))

# basic_example_net arcs
basic_example_net.add_input("cell_A", "juxtacrine_signaling_A_protein_cell_A_cell_B", Variable('x'), notify=[process_A_net])
basic_example_net.add_output("cell_B", "juxtacrine_signaling_A_protein_cell_A_cell_B", Expression('x.replace("protein", "receptor_active_protein")'), notify=[process_B_net])

# process_A_net arcs
process_A_net.add_input("A_gene", "A_gene_transcription", Value(dot))
process_A_net.add_input("A_mrna", "A_mrna_translation", Value(dot))
process_A_net.add_input("A_protein", "A_protein_degradation", Value(dot), notify=[basic_example_net.place('cell_A')])
process_A_net.add_output("A_gene", "A_gene_transcription", Value(dot))
process_A_net.add_output("A_mrna", "A_gene_transcription", Value(dot))
process_A_net.add_output("A_protein", "A_mrna_translation", MultiArc([Value(dot)]*3), notify=[basic_example_net.place('cell_A')])

# process_B_net arcs
process_B_net.add_input("A_receptor_active_protein", "A_receptor_active_protein_degradation", Value(dot), notify=[basic_example_net.place('cell_B')])

```
The complete source code for this example, and additional ones, can be found in the [examples](./examples) folder.

Useful links
------------
* [petrisim](https://github.com/leonardogian/nwn-petrisim), Nets within Nets simulator for Petri Nets modeled using 
  nwn-snakes.
* [bisdl2](https://github.com/leonardogian/nwn-bisdl2), the high-level Biology System Description Language (BiSDL) and 
  compiler to nwn-snakes syntax.
* [SNAKES homepage](http://www.ibisc.univ-evry.fr/~fpommereau/SNAKES/) with documentation, tutorial, and API reference 
of the original library by Franck Pommereau.

Copyright / Licence
-------------------
* [Original README with copyright notice](https://github.com/fpom/snakes/README.md)
