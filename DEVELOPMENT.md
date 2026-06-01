# Development Setup Skill

This file records how to set up, test, and run the development environment for the `entropy-prophet` package.

## Prerequisites
- Python 3.9 or higher

## Initial Setup
1. Clone the repository and navigate into the folder:
   ```bash
   cd entropy-prophet
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install package and dependencies in editable mode:
   ```bash
   pip install --upgrade pip
   pip install -e .
   ```

## Running the Tests
To run the automated test suite, use the Python standard unit testing module:
```bash
python -m unittest tests/test_entropy_prophet.py
```

## Running the Demo
To execute the proof of concept demo showing the joint entropy and liquidity calibration calculations:
```bash
python demo.py
```
