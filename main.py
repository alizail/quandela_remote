import perceval as pcvl
import qiskit
from perceval.components import BS, PERM, Port, PS, Unitary, Circuit
from perceval.utils import Encoding, Matrix, PostSelect
from deprecated import deprecated
import numpy as np
from perceval.converters import QiskitConverter
from perceval.components.component_catalog import CatalogItem, AsType


theta1 = 2*np.pi*54.74/180
theta2 = 2*np.pi*17.63/180


def get_CCZ() -> pcvl.Processor:
    # reference
    cz = (pcvl.Circuit(4, name="CZ")
            .add(0, pcvl.PS(np.pi), x_grid=1)
            .add(3, pcvl.PS(np.pi), x_grid=1)
            .add(0, pcvl.PERM([0,2,1,3]))
            .add([0,1], pcvl.BS.H(theta=theta1), x_grid=2)
            .add([2,3], pcvl.BS.H(theta=theta1), x_grid=2)
            .add(0, pcvl.PERM([0,2,1,3]))
            .add([0,1], pcvl.BS.H(theta=-theta1))
            .add([2,3], pcvl.BS.H(theta=theta2)))
    
    ccz = (pcvl.Circuit(8, name="CCZ")
                .add(1, PERM([1, 0]))
                .add(2, cz, merge=True)
                .add(4, cz, merge=True)
                .add(1, PERM([1, 0])))
    
    processor = pcvl.Processor("SLOS", ccz)

    processor.add_port(0, Port(Encoding.DUAL_RAIL, 'ctrl0')) \
            .add_port(2, Port(Encoding.DUAL_RAIL, 'ctrl1')) \
            .add_port(4, Port(Encoding.DUAL_RAIL, 'data')) \
            .add_herald(6, 1) \
            .add_herald(7, 1)
    
    processor.set_postselection(pcvl.PostSelect("[0,1]==1 & [2,3]==1 & [4,5]==1")) 
    
    return processor

def get_CZ():
    # Generate cz gate
    cz = (pcvl.Circuit(4, name="CZ")
            .add(0, pcvl.PS(np.pi), x_grid=1)
            .add(3, pcvl.PS(np.pi), x_grid=1)
            .add(0, pcvl.PERM([0,2,1,3]))
            .add([0,1], pcvl.BS.H(theta=theta1), x_grid=2)
            .add([2,3], pcvl.BS.H(theta=theta1), x_grid=2)
            .add(0, pcvl.PERM([0,2,1,3]))
            .add([0,1], pcvl.BS.H(theta=-theta1))
            .add([2,3], pcvl.BS.H(theta=theta2)))
    
    hcz = (pcvl.Circuit(6, name="Heralded CZ")
                .add(2, pcvl.BS.H())
                .add(1, PERM([1, 0]))
                .add(2, cz, merge=True)
                .add(1, PERM([1, 0]))
                .add(2, pcvl.BS.H()))
    
    p = pcvl.Processor("SLOS", hcz)

    p.add_port(0, Port(Encoding.DUAL_RAIL, 'ctrl')) \
            .add_port(2, Port(Encoding.DUAL_RAIL, 'data')) \
            .add_herald(4, 1) \
            .add_herald(5, 1)
    
    p.set_postselection(pcvl.PostSelect("[0,1]==1 & [2,3]==1"))  # Add a post-selection checking for a logical output state
    
    pcvl.pdisplay(p, recursive=True)
    
    states = {
        pcvl.BasicState([1, 0, 1, 0]): "00",
        pcvl.BasicState([1, 0, 0, 1]): "01",
        pcvl.BasicState([0, 1, 1, 0]): "10",
        pcvl.BasicState([0, 1, 0, 1]): "11"
    }

    ca = pcvl.algorithm.Analyzer(oooo, states)

    truth_table = {"00": "00", "01": "01", "10": "11", "11": "10"}
    ca.compute(expected=truth_table)

    pcvl.pdisplay(ca)
    print(
        f"performance = {ca.performance}, fidelity = {ca.fidelity.real}")

def CCZ_gate_qiskit(circ, ctrl1, ctrl2, targ):
    # Apply ccz gate to a 3 qubit qiskit circuit
    circ.h(targ)
    circ.h(targ)
    circ.cx(ctrl1,targ)
    circ.tdg(targ)
    circ.cx(ctrl2, targ)
    circ.t(targ)
    circ.cx(ctrl1,targ)
    circ.t(ctrl2)
    circ.cx(ctrl1,targ)
    circ.t(ctrl1)
    circ.h(targ)
    circ.h(targ)

def get_CCZ_qiskit():
    # Use qiskit to create the gate, then convert
    qc = qiskit.QuantumCircuit(3)
    CCZ_gate_qiskit(qc,0,1,2)

    print(qc.draw())

    qiskit_convertor = QiskitConverter(pcvl.catalog)
    processor = qiskit_convertor.convert(qc, use_postselection=True)

    pcvl.pdisplay(processor, recursive=True)
    return processor

def get_CCZ_catalog():
    # Use the gate from the catalog
    return pcvl.catalog['postprocessed ccz'].build_processor()