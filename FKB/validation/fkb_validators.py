"""
FKB Validators - Data-driven validation functions based on extracted FKB rules.

This module loads rules from the extracted YAML/MD files and provides
comprehensive validation for FKB datasets.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from shapely.geometry import shape, Polygon, LineString, Point
from shapely.validation import explain_validity

# Load rules at module initialization
RULES_DIR = Path(__file__).parent.parent / "extracted"

def _load_yaml(filename: str) -> Any:
    """Load a YAML file from the extracted rules directory."""
    filepath = RULES_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Rule file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Load rule databases
try:
    MANDATORY_ATTRIBUTES = _load_yaml("01-MANDATORY-ATTRIBUTES.yaml")
    GEOMETRIC_RULES = _load_yaml("02-GEOMETRIC-RULES.yaml")
    ACCURACY_STANDARDS = _load_yaml("03-ACCURACY-STANDARDS.yaml")
    TOPOLOGY_RULES = _load_yaml("04-TOPOLOGY-RULES.yaml")
    METADATA_RULES = _load_yaml("05-METADATA-RULES.yaml")
    SOSI_FORMAT_RULES = _load_yaml("08-SOSI-FORMAT-RULES.yaml")
except Exception as e:
    print(f"⚠️  Warning: Could not load all FKB rules: {e}")
    MANDATORY_ATTRIBUTES = {}
    GEOMETRIC_RULES = {}
    ACCURACY_STANDARDS = {}
    TOPOLOGY_RULES = {}
    METADATA_RULES = {}
    SOSI_FORMAT_RULES = {}


# ============================================================================
# 1. ATTRIBUTE VALIDATORS
# ============================================================================

def validate_mandatory_attributes(feature: Dict[str, Any], objtype: str) -> List[str]:
    """
    Validate feature has all mandatory attributes for its OBJTYPE.

    Args:
        feature: Parsed SOSI feature as dict with attributes
        objtype: The OBJTYPE value (e.g., 'Bygning', 'Vegkant')

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> feature = {'OBJTYPE': 'Bygning', 'posisjon': [10, 20, 30]}
        >>> errors = validate_mandatory_attributes(feature, 'Bygning')
        >>> # Returns errors if 'bygningsnummer' is missing
    """
    errors = []

    if not MANDATORY_ATTRIBUTES:
        errors.append("ATTR-000: Rule database not loaded")
        return errors

    # Find object type definition
    object_def = None
    for obj in MANDATORY_ATTRIBUTES.get('object_types', []):
        if obj.get('object_type') == objtype:
            object_def = obj
            break

    if not object_def:
        errors.append(f"ATTR-001: Unknown OBJTYPE '{objtype}'")
        return errors

    # Check each mandatory attribute
    mandatory_attrs = object_def.get('mandatory_attributes', [])
    for attr in mandatory_attrs:
        attr_name = attr.get('name')
        if not attr_name:
            continue

        # Check if attribute exists in feature
        if attr_name not in feature or feature[attr_name] is None:
            attr_type = attr.get('type', 'unknown')
            description = attr.get('description', '')
            errors.append(
                f"ATTR-002: Missing mandatory attribute '{attr_name}' "
                f"(type: {attr_type}) for {objtype}. {description}"
            )

    # Check inherited attributes from supertype
    supertype = object_def.get('supertype')
    if supertype:
        # Check common inherited attributes
        common_attrs = ['DATAFANGSTDATO', 'KVALITET']
        for attr in common_attrs:
            if attr not in feature or feature[attr] is None:
                errors.append(
                    f"ATTR-003: Missing inherited attribute '{attr}' "
                    f"from supertype {supertype}"
                )

    return errors


def validate_optional_attributes(feature: Dict[str, Any], objtype: str) -> List[str]:
    """
    Validate optional attributes are correctly formatted if present.

    Args:
        feature: Parsed SOSI feature as dict
        objtype: The OBJTYPE value

    Returns:
        List of validation warnings
    """
    warnings = []

    if not MANDATORY_ATTRIBUTES:
        return warnings

    # Find object type definition
    object_def = None
    for obj in MANDATORY_ATTRIBUTES.get('object_types', []):
        if obj.get('object_type') == objtype:
            object_def = obj
            break

    if not object_def:
        return warnings

    # Get all known attributes (mandatory + optional)
    known_attrs = set()
    for attr in object_def.get('mandatory_attributes', []):
        known_attrs.add(attr.get('name'))
    for attr in object_def.get('optional_attributes', []):
        known_attrs.add(attr.get('name'))

    # Check for unknown attributes
    for attr_name in feature.keys():
        if attr_name not in known_attrs and not attr_name.startswith('.'):
            warnings.append(
                f"ATTR-WARN-001: Unknown attribute '{attr_name}' for {objtype}"
            )

    return warnings


# ============================================================================
# 2. GEOMETRY VALIDATORS
# ============================================================================

def validate_geometry(feature: Dict[str, Any], objtype: str) -> List[str]:
    """
    Validate geometry meets FKB rules for object type.

    Args:
        feature: Parsed SOSI feature with geometry
        objtype: The OBJTYPE value

    Returns:
        List of validation errors
    """
    errors = []

    if 'geometry' not in feature:
        errors.append("GEOM-001: Missing geometry")
        return errors

    geom = feature['geometry']

    # Convert to Shapely geometry if needed
    if isinstance(geom, dict) and 'type' in geom:
        try:
            geom = shape(geom)
        except Exception as e:
            errors.append(f"GEOM-002: Invalid GeoJSON geometry: {e}")
            return errors

    # Check geometry validity
    if not geom.is_valid:
        explanation = explain_validity(geom)
        errors.append(f"GEOM-003: Invalid geometry: {explanation}")

    # Check geometry type matches specification
    if MANDATORY_ATTRIBUTES:
        object_def = None
        for obj in MANDATORY_ATTRIBUTES.get('object_types', []):
            if obj.get('object_type') == objtype:
                object_def = obj
                break

        if object_def:
            expected_type = object_def.get('geometry_type')
            actual_type = geom.geom_type

            # Map SOSI types to Shapely types
            type_mapping = {
                'PUNKT': 'Point',
                'KURVE': 'LineString',
                'FLATE': 'Polygon'
            }

            expected_shapely = type_mapping.get(expected_type, expected_type)
            if expected_shapely != actual_type:
                errors.append(
                    f"GEOM-004: Geometry type mismatch. Expected {expected_shapely}, "
                    f"got {actual_type} for {objtype}"
                )

    # Check for self-intersections (LineString and Polygon)
    if isinstance(geom, LineString):
        if not geom.is_simple:
            errors.append("GEOM-005: LineString has self-intersections")

    if isinstance(geom, Polygon):
        # Check exterior ring is closed
        exterior = geom.exterior
        if not exterior.is_ring:
            errors.append("GEOM-006: Polygon exterior ring is not closed")

        # Check for self-intersections in rings
        if not exterior.is_simple:
            errors.append("GEOM-007: Polygon exterior ring has self-intersections")

        for i, interior in enumerate(geom.interiors):
            if not interior.is_ring:
                errors.append(f"GEOM-008: Polygon hole {i} is not closed")
            if not interior.is_simple:
                errors.append(f"GEOM-009: Polygon hole {i} has self-intersections")

    # Check minimum segment length (pilhøyde constraint)
    if 'NØYAKTIGHET' in feature:
        noyaktighet = feature['NØYAKTIGHET']
        if isinstance(noyaktighet, (int, float)):
            min_segment = noyaktighet / 10  # Conservative check

            if isinstance(geom, (LineString, Polygon)):
                coords = list(geom.exterior.coords) if isinstance(geom, Polygon) else list(geom.coords)
                for i in range(len(coords) - 1):
                    p1 = np.array(coords[i][:2])
                    p2 = np.array(coords[i+1][:2])
                    dist = np.linalg.norm(p2 - p1)
                    if dist < min_segment:
                        errors.append(
                            f"GEOM-010: Segment {i} too short ({dist:.3f}m < {min_segment:.3f}m)"
                        )

    return errors


def validate_pilhoyde_constraint(feature: Dict[str, Any], fkb_standard: str) -> List[str]:
    """
    Validate line simplification meets pilhøyde constraint.

    Args:
        feature: Feature with LineString or Polygon geometry
        fkb_standard: FKB standard ('A', 'B', 'C', or 'D')

    Returns:
        List of validation errors
    """
    errors = []

    if 'geometry' not in feature:
        return errors

    geom = feature['geometry']
    if isinstance(geom, dict):
        geom = shape(geom)

    # Pilhøyde limits from accuracy standards
    pilhoyde_limits = {
        'A': 0.05,  # 5 cm
        'B': 0.10,  # 10 cm
        'C': 0.30,  # 30 cm
        'D': 1.00   # 1 m
    }

    max_pilhoyde = pilhoyde_limits.get(fkb_standard.upper(), 1.0)

    # Check if geometry could be simplified further
    if isinstance(geom, (LineString, Polygon)):
        coords = list(geom.exterior.coords) if isinstance(geom, Polygon) else list(geom.coords)

        # For each interior point, check perpendicular distance to line between neighbors
        for i in range(1, len(coords) - 1):
            p0 = np.array(coords[i-1][:2])
            p1 = np.array(coords[i][:2])
            p2 = np.array(coords[i+1][:2])

            # Calculate perpendicular distance
            line_vec = p2 - p0
            line_len = np.linalg.norm(line_vec)
            if line_len < 1e-6:
                continue

            line_unit = line_vec / line_len
            point_vec = p1 - p0
            proj_length = np.dot(point_vec, line_unit)
            proj_point = p0 + proj_length * line_unit
            perp_dist = np.linalg.norm(p1 - proj_point)

            if perp_dist < max_pilhoyde * 0.5:  # Less than half the limit
                errors.append(
                    f"GEOM-011: Point {i} could be removed (pilhøyde={perp_dist:.3f}m < {max_pilhoyde}m)"
                )

    return errors


# ============================================================================
# 3. ACCURACY VALIDATORS
# ============================================================================

def validate_accuracy(feature: Dict[str, Any], fkb_standard: str) -> List[str]:
    """
    Validate NØYAKTIGHET and H-NØYAKTIGHET meet FKB standards.

    Args:
        feature: Feature with KVALITET block
        fkb_standard: FKB standard ('A', 'B', 'C', or 'D')

    Returns:
        List of validation errors
    """
    errors = []

    if not ACCURACY_STANDARDS:
        errors.append("ACC-000: Accuracy standards not loaded")
        return errors

    # Get accuracy class from KVALITET block
    kvalitet = feature.get('KVALITET', {})
    if not kvalitet:
        errors.append("ACC-001: Missing KVALITET block")
        return errors

    noyaktighet = kvalitet.get('NØYAKTIGHET')
    h_noyaktighet = kvalitet.get('H-NØYAKTIGHET')

    if noyaktighet is None:
        errors.append("ACC-002: Missing NØYAKTIGHET in KVALITET block")
        return errors

    # Convert to accuracy class (1-4)
    accuracy_class = _determine_accuracy_class(noyaktighet)

    # Look up standard
    standard_key = f"FKB-{fkb_standard.upper()}"
    standard_def = None

    for std in ACCURACY_STANDARDS.get('accuracy_standards', []):
        if std.get('standard') == standard_key and std.get('class') == accuracy_class:
            standard_def = std
            break

    if not standard_def:
        errors.append(
            f"ACC-003: No standard found for {standard_key} class {accuracy_class}"
        )
        return errors

    # Check horizontal accuracy
    horiz = standard_def.get('horizontal', {})
    max_systematic = horiz.get('systematic_deviation_cm', 999) / 100  # Convert to meters
    max_std = horiz.get('standard_deviation_cm', 999) / 100

    if noyaktighet > max_std:
        errors.append(
            f"ACC-004: NØYAKTIGHET {noyaktighet}m exceeds {standard_key} class {accuracy_class} "
            f"standard deviation limit {max_std}m"
        )

    # Check vertical accuracy if 3D
    if h_noyaktighet is not None:
        vert = standard_def.get('vertical', {})
        max_h_std = vert.get('standard_deviation_cm', 999) / 100

        if h_noyaktighet > max_h_std:
            errors.append(
                f"ACC-005: H-NØYAKTIGHET {h_noyaktighet}m exceeds {standard_key} class {accuracy_class} "
                f"vertical standard deviation limit {max_h_std}m"
            )

    return errors


def _determine_accuracy_class(noyaktighet: float) -> int:
    """Map NØYAKTIGHET value to accuracy class (1-4)."""
    if noyaktighet <= 0.10:
        return 1
    elif noyaktighet <= 0.30:
        return 2
    elif noyaktighet <= 0.60:
        return 3
    else:
        return 4


# ============================================================================
# 4. METADATA VALIDATORS
# ============================================================================

def validate_kvalitet_block(feature: Dict[str, Any]) -> List[str]:
    """
    Validate KVALITET block completeness and validity.

    Args:
        feature: Feature with KVALITET block

    Returns:
        List of validation errors
    """
    errors = []

    kvalitet = feature.get('KVALITET', {})
    if not kvalitet:
        errors.append("META-001: Missing KVALITET block")
        return errors

    # Check 5 mandatory attributes from METADATA_RULES
    mandatory_kvalitet_attrs = [
        'MÅLEMETODE',
        'NØYAKTIGHET',
        'SYNBARHET',
        'DATAFANGSTDATO',
        'VERIFISERINGSDATO'
    ]

    for attr in mandatory_kvalitet_attrs:
        if attr not in kvalitet or kvalitet[attr] is None:
            errors.append(f"META-002: Missing mandatory KVALITET attribute '{attr}'")

    # Validate MÅLEMETODE (DATAFANGSTMETODE) codes
    valid_malemetode = ['byg', 'ukj', 'pla', 'sat', 'gen', 'fot', 'dig', 'lan', '99']
    malemetode = kvalitet.get('MÅLEMETODE')
    if malemetode and malemetode not in valid_malemetode:
        errors.append(
            f"META-003: Invalid MÅLEMETODE '{malemetode}'. "
            f"Valid values: {', '.join(valid_malemetode)}"
        )

    # Validate SYNBARHET codes (0-3)
    synbarhet = kvalitet.get('SYNBARHET')
    if synbarhet is not None:
        if not isinstance(synbarhet, int) or synbarhet not in [0, 1, 2, 3]:
            errors.append(
                f"META-004: Invalid SYNBARHET '{synbarhet}'. Valid values: 0, 1, 2, 3"
            )

    # Validate date formats (should be YYYYMMDD)
    for date_attr in ['DATAFANGSTDATO', 'VERIFISERINGSDATO']:
        date_val = kvalitet.get(date_attr)
        if date_val:
            date_str = str(date_val)
            if not (len(date_str) == 8 and date_str.isdigit()):
                errors.append(
                    f"META-005: Invalid date format for '{date_attr}': {date_val}. "
                    f"Expected YYYYMMDD"
                )

    return errors


def validate_common_attributes(feature: Dict[str, Any]) -> List[str]:
    """
    Validate common attributes present on most/all FKB objects.

    Args:
        feature: Parsed SOSI feature

    Returns:
        List of validation errors
    """
    errors = []

    # Check OBJTYPE
    if 'OBJTYPE' not in feature:
        errors.append("META-006: Missing OBJTYPE attribute")

    # Check DATAFANGSTDATO (should be at top level)
    if 'DATAFANGSTDATO' not in feature:
        errors.append("META-007: Missing DATAFANGSTDATO attribute")

    return errors


# ============================================================================
# 5. SOSI FORMAT VALIDATORS
# ============================================================================

def validate_sosi_header(header: Dict[str, Any]) -> List[str]:
    """
    Validate .HODE section meets SOSI format requirements.

    Args:
        header: Parsed .HODE section as dict

    Returns:
        List of validation errors
    """
    errors = []

    # Mandatory header attributes from 08-SOSI-FORMAT-RULES.yaml
    mandatory_header_attrs = [
        'TEGNSETT',
        'SOSI-VERSJON',
        'SOSI-NIVÅ',
        'TRANSPAR',
        'ORIGO-NØ',
        'ENHET',
        'OMRÅDE'
    ]

    for attr in mandatory_header_attrs:
        if attr not in header:
            errors.append(f"SOSI-001: Missing mandatory header attribute '{attr}'")

    # Validate TEGNSETT
    tegnsett = header.get('TEGNSETT')
    if tegnsett and tegnsett not in ['UTF-8', 'ISO8859-1', 'ISO8859-10']:
        errors.append(
            f"SOSI-002: Invalid TEGNSETT '{tegnsett}'. "
            f"Valid values: UTF-8, ISO8859-1, ISO8859-10"
        )

    # Validate SOSI-VERSJON format
    sosi_versjon = header.get('SOSI-VERSJON')
    if sosi_versjon:
        try:
            major, minor = map(int, str(sosi_versjon).split('.'))
            if major < 4:
                errors.append(f"SOSI-003: Old SOSI version {sosi_versjon}. Recommend 4.5+")
        except:
            errors.append(f"SOSI-004: Invalid SOSI-VERSJON format: {sosi_versjon}")

    # Validate coordinate system
    if 'KOORDINATSYSTEM' in header or 'KOORDSYS' in header:
        koordsys = header.get('KOORDINATSYSTEM') or header.get('KOORDSYS')
        valid_crs = [22, 23, 24, 25, 32, 33, 5972, 5973]
        if koordsys not in valid_crs:
            errors.append(
                f"SOSI-005: Uncommon coordinate system {koordsys}. "
                f"Typical values: {valid_crs}"
            )
    else:
        errors.append("SOSI-006: Missing KOORDINATSYSTEM or KOORDSYS")

    # Check ENHET (typically 0.01 for cm precision)
    enhet = header.get('ENHET')
    if enhet:
        if enhet not in [0.01, 0.001, 1.0]:
            errors.append(
                f"SOSI-007: Unusual ENHET value {enhet}. Typical: 0.01 (cm precision)"
            )

    return errors


def validate_coordinate_encoding(coords: List[Tuple[int, int]],
                                 origo: Tuple[float, float],
                                 enhet: float) -> List[str]:
    """
    Validate coordinate encoding in SOSI format.

    Args:
        coords: List of integer coordinate pairs
        origo: ORIGO-NØ reference point (northing, easting)
        enhet: ENHET scaling factor

    Returns:
        List of validation errors
    """
    errors = []

    # Check coordinates are integers
    for i, (n, e) in enumerate(coords):
        if not isinstance(n, int) or not isinstance(e, int):
            errors.append(
                f"SOSI-008: Coordinate {i} not encoded as integer: ({n}, {e})"
            )

    # Check coordinate range is reasonable
    for i, (n, e) in enumerate(coords):
        # Decode to real coordinates
        real_n = origo[0] + n * enhet
        real_e = origo[1] + e * enhet

        # Check if in Norway (rough bounds)
        if not (6400000 <= real_n <= 7950000):
            errors.append(
                f"SOSI-009: Coordinate {i} northing {real_n:.2f} outside Norway bounds"
            )
        if not (-75000 <= real_e <= 1200000):
            errors.append(
                f"SOSI-010: Coordinate {i} easting {real_e:.2f} outside reasonable bounds"
            )

    return errors


# ============================================================================
# 6. TOPOLOGY VALIDATORS
# ============================================================================

def validate_type2_flate_topology(flate: Dict[str, Any],
                                   avgrensning_features: List[Dict[str, Any]]) -> List[str]:
    """
    Validate Type 2 flate: område = union(avgrensningsobjekter).
    This is the MOST CRITICAL FKB validation rule (TOPO-CRITICAL-001).

    Args:
        flate: The flate feature (must have område geometry)
        avgrensning_features: List of boundary features that should form the flate

    Returns:
        List of validation errors
    """
    errors = []

    # Check flate has område geometry
    if 'område' not in flate:
        errors.append("TOPO-001: Type 2 flate missing 'område' geometry")
        return errors

    omrade_geom = flate['område']
    if isinstance(omrade_geom, dict):
        omrade_geom = shape(omrade_geom)

    if not isinstance(omrade_geom, Polygon):
        errors.append("TOPO-002: Type 2 flate 'område' must be a Polygon")
        return errors

    # Build union of boundary geometries
    from shapely.ops import linemerge, polygonize

    boundary_lines = []
    for avgrensning in avgrensning_features:
        if 'geometry' in avgrensning:
            geom = avgrensning['geometry']
            if isinstance(geom, dict):
                geom = shape(geom)
            if isinstance(geom, LineString):
                boundary_lines.append(geom)

    if not boundary_lines:
        errors.append("TOPO-003: No boundary LineStrings found for Type 2 flate")
        return errors

    # Merge lines and create polygon
    try:
        merged = linemerge(boundary_lines)
        polygons = list(polygonize([merged]))

        if not polygons:
            errors.append("TOPO-004: Boundary lines do not form closed polygon")
            return errors

        constructed_poly = polygons[0]

        # Compare with område geometry (with tolerance)
        tolerance = flate.get('KVALITET', {}).get('NØYAKTIGHET', 0.10) * 2

        # Check area difference
        area_diff = abs(omrade_geom.area - constructed_poly.area)
        if area_diff > tolerance * tolerance:  # Squared for area
            errors.append(
                f"TOPO-005: Type 2 flate area mismatch. "
                f"Område: {omrade_geom.area:.2f} m², "
                f"Constructed: {constructed_poly.area:.2f} m² "
                f"(diff: {area_diff:.2f} m²)"
            )

        # Check symmetric difference (XOR)
        sym_diff = omrade_geom.symmetric_difference(constructed_poly)
        if sym_diff.area > tolerance * tolerance:
            errors.append(
                f"TOPO-006: Type 2 flate geometry mismatch. "
                f"Symmetric difference area: {sym_diff.area:.2f} m²"
            )

    except Exception as e:
        errors.append(f"TOPO-007: Error constructing polygon from boundaries: {e}")

    return errors


def validate_network_topology(features: List[Dict[str, Any]],
                              network_type: str = 'road') -> List[str]:
    """
    Validate network connectivity (roads, utilities).

    Args:
        features: List of network segment features
        network_type: 'road', 'water', 'sewer', etc.

    Returns:
        List of validation errors
    """
    errors = []

    if not features:
        return errors

    # Build graph of endpoints
    from collections import defaultdict
    endpoint_graph = defaultdict(list)

    for feature in features:
        if 'geometry' not in feature:
            continue

        geom = feature['geometry']
        if isinstance(geom, dict):
            geom = shape(geom)

        if not isinstance(geom, LineString):
            continue

        # Get endpoints
        start = tuple(geom.coords[0][:2])
        end = tuple(geom.coords[-1][:2])

        endpoint_graph[start].append(feature)
        endpoint_graph[end].append(feature)

    # Check for dangling endpoints (degree 1)
    dangling_count = 0
    for point, connected_features in endpoint_graph.items():
        if len(connected_features) == 1:
            dangling_count += 1
            if dangling_count <= 5:  # Report first 5
                errors.append(
                    f"TOPO-008: Dangling {network_type} endpoint at "
                    f"({point[0]:.2f}, {point[1]:.2f})"
                )

    if dangling_count > 5:
        errors.append(
            f"TOPO-009: Found {dangling_count} dangling endpoints (showing first 5)"
        )

    return errors


def validate_shared_boundaries(features: List[Dict[str, Any]]) -> List[str]:
    """
    Validate shared boundaries (delt geometri) between adjacent polygons.

    Args:
        features: List of polygon features that should share boundaries

    Returns:
        List of validation errors
    """
    errors = []
    warnings = []

    polygons = []
    for feature in features:
        if 'geometry' not in feature:
            continue
        geom = feature['geometry']
        if isinstance(geom, dict):
            geom = shape(geom)
        if isinstance(geom, Polygon):
            polygons.append((feature, geom))

    # Check each pair of adjacent polygons
    for i, (feat1, poly1) in enumerate(polygons):
        for j, (feat2, poly2) in enumerate(polygons[i+1:], i+1):
            # Check if polygons touch
            if not poly1.touches(poly2):
                continue

            # Get shared boundary
            intersection = poly1.intersection(poly2)

            # Should be a LineString (1D), not a Polygon (2D overlap)
            if intersection.geom_type == 'Polygon' or intersection.area > 0:
                errors.append(
                    f"TOPO-010: Polygons {i} and {j} overlap (area: {intersection.area:.2f} m²)"
                )
            elif intersection.geom_type == 'LineString':
                # Good - they share a boundary
                # Check that coordinates match exactly (delt geometri)
                # This would require comparing actual coordinate arrays
                pass
            elif intersection.is_empty:
                # Check if they're close but not touching (gap)
                distance = poly1.distance(poly2)
                if distance < 0.01:  # Less than 1cm gap
                    warnings.append(
                        f"TOPO-WARN-001: Small gap ({distance*100:.1f} cm) between polygons {i} and {j}"
                    )

    return errors + warnings


# ============================================================================
# 7. COMPREHENSIVE VALIDATION
# ============================================================================

def validate_feature(feature: Dict[str, Any],
                     fkb_standard: str = 'B',
                     strict: bool = False) -> Dict[str, List[str]]:
    """
    Run all validators on a single feature.

    Args:
        feature: Parsed SOSI feature as dict
        fkb_standard: FKB standard ('A', 'B', 'C', 'D')
        strict: If True, also run optional validators

    Returns:
        Dictionary mapping validator names to error lists
    """
    results = {}

    objtype = feature.get('OBJTYPE', 'Unknown')

    # Run all validators
    results['attributes'] = validate_mandatory_attributes(feature, objtype)
    results['geometry'] = validate_geometry(feature, objtype)
    results['accuracy'] = validate_accuracy(feature, fkb_standard)
    results['metadata'] = validate_kvalitet_block(feature)
    results['common'] = validate_common_attributes(feature)

    if strict:
        results['optional_attrs'] = validate_optional_attributes(feature, objtype)
        results['pilhoyde'] = validate_pilhoyde_constraint(feature, fkb_standard)

    return results


def validate_dataset(features: List[Dict[str, Any]],
                     header: Dict[str, Any],
                     fkb_standard: str = 'B') -> Dict[str, Any]:
    """
    Validate entire FKB dataset.

    Args:
        features: List of all features in dataset
        header: Parsed .HODE section
        fkb_standard: FKB standard ('A', 'B', 'C', 'D')

    Returns:
        Comprehensive validation report
    """
    report = {
        'header_errors': validate_sosi_header(header),
        'feature_errors': [],
        'topology_errors': [],
        'summary': {
            'total_features': len(features),
            'total_errors': 0,
            'total_warnings': 0
        }
    }

    # Validate each feature
    for i, feature in enumerate(features):
        feature_results = validate_feature(feature, fkb_standard)

        # Count errors
        error_count = sum(len(errors) for errors in feature_results.values())
        if error_count > 0:
            report['feature_errors'].append({
                'feature_index': i,
                'objtype': feature.get('OBJTYPE', 'Unknown'),
                'errors': feature_results,
                'error_count': error_count
            })
            report['summary']['total_errors'] += error_count

    # Validate topology (requires all features)
    report['topology_errors'] = validate_network_topology(features)
    report['topology_errors'].extend(validate_shared_boundaries(features))

    report['summary']['total_errors'] += len(report['topology_errors'])

    return report
