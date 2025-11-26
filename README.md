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
- [Data Analysis](#data-analysis)
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

### Fix for Linux/Wayland users

If you encounter a segmentation fault on Linux with NVIDIA graphics:

```bash
SDL_VIDEODRIVER=wayland python -m evolution_sim
```

## 🎮 Quick Start

### Running the Simulation

After installation, run the simulation with:

```bash
python -m evolution_sim
```

### What You'll See

The simulation displays three main panels:

- **Center World** (1220×1080): 
  - **Green dots**: Plants (food for herbivores)
  - **Blue circles**: Herbivores (seek plants, avoid carnivores)
  - **Red circles**: Carnivores (hunt herbivores)
  - **Energy bars**: Green bars above creatures show their current energy level

- **Left Panel** (Statistics):
  - Real-time population counts (herbivores, carnivores, plants)
  - Species diversity information
  - Average neural network complexity (neurons and connections)
  - Population statistics and trends

- **Right Panel** (Creature Inspector):
  - Click on any creature to view its neural network visualization
  - Shows creature properties: age, energy, fitness, generation
  - Visual representation of neuron activations and connections

## 🧠 How It Works

### Neural Networks

Each creature possesses a neural network that receives sensory inputs and produces behavioral outputs:

**Inputs** (12 neurons):
- Bias (constant 1.0)
- Current energy level (normalized)
- Direction to nearest food (x, y)
- Direction to nearest threat (x, y)  
- Direction to nearest prey (x, y)
- Time since last reproduction (normalized)
- Population density around creature

**Outputs** (4 neurons):
- Movement in X direction
- Movement in Y direction
- Action trigger (eat/attack)
- Migration trigger (long-distance movement)

### Evolution Process

1. **Mutation**: Networks randomly mutate by:
   - Adjusting connection weights
   - Adding new neurons and connections
   - Removing neurons
   - Modifying neuron biases

2. **Selection**: Creatures with higher fitness (food eaten, survival time, reproduction success) are more likely to reproduce

3. **Reproduction**: Successful creatures create offspring with mutated copies of their neural networks
   - Minimum reproductive age prevents immature breeding
   - Age-based senescence reduces reproduction capability in older creatures

4. **Speciation**: Similar creatures are grouped into species using genetic distance to maintain diversity

5. **Migration**: Creatures can evolve the ability to migrate long distances when environmental conditions change (controlled by 4th neural output)

### Ecosystem Dynamics

- **Herbivores** consume plants to gain energy and avoid predators
- **Carnivores** hunt herbivores for energy, with improved predatory capabilities
- **Plants** regenerate over time based on growth rate
- **Energy** depletes through movement and metabolism costs
- **Death** occurs when energy reaches zero or from predation
- **Reproduction** requires sufficient energy reserves and must meet age requirements
- **Senescence** reduces reproductive capacity in older creatures while maintaining lifespan
- **Migration** allows creatures to escape resource-depleted areas and seek new opportunities

## ⚙️ Configuration

All simulation parameters can be adjusted in `config/config.yaml`:

### Display Settings

```yaml
display:
  window_width: 1920              # Total window width
  window_height: 1080             # Total window height
  fps: 60
  
  # Left panel (statistics and population info)
  left_panel_x: 0
  left_panel_width: 350
  
  # Center viewport (world simulation)
  world_x: 350          
  world_y: 0
  world_viewport_width: 1220      # Center simulation area
  world_viewport_height: 1080
  
  # Right panel (selected creature neural network visualization)
  right_panel_x: 1570
  right_panel_width: 350
```

### Evolution Parameters

```yaml
evolution:
  mutation_rate: 0.3              # Probability of mutation
  add_neuron_rate: 0.10           # Chance to add new neuron
  remove_neuron_rate: 0.03        # Chance to remove neuron
  add_connection_rate: 0.1        # Chance to add new connection
  weight_mutation_rate: 0.8       # Chance to mutate weights
  weight_mutation_strength: 0.3   # Magnitude of weight changes
  species_divergence_threshold: 3.0  # Genetic distance for speciation
  tournament_size: 3              # Size of tournament selection
  elite_count: 2                  # Top creatures preserved
  survival_rate: 0.5              # Percent of population that survives
  stagnation_limit: 15            # Generations before species extinction
```

### Population Settings

```yaml
creatures:
  initial_herbivores: 18          # Starting herbivore population
  initial_carnivores: 5           # Starting carnivore population
  max_energy: 100
  move_energy_cost: 0.1           # Energy consumed per movement step
  reproduction_energy_threshold: 65   # Min energy to reproduce
  reproduction_cost: 30           # Energy lost when reproducing
  herbivore_radius: 10            # Size of herbivores
  carnivore_radius: 14            # Size of carnivores (larger)
  
  # Age-based reproduction constraints
  herbivores_min_reproductive_age: 250     # Minimum age to reproduce
  herbivores_max_age_for_full_reproduction: 4000  # Age cap for full reproduction
  herbivores_senescence_period: 2000       # Post-reproductive lifespan
  carnivores_min_reproductive_age: 300
  carnivores_max_age_for_full_reproduction: 3800
  carnivores_senescence_period: 1800
  
  # Migration parameters
  migration_threshold: 0.7        # Neural output threshold for migration
  migration_energy_cost: 5        # Energy cost to migrate
  migration_cooldown: 300         # Steps between migrations
  migration_min_distance: 200     # Minimum migration distance
  migration_max_distance: 400     # Maximum migration distance
  
  # Reproduction urge
  reproduction_desire_threshold: 0.6  # Neural output threshold to reproduce

world:
  initial_plants: 320             # Starting plant count
  plant_growth_rate: 0.18         # Growth rate per step
  plant_energy: 20                # Energy from eating a plant
  herbivores_energy_eaten: 24     # Energy from hunting herbivore
```

### Neural Network Configuration

```yaml
neural_network:
  input_neurons: 12               # Includes energy, food direction, threats, age
  output_neurons: 4               # Movement X/Y, action, migration
  max_neurons: 30                 # Maximum network complexity
  vision_range: 150               # How far creatures can sense
```

## 📁 Project Structure

```
evolution-sim/
│
├── config/
│   └── config.yaml                    # Configuration parameters
│
├── src/evolution_sim/
│   │
│   ├── __init__.py                    # Package initialization
│   ├── __main__.py                    # Entry point (python -m evolution_sim)
│   ├── config.py                      # Configuration loader
│   ├── main.py                        # Main simulation loop
│   │
│   ├── core/                          # Core domain entities
│   │   ├── __init__.py
│   │   ├── creature.py                # Creature class (behavior, senses, actions)
│   │   ├── genome.py                  # Genetic encoding and mutations
│   │   └── neural_network.py          # Neural network implementation
│   │
│   ├── environment/                   # World simulation
│   │   ├── __init__.py
│   │   ├── resources.py               # Plant/resource management
│   │   └── world.py                   # Environment class (main simulation)
│   │
│   ├── evolution/                     # Evolutionary algorithms
│   │   ├── __init__.py
│   │   ├── evolution_tracker.py       # Track evolutionary progress
│   │   ├── mutation.py                # Mutation operators
│   │   ├── selection.py               # Selection algorithms
│   │   └── species.py                 # Species/speciation logic
│   │
│   └── visualization/                 # UI and rendering
│       ├── __init__.py
│       ├── left_panel.py              # Population statistics panel
│       ├── network_visualizer.py      # Neural network visualization
│       ├── renderer.py                # Main world renderer
│       ├── right_panel.py             # Creature inspector panel
│       └── ui.py                      # UI orchestration
│
├── tests/                             # Unit tests
│   ├── __init__.py
│   ├── conftest.py                    # Pytest configuration
│   ├── test_creature.py
│   ├── test_evolution.py
│   ├── test_genome.py
│   └── test_neural_network.py
│
├── docs/
│   └── architecture.md                # Architecture documentation
│
├── .gitignore
├── LICENCE
├── README.md
├── requirements.txt
└── setup.py
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

## 📊 Data Analysis

The simulation now includes a comprehensive data collection and analysis system:

### Data Collection

During simulation runs, detailed metrics are automatically collected:

- **Global Metrics** (every 10 frames): Population counts, energy statistics, birth/death rates, neural complexity
- **Creature Snapshots** (every 50 frames): Individual creature data including position, energy, age, fitness, and neural network stats

Data is automatically saved to Parquet format for efficient storage and analysis.

### Analysis Features

Located in `src/evolution_sim/analysis/`:

- **Storage Layer** (`infrastructure/`): Handles Parquet file I/O and data persistence
- **Domain Models** (`domain/`): Metrics and creature snapshot data classes
- **Analysis Facade** (`interfaces/`): High-level API for accessing simulation data
- **Buffer Management** (`application/`): Efficient data collection and batching


### Example Analysis Notebooks

Check `simulation_data/analysis/bottleneck_analysis.ipynb` for example analysis workflows and visualizations.

## 📈 Performance Tips

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

Start the simulation with:
```bash
SDL_VIDEODRIVER=wayland python -m evolution_sim
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

- [x] Real-time statistics and visualization
- [x] Multi-panel UI with creature inspector
- [x] Data collection and analysis system
- [x] Migration behavior
- [x] Age-based senescence
- [x] Advanced neural network features
- [ ] Save/load simulation states
- [ ] Sexual reproduction (crossover)
- [ ] Environmental hazards
- [ ] Web-based visualization
- [ ] GPU acceleration for neural networks
- [ ] Phylogenetic tree visualization
- [ ] Extended creature types (omnivores, scavengers)

## 📚 References

This project is inspired by:

- **NEAT** (NeuroEvolution of Augmenting Topologies)
- **The Bibites** - Digital Life Simulation
- **Primer** - Evolution Simulations on YouTube
- **Conway's Game of Life**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

- GitHub: [@PierreMrt](https://github.com/PierreMrt)

## 🙏 Acknowledgments

- Thanks to the Pygame community for the excellent graphics library
- Inspired by Kenneth Stanley's NEAT algorithm

---

**Made with ❤️ and evolutionary algorithms**
