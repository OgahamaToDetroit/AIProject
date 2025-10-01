import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
from argparse import Namespace

# Import the necessary components from the project
from pacman_module.pacman import runGame
from pacman_module.ghostAgents import ConfusedGhost, AfraidGhost, ScaredGhost
from bayesfilter import BeliefStateAgent
from sherlockpacman import PacmanAgent as SherlockPacman # A simple agent that moves randomly


def run_single_experiment(layout, ghost_type_str, sensor_variance, seed):
    """Runs a single game and returns the metrics."""
    ghost_map = {
        "confused": ConfusedGhost,
        "afraid": AfraidGhost,
        "scared": ScaredGhost
    }

    # Mock command-line arguments
    args = Namespace(
        layout=layout,
        ghostagent=ghost_type_str,
        sensorvariance=sensor_variance,
        nghosts=1,
        seed=seed,
        bsagentfile='bayesfilter.py',
        agentfile='sherlockpacman.py',
        hiddenghosts=True, # Ghosts are invisible
        edibleghosts=True,
        silentdisplay=True # No GUI for faster execution
    )

    # Set seed for reproducibility
    if seed >= 0:
        np.random.seed(seed)
        import random
        random.seed(seed)

    # Initialize agents
    pacman_agent = SherlockPacman(args)
    ghost_agent_class = ghost_map[ghost_type_str]
    ghost_agents = [ghost_agent_class(i + 1, args) for i in range(args.nghosts)]
    belief_agent = BeliefStateAgent(args)

    # Run the game
    game_result = runGame(
        args.layout,
        pacman_agent,
        ghost_agents,
        belief_agent,
        not args.silentdisplay,
        expout=0,
        hiddenGhosts=args.hiddenghosts,
        edibleGhosts=args.edibleghosts,
        startingIndex=args.nghosts + 1
    )

    return belief_agent.metrics

def plot_metrics(df, metric_name, title, filename):
    """Plots a given metric with mean and std deviation."""
    plt.figure(figsize=(12, 7))
    
    for ghost_type in df['ghost_type'].unique():
        subset = df[df['ghost_type'] == ghost_type]
        mean = subset.groupby('timestep')[metric_name].mean()
        std = subset.groupby('timestep')[metric_name].std()
        
        plt.plot(mean.index, mean, label=f'Ghost: {ghost_type}')
        plt.fill_between(mean.index, mean - std, mean + std, alpha=0.2)

    plt.title(title)
    plt.xlabel('Time Step')
    plt.ylabel(metric_name.replace('_', ' ').title())
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()
    print(f"Saved plot to {filename}")

if __name__ == '__main__':
    # --- Experiment Configuration ---
    N_TRIALS = 10  # Number of runs for each setting to average over
    MAX_STEPS = 100 # Duration of each game
    LAYOUTS = ['large_filter', 'large_filter_walls']
    GHOST_TYPES = ['confused', 'afraid', 'scared']
    DEFAULT_VARIANCE = 1.0

    # Create a directory for graphs if it doesn't exist
    if not os.path.exists('graphs'):
        os.makedirs('graphs')

    # --- Run Experiments ---
    all_results = []
    
    for layout in LAYOUTS:
        print(f"\n--- Running experiments for layout: {layout} ---")
        for ghost_type in GHOST_TYPES:
            print(f"  Ghost type: {ghost_type}, N_TRIALS: {N_TRIALS}")
            for trial in range(N_TRIALS):
                # Use a different seed for each trial for variability
                metrics = run_single_experiment(layout, ghost_type, DEFAULT_VARIANCE, seed=trial)
                
                # Process metrics for this trial
                for t, step_metrics in enumerate(metrics):
                    if t >= MAX_STEPS: break
                    all_results.append({
                        'layout': layout,
                        'ghost_type': ghost_type,
                        'trial': trial,
                        'timestep': t,
                        'ghost_0_entropy': step_metrics.get('ghost_0_entropy'),
                        'ghost_0_error_dist': step_metrics.get('ghost_0_error_dist'),
                        'ghost_0_prob_at_true': step_metrics.get('ghost_0_prob_at_true')
                    })

    # Convert results to a DataFrame for easier analysis
    results_df = pd.DataFrame(all_results)
    results_df.dropna(inplace=True) # Remove rows where metrics couldn't be calculated

    # --- Generate and Save Plots ---
    for layout in LAYOUTS:
        df_layout = results_df[results_df['layout'] == layout]
        
        # Plot Entropy
        plot_metrics(df_layout, 'ghost_0_entropy', 
                     f'Uncertainty (Entropy) vs. Time on {layout} layout', 
                     f'graphs/entropy_{layout}.png')

        # Plot Error Distance
        plot_metrics(df_layout, 'ghost_0_error_dist', 
                     f'Quality (Error Distance) vs. Time on {layout} layout', 
                     f'graphs/error_dist_{layout}.png')

    print("\nAll experiments finished and plots saved in 'graphs' directory.")