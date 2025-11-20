"""Example script showing how to load and query analysis data."""

import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


def load_simulation_data(run_dir: str):
    """
    Load all analysis data from a simulation run.
    
    Args:
        run_dir: Path to simulation run directory
        
    Returns:
        Tuple of (global_df, creatures_df, plants_df)
    """
    run_path = Path(run_dir)
    
    # Load Parquet files
    global_df = pd.read_parquet(run_path / "global_metrics.parquet")
    creatures_df = pd.read_parquet(run_path / "creature_snapshots.parquet")
    plants_df = pd.read_parquet(run_path / "plant_positions.parquet")
    
    print(f"Loaded {len(global_df)} global metrics")
    print(f"Loaded {len(creatures_df)} creature snapshots")
    print(f"Loaded {len(plants_df)} plant positions")
    
    return global_df, creatures_df, plants_df


def analyze_population_dynamics(global_df: pd.DataFrame):
    """Analyze population dynamics over time."""
    print("\n=== Population Dynamics ===")
    print(f"Total frames: {global_df['frame'].max()}")
    print(f"Peak total population: {global_df['total_population'].max()}")
    print(f"Average herbivore count: {global_df['herbivore_count'].mean():.1f}")
    print(f"Average carnivore count: {global_df['carnivore_count'].mean():.1f}")
    
    # Plot population over time
    plt.figure(figsize=(12, 6))
    plt.plot(global_df['frame'], global_df['herbivore_count'], label='Herbivores', color='blue')
    plt.plot(global_df['frame'], global_df['carnivore_count'], label='Carnivores', color='red')
    plt.plot(global_df['frame'], global_df['plant_count'], label='Plants', color='green', alpha=0.5)
    plt.xlabel('Frame')
    plt.ylabel('Count')
    plt.title('Population Dynamics Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('population_dynamics.png', dpi=150)
    print("Saved: population_dynamics.png")


def analyze_neural_evolution(global_df: pd.DataFrame):
    """Analyze neural network evolution."""
    print("\n=== Neural Network Evolution ===")
    print(f"Initial avg neurons: {global_df['avg_neurons'].iloc[0]:.1f}")
    print(f"Final avg neurons: {global_df['avg_neurons'].iloc[-1]:.1f}")
    print(f"Initial avg connections: {global_df['avg_connections'].iloc[0]:.1f}")
    print(f"Final avg connections: {global_df['avg_connections'].iloc[-1]:.1f}")
    
    # Plot neural complexity over time
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    ax1.plot(global_df['frame'], global_df['avg_neurons'], color='purple')
    ax1.set_ylabel('Average Neurons')
    ax1.set_title('Neural Network Complexity Evolution')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(global_df['frame'], global_df['avg_connections'], color='orange')
    ax2.set_xlabel('Frame')
    ax2.set_ylabel('Average Connections')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('neural_evolution.png', dpi=150)
    print("Saved: neural_evolution.png")


def analyze_creature_behavior(creatures_df: pd.DataFrame):
    """Analyze individual creature behavior."""
    print("\n=== Creature Behavior Analysis ===")
    
    # Group by creature type
    herbivores = creatures_df[creatures_df['creature_type'] == 'herbivore']
    carnivores = creatures_df[creatures_df['creature_type'] == 'carnivore']
    
    print(f"\nHerbivores:")
    print(f"  Average fitness: {herbivores['fitness'].mean():.2f}")
    print(f"  Average food eaten: {herbivores['food_eaten'].mean():.2f}")
    print(f"  Average distance: {herbivores['distance_traveled'].mean():.2f}")
    
    print(f"\nCarnivores:")
    print(f"  Average fitness: {carnivores['fitness'].mean():.2f}")
    print(f"  Average food eaten: {carnivores['food_eaten'].mean():.2f}")
    print(f"  Average distance: {carnivores['distance_traveled'].mean():.2f}")
    
    # Find most successful creatures
    print("\n=== Top 10 Creatures by Fitness ===")
    top_creatures = creatures_df.nlargest(10, 'fitness')[
        ['creature_id', 'creature_type', 'fitness', 'food_eaten', 'children_count', 'generation']
    ]
    print(top_creatures.to_string(index=False))


def find_bottlenecks(global_df: pd.DataFrame):
    """Identify potential bottlenecks in the simulation."""
    print("\n=== Bottleneck Analysis ===")
    
    # Find frames with low population
    low_pop_threshold = global_df['total_population'].quantile(0.1)
    bottlenecks = global_df[global_df['total_population'] < low_pop_threshold]
    
    if len(bottlenecks) > 0:
        print(f"Found {len(bottlenecks)} frames with critically low population (<{low_pop_threshold:.0f})")
        print(f"Lowest population: {global_df['total_population'].min()} at frame {global_df.loc[global_df['total_population'].idxmin(), 'frame']}")
    
    # Check energy levels
    low_energy_frames = global_df[global_df['avg_energy'] < 30]
    if len(low_energy_frames) > 0:
        print(f"Found {len(low_energy_frames)} frames with low average energy (<30)")
    
    # Check for extinction events
    extinctions = global_df[
        (global_df['herbivore_count'] == 0) | (global_df['carnivore_count'] == 0)
    ]
    if len(extinctions) > 0:
        print(f"Warning: {len(extinctions)} frames with extinct species!")


def main():
    """Main analysis workflow."""
    # Replace with your actual run directory
    run_dir = "simulation_data/run_20251120_220000"
    
    # Load data
    global_df, creatures_df, plants_df = load_simulation_data(run_dir)
    
    # Run analyses
    analyze_population_dynamics(global_df)
    analyze_neural_evolution(global_df)
    analyze_creature_behavior(creatures_df)
    find_bottlenecks(global_df)
    
    print("\n=== Analysis Complete ===")


if __name__ == "__main__":
    main()
