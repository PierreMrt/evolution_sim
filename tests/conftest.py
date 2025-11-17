"""Pytest configuration and shared fixtures."""
import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'neural_network': {
            'input_neurons': 8,
            'output_neurons': 3,
            'max_neurons': 20,
            'vision_range': 150
        },
        'creatures': {
            'max_energy': 100,
            'herbivore_radius': 8,
            'carnivore_radius': 10
        },
        'evolution': {
            'mutation_rate': 0.3,
            'weight_mutation_strength': 0.3
        }
    }
