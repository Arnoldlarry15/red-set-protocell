"""
Red Set ProtoCell - Telemetry Exporter

Export telemetry data in multiple formats (CSV, JSON, etc.).
"""

import csv
import io
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""

    CSV = "csv"
    JSON = "json"
    JSON_LINES = "jsonl"


@dataclass
class MetricsSnapshot:
    """
    Snapshot of metrics at a point in time.

    Provides a standardized structure for metric data.
    """

    timestamp: str
    session_id: str
    metrics: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class TelemetryExporter:
    """
    Export telemetry data in various formats.

    Supports:
    - CSV export for spreadsheet analysis
    - JSON export for programmatic processing
    - JSON Lines for streaming data
    """

    def __init__(self, output_dir: str = "telemetry_exports"):
        """
        Initialize telemetry exporter.

        Args:
            output_dir: Directory for storing exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Telemetry exporter initialized with output dir: {self.output_dir}")

    def export_to_csv(
        self,
        data: List[Dict[str, Any]],
        filename: str,
        flatten: bool = True,
    ) -> Path:
        """
        Export data to CSV format.

        Args:
            data: List of dictionaries to export
            filename: Output filename
            flatten: Whether to flatten nested dictionaries

        Returns:
            Path to exported file
        """
        if not data:
            logger.warning("No data to export")
            return None

        filepath = self.output_dir / filename

        # Flatten nested dictionaries if requested
        if flatten:
            data = [self._flatten_dict(item) for item in data]

        # Get all unique keys across all items
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(fieldnames)

        # Write CSV
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        logger.info(f"Exported {len(data)} records to CSV: {filepath}")
        return filepath

    def export_to_json(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        filename: str,
        pretty: bool = True,
    ) -> Path:
        """
        Export data to JSON format.

        Args:
            data: Dictionary or list of dictionaries to export
            filename: Output filename
            pretty: Whether to pretty-print JSON

        Returns:
            Path to exported file
        """
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)

        logger.info(f"Exported data to JSON: {filepath}")
        return filepath

    def export_to_jsonlines(
        self,
        data: List[Dict[str, Any]],
        filename: str,
    ) -> Path:
        """
        Export data to JSON Lines format (one JSON object per line).

        Args:
            data: List of dictionaries to export
            filename: Output filename

        Returns:
            Path to exported file
        """
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")

        logger.info(f"Exported {len(data)} records to JSON Lines: {filepath}")
        return filepath

    def export(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        format: ExportFormat,
        filename: Optional[str] = None,
        **kwargs,
    ) -> Path:
        """
        Export data in the specified format.

        Args:
            data: Data to export
            format: Export format
            filename: Optional filename (auto-generated if not provided)
            **kwargs: Additional format-specific arguments

        Returns:
            Path to exported file
        """
        # Auto-generate filename if not provided
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"telemetry_{timestamp}.{format.value}"

        # Ensure filename has correct extension
        if not filename.endswith(f".{format.value}"):
            filename = f"{filename}.{format.value}"

        # Export based on format
        if format == ExportFormat.CSV:
            if isinstance(data, dict):
                data = [data]
            return self.export_to_csv(data, filename, **kwargs)
        elif format == ExportFormat.JSON:
            return self.export_to_json(data, filename, **kwargs)
        elif format == ExportFormat.JSON_LINES:
            if isinstance(data, dict):
                data = [data]
            return self.export_to_jsonlines(data, filename)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def export_to_string(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        format: ExportFormat,
        **kwargs,
    ) -> str:
        """
        Export data to string (in-memory).

        Args:
            data: Data to export
            format: Export format
            **kwargs: Additional format-specific arguments

        Returns:
            Exported data as string
        """
        if format == ExportFormat.CSV:
            if isinstance(data, dict):
                data = [data]

            # Flatten if requested
            if kwargs.get("flatten", True):
                data = [self._flatten_dict(item) for item in data]

            # Get fieldnames
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(fieldnames)

            # Write to string buffer
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()

        elif format == ExportFormat.JSON:
            pretty = kwargs.get("pretty", True)
            if pretty:
                return json.dumps(data, indent=2)
            else:
                return json.dumps(data)

        elif format == ExportFormat.JSON_LINES:
            if isinstance(data, dict):
                data = [data]
            return "\n".join(json.dumps(item) for item in data)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _flatten_dict(
        self,
        d: Dict[str, Any],
        parent_key: str = "",
        sep: str = ".",
    ) -> Dict[str, Any]:
        """
        Flatten a nested dictionary.

        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert list to string representation
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)


def create_metrics_snapshot(
    session_id: str,
    metrics: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> MetricsSnapshot:
    """
    Create a metrics snapshot.

    Args:
        session_id: Session identifier
        metrics: Dictionary of metrics
        metadata: Optional metadata

    Returns:
        Metrics snapshot
    """
    return MetricsSnapshot(
        timestamp=datetime.now(timezone.utc).isoformat(),
        session_id=session_id,
        metrics=metrics,
        metadata=metadata,
    )
