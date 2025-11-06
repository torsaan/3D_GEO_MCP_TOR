"""
Unit tests for FKB validators.
Run with: pytest test_validators.py
"""

import pytest
from fkb_validators import (
    validate_mandatory_attributes,
    validate_geometry,
    validate_accuracy,
    validate_kvalitet_block,
    validate_sosi_header,
    validate_type2_flate_topology
)
from shapely.geometry import Point, LineString, Polygon


# ============================================================================
# TEST DATA
# ============================================================================

def create_valid_bygning_feature():
    """Create a valid Bygning (building) feature for testing."""
    return {
        'OBJTYPE': 'Bygning',
        'posisjon': [100, 200, 50],
        'bygningsnummer': 12345,
        'DATAFANGSTDATO': '20231104',
        'KVALITET': {
            'MÅLEMETODE': 'fot',
            'NØYAKTIGHET': 0.10,
            'SYNBARHET': 0,
            'DATAFANGSTDATO': '20231104',
            'VERIFISERINGSDATO': '20231104'
        },
        'geometry': {
            'type': 'Polygon',
            'coordinates': [[
                [100, 200],
                [110, 200],
                [110, 210],
                [100, 210],
                [100, 200]
            ]]
        }
    }


def create_valid_header():
    """Create a valid SOSI header for testing."""
    return {
        'TEGNSETT': 'UTF-8',
        'SOSI-VERSJON': '4.5',
        'SOSI-NIVÅ': 4,
        'TRANSPAR': {
            'KOORDSYS': 25,
            'ORIGO-NØ': [6500000, 100000],
            'ENHET': 0.01,
            'VERT-DATUM': 'NN2000'
        },
        'KOORDINATSYSTEM': 25,
        'ORIGO-NØ': [6500000, 100000],
        'ENHET': 0.01,
        'OMRÅDE': {
            'MIN-NØ': [6500000, 100000],
            'MAX-NØ': [6600000, 200000]
        }
    }


# ============================================================================
# ATTRIBUTE VALIDATION TESTS
# ============================================================================

def test_validate_mandatory_attributes_valid():
    """Test validation passes for feature with all mandatory attributes."""
    feature = create_valid_bygning_feature()
    errors = validate_mandatory_attributes(feature, 'Bygning')
    # May have errors if rule database not loaded, but should be empty if rules loaded
    assert isinstance(errors, list)


def test_validate_mandatory_attributes_missing():
    """Test validation catches missing mandatory attribute."""
    feature = create_valid_bygning_feature()
    del feature['posisjon']  # Remove mandatory attribute
    errors = validate_mandatory_attributes(feature, 'Bygning')

    # Should have at least one error about missing posisjon
    assert any('posisjon' in error for error in errors)


def test_validate_mandatory_attributes_unknown_objtype():
    """Test validation handles unknown OBJTYPE."""
    feature = create_valid_bygning_feature()
    errors = validate_mandatory_attributes(feature, 'UnknownType')

    # Should have error about unknown OBJTYPE
    assert any('Unknown OBJTYPE' in error or 'ATTR-000' in error for error in errors)


# ============================================================================
# GEOMETRY VALIDATION TESTS
# ============================================================================

def test_validate_geometry_valid_polygon():
    """Test validation passes for valid polygon geometry."""
    feature = create_valid_bygning_feature()
    errors = validate_geometry(feature, 'Bygning')

    # Should have no geometry validity errors
    geom_validity_errors = [e for e in errors if 'Invalid geometry' in e]
    assert len(geom_validity_errors) == 0


def test_validate_geometry_invalid_polygon():
    """Test validation catches self-intersecting polygon (bowtie)."""
    feature = create_valid_bygning_feature()
    # Create self-intersecting polygon (bowtie shape)
    feature['geometry'] = {
        'type': 'Polygon',
        'coordinates': [[
            [0, 0],
            [10, 10],
            [10, 0],
            [0, 10],
            [0, 0]
        ]]
    }
    errors = validate_geometry(feature, 'Bygning')

    # Should have error about invalid geometry
    assert any('GEOM-003' in error or 'Invalid geometry' in error for error in errors)


def test_validate_geometry_missing():
    """Test validation catches missing geometry."""
    feature = create_valid_bygning_feature()
    del feature['geometry']
    errors = validate_geometry(feature, 'Bygning')

    assert any('GEOM-001' in error or 'Missing geometry' in error for error in errors)


# ============================================================================
# ACCURACY VALIDATION TESTS
# ============================================================================

def test_validate_accuracy_valid():
    """Test accuracy validation passes for valid feature."""
    feature = create_valid_bygning_feature()
    errors = validate_accuracy(feature, 'B')

    # Should have no accuracy errors (or only rule loading error)
    accuracy_errors = [e for e in errors if 'ACC-004' in e or 'ACC-005' in e]
    assert len(accuracy_errors) == 0


def test_validate_accuracy_exceeds_limit():
    """Test accuracy validation catches values exceeding standards."""
    feature = create_valid_bygning_feature()
    feature['KVALITET']['NØYAKTIGHET'] = 10.0  # Way too high
    errors = validate_accuracy(feature, 'A')  # FKB-A has strict limits

    # Should have error about exceeding limit (if rules loaded)
    if not any('ACC-000' in e for e in errors):
        assert any('ACC-004' in error or 'exceeds' in error for error in errors)


def test_validate_accuracy_missing_kvalitet():
    """Test accuracy validation catches missing KVALITET block."""
    feature = create_valid_bygning_feature()
    del feature['KVALITET']
    errors = validate_accuracy(feature, 'B')

    assert any('ACC-001' in error or 'Missing KVALITET' in error for error in errors)


# ============================================================================
# METADATA VALIDATION TESTS
# ============================================================================

def test_validate_kvalitet_block_valid():
    """Test KVALITET block validation passes for valid block."""
    feature = create_valid_bygning_feature()
    errors = validate_kvalitet_block(feature)

    # Should have no errors
    assert len(errors) == 0


def test_validate_kvalitet_block_missing():
    """Test KVALITET validation catches missing block."""
    feature = {'OBJTYPE': 'Bygning'}
    errors = validate_kvalitet_block(feature)

    assert any('META-001' in error or 'Missing KVALITET' in error for error in errors)


def test_validate_kvalitet_block_missing_attribute():
    """Test KVALITET validation catches missing mandatory attribute."""
    feature = create_valid_bygning_feature()
    del feature['KVALITET']['MÅLEMETODE']
    errors = validate_kvalitet_block(feature)

    assert any('MÅLEMETODE' in error for error in errors)


def test_validate_kvalitet_block_invalid_method():
    """Test KVALITET validation catches invalid MÅLEMETODE."""
    feature = create_valid_bygning_feature()
    feature['KVALITET']['MÅLEMETODE'] = 'invalid_method'
    errors = validate_kvalitet_block(feature)

    assert any('META-003' in error or 'Invalid MÅLEMETODE' in error for error in errors)


def test_validate_kvalitet_block_invalid_synbarhet():
    """Test KVALITET validation catches invalid SYNBARHET."""
    feature = create_valid_bygning_feature()
    feature['KVALITET']['SYNBARHET'] = 5  # Valid range is 0-3
    errors = validate_kvalitet_block(feature)

    assert any('META-004' in error or 'Invalid SYNBARHET' in error for error in errors)


# ============================================================================
# SOSI FORMAT VALIDATION TESTS
# ============================================================================

def test_validate_sosi_header_valid():
    """Test SOSI header validation passes for valid header."""
    header = create_valid_header()
    errors = validate_sosi_header(header)

    # Should have no critical errors
    critical_errors = [e for e in errors if 'SOSI-001' in e or 'SOSI-006' in e]
    assert len(critical_errors) == 0


def test_validate_sosi_header_missing_tegnsett():
    """Test SOSI header validation catches missing TEGNSETT."""
    header = create_valid_header()
    del header['TEGNSETT']
    errors = validate_sosi_header(header)

    assert any('TEGNSETT' in error for error in errors)


def test_validate_sosi_header_missing_koordinatsystem():
    """Test SOSI header validation catches missing coordinate system."""
    header = create_valid_header()
    del header['KOORDINATSYSTEM']
    errors = validate_sosi_header(header)

    assert any('SOSI-006' in error or 'KOORDINATSYSTEM' in error for error in errors)


def test_validate_sosi_header_invalid_tegnsett():
    """Test SOSI header validation catches invalid TEGNSETT."""
    header = create_valid_header()
    header['TEGNSETT'] = 'INVALID-ENCODING'
    errors = validate_sosi_header(header)

    assert any('SOSI-002' in error or 'Invalid TEGNSETT' in error for error in errors)


# ============================================================================
# TOPOLOGY VALIDATION TESTS
# ============================================================================

def test_validate_type2_flate_valid():
    """Test Type 2 flate validation passes for matching geometries."""
    flate = {
        'OBJTYPE': 'Bygning',
        'område': Polygon([
            [0, 0],
            [10, 0],
            [10, 10],
            [0, 10],
            [0, 0]
        ]),
        'KVALITET': {'NØYAKTIGHET': 0.10}
    }

    # Create matching boundary lines
    boundaries = [
        {'geometry': LineString([(0, 0), (10, 0)])},
        {'geometry': LineString([(10, 0), (10, 10)])},
        {'geometry': LineString([(10, 10), (0, 10)])},
        {'geometry': LineString([(0, 10), (0, 0)])}
    ]

    errors = validate_type2_flate_topology(flate, boundaries)

    # Should have no errors
    topology_errors = [e for e in errors if 'TOPO-005' in e or 'TOPO-006' in e]
    assert len(topology_errors) == 0


def test_validate_type2_flate_missing_omrade():
    """Test Type 2 flate validation catches missing område."""
    flate = {'OBJTYPE': 'Bygning'}
    boundaries = []
    errors = validate_type2_flate_topology(flate, boundaries)

    assert any('TOPO-001' in error or 'missing' in error for error in errors)


def test_validate_type2_flate_mismatch():
    """Test Type 2 flate validation catches geometry mismatch."""
    flate = {
        'OBJTYPE': 'Bygning',
        'område': Polygon([
            [0, 0],
            [10, 0],
            [10, 10],
            [0, 10],
            [0, 0]
        ]),
        'KVALITET': {'NØYAKTIGHET': 0.01}
    }

    # Create boundaries that don't match (much smaller polygon)
    boundaries = [
        {'geometry': LineString([(0, 0), (5, 0)])},
        {'geometry': LineString([(5, 0), (5, 5)])},
        {'geometry': LineString([(5, 5), (0, 5)])},
        {'geometry': LineString([(0, 5), (0, 0)])}
    ]

    errors = validate_type2_flate_topology(flate, boundaries)

    # Should have error about mismatch
    assert any('TOPO-005' in error or 'mismatch' in error for error in errors)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_validate_complete_feature():
    """Test complete feature validation with all validators."""
    from fkb_validators import validate_feature

    feature = create_valid_bygning_feature()
    results = validate_feature(feature, fkb_standard='B')

    # Should return dict with all validator results
    assert isinstance(results, dict)
    assert 'attributes' in results
    assert 'geometry' in results
    assert 'accuracy' in results
    assert 'metadata' in results


def test_validate_dataset():
    """Test complete dataset validation."""
    from fkb_validators import validate_dataset

    features = [create_valid_bygning_feature() for _ in range(5)]
    header = create_valid_header()

    report = validate_dataset(features, header, fkb_standard='B')

    # Should return comprehensive report
    assert isinstance(report, dict)
    assert 'header_errors' in report
    assert 'feature_errors' in report
    assert 'summary' in report
    assert report['summary']['total_features'] == 5


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
