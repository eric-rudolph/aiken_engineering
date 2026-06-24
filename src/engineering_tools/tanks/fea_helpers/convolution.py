import numpy as np
import pandas as pd


def angular_distance(theta_a: np.ndarray,
                     theta_b: float) -> np.ndarray:
    return np.abs((theta_a - theta_b + np.pi) % (2 * np.pi) - np.pi)


def convolve(theta: float,
             z: float,
             scan_theta: pd.Series,
             scan_z: pd.Series,
             scan_delta_r: pd.Series,
             tank_radius: float,
             convolution_radius: float):
    s = convolution_radius
    scan_theta = np.asarray(scan_theta, dtype=float)
    scan_z = np.asarray(scan_z, dtype=float)
    scan_delta_r = np.asarray(scan_delta_r, dtype=float)

    dt = s / tank_radius
    mask = (angular_distance(scan_theta, theta) < dt) & (np.abs(scan_z - z) < s)
    if not mask.any():
        return np.nan
    return scan_delta_r[mask].mean()


#######################################
# This is optimized for shell nodes
#######################################

def convolve_nodes(node_theta: pd.Series, node_z: pd.Series,
                   scan_theta: pd.Series, scan_z: pd.Series,
                   scan_delta_r: pd.Series,
                   tank_radius: float, s: float) -> np.ndarray:
    dt = s / tank_radius
    node_theta = np.asarray(node_theta, dtype=float)
    node_z = np.asarray(node_z, dtype=float)
    scan_theta = np.asarray(scan_theta, dtype=float)
    scan_z = np.asarray(scan_z, dtype=float)
    scan_delta_r = np.asarray(scan_delta_r, dtype=float)

    result = np.full(node_theta.shape, np.nan)

    scan_order = np.argsort(scan_z)
    scan_z_sorted = scan_z[scan_order]
    scan_theta_sorted_by_z = scan_theta[scan_order]
    scan_delta_sorted_by_z = scan_delta_r[scan_order]

    for z_level in np.unique(node_z):
        node_mask = node_z == z_level
        z_left = np.searchsorted(scan_z_sorted, z_level - s, side="right")
        z_right = np.searchsorted(scan_z_sorted, z_level + s, side="left")

        if z_left == z_right:
            continue

        row_theta = scan_theta_sorted_by_z[z_left:z_right]
        row_delta = scan_delta_sorted_by_z[z_left:z_right]

        theta_order = np.argsort(row_theta)
        row_theta = row_theta[theta_order]
        row_delta = row_delta[theta_order]

        row_theta = np.concatenate((row_theta - 2 * np.pi, row_theta, row_theta + 2 * np.pi))
        row_delta = np.concatenate((row_delta, row_delta, row_delta))
        row_prefix = np.concatenate(([0.0], np.cumsum(row_delta)))

        query_theta = node_theta[node_mask]
        left = np.searchsorted(row_theta, query_theta - dt, side="left")
        right = np.searchsorted(row_theta, query_theta + dt, side="right")

        counts = right - left
        sums = row_prefix[right] - row_prefix[left]
        values = np.divide(sums, counts, out=np.full(query_theta.shape, np.nan), where=counts > 0)
        result[node_mask] = values

    return result
