"""Entry point for running as module with: python -m evolution_sim"""
import os
import sys


# Force XWayland compatibility
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Now import and run
from evolution_sim.main import main

if __name__ == '__main__':
    main()