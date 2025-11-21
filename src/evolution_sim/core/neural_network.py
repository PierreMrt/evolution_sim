"""Neural network implementation for creature brains."""
import numpy as np
import numba
import random
from typing import List, Dict


# Backward compatibility wrappers for old Neuron and Connection classes
class Neuron:
    """Backward compatibility wrapper for neuron dict structure."""
    
    def __init__(self, neuron_id: int, neuron_type: str):
        """Initialize a neuron wrapper."""
        self.id = neuron_id
        self.type = neuron_type
        self.value = 0.0
        self.bias = random.uniform(-2, 2)
    
    def activate(self, x: float) -> float:
        """Apply sigmoid activation function."""
        return 1 / (1 + np.exp(-max(-20, min(20, x))))


class Connection:
    """Backward compatibility wrapper for connection dict structure."""
    
    def __init__(self, from_neuron: int, to_neuron: int, weight: float, enabled: bool = True):
        """Initialize a connection wrapper."""
        self.from_neuron = from_neuron
        self.to_neuron = to_neuron
        self.weight = weight
        self.enabled = enabled
        self.innovation = (from_neuron, to_neuron)


@numba.njit(cache=True, fastmath=True)
def sigmoid(x: float) -> float:
    """
    Sigmoid activation with clipping to avoid overflow.
    """
    x = max(-20.0, min(20.0, x))
    return 1.0 / (1.0 + np.exp(-x))


@numba.njit(cache=True, fastmath=True)
def forward_pass(
    inputs: np.ndarray,
    neuron_biases: np.ndarray,
    conn_from: np.ndarray,
    conn_to: np.ndarray,
    conn_weights: np.ndarray,
    conn_enabled: np.ndarray,
    neuron_types: np.ndarray,
    n_inputs: int,
    n_outputs: int
) -> np.ndarray:
    """
    Numba-accelerated feedforward inference.
    neuron_types: 0=input, 1=hidden, 2=output.
    All arrays must be contiguous, shape-documented.
    - neuron_biases: (n_total,)
    - conn_from, conn_to: (n_connections,)
    - conn_weights, conn_enabled: (n_connections,)
    - neuron_types: (n_total,)
    - inputs: (n_inputs,)
    """
    n_total = neuron_types.shape[0]
    neuron_values = np.zeros(n_total, dtype=np.float32)
    # Set input neurons
    for i in range(n_inputs):
        neuron_values[i] = inputs[i]
    # Process all non-inputs in order (assuming correct topological order)
    for i in range(n_inputs, n_total):
        acc = neuron_biases[i]
        for j in range(conn_from.shape[0]):
            if conn_enabled[j] and conn_to[j] == i:
                acc += neuron_values[conn_from[j]] * conn_weights[j]
        neuron_values[i] = sigmoid(acc)
    # Collect output neurons
    outputs = []
    for i in range(n_total):
        if neuron_types[i] == 2:
            outputs.append(neuron_values[i])
            if len(outputs) == n_outputs:
                break
    return np.array(outputs, dtype=np.float32)


class NeuralNetwork:
    """
    Numba-optimized feedforward network for evolutionary simulation.
    Mutable topology for evolution; array-based inference for speed.
    Neuron type: 0=input, 1=hidden, 2=output.
    """
    def __init__(self):
        """Initialize an empty neural network."""
        self.neurons: Dict[int, Dict] = {}
        self.connections: List[Dict] = []
        self.next_neuron_id: int = 0

        # Compiled NumPy arrays (initialized on first compile)
        self._neuron_biases: np.ndarray = None
        self._conn_from: np.ndarray = None
        self._conn_to: np.ndarray = None
        self._conn_weights: np.ndarray = None
        self._conn_enabled: np.ndarray = None
        self._neuron_types: np.ndarray = None
        self._n_inputs: int = 0
        self._n_outputs: int = 0
        self._compiled: bool = False

    def add_neuron(self, neuron_type: str) -> int:
        """
        Add a neuron.
        neuron_type: 'input', 'hidden', or 'output'
        """
        neuron_id = self.next_neuron_id
        type_idx = {'input': 0, 'hidden': 1, 'output': 2}[neuron_type]
        self.neurons[neuron_id] = {
            'id': neuron_id,
            'type': neuron_type,
            'type_idx': type_idx,
            'bias': np.float32(random.uniform(-2, 2))
        }
        self.next_neuron_id += 1
        self._compiled = False
        return neuron_id

    def add_connection(self, from_id: int, to_id: int, weight: float, enabled: bool = True) -> None:
        """
        Add a connection if not a duplicate; allow dynamic topology.
        """
        for conn in self.connections:
            if conn['from'] == from_id and conn['to'] == to_id:
                return
        self.connections.append({'from': from_id, 'to': to_id, 'weight': np.float32(weight), 'enabled': enabled})
        self._compiled = False

    def _compile_to_arrays(self) -> None:
        """
        Convert neurons/connections to contiguous NumPy arrays for Numba.
        Call after any mutation or topology change.
        """
        n_total = len(self.neurons)
        if n_total == 0:
            self._compiled = True
            return
        ids = sorted(self.neurons.keys())
        id_map = {nid: i for i, nid in enumerate(ids)}
        biases = np.zeros(n_total, dtype=np.float32)
        types = np.zeros(n_total, dtype=np.int32)
        type_strs = [self.neurons[nid]['type'] for nid in ids]
        for i, nid in enumerate(ids):
            biases[i] = self.neurons[nid]['bias']
            types[i] = self.neurons[nid]['type_idx']
        # Connections to parallel arrays
        conn_from, conn_to, conn_weights, conn_enabled = [], [], [], []
        for conn in self.connections:
            if conn['from'] in id_map and conn['to'] in id_map:
                conn_from.append(id_map[conn['from']])
                conn_to.append(id_map[conn['to']])
                conn_weights.append(conn['weight'])
                conn_enabled.append(conn['enabled'])
        self._neuron_biases = np.ascontiguousarray(biases)
        self._neuron_types = np.ascontiguousarray(types)
        self._conn_from = np.ascontiguousarray(np.array(conn_from, dtype=np.int32))
        self._conn_to = np.ascontiguousarray(np.array(conn_to, dtype=np.int32))
        self._conn_weights = np.ascontiguousarray(np.array(conn_weights, dtype=np.float32))
        self._conn_enabled = np.ascontiguousarray(np.array(conn_enabled, dtype=np.bool_))
        self._n_inputs = type_strs.count('input')
        self._n_outputs = type_strs.count('output')
        self._compiled = True

    def forward(self, inputs: List[float]) -> List[float]:
        """
        Inference: calls Numba-accelerated forward_pass.
        """
        if not self._compiled:
            self._compile_to_arrays()
        arr_inputs = np.zeros(self._n_inputs, dtype=np.float32)
        for i in range(min(len(inputs), self._n_inputs)):
            arr_inputs[i] = np.float32(inputs[i])
        output = forward_pass(
            arr_inputs, self._neuron_biases, self._conn_from, self._conn_to,
            self._conn_weights, self._conn_enabled, self._neuron_types,
            self._n_inputs, self._n_outputs
        )
        return output.tolist()

    def copy(self) -> "NeuralNetwork":
        """
        Deep copy supporting arrays and dicts.
        """
        new_net = NeuralNetwork()
        new_net.next_neuron_id = self.next_neuron_id
        new_net.neurons = {nid: dict(neuron) for nid, neuron in self.neurons.items()}
        new_net.connections = [dict(conn) for conn in self.connections]
        new_net._compile_to_arrays()
        return new_net
