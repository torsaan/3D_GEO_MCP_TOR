from app import mcp
from shapely.geometry import base , LineString
import numpy as np

@mcp.tool
def calculate_quality_metrics(extracted_geom: base.BaseGeometry, 
                              reference_geom: base.BaseGeometry) -> dict:
    """
    Computes Completeness, Correctness, and Quality for a
    single extracted geometry against a reference geometry.
    
    :param extracted_geom: The Shapely geometry you extracted.
    :param reference_geom: The "ground truth" Shapely geometry.
    :return: A dictionary with completeness, correctness, and quality scores.
    """
    if not extracted_geom.is_valid:
        return {"error": "Extracted geometry is invalid."}
    if not reference_geom.is_valid:
        return {"error": "Reference geometry is invalid."}

    # True Positives: extracted ∩ reference
    tp = extracted_geom.intersection(reference_geom).area
    
    # False Positives: extracted - reference
    fp = extracted_geom.difference(reference_geom).area
    
    # False Negatives: reference - extracted
    fn = reference_geom.difference(extracted_geom).area
    
    completeness = tp / (tp + fn) if (tp + fn) > 0 else 0
    correctness = tp / (tp + fp) if (tp + fp) > 0 else 0
    quality = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0
    
    return {
        'completeness': round(completeness, 4),
        'correctness': round(correctness, 4),
        'quality': round(quality, 4)
    }
@mcp.tool
def validate_fkb_object(geometry: base.BaseGeometry, metadata: dict) -> dict:
    """
    Validates an FKB object against rules: metadata presence and pilhøyde (curve precision).

    :param geometry: Shapely geometry.
    :param metadata: Dict with FKB keys like 'DATAFANGSTDATO', 'KVALITET', etc.
    :return: Dict with validation results.
    """
    results = {'valid': True, 'errors': []}

    # Check mandatory metadata
    required_keys = ['OBJTYPE', 'DATAFANGSTDATO', 'REGISTRERINGSVERSJON', 'KVALITET']
    for key in required_keys:
        if key not in metadata:
            results['valid'] = False
            results['errors'].append(f"Missing metadata: {key}")
            
    # Pilhøyde check for lines
    if isinstance(geometry, LineString):
        coords = np.array(geometry.coords)
        if len(coords) > 2: # Need at least 3 points to check deviation
            # Get tolerance from metadata if available, else default
            try:
                # Assumes KVALITET is a dict after being processed
                tolerance = float(metadata.get('KVALITET', {}).get('NØYAKTIGHET', 10)) / 100.0 # Convert cm to meters
            except:
                 tolerance = 0.1 # Default 10cm if metadata missing/invalid
                 
            for i in range(len(coords) - 2):
                p1 = coords[i]
                p2 = coords[i+1]
                p3 = coords[i+2]
                
                # Create a straight line segment from p1 to p3
                segment = LineString([p1, p3])
                
                # Calculate the distance from the midpoint (p2) to the segment
                deviation = segment.distance(Point(p2))
                
                if deviation > tolerance:
                    results['valid'] = False
                    results['errors'].append(f"Pilhøyde violation: Point {i+1} deviates {deviation:.3f}m > tolerance {tolerance:.3f}m")

    # Add more checks: self-intersection, correct geometry type based on OBJTYPE, etc.

    return results