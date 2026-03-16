"""
Additional tests for telemetry exporter module - covering missing branches.
"""

import json

import pytest

from app.telemetry.exporter import (
    ExportFormat,
    MetricsSnapshot,
    TelemetryExporter,
    create_metrics_snapshot,
)


class TestMetricsSnapshotToDict:
    def test_to_dict(self):
        snapshot = MetricsSnapshot(
            timestamp="2024-01-01T00:00:00",
            session_id="sess_1",
            metrics={"score": 0.5},
            metadata={"model": "gpt-4"},
        )
        d = snapshot.to_dict()
        assert d["session_id"] == "sess_1"
        assert d["metrics"]["score"] == 0.5
        assert d["metadata"]["model"] == "gpt-4"
        assert d["timestamp"] == "2024-01-01T00:00:00"


class TestExporterMissingBranches:
    def test_export_to_csv_empty_data(self, tmp_path):
        """export_to_csv with empty list returns None and logs warning."""
        exporter = TelemetryExporter(output_dir=str(tmp_path))
        result = exporter.export_to_csv([], "test.csv")
        assert result is None

    def test_export_to_csv_no_flatten(self, tmp_path):
        """export_to_csv with flatten=False skips flattening."""
        exporter = TelemetryExporter(output_dir=str(tmp_path))
        data = [{"round": 1, "score": 0.5}]
        filepath = exporter.export_to_csv(data, "test_no_flatten.csv", flatten=False)
        assert filepath.exists()
        content = filepath.read_text()
        assert "round" in content
        assert "score" in content

    def test_export_to_json_not_pretty(self, tmp_path):
        """export_to_json with pretty=False writes compact JSON."""
        exporter = TelemetryExporter(output_dir=str(tmp_path))
        data = {"session_id": "test", "score": 0.5}
        filepath = exporter.export_to_json(data, "compact.json", pretty=False)
        assert filepath.exists()
        content = filepath.read_text()
        loaded = json.loads(content)
        assert loaded["session_id"] == "test"

    def test_export_auto_filename(self, tmp_path):
        """export() with no filename auto-generates one."""
        exporter = TelemetryExporter(output_dir=str(tmp_path))
        data = [{"round": 1, "score": 0.5}]
        filepath = exporter.export(data, ExportFormat.CSV)
        assert filepath is not None
        assert filepath.suffix == ".csv"

    def test_export_csv_dict_input(self, tmp_path):
        """export() with dict input for CSV wraps it in a list."""
        exporter = TelemetryExporter(output_dir=str(tmp_path))
        data = {"round": 1, "score": 0.5}
        filepath = exporter.export(data, ExportFormat.CSV, filename="single.csv")
        assert filepath.exists()

    def test_export_json_lines_format(self, tmp_path):
        """export() with JSON_LINES format."""
        exporter = TelemetryExporter(output_dir=str(tmp_path))
        data = [{"round": 1}, {"round": 2}]
        filepath = exporter.export(data, ExportFormat.JSON_LINES, filename="test.jsonl")
        assert filepath.exists()
        lines = filepath.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_export_json_lines_dict_input(self, tmp_path):
        """export() with dict input for JSON_LINES wraps it in a list."""
        exporter = TelemetryExporter(output_dir=str(tmp_path))
        data = {"round": 1}
        filepath = exporter.export(data, ExportFormat.JSON_LINES, filename="single.jsonl")
        assert filepath.exists()

    def test_export_auto_filename_adds_extension(self, tmp_path):
        """export() with filename missing extension adds it."""
        exporter = TelemetryExporter(output_dir=str(tmp_path))
        data = [{"round": 1}]
        filepath = exporter.export(data, ExportFormat.CSV, filename="myexport")
        assert filepath.suffix == ".csv"

    def test_export_to_string_json_lines(self):
        """export_to_string with JSON_LINES format."""
        exporter = TelemetryExporter()
        data = [{"round": 1}, {"round": 2}]
        result = exporter.export_to_string(data, ExportFormat.JSON_LINES)
        lines = result.split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["round"] == 1

    def test_export_to_string_json_lines_dict(self):
        """export_to_string with JSON_LINES dict input wraps to list."""
        exporter = TelemetryExporter()
        data = {"round": 1}
        result = exporter.export_to_string(data, ExportFormat.JSON_LINES)
        assert '"round"' in result

    def test_export_to_string_json_not_pretty(self):
        """export_to_string with JSON format and pretty=False."""
        exporter = TelemetryExporter()
        data = [{"round": 1}]
        result = exporter.export_to_string(data, ExportFormat.JSON, pretty=False)
        loaded = json.loads(result)
        assert loaded[0]["round"] == 1

    def test_export_to_string_csv_dict_input(self):
        """export_to_string with CSV format and dict input."""
        exporter = TelemetryExporter()
        data = {"round": 1, "score": 0.5}
        result = exporter.export_to_string(data, ExportFormat.CSV)
        assert "round" in result
        assert "score" in result

    def test_flatten_dict_with_list_value(self):
        """_flatten_dict converts list values to strings."""
        exporter = TelemetryExporter()
        d = {"tags": ["a", "b", "c"], "name": "test"}
        result = exporter._flatten_dict(d)
        assert result["name"] == "test"
        assert isinstance(result["tags"], str)
        assert "a" in result["tags"]

    def test_export_invalid_format_raises(self, tmp_path):
        """export() with unknown format raises ValueError."""
        exporter = TelemetryExporter(output_dir=str(tmp_path))
        # Create a fake format value that doesn't match any case
        import enum

        FakeFormat = enum.Enum("FakeFormat", {"UNKNOWN": "unknown"})
        with pytest.raises((ValueError, AttributeError)):
            exporter.export([{"x": 1}], FakeFormat.UNKNOWN, filename="test.unknown")

    def test_export_to_string_invalid_format_raises(self):
        """export_to_string() with unknown format raises ValueError."""
        exporter = TelemetryExporter()
        import enum

        FakeFormat = enum.Enum("FakeFormat", {"UNKNOWN": "unknown"})
        with pytest.raises((ValueError, AttributeError)):
            exporter.export_to_string([{"x": 1}], FakeFormat.UNKNOWN)

    def test_export_to_string_csv_no_flatten(self):
        """export_to_string with CSV format and flatten=False skips flattening."""
        exporter = TelemetryExporter()
        data = [{"round": 1, "score": 0.5}]
        result = exporter.export_to_string(data, ExportFormat.CSV, flatten=False)
        assert "round" in result
        assert "score" in result
