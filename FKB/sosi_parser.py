"""
SOSI File Parser for FKB Data

Parses SOSI format files into structured Python data for validation and processing.
Handles .HODE sections, features with nested attributes, KVALITET blocks, and geometries.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from shapely.geometry import Point, LineString, Polygon
import logging

logger = logging.getLogger(__name__)


class SOSIParser:
    """Parse SOSI format files into structured data."""

    def __init__(self, filepath: str):
        """
        Initialize SOSI parser.

        Args:
            filepath: Path to SOSI file

        Example:
            >>> parser = SOSIParser('data/bygninger.sos')
            >>> features, header = parser.parse()
        """
        self.filepath = Path(filepath)
        self.lines = []
        self.current_line = 0

    def parse(self) -> Tuple[List[Dict], Dict]:
        """
        Parse complete SOSI file.

        Returns:
            Tuple of (features, header)
            - features: List of feature dictionaries
            - header: Parsed .HODE section as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not self.filepath.exists():
            raise FileNotFoundError(f"SOSI file not found: {self.filepath}")

        # Read file
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.lines = [line.rstrip() for line in f.readlines()]

        logger.info(f"Parsing SOSI file: {self.filepath} ({len(self.lines)} lines)")

        # Parse header
        header = self._parse_header()

        # Parse features
        features = self._parse_features(header)

        logger.info(f"Parsed {len(features)} features from {self.filepath.name}")

        return features, header

    def _parse_header(self) -> Dict:
        """
        Parse .HODE section.

        Returns:
            Dictionary with header attributes
        """
        header = {}

        if not self.lines or not self.lines[0].startswith('.HODE'):
            raise ValueError("SOSI file must start with .HODE")

        self.current_line = 1

        # Parse until we hit a feature or .SLUTT
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            # End of header
            if line.startswith('.') and not line.startswith('..'):
                break

            # Parse attribute
            if line.startswith('..'):
                key, value = self._parse_attribute(line, level=2)

                # Handle nested TRANSPAR
                if key == 'TRANSPAR':
                    self.current_line += 1
                    transpar = {}
                    while self.current_line < len(self.lines) and self.lines[self.current_line].startswith('...'):
                        sub_line = self.lines[self.current_line]
                        sub_key, sub_value = self._parse_attribute(sub_line, level=3)
                        transpar[sub_key] = sub_value
                        self.current_line += 1
                    header['TRANSPAR'] = transpar
                    continue

                # Handle nested OMRÅDE
                elif key == 'OMRÅDE':
                    self.current_line += 1
                    omrade = {}
                    while self.current_line < len(self.lines) and self.lines[self.current_line].startswith('...'):
                        sub_line = self.lines[self.current_line]
                        sub_key, sub_value = self._parse_attribute(sub_line, level=3)
                        omrade[sub_key] = sub_value
                        self.current_line += 1
                    header['OMRÅDE'] = omrade
                    continue

                else:
                    header[key] = value

            self.current_line += 1

        # Extract common values for convenience
        if 'TRANSPAR' in header:
            header['KOORDINATSYSTEM'] = header['TRANSPAR'].get('KOORDSYS')
            header['ORIGO-NØ'] = header['TRANSPAR'].get('ORIGO-NØ')
            header['ENHET'] = header['TRANSPAR'].get('ENHET')

        logger.info(f"Parsed header: {header.get('EIER', 'Unknown')} - SOSI {header.get('SOSI-VERSJON', '?')}")

        return header

    def _parse_features(self, header: Dict) -> List[Dict]:
        """
        Parse all features in file.

        Args:
            header: Parsed header (needed for coordinate decoding)

        Returns:
            List of feature dictionaries
        """
        features = []

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            # Skip empty lines
            if not line.strip():
                self.current_line += 1
                continue

            # End of file
            if line.startswith('.SLUTT'):
                break

            # Feature start (single dot, not .HODE)
            if line.startswith('.') and not line.startswith('..'):
                feature = self._parse_feature(header)
                if feature:
                    features.append(feature)
                continue

            self.current_line += 1

        return features

    def _parse_feature(self, header: Dict) -> Optional[Dict]:
        """
        Parse single feature.

        Args:
            header: Parsed header

        Returns:
            Feature dictionary or None if parsing fails
        """
        start_line = self.current_line
        line = self.lines[self.current_line]

        # Parse feature header: .OBJTYPE ID:
        match = re.match(r'\.(\w+)\s+(\d+):', line)
        if not match:
            logger.warning(f"Invalid feature header at line {start_line + 1}: {line}")
            self.current_line += 1
            return None

        objtype = match.group(1)
        feature_id = int(match.group(2))

        feature = {
            'OBJTYPE': objtype,
            'id': feature_id,
            'line_number': start_line + 1
        }

        self.current_line += 1

        # Parse attributes and geometry
        geometry = None
        kvalitet = {}

        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            # End of feature (next feature or end of file)
            if line.startswith('.') and not line.startswith('..'):
                break

            # Attribute
            if line.startswith('..'):
                key, value = self._parse_attribute(line, level=2)

                # KVALITET block
                if key == 'KVALITET':
                    self.current_line += 1
                    while self.current_line < len(self.lines) and self.lines[self.current_line].startswith('...'):
                        sub_line = self.lines[self.current_line]
                        sub_key, sub_value = self._parse_attribute(sub_line, level=3)
                        kvalitet[sub_key] = sub_value
                        self.current_line += 1
                    feature['KVALITET'] = kvalitet
                    continue

                # Geometry keywords
                elif key == 'PUNKT':
                    geometry = self._parse_point_geometry(header)
                elif key == 'KURVE':
                    geometry = self._parse_kurve_geometry(header, value)
                elif key == 'FLATE':
                    geometry = self._parse_flate_geometry(header)

                # Regular attribute
                else:
                    feature[key] = value

            self.current_line += 1

        # Add geometry if found
        if geometry:
            feature['geometry'] = geometry

        logger.debug(f"Parsed {objtype} #{feature_id}")

        return feature

    def _parse_point_geometry(self, header: Dict) -> Point:
        """Parse PUNKT geometry (single point)."""
        self.current_line += 1
        line = self.lines[self.current_line]

        # Parse integer coordinates
        parts = line.strip().split()
        if len(parts) < 2:
            raise ValueError(f"Invalid PUNKT at line {self.current_line + 1}")

        n_int = int(parts[0])
        e_int = int(parts[1])
        h_int = int(parts[2]) if len(parts) > 2 else 0

        # Decode to real coordinates
        n, e, h = self._decode_coordinates(n_int, e_int, h_int, header)

        return Point(e, n, h) if h != 0 else Point(e, n)

    def _parse_kurve_geometry(self, header: Dict, num_points: Any) -> LineString:
        """
        Parse KURVE geometry (linestring).

        Args:
            header: Header with coordinate system info
            num_points: Number of points (from ..KURVE line)
        """
        # Parse number of points
        if isinstance(num_points, str):
            try:
                num_points = int(num_points)
            except:
                num_points = None

        coords = []
        self.current_line += 1

        # Read coordinates until we hit non-coordinate line
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            # End of coordinates (attribute or feature)
            if line.startswith('.'):
                self.current_line -= 1  # Back up one line
                break

            # Parse coordinate line
            parts = line.strip().split()
            if len(parts) < 2:
                break

            try:
                n_int = int(parts[0])
                e_int = int(parts[1])
                h_int = int(parts[2]) if len(parts) > 2 else 0

                n, e, h = self._decode_coordinates(n_int, e_int, h_int, header)
                coords.append((e, n, h) if h != 0 else (e, n))

            except ValueError:
                break

            self.current_line += 1

            # Stop if we have expected number of points
            if num_points and len(coords) >= num_points:
                break

        if not coords:
            raise ValueError(f"No coordinates found for KURVE at line {self.current_line}")

        return LineString(coords)

    def _parse_flate_geometry(self, header: Dict) -> Polygon:
        """
        Parse FLATE geometry (polygon).

        FLATE is defined by a KURVE boundary.
        """
        self.current_line += 1

        # Look for KURVE defining the boundary
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]

            if line.startswith('..KURVE'):
                # Parse as LineString, then convert to Polygon
                key, value = self._parse_attribute(line, level=2)
                boundary = self._parse_kurve_geometry(header, value)

                # Convert to Polygon
                coords = list(boundary.coords)

                # Ensure closed (first == last)
                if coords[0] != coords[-1]:
                    coords.append(coords[0])

                return Polygon(coords)

            elif line.startswith('.'):
                # End of feature without KURVE
                raise ValueError(f"FLATE without KURVE at line {self.current_line}")

            self.current_line += 1

        raise ValueError("Unexpected end of file while parsing FLATE")

    def _parse_attribute(self, line: str, level: int) -> Tuple[str, Any]:
        """
        Parse attribute line.

        Args:
            line: Attribute line (e.g., "..OBJTYPE Bygning")
            level: Nesting level (2=.., 3=..., etc.)

        Returns:
            Tuple of (key, value)
        """
        # Remove leading dots
        prefix = '.' * level
        if not line.startswith(prefix):
            raise ValueError(f"Invalid attribute line: {line}")

        content = line[level:].strip()

        # Split on first whitespace
        parts = content.split(None, 1)

        if len(parts) == 1:
            # No value (e.g., "..KVALITET")
            return parts[0], None

        key = parts[0]
        value_str = parts[1]

        # Parse value
        value = self._parse_value(value_str)

        return key, value

    def _parse_value(self, value_str: str) -> Any:
        """
        Parse attribute value, handling different types.

        Args:
            value_str: String value

        Returns:
            Parsed value (str, int, float, list)
        """
        # Remove quotes if present
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]

        # Try to parse as number
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass

        # Multiple values (space-separated)
        parts = value_str.split()
        if len(parts) > 1:
            # Try to parse as numeric list
            try:
                return [float(p) if '.' in p else int(p) for p in parts]
            except ValueError:
                pass

        # Return as string
        return value_str

    def _decode_coordinates(
        self,
        n_int: int,
        e_int: int,
        h_int: int,
        header: Dict
    ) -> Tuple[float, float, float]:
        """
        Decode integer SOSI coordinates to real coordinates.

        Args:
            n_int: Integer northing
            e_int: Integer easting
            h_int: Integer height
            header: Header with ORIGO-NØ and ENHET

        Returns:
            Tuple of (northing, easting, height) in real coordinates
        """
        origo_ne = header.get('ORIGO-NØ', [0, 0])
        enhet = header.get('ENHET', 0.01)

        if isinstance(origo_ne, list) and len(origo_ne) >= 2:
            origo_n = origo_ne[0]
            origo_e = origo_ne[1]
        else:
            origo_n = 0
            origo_e = 0

        # Decode
        n = origo_n + n_int * enhet
        e = origo_e + e_int * enhet
        h = h_int * enhet if h_int != 0 else 0

        return n, e, h


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def parse_sosi_file(filepath: str) -> Tuple[List[Dict], Dict]:
    """
    Parse SOSI file into features and header.

    Args:
        filepath: Path to SOSI file

    Returns:
        Tuple of (features, header)

    Example:
        >>> features, header = parse_sosi_file('data/bygninger.sos')
        >>> print(f"Parsed {len(features)} features")
        >>> print(f"Dataset: {header.get('EIER')}")
    """
    parser = SOSIParser(filepath)
    return parser.parse()


def sosi_to_geojson(filepath: str, output_path: Optional[str] = None) -> Dict:
    """
    Convert SOSI file to GeoJSON.

    Args:
        filepath: Path to SOSI file
        output_path: Optional output path for GeoJSON

    Returns:
        GeoJSON FeatureCollection dict

    Example:
        >>> geojson = sosi_to_geojson('data/bygninger.sos', 'output/bygninger.geojson')
    """
    from shapely.geometry import mapping
    import json

    features, header = parse_sosi_file(filepath)

    # Convert to GeoJSON
    geojson_features = []
    for feature in features:
        geom = feature.get('geometry')
        if not geom:
            continue

        # Build properties
        properties = {k: v for k, v in feature.items() if k not in ['geometry', 'id', 'line_number']}

        geojson_feature = {
            'type': 'Feature',
            'id': feature.get('id'),
            'geometry': mapping(geom),
            'properties': properties
        }

        geojson_features.append(geojson_feature)

    geojson = {
        'type': 'FeatureCollection',
        'crs': {
            'type': 'name',
            'properties': {
                'name': f"EPSG:{header.get('KOORDINATSYSTEM', 'unknown')}"
            }
        },
        'features': geojson_features
    }

    # Write if output path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)
        logger.info(f"GeoJSON written to {output_path}")

    return geojson


def extract_kvalitet_summary(features: List[Dict]) -> Dict:
    """
    Extract summary of KVALITET metadata from features.

    Args:
        features: List of parsed features

    Returns:
        Dictionary with KVALITET statistics

    Example:
        >>> features, header = parse_sosi_file('data.sos')
        >>> summary = extract_kvalitet_summary(features)
        >>> print(f"Average accuracy: {summary['avg_noyaktighet']:.3f}m")
    """
    from collections import Counter

    metoder = []
    noyaktigheter = []
    synbarheter = []

    for feature in features:
        kvalitet = feature.get('KVALITET', {})
        if kvalitet:
            if 'MÅLEMETODE' in kvalitet:
                metoder.append(kvalitet['MÅLEMETODE'])
            if 'NØYAKTIGHET' in kvalitet:
                noyaktigheter.append(kvalitet['NØYAKTIGHET'])
            if 'SYNBARHET' in kvalitet:
                synbarheter.append(kvalitet['SYNBARHET'])

    summary = {
        'total_features': len(features),
        'features_with_kvalitet': sum(1 for f in features if 'KVALITET' in f),
        'metode_counts': dict(Counter(metoder)),
        'avg_noyaktighet': sum(noyaktigheter) / len(noyaktigheter) if noyaktigheter else 0,
        'min_noyaktighet': min(noyaktigheter) if noyaktigheter else 0,
        'max_noyaktighet': max(noyaktigheter) if noyaktigheter else 0,
        'synbarhet_counts': dict(Counter(synbarheter))
    }

    return summary


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python sosi_parser.py <sosi_file>")
        sys.exit(1)

    sosi_file = sys.argv[1]

    print(f"Parsing SOSI file: {sosi_file}")
    print("=" * 60)

    # Parse
    features, header = parse_sosi_file(sosi_file)

    # Print header info
    print(f"\nHeader Information:")
    print(f"  Dataset: {header.get('EIER', 'Unknown')}")
    print(f"  SOSI Version: {header.get('SOSI-VERSJON', 'Unknown')}")
    print(f"  Coordinate System: {header.get('KOORDINATSYSTEM', 'Unknown')}")
    print(f"  ORIGO-NØ: {header.get('ORIGO-NØ', 'Unknown')}")
    print(f"  ENHET: {header.get('ENHET', 'Unknown')}")

    # Print feature summary
    from collections import Counter
    objtype_counts = Counter(f['OBJTYPE'] for f in features)

    print(f"\nFeatures ({len(features)} total):")
    for objtype, count in objtype_counts.most_common():
        print(f"  {objtype}: {count}")

    # KVALITET summary
    kvalitet_summary = extract_kvalitet_summary(features)
    print(f"\nKVALITET Summary:")
    print(f"  Features with KVALITET: {kvalitet_summary['features_with_kvalitet']}/{kvalitet_summary['total_features']}")
    print(f"  Average accuracy: {kvalitet_summary['avg_noyaktighet']:.3f}m")
    print(f"  Methods used: {kvalitet_summary['metode_counts']}")

    # Export to GeoJSON
    output_geojson = sosi_file.replace('.sos', '_parsed.geojson')
    geojson = sosi_to_geojson(sosi_file, output_geojson)
    print(f"\n✅ GeoJSON exported to: {output_geojson}")
