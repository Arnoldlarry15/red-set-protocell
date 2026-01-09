"""
Tests for telemetry export module.
"""

import pytest
from pathlib import Path

from app.telemetry.exporter import (
    TelemetryExporter,
    ExportFormat,
    MetricsSnapshot,
    create_metrics_snapshot,
)


def test_create_metrics_snapshot():
    """Test creating a metrics snapshot."""
    snapshot = create_metrics_snapshot(
        session_id="test_session",
        metrics={'score': 0.34, 'rounds': 50},
        metadata={'model': 'gpt-3.5-turbo'},
    )
    
    assert snapshot.session_id == "test_session"
    assert snapshot.metrics['score'] == 0.34
    assert snapshot.metadata['model'] == 'gpt-3.5-turbo'
    assert snapshot.timestamp is not None


def test_export_to_csv(tmp_path):
    """Test exporting data to CSV."""
    exporter = TelemetryExporter(output_dir=str(tmp_path))
    
    data = [
        {'round': 1, 'score': 0.23, 'blocked': False},
        {'round': 2, 'score': 0.45, 'blocked': False},
        {'round': 3, 'score': 0.89, 'blocked': True},
    ]
    
    filepath = exporter.export_to_csv(data, "test.csv")
    
    assert filepath.exists()
    
    # Read and verify
    with open(filepath, 'r') as f:
        content = f.read()
        assert 'round' in content
        assert 'score' in content
        assert '0.23' in content


def test_export_to_json(tmp_path):
    """Test exporting data to JSON."""
    exporter = TelemetryExporter(output_dir=str(tmp_path))
    
    data = {'session_id': 'test', 'score': 0.34}
    
    filepath = exporter.export_to_json(data, "test.json")
    
    assert filepath.exists()
    
    # Read and verify
    import json
    with open(filepath, 'r') as f:
        loaded = json.load(f)
        assert loaded['session_id'] == 'test'
        assert loaded['score'] == 0.34


def test_export_to_jsonlines(tmp_path):
    """Test exporting data to JSON Lines."""
    exporter = TelemetryExporter(output_dir=str(tmp_path))
    
    data = [
        {'round': 1, 'score': 0.23},
        {'round': 2, 'score': 0.45},
    ]
    
    filepath = exporter.export_to_jsonlines(data, "test.jsonl")
    
    assert filepath.exists()
    
    # Read and verify
    with open(filepath, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 2


def test_export_with_format(tmp_path):
    """Test export with format parameter."""
    exporter = TelemetryExporter(output_dir=str(tmp_path))
    
    data = [{'test': 'value'}]
    
    # Test CSV
    csv_path = exporter.export(data, ExportFormat.CSV)
    assert csv_path.exists()
    assert csv_path.suffix == '.csv'
    
    # Test JSON
    json_path = exporter.export(data, ExportFormat.JSON)
    assert json_path.exists()
    assert json_path.suffix == '.json'


def test_export_to_string():
    """Test exporting to string."""
    exporter = TelemetryExporter()
    
    data = [{'round': 1, 'score': 0.23}]
    
    # CSV string
    csv_str = exporter.export_to_string(data, ExportFormat.CSV)
    assert 'round' in csv_str
    assert '0.23' in csv_str
    
    # JSON string
    json_str = exporter.export_to_string(data, ExportFormat.JSON)
    assert '"round"' in json_str
    assert '0.23' in json_str


def test_flatten_dict():
    """Test dictionary flattening."""
    exporter = TelemetryExporter()
    
    nested = {
        'level1': 'value1',
        'nested': {
            'level2': 'value2',
            'deep': {
                'level3': 'value3',
            }
        }
    }
    
    flattened = exporter._flatten_dict(nested)
    
    assert flattened['level1'] == 'value1'
    assert flattened['nested.level2'] == 'value2'
    assert flattened['nested.deep.level3'] == 'value3'
