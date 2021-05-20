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

[comment]: <> (### Example)

[comment]: <> (Additional examples can be found in the [examples]&#40;./examples&#41; folder.)

Useful links
------------
* [petrisim](https://github.com/leonardogian/nwn-petrisim), Nets within Nets simulator for Petri Nets modeled using nwn-snakes.
* [bisdl2](https://github.com/leonardogian/nwn-bisdl2), the companion high-level modeling language and compiler to nwn-snakes syntax.
* [SNAKES homepage](http://www.ibisc.univ-evry.fr/~fpommereau/SNAKES/) (documentation, tutorial, API reference, ...)

Copyright / Licence
-------------------
* [Original README with copyright notice](https://github.com/fpom/snakes/README.md)
