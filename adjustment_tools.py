# --- adjustment_tools.py ---
from app import mcp
import numpy as np
import math
from scipy.stats import t as t_distribution # For statistical tests

@mcp.tool
def propagate_error_covariance(A_matrix: np.ndarray, input_covariance: np.ndarray) -> np.ndarray:
    """
    Applies the law of error propagation using covariance matrices.
    [cite_start]Calculates Sigma_zz = A * Sigma_xx * A_transpose. [cite: 2850]

    :param A_matrix: The design or Jacobian matrix (m x n).
    :param input_covariance: The variance-covariance matrix of the input variables (Sigma_xx, n x n).
    :return: The variance-covariance matrix of the calculated variables (Sigma_zz, m x m).
    """
    try:
        A = np.asanyarray(A_matrix)
        Sigma_xx = np.asanyarray(input_covariance)
        
        if A.shape[1] != Sigma_xx.shape[0] or Sigma_xx.shape[0] != Sigma_xx.shape[1]:
             raise ValueError("Matrix dimensions mismatch for A * Sigma * A.T")

        # Sigma_zz = A @ Sigma_xx @ A.T
        Sigma_zz = np.dot(A, np.dot(Sigma_xx, A.T))
        return Sigma_zz
    except Exception as e:
        print(f"Error in propagate_error_covariance: {e}")
        # Return an identity matrix or raise error? Returning NaN matrix for clarity.
        m = A_matrix.shape[0]
        return np.full((m, m), np.nan)


@mcp.tool
def calculate_residual_test_statistic(residual: float, std_dev_residual: float) -> float | str:
    """
    Calculates a simple test statistic (like a standardized residual) for outlier detection.
    Note: This is a basic form. Proper Data Snooping requires comparing against
    [cite_start]critical values adjusted for multiple tests. [cite: 3433-3435]

    :param residual: The calculated residual (v = Ax - L) for an observation.
    :param std_dev_residual: The calculated standard deviation of that residual.
    :return: The test statistic (w = v / sigma_v) or error string.
    """
    if std_dev_residual is None or std_dev_residual < 1e-9: # Avoid division by zero
        return "Error: Standard deviation of residual is zero or invalid."
    
    test_statistic = residual / std_dev_residual
    return test_statistic

# Placeholder - requires more context like degrees of freedom, alpha
# @mcp.tool
# def get_t_test_critical_value(degrees_of_freedom: int, alpha: float = 0.05) -> float:
#     """Gets the critical value from the t-distribution for outlier testing."""
#     if degrees_of_freedom <= 0:
#         return float('inf') # Or handle error
#     # For a two-tailed test
#     critical_value = t_distribution.ppf(1 - alpha / 2, df=degrees_of_freedom)
#     return critical_value

@mcp.tool
def calculate_error_ellipse(covariance_matrix_2d: np.ndarray) -> dict | str:
    """
    Calculates the parameters of the standard error ellipse from a 2x2
    [cite_start]variance-covariance matrix (e.g., for Northing, Easting). [cite: 3311-3312]

    :param covariance_matrix_2d: A 2x2 NumPy array [[var_N, cov_NE], [cov_NE, var_E]].
    :return: Dict {'semi_major_axis': a, 'semi_minor_axis': b, 'orientation_gon': phi_a_gon} or error.
             Orientation is angle of major axis from North, clockwise positive.
    """
    try:
        Sigma_NE = np.asanyarray(covariance_matrix_2d)
        if Sigma_NE.shape != (2, 2):
            raise ValueError("Input must be a 2x2 covariance matrix.")

        var_N = Sigma_NE[0, 0]
        var_E = Sigma_NE[1, 1]
        cov_NE = Sigma_NE[0, 1]

        # Calculate semi-axes squared using eigenvalue approach implicitly
        # [cite_start](Formulas adapted from[cite: 3316, 3317], assuming sigma0=1 or already included)
        term1 = (var_N + var_E) / 2.0
        term2_squared = ((var_N - var_E) / 2.0)**2 + cov_NE**2
        
        # Check if term2 is non-negative before sqrt
        if term2_squared < -1e-12: # Allow for tiny floating point negatives
             print(f"Warning: Negative value encountered in error ellipse calculation ({term2_squared}). Clamping to zero.")
             term2 = 0.0
        else:
            term2 = math.sqrt(max(0.0, term2_squared)) # Ensure non-negative

        # Standard error ellipse axes (k=1 standard deviation)
        a_squared = term1 + term2
        b_squared = term1 - term2
        
        # Clamp negative results due to potential floating point issues with near-zero covariance matrix
        a = math.sqrt(max(0.0, a_squared)) 
        b = math.sqrt(max(0.0, b_squared)) 

        # Ensure a is always the semi-major axis
        if b > a:
            a, b = b, a # Swap if b is larger

        # [cite_start]Calculate orientation of the semi-major axis (a) [cite: 3315]
        # Angle relative to North axis (index 0)
        # Using atan2 for quadrant correctness
        orientation_rad = 0.5 * math.atan2(2 * cov_NE, var_N - var_E)
        
        # Convert orientation to Gon (0-200 range, clockwise from North)
        # atan2 gives angle from positive x-axis (Easting). We want angle from positive y-axis (Northing).
        # Angle from North = 100 gon - angle from East
        orientation_gon_from_east = rad_to_gon(orientation_rad)
        orientation_gon = (100.0 - orientation_gon_from_east) % 200.0 # Ensure positive 0-200

        # Adjust orientation if axes were swapped
        if b_squared > a_squared:
             orientation_gon = (orientation_gon + 100.0) % 200.0 # Rotate by 100 gon (90 deg)


        return {
            'semi_major_axis': a,
            'semi_minor_axis': b,
            'orientation_gon': orientation_gon
        }
    except Exception as e:
        print(f"Error calculating error ellipse: {e}")
        return f"Error calculating error ellipse: {e}"