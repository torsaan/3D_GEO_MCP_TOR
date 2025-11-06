"""
FKB-specific MCP tools for validation, parsing, and extraction.
"""

from app import mcp
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@mcp.tool
def validate_fkb_sosi_file(
    filepath: str,
    fkb_standard: str = 'B',
    generate_html_report: bool = True
) -> dict:
    """
    Validate SOSI file against FKB rules and generate validation report.

    Args:
        filepath: Path to SOSI file (.sos)
        fkb_standard: FKB standard to validate against ('A', 'B', 'C', or 'D')
        generate_html_report: Generate HTML validation report (default: True)

    Returns:
        Validation results with summary and optional report path

    Example:
        >>> result = validate_fkb_sosi_file('data/bygninger.sos', 'B', True)
        >>> print(f"Status: {result['status']}")
        >>> print(f"Errors: {result['total_errors']}")
        >>> print(f"Report: {result['html_report']}")
    """
    from FKB.sosi_parser import parse_sosi_file
    from FKB.validation import validate_dataset, generate_html_report, generate_summary_report

    try:
        # Parse SOSI file
        logger.info(f"Parsing SOSI file: {filepath}")
        features, header = parse_sosi_file(filepath)

        # Validate
        logger.info(f"Validating against FKB-{fkb_standard}")
        validation_report = validate_dataset(features, header, fkb_standard)

        # Build result
        result = {
            'status': 'PASS' if validation_report['summary']['total_errors'] == 0 else 'FAIL',
            'total_features': validation_report['summary']['total_features'],
            'total_errors': validation_report['summary']['total_errors'],
            'features_with_errors': len(validation_report.get('feature_errors', [])),
            'fkb_standard': fkb_standard,
            'source_file': filepath
        }

        # Generate HTML report if requested
        if generate_html_report:
            dataset_name = Path(filepath).stem
            report_path = str(Path(filepath).with_suffix('.validation.html'))

            generate_html_report(
                validation_report,
                dataset_name=dataset_name,
                output_path=report_path
            )

            result['html_report'] = report_path
            logger.info(f"HTML report generated: {report_path}")

        # Add text summary
        result['summary'] = generate_summary_report(validation_report)

        return result

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {
            'status': 'ERROR',
            'error': str(e),
            'source_file': filepath
        }


@mcp.tool
def convert_sosi_to_geojson(
    sosi_filepath: str,
    output_path: Optional[str] = None
) -> dict:
    """
    Convert SOSI file to GeoJSON format.

    Args:
        sosi_filepath: Path to SOSI file (.sos)
        output_path: Optional output path for GeoJSON (default: same name with .geojson)

    Returns:
        Result with output path and feature count

    Example:
        >>> result = convert_sosi_to_geojson('data/bygninger.sos')
        >>> print(f"Converted {result['feature_count']} features")
        >>> print(f"Output: {result['output_path']}")
    """
    from FKB.sosi_parser import sosi_to_geojson

    try:
        # Default output path
        if output_path is None:
            output_path = str(Path(sosi_filepath).with_suffix('.geojson'))

        # Convert
        logger.info(f"Converting {sosi_filepath} to GeoJSON")
        geojson = sosi_to_geojson(sosi_filepath, output_path)

        return {
            'status': 'SUCCESS',
            'source_file': sosi_filepath,
            'output_path': output_path,
            'feature_count': len(geojson['features']),
            'crs': geojson.get('crs', {}).get('properties', {}).get('name', 'unknown')
        }

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return {
            'status': 'ERROR',
            'error': str(e),
            'source_file': sosi_filepath
        }


@mcp.tool
def analyze_point_cloud_file(
    las_filepath: str,
    classification_codes: Optional[list] = None,
    compute_statistics: bool = True
) -> dict:
    """
    Analyze LAS/LAZ point cloud file and return statistics.

    Args:
        las_filepath: Path to LAS or LAZ file
        classification_codes: Optional list of classification codes to analyze (e.g., [6] for buildings)
        compute_statistics: Compute detailed statistics (default: True)

    Returns:
        Point cloud statistics and metadata

    Example:
        >>> result = analyze_point_cloud_file('scan.las', classification_codes=[6])
        >>> print(f"Total points: {result['total_points']:,}")
        >>> print(f"Building points: {result['filtered_points']:,}")
        >>> print(f"Bounds: {result['bounds']}")
    """
    from pointcloud_core import PointCloudProcessor
    import numpy as np

    try:
        # Load point cloud
        logger.info(f"Analyzing point cloud: {las_filepath}")
        processor = PointCloudProcessor(las_filepath)
        processor.load()

        result = {
            'status': 'SUCCESS',
            'source_file': las_filepath,
            'total_points': len(processor.points)
        }

        # Filter if requested
        if classification_codes:
            filtered_points = processor.filter_by_classification(classification_codes)
            result['filtered_points'] = len(filtered_points)
            result['classification_codes'] = classification_codes
            points_to_analyze = filtered_points
        else:
            points_to_analyze = processor.points

        # Compute statistics
        if compute_statistics and len(points_to_analyze) > 0:
            result['bounds'] = {
                'min_x': float(points_to_analyze[:, 0].min()),
                'max_x': float(points_to_analyze[:, 0].max()),
                'min_y': float(points_to_analyze[:, 1].min()),
                'max_y': float(points_to_analyze[:, 1].max()),
                'min_z': float(points_to_analyze[:, 2].min()),
                'max_z': float(points_to_analyze[:, 2].max())
            }

            result['statistics'] = {
                'mean_x': float(points_to_analyze[:, 0].mean()),
                'mean_y': float(points_to_analyze[:, 1].mean()),
                'mean_z': float(points_to_analyze[:, 2].mean()),
                'std_z': float(points_to_analyze[:, 2].std())
            }

            # Estimate point density
            area = (result['bounds']['max_x'] - result['bounds']['min_x']) * \
                   (result['bounds']['max_y'] - result['bounds']['min_y'])
            if area > 0:
                result['point_density'] = float(len(points_to_analyze) / area)

        return result

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {
            'status': 'ERROR',
            'error': str(e),
            'source_file': las_filepath
        }


@mcp.tool
def extract_buildings_to_sosi(
    las_filepath: str,
    output_sosi_path: str,
    fkb_standard: str = 'B',
    coordinate_system: int = 25,
    origo_ne: list = [6500000, 100000],
    min_building_points: int = 50,
    validate_output: bool = True
) -> dict:
    """
    Extract buildings from LAS file and generate FKB-compliant SOSI file.

    Args:
        las_filepath: Path to LAS/LAZ file
        output_sosi_path: Output path for SOSI file
        fkb_standard: FKB standard ('A', 'B', 'C', or 'D')
        coordinate_system: EPSG coordinate system code (e.g., 25 for UTM33N)
        origo_ne: ORIGO-NØ reference point [northing, easting]
        min_building_points: Minimum points to consider as building
        validate_output: Validate generated SOSI file (default: True)

    Returns:
        Extraction results with building count and file paths

    Example:
        >>> result = extract_buildings_to_sosi(
        ...     'scan.las',
        ...     'output/buildings.sos',
        ...     fkb_standard='B',
        ...     coordinate_system=25
        ... )
        >>> print(f"Extracted {result['building_count']} buildings")
        >>> print(f"Output: {result['sosi_file']}")
    """
    from pointcloud_core import PointCloudProcessor
    from clustering import PointCloudClusterer
    from geometric_extraction import extract_building_footprint
    from sosi_generator import SOSIGenerator

    try:
        # 1. Load and filter building points
        logger.info(f"Loading point cloud: {las_filepath}")
        processor = PointCloudProcessor(las_filepath, fkb_standard=fkb_standard)
        processor.load()

        building_points = processor.filter_by_classification([6])  # Class 6 = Buildings
        logger.info(f"Found {len(building_points)} building points")

        if len(building_points) < min_building_points:
            return {
                'status': 'WARNING',
                'message': f'Only {len(building_points)} building points found (minimum: {min_building_points})',
                'building_count': 0
            }

        # 2. Cluster buildings
        logger.info("Clustering buildings...")
        params = processor.get_recommended_parameters()
        clusterer = PointCloudClusterer(building_points)
        labels = clusterer.cluster_hdbscan(
            min_cluster_size=params['min_cluster_size']
        )
        clusters = clusterer.extract_clusters()
        logger.info(f"Found {len(clusters)} building clusters")

        # 3. Initialize SOSI generator
        generator = SOSIGenerator(
            fkb_dataset='FKB-Bygning',
            coordinate_system=coordinate_system,
            origo_ne=tuple(origo_ne),
            fkb_standard=fkb_standard
        )

        # 4. Extract footprints and add to SOSI
        building_count = 0
        for i, cluster in enumerate(clusters):
            if cluster['size'] < min_building_points:
                continue

            # Extract footprint
            footprint = extract_building_footprint(
                cluster['points'],
                fkb_standard=fkb_standard,
                simplify=True
            )

            # Add to SOSI
            metadata = {
                'bygningsnummer': 10000 + building_count,
                **processor.get_fkb_metadata()
            }

            generator.add_feature(footprint, 'Bygning', metadata, validate=False)
            building_count += 1

        # 5. Write SOSI file
        logger.info(f"Writing SOSI file with {building_count} buildings")
        sosi_path = generator.write_file(output_sosi_path, validate_output=False)

        result = {
            'status': 'SUCCESS',
            'source_file': las_filepath,
            'sosi_file': sosi_path,
            'building_count': building_count,
            'total_building_points': len(building_points),
            'fkb_standard': fkb_standard
        }

        # 6. Validate if requested
        if validate_output and building_count > 0:
            validation_result = validate_fkb_sosi_file(
                sosi_path,
                fkb_standard=fkb_standard,
                generate_html_report=True
            )
            result['validation'] = validation_result

        # Also generate GeoJSON
        geojson_path = str(Path(output_sosi_path).with_suffix('.geojson'))
        geojson = generator.to_geojson()
        import json
        with open(geojson_path, 'w') as f:
            json.dump(geojson, f, indent=2)
        result['geojson_file'] = geojson_path

        return result

    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return {
            'status': 'ERROR',
            'error': str(e),
            'source_file': las_filepath
        }


@mcp.tool
def get_fkb_accuracy_recommendations(
    fkb_standard: str,
    accuracy_class: int = 2
) -> dict:
    """
    Get recommended processing parameters for FKB standard and accuracy class.

    Args:
        fkb_standard: FKB standard ('A', 'B', 'C', or 'D')
        accuracy_class: Accuracy class (1-4)

    Returns:
        Dictionary with recommended parameters for point cloud processing

    Example:
        >>> params = get_fkb_accuracy_recommendations('B', 2)
        >>> print(f"Voxel size: {params['voxel_size']}m")
        >>> print(f"RANSAC threshold: {params['ransac_threshold']}m")
    """
    from pointcloud_core import PointCloudProcessor, FKB_ACCURACY_STANDARDS

    # Get accuracy standard
    standard_key = f'class_{accuracy_class}'
    accuracy = FKB_ACCURACY_STANDARDS.get(fkb_standard.upper(), {}).get(standard_key, 0.50)

    # Calculate recommended parameters
    params = {
        'fkb_standard': fkb_standard.upper(),
        'accuracy_class': accuracy_class,
        'accuracy_standard': accuracy,
        'voxel_size': accuracy / 2.0,
        'ransac_threshold': accuracy * 2.0,
        'simplification_tolerance': accuracy,
        'clustering_eps': accuracy * 3.0,
        'min_cluster_size': int(100 / accuracy_class),
        'alpha_shape_alpha': accuracy * 2.0
    }

    return params
