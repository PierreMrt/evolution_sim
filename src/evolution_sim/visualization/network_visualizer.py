"""Neural network visualization."""

import pygame
import math
from typing import TYPE_CHECKING, Dict, Tuple, List

if TYPE_CHECKING:
    from ..core.neural_network import NeuralNetwork, Neuron

class NetworkVisualizer:
    """Visualizes neural network structure and activations."""
    
    def __init__(self):
        """Initialize the network visualizer."""
        self.font = pygame.font.Font(None, 16)
        self.small_font = pygame.font.Font(None, 12)
    
    def draw_network(self, screen: pygame.Surface, network: 'NeuralNetwork', 
                     x: int, y: int, width: int, height: int) -> None:
        """
        Draw the neural network visualization.
        
        Args:
            screen: Pygame surface to draw on
            network: Neural network to visualize
            x, y: Top-left position
            width, height: Size of visualization area
        """
        if not network or not network.neurons:
            return
        
        # Separate neurons by type
        input_neurons = [n for n in network.neurons.values() if n['type'] == 'input']
        hidden_neurons = [n for n in network.neurons.values() if n['type'] == 'hidden']
        output_neurons = [n for n in network.neurons.values() if n['type'] == 'output']
        
        # Calculate positions for neurons
        positions = self._calculate_positions(
            input_neurons, hidden_neurons, output_neurons,
            x, y, width, height
        )
        
        # Draw connections first (so they're behind neurons)
        self._draw_connections(screen, network, positions)
        
        # Draw neurons
        self._draw_neurons(screen, input_neurons, positions, (100, 200, 255))  # Blue for input
        self._draw_neurons(screen, hidden_neurons, positions, (150, 150, 255))  # Purple for hidden
        self._draw_neurons(screen, output_neurons, positions, (255, 150, 100))  # Orange for output
        
        # Draw labels
        self._draw_labels(screen, x, y, width, len(input_neurons), len(hidden_neurons), len(output_neurons))
    
    def _calculate_positions(self, input_neurons: List, hidden_neurons: List, 
                            output_neurons: List, x: int, y: int, 
                            width: int, height: int) -> Dict[int, Tuple[float, float]]:
        """Calculate screen positions for all neurons."""
        positions = {}
        
        margin_x = 60
        margin_y = 60
        layer_width = (width - 2 * margin_x) / 3
        
        # Input neurons - left column
        if input_neurons:
            spacing = (height - 2 * margin_y) / max(1, len(input_neurons) - 1) if len(input_neurons) > 1 else 0
            for i, neuron in enumerate(input_neurons):
                pos_x = x + margin_x
                pos_y = y + margin_y + i * spacing if len(input_neurons) > 1 else y + height / 2
                positions[neuron['id']] = (pos_x, pos_y)
        
        # Hidden neurons - middle column(s)
        if hidden_neurons:
            spacing = (height - 2 * margin_y) / max(1, len(hidden_neurons) - 1) if len(hidden_neurons) > 1 else 0
            for i, neuron in enumerate(hidden_neurons):
                pos_x = x + margin_x + layer_width * 1.5
                pos_y = y + margin_y + i * spacing if len(hidden_neurons) > 1 else y + height / 2
                positions[neuron['id']] = (pos_x, pos_y)
        
        # Output neurons - right column
        if output_neurons:
            spacing = (height - 2 * margin_y) / max(1, len(output_neurons) - 1) if len(output_neurons) > 1 else 0
            for i, neuron in enumerate(output_neurons):
                pos_x = x + width - margin_x
                pos_y = y + margin_y + i * spacing if len(output_neurons) > 1 else y + height / 2
                positions[neuron['id']] = (pos_x, pos_y)
        
        return positions
    
    def _draw_connections(self, screen: pygame.Surface, network: 'NeuralNetwork', 
                         positions: Dict[int, Tuple[float, float]]) -> None:
        """Draw all connections between neurons."""
        for conn in network.connections:
            if not conn['enabled']:
                continue
            
            if conn['from'] not in positions or conn['to'] not in positions:
                continue
            
            from_pos = positions[conn['from']]
            to_pos = positions[conn['to']]
            
            # Color based on weight (red for negative, green for positive)
            weight = conn['weight']
            if weight > 0:
                # Positive weights in green
                intensity = min(255, int(abs(weight) * 127))
                color = (0, intensity, 0)
            else:
                # Negative weights in red
                intensity = min(255, int(abs(weight) * 127))
                color = (intensity, 0, 0)
            
            # Line thickness based on weight magnitude
            thickness = max(1, min(3, int(abs(weight) * 2)))
            
            pygame.draw.line(screen, color, from_pos, to_pos, thickness)
    
    def _draw_neurons(self, screen: pygame.Surface, neurons: List, 
                     positions: Dict[int, Tuple[float, float]], color: Tuple[int, int, int]) -> None:
        """Draw neuron circles with activation values."""
        for neuron in neurons:
            if neuron['id'] not in positions:
                continue
            
            pos = positions[neuron['id']]
            
            # Neuron size
            radius = 12
            
            # Activation intensity (brighter = more activated)
            # For the new dict-based structure, we don't store activation values
            # So we use bias as a proxy or default to neutral
            activation = 0.5  # Default neutral activation
            brightness = int(activation * 200) + 55  # Map [0,1] to [55,255]
            
            # Draw neuron circle
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), radius)
            
            # Draw activation overlay (white glow)
            if activation > 0.1:
                overlay_radius = int(radius * 0.7)
                overlay_color = (brightness, brightness, brightness)
                pygame.draw.circle(screen, overlay_color, (int(pos[0]), int(pos[1])), overlay_radius)
            
            # Draw neuron ID
            id_text = self.small_font.render(str(neuron['id']), True, (0, 0, 0))
            text_rect = id_text.get_rect(center=pos)
            screen.blit(id_text, text_rect)
    
    def _draw_labels(self, screen: pygame.Surface, x: int, y: int, width: int,
                    n_input: int, n_hidden: int, n_output: int) -> None:
        """Draw layer labels."""
        label_y = y + 30
        
        # Input label
        input_label = self.small_font.render(f"Input ({n_input})", True, (100, 200, 255))
        screen.blit(input_label, (x + 10, label_y))
        
        # Hidden label
        if n_hidden > 0:
            hidden_label = self.small_font.render(f"Hidden ({n_hidden})", True, (150, 150, 255))
            screen.blit(hidden_label, (x + width // 2 - 30, label_y))
        
        # Output label
        output_label = self.small_font.render(f"Output ({n_output})", True, (255, 150, 100))
        screen.blit(output_label, (x + width - 70, label_y))
