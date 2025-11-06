"""
FKB Validation Module

Comprehensive validation tools for FKB (Felles Kartgrunnlag) datasets.
Based on FKB 5.1 specifications.

Usage:
    from FKB.validation import validate_feature, validate_dataset
    from FKB.validation import generate_html_report

Example:
    # Validate single feature
    feature = {...}
    results = validate_feature(feature, fkb_standard='B')

    # Validate entire dataset
    features = [...]
    header = {...}
    report = validate_dataset(features, header, fkb_standard='B')

    # Generate HTML report
    html_path = generate_html_report(report, dataset_name="My Dataset")
"""

from .fkb_validators import (
    # Attribute validators
    validate_mandatory_attributes,
    validate_optional_attributes,

    # Geometry validators
    validate_geometry,
    validate_pilhoyde_constraint,

    # Accuracy validators
    validate_accuracy,

    # Metadata validators
    validate_kvalitet_block,
    validate_common_attributes,

    # SOSI format validators
    validate_sosi_header,
    validate_coordinate_encoding,

    # Topology validators
    validate_type2_flate_topology,
    validate_network_topology,
    validate_shared_boundaries,

    # Comprehensive validators
    validate_feature,
    validate_dataset,
)

from .validation_report import (
    generate_html_report,
    generate_json_report,
    generate_summary_report,
)

__all__ = [
    # Validators
    'validate_mandatory_attributes',
    'validate_optional_attributes',
    'validate_geometry',
    'validate_pilhoyde_constraint',
    'validate_accuracy',
    'validate_kvalitet_block',
    'validate_common_attributes',
    'validate_sosi_header',
    'validate_coordinate_encoding',
    'validate_type2_flate_topology',
    'validate_network_topology',
    'validate_shared_boundaries',
    'validate_feature',
    'validate_dataset',

    # Report generators
    'generate_html_report',
    'generate_json_report',
    'generate_summary_report',
]

__version__ = '1.0.0'
__author__ = 'GEO-MCP Server'
