"""Setup configuration for evolution-sim package."""
import os
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Base requirements
install_requires = [
    'pygame>=2.6.0',
    'numpy>=1.24.0',
    'pyyaml>=6.0',
]

# Development requirements
dev_requires = [
    'pytest>=7.0.0',
    'pytest-cov>=4.0.0',
    'black>=23.0.0',
    'flake8>=6.0.0',
    'mypy>=1.0.0',
]

setup(
    name='evolution-sim',
    version='0.1.0',
    description='Neural evolution ecosystem simulation with evolving creatures',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PierreMrt/evolution-sim',
    project_urls={
        'Bug Tracker': 'https://github.com/PierreMrt/evolution-sim/issues',
        'Documentation': 'https://github.com/PierreMrt/evolution-sim#readme',
        'Source Code': 'https://github.com/PierreMrt/evolution-sim',
    },
    
    # Package configuration
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    # Dependencies
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
    },
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Artificial Life',
    ],
    
    # Keywords
    keywords='evolution neural-network simulation artificial-life neat',
    
    # Include additional files
    include_package_data=True,
    package_data={
        'evolution_sim': ['config/*.yaml'],
    },
    
    # Zip safe
    zip_safe=False,
)
