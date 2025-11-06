"""
SOSI File Generator for FKB Data

Generates FKB-compliant SOSI files from extracted geometries.
Includes validation using FKB rules.
"""

import numpy as np
from shapely.geometry import Point, LineString, Polygon, mapping
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SOSIGenerator:
    """Generate FKB-compliant SOSI files from extracted features."""

    def __init__(
        self,
        fkb_dataset: str,
        coordinate_system: int,
        origo_ne: Tuple[float, float],
        fkb_standard: str = 'B',
        enhet: float = 0.01
    ):
        """
        Initialize SOSI generator.

        Args:
            fkb_dataset: FKB dataset name (e.g., 'FKB-Bygning', 'FKB-Veg')
            coordinate_system: EPSG/SOSI coordinate system code (e.g., 25 for UTM33N)
            origo_ne: ORIGO-NØ reference point (northing, easting)
            fkb_standard: FKB standard ('A', 'B', 'C', or 'D')
            enhet: ENHET scaling factor (0.01 = cm precision, 0.001 = mm)

        Example:
            >>> generator = SOSIGenerator(
            ...     fkb_dataset='FKB-Bygning',
            ...     coordinate_system=25,  # UTM33N
            ...     origo_ne=(6500000, 100000),
            ...     fkb_standard='B'
            ... )
        """
        self.fkb_dataset = fkb_dataset
        self.coordinate_system = coordinate_system
        self.origo_ne = origo_ne
        self.fkb_standard = fkb_standard.upper()
        self.enhet = enhet

        self.features = []
        self.feature_id_counter = 1

        # Calculate bounds
        self.min_ne = [float('inf'), float('inf')]
        self.max_ne = [float('-inf'), float('-inf')]

        logger.info(f"SOSI Generator initialized for {fkb_dataset} (FKB-{fkb_standard})")
        logger.info(f"Coordinate system: {coordinate_system}, ENHET: {enhet}")

    def add_feature(
        self,
        geometry,
        objtype: str,
        metadata: Optional[Dict] = None,
        validate: bool = True
    ) -> int:
        """
        Add feature to SOSI file.

        Args:
            geometry: Shapely geometry (Point, LineString, Polygon)
            objtype: FKB OBJTYPE (e.g., 'Bygning', 'Vegkant')
            metadata: Feature attributes (automatically adds KVALITET if missing)
            validate: Run validation before adding (default: True)

        Returns:
            Feature ID assigned

        Example:
            >>> from shapely.geometry import Polygon
            >>> poly = Polygon([(100000, 6500000), (100010, 6500000),
            ...                 (100010, 6500010), (100000, 6500010),
            ...                 (100000, 6500000)])
            >>> feature_id = generator.add_feature(
            ...     poly,
            ...     'Bygning',
            ...     {'bygningsnummer': 12345}
            ... )
        """
        from geometric_extraction import geometry_to_sosi_coords, format_fkb_attributes

        # Prepare metadata
        if metadata is None:
            metadata = {}

        # Ensure KVALITET block exists
        if 'KVALITET' not in metadata:
            metadata['KVALITET'] = self._get_default_kvalitet()

        # Format complete attributes
        attributes = format_fkb_attributes(
            objtype,
            {k: v for k, v in metadata.items() if k != 'KVALITET'},
            metadata['KVALITET']
        )

        # Validate if requested
        if validate:
            errors = self._validate_feature(geometry, objtype, attributes)
            if errors:
                logger.warning(f"Feature validation found {len(errors)} errors:")
                for error in errors[:5]:  # Show first 5
                    logger.warning(f"  - {error}")

        # Convert geometry and update bounds
        coords = geometry_to_sosi_coords(geometry, self.origo_ne, self.enhet)
        self._update_bounds(coords)

        # Store feature
        feature = {
            'id': self.feature_id_counter,
            'objtype': objtype,
            'geometry': geometry,
            'attributes': attributes,
            'sosi_coords': coords
        }

        self.features.append(feature)
        logger.info(f"Added {objtype} feature #{self.feature_id_counter}")

        self.feature_id_counter += 1
        return feature.get('id')

    def _get_default_kvalitet(self) -> Dict:
        """Get default KVALITET block based on FKB standard."""
        from pointcloud_core import FKB_ACCURACY_STANDARDS

        # Get accuracy for standard class 2 (typical default)
        accuracy = FKB_ACCURACY_STANDARDS.get(self.fkb_standard, {}).get('class_2', 0.50)

        today = datetime.now().strftime('%Y%m%d')

        return {
            'MÅLEMETODE': 'lan',  # Laser scanning
            'NØYAKTIGHET': accuracy,
            'H-NØYAKTIGHET': accuracy,
            'SYNBARHET': 0,
            'DATAFANGSTDATO': today,
            'VERIFISERINGSDATO': today
        }

    def _update_bounds(self, coords: List[Tuple[int, int]]):
        """Update dataset bounds based on coordinates."""
        for n, e in coords:
            self.min_ne[0] = min(self.min_ne[0], n)
            self.min_ne[1] = min(self.min_ne[1], e)
            self.max_ne[0] = max(self.max_ne[0], n)
            self.max_ne[1] = max(self.max_ne[1], e)

    def _validate_feature(self, geometry, objtype: str, attributes: Dict) -> List[str]:
        """
        Basic validation using FKB rules.

        Args:
            geometry: Shapely geometry
            objtype: OBJTYPE
            attributes: Feature attributes

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check geometry validity
        if not geometry.is_valid:
            from shapely.validation import explain_validity
            errors.append(f"Invalid geometry: {explain_validity(geometry)}")

        # Check KVALITET block
        if 'KVALITET' not in attributes:
            errors.append("Missing KVALITET block")
        else:
            kvalitet = attributes['KVALITET']
            required = ['MÅLEMETODE', 'NØYAKTIGHET', 'SYNBARHET', 'DATAFANGSTDATO', 'VERIFISERINGSDATO']
            for attr in required:
                if attr not in kvalitet:
                    errors.append(f"Missing KVALITET attribute: {attr}")

        # Check OBJTYPE
        if 'OBJTYPE' not in attributes:
            errors.append("Missing OBJTYPE attribute")

        return errors

    def write_file(self, output_path: str, validate_output: bool = True) -> str:
        """
        Write complete SOSI file.

        Args:
            output_path: Output file path
            validate_output: Run validation on generated file (default: True)

        Returns:
            Path to generated file

        Example:
            >>> generator.write_file('output/bygninger.sos')
            'output/bygninger.sos'
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = []

        # .HODE section
        lines.extend(self._generate_header())

        # Features
        for feature in self.features:
            lines.extend(self._generate_feature(feature))

        # .SLUTT
        lines.append(".SLUTT")

        # Write to file
        content = '\n'.join(lines)
        output_path.write_text(content, encoding='utf-8')

        logger.info(f"SOSI file written: {output_path}")
        logger.info(f"  Features: {len(self.features)}")
        logger.info(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

        # Validate if requested
        if validate_output:
            validation_errors = self.validate_output()
            if validation_errors:
                logger.warning(f"Output validation found {len(validation_errors)} issues:")
                for error in validation_errors[:10]:
                    logger.warning(f"  - {error}")
            else:
                logger.info("✅ Output validation passed")

        return str(output_path)

    def _generate_header(self) -> List[str]:
        """Generate .HODE section."""
        today = datetime.now().strftime('%Y%m%d')

        # Convert bounds to real coordinates
        min_n = self.origo_ne[0] + self.min_ne[0] * self.enhet
        min_e = self.origo_ne[1] + self.min_ne[1] * self.enhet
        max_n = self.origo_ne[0] + self.max_ne[0] * self.enhet
        max_e = self.origo_ne[1] + self.max_ne[1] * self.enhet

        header = [
            ".HODE",
            "..TEGNSETT UTF-8",
            "..SOSI-VERSJON 4.5",
            "..SOSI-NIVÅ 4",
            f"..TRANSPAR",
            f"...KOORDSYS {self.coordinate_system}",
            f"...ORIGO-NØ {self.origo_ne[0]} {self.origo_ne[1]}",
            f"...ENHET {self.enhet}",
            f"...VERT-DATUM NN2000",
            f"..OMRÅDE",
            f"...MIN-NØ {min_n:.2f} {min_e:.2f}",
            f"...MAX-NØ {max_n:.2f} {max_e:.2f}",
            f"..EIER \"{self.fkb_dataset}\"",
            f"..PRODUSENT \"GEO-MCP Point Cloud Extractor\"",
            f"..OBJEKTKATALOG \"{self.fkb_dataset} 5.1\"",
            f"..DATO {today}",
        ]

        return header

    def _generate_feature(self, feature: Dict) -> List[str]:
        """Generate SOSI feature text."""
        lines = []

        # Feature header
        objtype = feature['objtype']
        feature_id = feature['id']
        lines.append(f".{objtype} {feature_id}:")

        # Attributes
        for key, value in feature['attributes'].items():
            if key == 'OBJTYPE':
                continue  # Already in header
            elif key == 'KVALITET':
                # Nested KVALITET block
                lines.append("..KVALITET")
                for k, v in value.items():
                    if isinstance(v, str):
                        lines.append(f"...{k} \"{v}\"")
                    else:
                        lines.append(f"...{k} {v}")
            elif isinstance(value, str):
                lines.append(f"..{key} \"{value}\"")
            else:
                lines.append(f"..{key} {value}")

        # Geometry
        geom = feature['geometry']
        coords = feature['sosi_coords']

        if isinstance(geom, Point):
            n, e = coords[0]
            lines.append(f"..PUNKT")
            lines.append(f"{n} {e}")

        elif isinstance(geom, LineString):
            lines.append(f"..KURVE {len(coords)}:")
            for n, e in coords:
                lines.append(f"{n} {e}")

        elif isinstance(geom, Polygon):
            lines.append(f"..FLATE")
            lines.append(f"..KURVE {len(coords)}:")
            for n, e in coords:
                lines.append(f"{n} {e}")

        return lines

    def validate_output(self) -> List[str]:
        """
        Validate generated features using FKB validation rules.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check header
        if not self.features:
            errors.append("No features added to SOSI file")

        # Check bounds
        if self.min_ne[0] == float('inf'):
            errors.append("Bounds not calculated (no features added?)")

        # Basic feature validation
        for feature in self.features:
            feature_errors = self._validate_feature(
                feature['geometry'],
                feature['objtype'],
                feature['attributes']
            )
            if feature_errors:
                errors.extend([f"Feature {feature['id']}: {e}" for e in feature_errors])

        return errors

    def to_geojson(self) -> Dict:
        """
        Export features as GeoJSON FeatureCollection.

        Returns:
            GeoJSON dictionary

        Example:
            >>> geojson = generator.to_geojson()
            >>> import json
            >>> with open('output.geojson', 'w') as f:
            ...     json.dump(geojson, f, indent=2)
        """
        features = []

        for feature in self.features:
            geojson_feature = {
                'type': 'Feature',
                'id': feature['id'],
                'geometry': mapping(feature['geometry']),
                'properties': {
                    **feature['attributes'],
                    'sosi_id': feature['id']
                }
            }
            features.append(geojson_feature)

        return {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                    'name': f'EPSG:{self.coordinate_system}'
                }
            },
            'features': features
        }

    def get_statistics(self) -> Dict:
        """
        Get statistics about generated dataset.

        Returns:
            Dictionary with dataset statistics
        """
        from collections import Counter

        objtype_counts = Counter(f['objtype'] for f in self.features)

        # Calculate real-world bounds
        min_n = self.origo_ne[0] + self.min_ne[0] * self.enhet
        min_e = self.origo_ne[1] + self.min_ne[1] * self.enhet
        max_n = self.origo_ne[0] + self.max_ne[0] * self.enhet
        max_e = self.origo_ne[1] + self.max_ne[1] * self.enhet

        return {
            'total_features': len(self.features),
            'objtype_counts': dict(objtype_counts),
            'fkb_dataset': self.fkb_dataset,
            'fkb_standard': self.fkb_standard,
            'coordinate_system': self.coordinate_system,
            'bounds': {
                'min_n': min_n,
                'min_e': min_e,
                'max_n': max_n,
                'max_e': max_e,
                'width': max_e - min_e,
                'height': max_n - min_n
            }
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_building_extraction():
    """
    Example: Extract buildings from point cloud and generate SOSI file.
    """
    from shapely.geometry import Polygon
    from pointcloud_core import PointCloudProcessor

    # Initialize generator
    generator = SOSIGenerator(
        fkb_dataset='FKB-Bygning',
        coordinate_system=25,  # UTM33N
        origo_ne=(6500000, 100000),
        fkb_standard='B'
    )

    # Example building footprints (in reality, extracted from point cloud)
    buildings = [
        {
            'geometry': Polygon([
                (100000, 6500000),
                (100020, 6500000),
                (100020, 6500015),
                (100000, 6500015),
                (100000, 6500000)
            ]),
            'bygningsnummer': 100001,
            'area': 300.0
        },
        {
            'geometry': Polygon([
                (100030, 6500000),
                (100045, 6500000),
                (100045, 6500012),
                (100030, 6500012),
                (100030, 6500000)
            ]),
            'bygningsnummer': 100002,
            'area': 180.0
        }
    ]

    # Add buildings to SOSI
    for building in buildings:
        metadata = {
            'bygningsnummer': building['bygningsnummer'],
            'KVALITET': {
                'MÅLEMETODE': 'lan',
                'NØYAKTIGHET': 0.20,
                'SYNBARHET': 0,
                'DATAFANGSTDATO': '20231104',
                'VERIFISERINGSDATO': '20231104'
            }
        }

        generator.add_feature(
            building['geometry'],
            'Bygning',
            metadata
        )

    # Write SOSI file
    output_file = generator.write_file('output/bygninger.sos')
    print(f"✅ SOSI file generated: {output_file}")

    # Print statistics
    stats = generator.get_statistics()
    print(f"\nDataset Statistics:")
    print(f"  Total features: {stats['total_features']}")
    print(f"  FKB standard: FKB-{stats['fkb_standard']}")
    print(f"  Bounds: {stats['bounds']['width']:.1f}m × {stats['bounds']['height']:.1f}m")

    # Also export as GeoJSON
    import json
    geojson = generator.to_geojson()
    with open('output/bygninger.geojson', 'w') as f:
        json.dump(geojson, f, indent=2)
    print("✅ GeoJSON file generated: output/bygninger.geojson")


if __name__ == "__main__":
    print("SOSI Generator Example\n" + "=" * 50)
    example_building_extraction()
