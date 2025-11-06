# --- surveying_tools.py ---
from app import mcp
import numpy as np
import math

# --- Constants (GRS80 Ellipsoid, used by EUREF89) ---
GRS80_A = 6378137.0  # Semi-major axis
GRS80_F_INV = 298.257222101 # Inverse flattening
GRS80_F = 1 / GRS80_F_INV
GRS80_B = GRS80_A * (1 - GRS80_F) # Semi-minor axis
GRS80_E2 = (GRS80_A**2 - GRS80_B**2) / GRS80_A**2 # First eccentricity squared
GRS80_EP2 = (GRS80_A**2 - GRS80_B**2) / GRS80_B**2 # Second eccentricity squared

# --- UTM Constants ---
UTM_K0 = 0.9996 # Scale factor on central meridian [cite: 2016]
UTM_FALSE_EASTING = 500000.0 # [cite: 2023]

# --- Helper: Radians/Degrees/Gon Conversions ---
def deg_to_rad(deg): return math.radians(deg)
def rad_to_deg(rad): return math.degrees(rad)
def gon_to_rad(gon): return gon * math.pi / 200.0
def rad_to_gon(rad): return rad * 200.0 / math.pi
def deg_to_gon(deg): return deg * 200.0 / 180.0
def gon_to_deg(gon): return gon * 180.0 / 200.0

# --- Geodetic Calculations ---

@mcp.tool
def geodetic_to_utm(latitude_deg: float, longitude_deg: float, utm_zone: int) -> dict:
    """
    Converts Geodetic coordinates (Lat, Lon - EUREF89/GRS80) to UTM coordinates.
    [cite_start]Simplified implementation based on formulas in [cite: 2106-2126].
    Does not handle zones outside Norway precisely.

    :param latitude_deg: Latitude in decimal degrees.
    :param longitude_deg: Longitude in decimal degrees.
    :param utm_zone: The target UTM zone number (e.g., 32, 33, 35).
    :return: Dictionary {'northing': N, 'easting': E} or error.
    """
    lat_rad = deg_to_rad(latitude_deg)
    lon_rad = deg_to_rad(longitude_deg)

    # Central Meridian for the zone
    lon0_deg = float((utm_zone - 1) * 6 - 180 + 3)
    lon0_rad = deg_to_rad(lon0_deg)

    delta_lon = lon_rad - lon0_rad

    a = GRS80_A
    e2 = GRS80_E2
    ep2 = GRS80_EP2
    k0 = UTM_K0

    N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2) # [cite: 2117]
    T = math.tan(lat_rad)**2
    C = ep2 * math.cos(lat_rad)**2
    A_ = delta_lon * math.cos(lat_rad)

    # [cite_start]Calculate Meridian Arc Length (S) - simplified from series expansion [cite: 2120]
    # For higher accuracy, implement the full series (a0, a2, a4...)
    M = a * ((1 - e2/4 - 3*e2**2/64 - 5*e2**3/256) * lat_rad
             - (3*e2/8 + 3*e2**2/32 + 45*e2**3/1024) * math.sin(2*lat_rad)
             + (15*e2**2/256 + 45*e2**3/1024) * math.sin(4*lat_rad)
             - (35*e2**3/3072) * math.sin(6*lat_rad))

    # [cite_start]Calculate Northing (y in formula) [cite: 2112]
    northing = k0 * (M + N * math.tan(lat_rad) * (
                      A_**2/2 +
                      A_**4/24 * (5 - T + 9*C + 4*C**2) +
                      A_**6/720 * (61 - 58*T + T**2 + 600*C - 330*ep2)
                     ))

    # [cite_start]Calculate Easting (x in formula, relative to CM) [cite: 2108-2109]
    easting_rel = k0 * N * (
                   A_ +
                   A_**3/6 * (1 - T + C) +
                   A_**5/120 * (5 - 18*T + T**2 + 72*C - 58*ep2)
                  )

    # Add False Easting
    easting = easting_rel + UTM_FALSE_EASTING

    # Handle Norway's Zone 32 extension approx. (Very simplified)
    if utm_zone == 32 and longitude_deg < 6.0:
         print("Warning: Point is West of 6deg E in Zone 32, accuracy might be lower.")

    return {'northing': northing, 'easting': easting}


@mcp.tool
def utm_to_geodetic(northing: float, easting: float, utm_zone: int) -> dict:
    """
    Converts UTM coordinates back to Geodetic (Lat, Lon - EUREF89/GRS80).
    Simplified implementation based on formulas in [cite: 2166-2187].

    :param northing: Northing in meters.
    :param easting: Easting in meters.
    :param utm_zone: The source UTM zone number.
    :return: Dictionary {'latitude': lat_deg, 'longitude': lon_deg} or error.
    """
    x = easting - UTM_FALSE_EASTING # Easting relative to CM (x in formula [cite: 2170])
    y = northing                  # Northing (y in formula [cite: 2170])
    k0 = UTM_K0
    a = GRS80_A
    e2 = GRS80_E2
    ep2 = GRS80_EP2
    b = GRS80_B
    f = GRS80_F

    # Calculate Footprint Latitude (phi_f) [cite: 2177]
    M = y / k0 # Arc length from equator
    mu = M / (a * (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256))
    e1 = (1 - math.sqrt(1-e2)) / (1 + math.sqrt(1-e2))

    phi_f = mu + (3*e1/2 - 27*e1**3/32) * math.sin(2*mu) \
             + (21*e1**2/16 - 55*e1**4/32) * math.sin(4*mu) \
             + (151*e1**3/96) * math.sin(6*mu) \
             + (1097*e1**4/512) * math.sin(8*mu)

    # [cite_start]Calculate intermediate values at phi_f [cite: 2179-2181]
    Nf = a / math.sqrt(1 - e2 * math.sin(phi_f)**2)
    Tf = math.tan(phi_f)**2
    Cf = ep2 * math.cos(phi_f)**2
    Rf = a * (1 - e2) / (1 - e2 * math.sin(phi_f)**2)**1.5 # Meridian radius of curvature M (confusingly named R here)

    D = x / (Nf * k0)

    # [cite_start]Calculate Latitude (phi) [cite: 2183-2184]
    lat_rad = phi_f - (Nf * math.tan(phi_f) / Rf) * (
                       D**2/2 -
                       D**4/24 * (5 + 3*Tf + 10*Cf - 4*Cf**2 - 9*ep2) +
                       D**6/720 * (61 + 90*Tf + 298*Cf + 45*Tf**2 - 252*ep2 - 3*Cf**2)
                      )

    # [cite_start]Calculate Longitude (lambda) [cite: 2186]
    lon0_deg = float((utm_zone - 1) * 6 - 180 + 3)
    lon0_rad = deg_to_rad(lon0_deg)

    delta_lon = ( D -
                  D**3/6 * (1 + 2*Tf + Cf) +
                  D**5/120 * (5 - 2*Cf + 28*Tf - 3*Cf**2 + 8*ep2 + 24*Tf**2)
                ) / math.cos(phi_f)

    lon_rad = lon0_rad + delta_lon

    return {'latitude': rad_to_deg(lat_rad), 'longitude': rad_to_deg(lon_rad)}

@mcp.tool
def correct_utm_distance(distance_ellipsoid: float, easting1: float, easting2: float, earth_radius: float = 6390000.0) -> float:
    """
    Corrects a distance measured on the ellipsoid (De) to the UTM map plane (Dk).
    [cite_start]Based on formula 10.9 [cite: 4146-4147].

    :param distance_ellipsoid: The distance on the GRS80 ellipsoid (De).
    :param easting1: UTM Easting of the start point.
    :param easting2: UTM Easting of the end point.
    :param earth_radius: Approximate Earth radius (mean radius of curvature M). Default for S. Norway.
    :return: The distance on the UTM map plane (Dk).
    """
    y1 = easting1 - UTM_FALSE_EASTING # Distance from Central Meridian [cite: 4147]
    y2 = easting2 - UTM_FALSE_EASTING # Distance from Central Meridian [cite: 4147]
    R = earth_radius

    # Combined scale factor (projection + k0)
    scale_factor = UTM_K0 * (1 + (y1**2 + y1*y2 + y2**2) / (6 * R**2))

    distance_map = distance_ellipsoid * scale_factor
    return distance_map


@mcp.tool
def correct_direction_for_utm(direction_measured: float, northing1: float, northing2: float, easting1: float, easting2: float, earth_radius: float = 6390000.0) -> float:
    """
    Corrects a measured direction (relative to grid North at point 1) to the
    [cite_start]straight grid bearing on the UTM map plane. Based on formula 10.11 [cite: 4154-4156].

    :param direction_measured: The direction/angle measured at point 1 (in Gon).
    :param northing1: UTM Northing of the observation point.
    :param northing2: UTM Northing of the target point.
    :param easting1: UTM Easting of the observation point.
    :param easting2: UTM Easting of the target point.
    :param earth_radius: Approximate Earth radius.
    :return: The corrected grid bearing (in Gon).
    """
    x1 = northing1 # In formula, x is Northing [cite: 4155]
    x2 = northing2
    y1 = easting1 - UTM_FALSE_EASTING # y is relative Easting [cite: 4155]
    y2 = easting2 - UTM_FALSE_EASTING
    R = earth_radius

    # Calculate correction in radians
    delta_r_rad = ((x1 - x2) * (2*y1 + y2)) / (6 * R**2)
    # Convert correction to Gon
    delta_r_gon = rad_to_gon(delta_r_rad)

    # Apply correction
    direction_corrected = direction_measured + delta_r_gon # rk = r + ∆r [cite: 4155]
    return direction_corrected


@mcp.tool
def correct_vertical_angle(vertical_angle_gon: float, slant_distance: float, k_factor: float = 0.15, earth_radius: float = 6390000.0) -> float:
    """
    Corrects a measured vertical angle (zenith angle) for Earth curvature and
    [cite_start]atmospheric refraction. Based on formula Zjr [cite: 4059-4060].

    :param vertical_angle_gon: Measured zenith angle in Gon (0=up, 100=horizontal, 200=down).
    :param slant_distance: Measured distance Ds along the line of sight.
    :param k_factor: Refraction coefficient (typically 0.13-0.20 in Norway).
    :param earth_radius: Approximate Earth radius.
    :return: The corrected zenith angle in Gon (Zjr).
    """
    z_obs_rad = gon_to_rad(vertical_angle_gon)
    Ds = slant_distance
    Rj = earth_radius
    k = k_factor

    # Calculate corrections in radians
    # [cite_start]delta_Zr = asin(Ds * k / (2 * Rj)) # Formula from [cite: 4046]
    # Dh approx = Ds * sin(z_obs_rad + delta_Zr)
    # [cite_start]delta_Zj = asin(Dh / (2 * Rj))     # Formula from [cite: 4057]

    # Combined simplified approximation often used: delta_Z_rad = Ds * (1 - k) / (2 * Rj) * sin(z_obs_rad)
    # [cite_start]Let's use the slightly more complex form derived [cite: 4060] - Requires arcsin
    # Note: arcsin arguments must be between -1 and 1
    arg_zr = (Ds * k) / (2 * Rj)
    if abs(arg_zr) > 1: arg_zr = np.sign(arg_zr) # Clamp if out of bounds due to extreme distance
    delta_zr_rad = math.asin(arg_zr)

    # Approximate Dh for Zj correction (using observed angle is usually sufficient)
    dh_approx = Ds * math.sin(z_obs_rad)
    arg_zj = dh_approx / (2 * Rj)
    if abs(arg_zj) > 1: arg_zj = np.sign(arg_zj)
    delta_zj_rad = math.asin(arg_zj)

    # [cite_start]Apply corrections [cite: 4059]
    z_jr_rad = z_obs_rad + delta_zr_rad - delta_zj_rad

    return rad_to_gon(z_jr_rad)