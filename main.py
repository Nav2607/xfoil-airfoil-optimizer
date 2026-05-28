import numpy as np
from scipy.optimize import minimize, Bounds
import subprocess
import os
from scipy.interpolate import interp1d

iteration_counter = 1  # Initialize a global counter for iterations

def airfoil_coordinates(a1, a2, t_c, x): 
    y_c = a1 * x + a2 * x**2
    y_t = 5 * t_c * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
    y_u = y_c + y_t
    y_l = y_c - y_t
    return y_u, y_l

def save_selig_format(filename, x, y_u, y_l):
    with open(filename, 'w') as file:
        for xi, yu in zip(reversed(x), reversed(y_u)):
            file.write(f'{xi:.6f} {yu:.6f}\n')
        for xi, yl in zip(x, y_l):
            file.write(f'{xi:.6f} {yl:.6f}\n')

def run_xfoil(filename, alpha_start, alpha_end, alpha_step, reynolds, mach, timeout=45):
    if os.path.exists('polar.dat'):
        os.remove('polar.dat')

    xfoil_input = f"""
LOAD {filename}

PANE

OPER
ITER 250
VISC {reynolds}
MACH {mach}
PACC
polar.dat

ASEQ {alpha_start} {alpha_end} {alpha_step}

QUIT
"""

    with open('xfoil_input.txt', 'w') as f:
        f.write(xfoil_input)

    xfoil_path = os.path.join(os.getcwd(), "xfoil.exe")

    try:
        process = subprocess.Popen([xfoil_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.stdin.write(xfoil_input.encode())
        process.stdin.flush()

        try:
            output, error = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            output, error = process.communicate()
            print("XFOIL process timed out and was terminated.")
            return None

        if process.returncode != 0:
            print(f"XFOIL process failed with return code {process.returncode}.")
            print(error.decode())
            return None

        output = output.decode()

        with open('xfoil_output.txt', 'w') as f:
            f.write(output)

        print(output)
        return output

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def process_polar_data(CL_target):
    filename = 'polar.dat'
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print("polar.dat file not found. XFOIL may have failed to generate it.")
        return 1e6

    data_start_line = 12  
    data_lines = lines[data_start_line:]

    CL_values = []
    CD_values = []

    for line in data_lines:
        if line.strip():
            columns = line.split()
            alpha = float(columns[0])
            CL = float(columns[1])
            CD = float(columns[2])

            CL_values.append(CL)
            CD_values.append(CD)

    CL_values = np.array(CL_values)
    CD_values = np.array(CD_values)

    if len(CL_values) == 0 or len(CD_values) == 0:
        print("CL_values or CD_values are empty. Likely due to XFOIL convergence failure.")
        return 1e6

    print("CL_values:", CL_values)
    print("CD_values:", CD_values)

    interp_function = interp1d(CL_values, CD_values, kind='linear', fill_value="extrapolate")
    CD = interp_function(CL_target)
    print("CD: ", CD)
    return CD

def log_iteration_data(iteration, a1, a2, t_c, CD):
    log_filename = 'iteration_log.txt'
    header = "Iteration\ta1\ta2\tt_c\tCD\n"
    log_entry = f"{iteration}\t{a1:.6f}\t{a2:.6f}\t{t_c:.6f}\t{CD:.6f}\n"

    if not os.path.exists(log_filename):
        with open(log_filename, 'w') as file:
            file.write(header)

    with open(log_filename, 'a') as file:
        file.write(log_entry)

def save_optimized_values(a1_opt, a2_opt, t_c_opt, CD_opt):
    filename = 'optimized_values.txt'
    with open(filename, 'w') as file:
        file.write(f"Optimized Values:\n")
        file.write(f"a1: {a1_opt:.6f}\n")
        file.write(f"a2: {a2_opt:.6f}\n")
        file.write(f"t_c: {t_c_opt:.6f}\n")
        file.write(f"CD: {CD_opt:.6f}\n")
def function_eval(x):
    global iteration_counter
    airfoil_file = 'Save_Airfoil.txt'
    airfoil_name = 'Save_Airfoil'
    alpha_start = -5
    alpha_end = 10
    alpha_step = 0.5
    reynolds = 3000000
    mach = 0.2
    CL_target = 0.338
    (a1, a2, t_c) = x

    print("Properties: ", a1, a2, t_c)

    x_coords = np.linspace(0, 1, 100)
    y_u, y_l = airfoil_coordinates(a1, a2, t_c, x_coords)

    filename = 'testing_airfoil.txt'
    save_selig_format(filename, x_coords, y_u, y_l)

    run_xfoil(filename, alpha_start, alpha_end, alpha_step, reynolds, mach)

    CD = process_polar_data(CL_target)

    # Log the iteration data
    log_iteration_data(iteration_counter, a1, a2, t_c, CD)
    iteration_counter += 1

    return CD

if __name__ == "__main__":
    a1 = 0
    a2 = -0.2
    t_c = 0.12
    x0 = [a1, a2, t_c]

    lower_bounds = [-0.5, -0.5, 0.05]
    upper_bounds = [0.5, 0.5, 0.4]

    bounds = Bounds(lower_bounds, upper_bounds)

    if os.path.exists('iteration_log.txt'):
        os.remove('iteration_log.txt')

    result = minimize(function_eval, x0, method='nelder-mead',  
                       options={'xatol': 1e-8, 'disp': True},
                       bounds=bounds)

    a1_opt, a2_opt, t_c_opt = result.x

    x_coords = np.linspace(0, 1, 100)
    y_u, y_l = airfoil_coordinates(a1_opt, a2_opt, t_c_opt, x_coords)

    filename = 'testing_airfoil.txt'
    save_selig_format(filename, x_coords, y_u, y_l)

    print("Properties: ", a1_opt, a2_opt, t_c_opt)
    print("Optimized y-coordinates:", y_u, y_l)

        # Process the optimized CD value
    optimized_CD = process_polar_data(0.338)

    # Save optimized values to a file
    save_optimized_values(a1_opt, a2_opt, t_c_opt, optimized_CD)
