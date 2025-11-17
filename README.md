# Neural Evolution Ecosystem Simulation 🧬

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A real-time evolutionary simulation where creatures with neural network brains evolve through natural selection, mutation, and survival. Watch as herbivores learn to find food and avoid predators while carnivores develop hunting strategies—all driven by evolving neural networks.

## 🌟 Features

- **Neural Network Brains**: Each creature has a dynamic neural network that controls its behavior
- **NEAT-Inspired Evolution**: Networks evolve through mutations—adding/removing neurons and connections
- **Ecosystem Dynamics**: Predator-prey relationships with plants, herbivores, and carnivores
- **Species Divergence**: Creatures naturally form species through genetic similarity
- **Real-Time Visualization**: Watch evolution happen with live statistics and creature tracking
- **Configurable Parameters**: Easily adjust mutation rates, population sizes, and environmental factors

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Controls](#controls)
- [Advanced Usage](#advanced-usage)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/PierreMrt/evolution-sim.git
cd evolution-sim
```

2. **Create and activate a virtual environment**

```bash
# On Linux/Mac
python -m venv .venv
source .venv/bin/activate

# On Windows
python -m venv .venv
.venv\Scripts\activate
```

3. **Install the package**

```bash
pip install -e .
```

4. **Install development dependencies (optional)**

```bash
pip install -e ".[dev]"
```

### Fix for Linux/NVIDIA Users

If you encounter a segmentation fault on Linux with NVIDIA graphics:

```bash
export SDL_VIDEODRIVER=x11
```

Or add this line at the top of your `~/.bashrc`:

```bash
echo 'export SDL_VIDEODRIVER=x11' >> ~/.bashrc
```

## 🎮 Quick Start

### Running the Simulation

After installation, run the simulation with:

```bash
evolution-sim
```

Or navigate to the source directory:

```bash
cd src/evolution_sim
python main.py
```

### What You'll See

- **Green dots**: Plants (food for herbivores)
- **Blue circles**: Herbivores (seek plants, avoid carnivores)
- **Red circles**: Carnivores (hunt herbivores)
- **Energy bars**: Green bars above creatures show their current energy level
- **Statistics panel**: Real-time population counts and neural network complexity

## 🧠 How It Works

### Neural Networks

Each creature possesses a neural network that receives sensory inputs and produces behavioral outputs:

**Inputs** (8 neurons):
- Bias (constant 1.0)
- Current energy level
- Direction to nearest food (x, y)
- Direction to nearest threat (x, y)  
- Direction to nearest prey (x, y)

**Outputs** (3 neurons):
- Movement in X direction
- Movement in Y direction
- Action trigger (eat/attack)

### Evolution Process

1. **Mutation**: Networks randomly mutate by:
   - Adjusting connection weights
   - Adding new neurons
   - Removing neurons
   - Creating new connections
   - Modifying neuron biases

2. **Selection**: Creatures with higher fitness (food eaten, survival time) are more likely to reproduce

3. **Reproduction**: Successful creatures create offspring with mutated copies of their neural networks

4. **Speciation**: Similar creatures are grouped into species to maintain diversity

### Ecosystem Dynamics

- **Herbivores** consume plants to gain energy
- **Carnivores** hunt herbivores for energy
- **Plants** regenerate over time
- **Energy** depletes through movement and metabolism
- **Death** occurs when energy reaches zero or from predation
- **Reproduction** requires sufficient energy reserves

## ⚙️ Configuration

All simulation parameters can be adjusted in `config/config.yaml`:

### Display Settings

```yaml
display:
  window_width: 1200
  window_height: 800
  fps: 60
```

### Evolution Parameters

```yaml
evolution:
  mutation_rate: 0.3              # Probability of mutation
  add_neuron_rate: 0.05           # Chance to add new neuron
  remove_neuron_rate: 0.03        # Chance to remove neuron
  weight_mutation_strength: 0.3   # Magnitude of weight changes
```

### Population Settings

```yaml
creatures:
  initial_herbivores: 10
  initial_carnivores: 5
  max_energy: 100
  reproduction_energy_threshold: 70
```

### Neural Network Configuration

```yaml
neural_network:
  input_neurons: 8
  output_neurons: 3
  max_neurons: 20
  vision_range: 150
```

## 📁 Project Structure

```
evolution-sim/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── setup.py                     # Package configuration
├── requirements.txt             # Python dependencies
├── config/
│   └── config.yaml             # Simulation parameters
├── src/
│   └── evolution_sim/
│       ├── main.py             # Entry point
│       ├── config.py           # Configuration loader
│       ├── core/               # Core simulation logic
│       │   ├── neural_network.py
│       │   ├── genome.py
│       │   └── creature.py
│       ├── environment/        # World simulation
│       │   ├── resources.py
│       │   └── world.py
│       ├── evolution/          # Genetic algorithms
│       │   ├── mutation.py
│       │   ├── selection.py
│       │   └── species.py
│       └── visualization/      # Graphics and UI
│           ├── ui.py
│           ├── renderer.py
│           └── stats_display.py
├── tests/                      # Unit tests
│   ├── test_neural_network.py
│   ├── test_genome.py
│   ├── test_creature.py
│   └── test_evolution.py
└── docs/                       # Documentation
```

## 🎯 Controls

| Key | Action |
|-----|--------|
| `SPACE` | Pause/Resume simulation |
| `ESC` | Quit simulation |

## 🔬 Advanced Usage

### Customizing Creature Behavior

Edit `src/evolution_sim/core/creature.py` to modify how creatures interpret their neural network outputs:

```python
def think_and_act(self, environment):
    outputs = self.genome.network.forward(inputs)
    move_x = (outputs[0] - 0.5) * 2 * 3  # Adjust speed multiplier
    move_y = (outputs[1] - 0.5) * 2 * 3
    action = outputs[2] > 0.5  # Adjust threshold
```

### Adding New Sensory Inputs

Extend the `get_inputs()` method in `Creature` class:

```python
def get_inputs(self, environment):
    inputs = [1.0]  # Bias
    inputs.append(self.energy / max_energy)
    # Add your custom inputs here
    return inputs
```

Remember to update `config.yaml` to reflect the new input count.

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=evolution_sim --cov-report=html
```

## 📊 Performance Tips

- Reduce `fps` in config for faster evolution
- Lower `window_width` and `window_height` for better performance
- Decrease `initial_plants` for simpler ecosystems
- Adjust `max_neurons` to limit network complexity

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
pip install -e ".[dev]"
pre-commit install
```

### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Run before committing:

```bash
black src/
flake8 src/
mypy src/
```

## 🐛 Troubleshooting

### Segmentation Fault (Linux)

Set the SDL video driver:
```bash
export SDL_VIDEODRIVER=x11
```

### Slow Performance

- Lower the FPS in `config.yaml`
- Reduce creature population
- Decrease window size

### Import Errors

Make sure you installed the package:
```bash
pip install -e .
```

## 🗺️ Roadmap

- [ ] Save/load simulation states
- [ ] Export evolution data to CSV
- [ ] Add more creature types (omnivores, scavengers)
- [ ] Implement sexual reproduction (crossover)
- [ ] Add environmental hazards
- [ ] Web-based visualization
- [ ] GPU acceleration for neural networks
- [ ] Phylogenetic tree visualization

## 📚 References

This project is inspired by:

- **NEAT** (NeuroEvolution of Augmenting Topologies)
- **The Bibites** - Digital Life Simulation
- **Primer** - Evolution Simulations on YouTube
- **Conway's Game of Life**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**
- GitHub: [@PierreMrt](https://github.com/PierreMrt)

## 🙏 Acknowledgments

- Thanks to the Pygame community for the excellent graphics library
- Inspired by Kenneth Stanley's NEAT algorithm

---

**Made with ❤️ and evolutionary algorithms**
