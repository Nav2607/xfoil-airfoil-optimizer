# XFOIL Airfoil Optimizer

A Python-based airfoil shape optimizer that uses [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/) and SciPy's Nelder-Mead method to minimize drag coefficient (CD) for a target lift coefficient.

## How It Works

The optimizer iteratively adjusts three airfoil shape parameters:

| Parameter | Description |
|-----------|-------------|
| `a1` | Linear camber coefficient |
| `a2` | Quadratic camber coefficient |
| `t_c` | Thickness-to-chord ratio |

Each iteration: generates an airfoil shape → runs XFOIL to compute aerodynamic performance → extracts CD at the target CL → feeds the result back to the optimizer.

**Default operating conditions:**
- Reynolds number: 3,000,000
- Mach number: 0.2
- Target CL: 0.338
- Angle of attack sweep: -5° to 10° (0.5° steps)

## Prerequisites

- **Python 3.7+**
- **XFOIL 6.99** — must be downloaded separately (see [Setup](#setup))

### Python Dependencies

```
numpy
scipy
```

Install with:

```bash
pip install numpy scipy
```

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/XFOIL-Airfoil-Optimizer.git
   cd XFOIL-Airfoil-Optimizer
   ```

2. **Download XFOIL:**

   Download XFOIL 6.99 from the [official MIT page](https://web.mit.edu/drela/Public/web/xfoil/) and place `xfoil.exe` in the project root directory.

   > **Note:** `pplot.exe` and `pxplot.exe` are optional plotting utilities included with XFOIL. They are not required by this optimizer.

3. **Install Python dependencies:**

   ```bash
   pip install numpy scipy
   ```

## Usage

```bash
python main.py
```

The optimizer will run and produce:

| Output File | Description |
|-------------|-------------|
| `iteration_log.txt` | Log of each iteration's parameters and CD value |
| `optimized_values.txt` | Final optimized parameters and drag coefficient |
| `testing_airfoil.txt` | Airfoil coordinates of the optimized shape (Selig format) |

## Project Structure

```
├── main.py              # Main optimization script
├── xfoil.exe            # XFOIL solver (not tracked — download separately)
├── .gitignore
└── README.md
```

## License

This project uses [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/) by Mark Drela and Harold Youngren (MIT).