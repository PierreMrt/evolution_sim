import matplotlib.pyplot as plt
import numpy as np

VISION_RANGE = 150  # From config.yaml

def plot_spatial_distribution(frame, plants_df, creatures_df, global_df, title_suffix="", show_vision=False):
    """
    Plot spatial distribution at a specific frame.
    
    Args:
        frame: Frame number to plot
        title_suffix: Additional text for title
        show_vision: If True, draw vision range circles around creatures
    """
    # Get data for this frame
    frame_plants = plants_df[plants_df['frame'] == frame]
    frame_creatures = creatures_df[creatures_df['frame'] == frame]
    
    if len(frame_creatures) == 0:
        print(f"⚠️  No creatures at frame {frame} - likely extinction event")
        return
    
    herbivores = frame_creatures[frame_creatures['creature_type'] == 'herbivore']
    carnivores = frame_creatures[frame_creatures['creature_type'] == 'carnivore']
    
    # Get global metrics for this frame
    global_metrics = global_df[global_df['frame'] == frame]
    if len(global_metrics) > 0:
        avg_energy = global_metrics.iloc[0]['avg_energy']
        total_pop = global_metrics.iloc[0]['total_population']
    else:
        avg_energy = "N/A"
        total_pop = len(frame_creatures)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Plot plants
    ax.scatter(frame_plants['plant_x'], frame_plants['plant_y'], 
               c='green', s=15, alpha=0.4, label=f'Plants ({len(frame_plants)})', 
               marker='o', edgecolors='none')
    
    # Plot herbivores with energy-based coloring
    if len(herbivores) > 0:
        scatter_h = ax.scatter(herbivores['pos_x'], herbivores['pos_y'], 
                              c=herbivores['energy'], cmap='Blues', 
                              s=100, label=f'Herbivores ({len(herbivores)})',
                              vmin=0, vmax=100, edgecolors='black', linewidth=0.5)
        
        # Optional: Show vision range for a few herbivores
        if show_vision:
            for idx, (_, creature) in enumerate(herbivores.head(5).iterrows()):
                circle = plt.Circle((creature['pos_x'], creature['pos_y']), 
                                   VISION_RANGE, color='blue', fill=False, 
                                   alpha=0.2, linestyle='--', linewidth=1)
                ax.add_patch(circle)
    
    # Plot carnivores with energy-based coloring
    if len(carnivores) > 0:
        scatter_c = ax.scatter(carnivores['pos_x'], carnivores['pos_y'], 
                              c=carnivores['energy'], cmap='Reds', 
                              s=150, label=f'Carnivores ({len(carnivores)})',
                              vmin=0, vmax=100, edgecolors='black', linewidth=0.5,
                              marker='s')
        
        # Optional: Show vision range for carnivores
        if show_vision:
            for _, creature in carnivores.head(3).iterrows():
                circle = plt.Circle((creature['pos_x'], creature['pos_y']), 
                                   VISION_RANGE, color='red', fill=False, 
                                   alpha=0.2, linestyle='--', linewidth=1)
                ax.add_patch(circle)
    
    # Add colorbars
    if len(herbivores) > 0:
        cbar_h = plt.colorbar(scatter_h, ax=ax, pad=0.02, aspect=30)
        cbar_h.set_label('Herbivore Energy', rotation=270, labelpad=15)
    
    if len(carnivores) > 0:
        cbar_c = plt.colorbar(scatter_c, ax=ax, pad=0.08, aspect=30)
        cbar_c.set_label('Carnivore Energy', rotation=270, labelpad=15)
    
    # Formatting
    ax.set_xlim(0, 1220)
    ax.set_ylim(0, 1080)
    ax.set_xlabel('X Position', fontsize=12)
    ax.set_ylabel('Y Position', fontsize=12)
    ax.set_title(f'Spatial Distribution at Frame {frame}{title_suffix}\n'
                 f'Population: {total_pop} | Avg Energy: {avg_energy}', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.show()


def plot_density_heatmap(frame, plants_df, creatures_df, global_df, title_suffix=""):
    """
    Plot density heatmap showing resource and creature concentrations.
    
    Args:
        frame: Frame number to plot
        title_suffix: Additional text for title
    """
    frame_plants = plants_df[plants_df['frame'] == frame]
    frame_creatures = creatures_df[creatures_df['frame'] == frame]
    herbivores = frame_creatures[frame_creatures['creature_type'] == 'herbivore']
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plant density heatmap
    if len(frame_plants) > 0:
        heatmap, xedges, yedges = np.histogram2d(
            frame_plants['plant_x'], frame_plants['plant_y'],
            bins=[24, 20], range=[[0, 1220], [0, 1080]]
        )
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        
        im1 = axes[0].imshow(heatmap.T, extent=extent, origin='lower', 
                            cmap='Greens', interpolation='bilinear', aspect='auto')
        axes[0].set_title(f'Plant Density at Frame {frame}', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('X Position')
        axes[0].set_ylabel('Y Position')
        plt.colorbar(im1, ax=axes[0], label='Plant Count per Region')
    
    # Herbivore density heatmap
    if len(herbivores) > 0:
        heatmap, xedges, yedges = np.histogram2d(
            herbivores['pos_x'], herbivores['pos_y'],
            bins=[24, 20], range=[[0, 1220], [0, 1080]]
        )
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        
        im2 = axes[1].imshow(heatmap.T, extent=extent, origin='lower', 
                            cmap='Blues', interpolation='bilinear', aspect='auto')
        axes[1].set_title(f'Herbivore Density at Frame {frame}', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('X Position')
        axes[1].set_ylabel('Y Position')
        plt.colorbar(im2, ax=axes[1], label='Herbivore Count per Region')
    
    plt.suptitle(f'Resource vs Consumer Distribution{title_suffix}', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()


def analyze_nearest_neighbor_distances(frame, plants_df, creatures_df):
    """
    Calculate and visualize nearest neighbor distances for resource finding.
    
    Args:
        frame: Frame number to analyze
    """
    frame_plants = plants_df[plants_df['frame'] == frame]
    frame_creatures = creatures_df[creatures_df['frame'] == frame]
    herbivores = frame_creatures[frame_creatures['creature_type'] == 'herbivore']
    
    if len(herbivores) == 0 or len(frame_plants) == 0:
        print(f"⚠️  Insufficient data at frame {frame}")
        return
    
    # Calculate distance from each herbivore to nearest plant
    nearest_plant_distances = []
    for _, herb in herbivores.iterrows():
        distances = np.sqrt(
            (frame_plants['plant_x'] - herb['pos_x'])**2 + 
            (frame_plants['plant_y'] - herb['pos_y'])**2
        )
        nearest_plant_distances.append(distances.min())
    
    # Plot distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(nearest_plant_distances, bins=30, color='green', alpha=0.7, edgecolor='black')
    ax.axvline(VISION_RANGE, color='red', linestyle='--', linewidth=2, 
               label=f'Vision Range ({VISION_RANGE}px)')
    ax.axvline(np.mean(nearest_plant_distances), color='blue', linestyle='--', 
               linewidth=2, label=f'Mean Distance ({np.mean(nearest_plant_distances):.1f}px)')
    
    # Calculate stats
    beyond_vision = sum(d > VISION_RANGE for d in nearest_plant_distances)
    pct_beyond = (beyond_vision / len(nearest_plant_distances)) * 100
    
    ax.set_xlabel('Distance to Nearest Plant (pixels)', fontsize=12)
    ax.set_ylabel('Number of Herbivores', fontsize=12)
    ax.set_title(f'Herbivore Food Accessibility at Frame {frame}\n'
                 f'{pct_beyond:.1f}% of herbivores cannot see food', 
                 fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    print(f"  Mean distance to food: {np.mean(nearest_plant_distances):.1f}px")
    print(f"  {pct_beyond:.1f}% herbivores beyond vision range")
    plt.show()