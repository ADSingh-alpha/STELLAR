"""
Geospatial ingestion, validation, metadata extraction and raster preprocessing
utilities for Stellar AI.

Supported formats:
- GeoTIFF / TIFF
- PNG
- JPEG / JPG
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

try:
    import rasterio
    from rasterio.warp import transform_bounds

    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


SUPPORTED_RASTER_EXTENSIONS = {
    ".tif",
    ".tiff",
    ".png",
    ".jpg",
    ".jpeg",
}


def validate_file_format(file_path: str) -> Dict[str, Any]:
    """
    Validate whether a file exists and has a supported raster extension.
    """
    path = Path(file_path)

    if not path.exists():
        return {
            "valid": False,
            "error": f"File not found: {file_path}",
        }

    if not path.is_file():
        return {
            "valid": False,
            "error": f"Path is not a file: {file_path}",
        }

    extension = path.suffix.lower()

    if extension not in SUPPORTED_RASTER_EXTENSIONS:
        return {
            "valid": False,
            "error": (
                f"Unsupported raster format: {extension}. "
                f"Supported formats: {sorted(SUPPORTED_RASTER_EXTENSIONS)}"
            ),
        }

    return {
        "valid": True,
        "file_name": path.name,
        "extension": extension,
        "size_bytes": path.stat().st_size,
    }


def _serialize_transform(transform: Any) -> Optional[list]:
    """Convert a Rasterio affine transform into JSON-safe values."""
    if transform is None:
        return None

    try:
        return [
            float(transform.a),
            float(transform.b),
            float(transform.c),
            float(transform.d),
            float(transform.e),
            float(transform.f),
        ]
    except Exception:
        return None


def _extract_wgs84_bounds(src: Any) -> Optional[list]:
    """Convert native raster bounds into EPSG:4326."""
    if not src.crs:
        return None

    try:
        bounds = src.bounds

        if src.crs.to_epsg() == 4326:
            return [
                float(bounds.left),
                float(bounds.bottom),
                float(bounds.right),
                float(bounds.top),
            ]

        converted = transform_bounds(
            src.crs,
            "EPSG:4326",
            bounds.left,
            bounds.bottom,
            bounds.right,
            bounds.top,
        )

        return [float(value) for value in converted]

    except Exception:
        return None


def _infer_modality_from_bands(
    band_count: int,
    descriptions: Sequence[Optional[str]],
) -> Tuple[str, float, list]:
    """
    Infer optical/SAR modality.

    This is intentionally conservative. Band count alone cannot reliably
    determine whether a raster is SAR, so polarization/band descriptions
    are preferred when available.
    """
    normalized_descriptions = [
        str(description).strip().lower()
        for description in descriptions
        if description
    ]

    joined = " ".join(normalized_descriptions)

    if "vv" in joined or "vh" in joined or "hh" in joined or "hv" in joined:
        polarizations = [
            polarization
            for polarization in ("VV", "VH", "HH", "HV")
            if polarization.lower() in joined
        ]

        return "sar", 0.95, polarizations

    if band_count == 1:
        return "unknown", 0.40, []

    if band_count == 2:
        return "unknown", 0.40, []

    if band_count == 3:
        return "optical", 0.80, ["RGB"]

    if band_count == 4:
        return "optical", 0.90, ["RGB", "NIR"]

    if 10 <= band_count <= 13:
        return "optical", 0.75, ["multispectral"]

    if band_count > 13:
        return "unknown", 0.30, []

    return "unknown", 0.20, []


def identify_sensor_modality(band_count: int) -> str:
    """
    Identify sensor modality (optical vs sar) from band count.
    Used for rapid validation checks across models and test suites.
    """
    if band_count in (1, 2):
        return "sar"
    elif band_count >= 3:
        return "optical"
    return "unknown"


def extract_geotiff_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract detailed metadata from a GeoTIFF/TIFF raster.

    Includes:
    - dimensions
    - band count
    - data types
    - CRS
    - native bounds
    - WGS84 bounds
    - spatial resolution
    - affine transform
    - nodata
    - band descriptions
    - inferred modality
    """
    validation = validate_file_format(file_path)

    if not validation["valid"]:
        return validation

    if not RASTERIO_AVAILABLE:
        return {
            "valid": False,
            "error": "rasterio is not installed.",
        }

    extension = Path(file_path).suffix.lower()

    if extension not in {".tif", ".tiff"}:
        return {
            "valid": False,
            "error": "extract_geotiff_metadata requires a TIFF/GeoTIFF file.",
        }

    try:
        with rasterio.open(file_path) as src:
            bounds = src.bounds

            descriptions = list(src.descriptions)

            modality, modality_confidence, polarizations = (
                _infer_modality_from_bands(
                    src.count,
                    descriptions,
                )
            )

            metadata = {
                "valid": True,
                "file_name": Path(file_path).name,
                "file_format": "geotiff",
                "width": int(src.width),
                "height": int(src.height),
                "band_count": int(src.count),
                "crs": src.crs.to_string() if src.crs else None,
                "bounds_native": [
                    float(bounds.left),
                    float(bounds.bottom),
                    float(bounds.right),
                    float(bounds.top),
                ],
                "bounds_wgs84": _extract_wgs84_bounds(src),
                "resolution": [
                    float(src.res[0]),
                    float(src.res[1]),
                ],
                "transform": _serialize_transform(src.transform),
                "dtypes": [str(dtype) for dtype in src.dtypes],
                "nodata": (
                    float(src.nodata)
                    if src.nodata is not None
                    else None
                ),
                "band_descriptions": descriptions,
                "modality": modality,
                "modality_confidence": modality_confidence,
                "polarizations": polarizations,
                "driver": src.driver,
            }

            # Preserve useful dataset tags, but don't expose everything
            # because some satellite products contain very large metadata.
            tags = src.tags()

            useful_tags = {}
            for key in (
                "DATE_ACQUIRED",
                "ACQUISITION_DATE",
                "DATETIME",
                "TIFFTAG_DATETIME",
                "SENSOR",
                "SATELLITE",
                "PLATFORM",
            ):
                if key in tags:
                    useful_tags[key.lower()] = tags[key]

            metadata["tags"] = useful_tags

            return metadata

    except Exception as exc:
        return {
            "valid": False,
            "error": f"Failed to read GeoTIFF: {exc}",
        }


def extract_standard_image_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from PNG/JPEG images.

    PNG/JPEG normally do not contain reliable geospatial CRS/bounds,
    so those fields are returned as None.
    """
    validation = validate_file_format(file_path)

    if not validation["valid"]:
        return validation

    if not PIL_AVAILABLE:
        return {
            "valid": False,
            "error": "Pillow is not installed.",
        }

    extension = Path(file_path).suffix.lower()

    if extension not in {".png", ".jpg", ".jpeg"}:
        return {
            "valid": False,
            "error": "This function supports PNG/JPEG files only.",
        }

    try:
        with Image.open(file_path) as image:
            width, height = image.size

            if image.mode in ("RGB", "RGBA"):
                modality = "optical"
                confidence = 0.80
            elif image.mode == "L":
                modality = "unknown"
                confidence = 0.40
            else:
                modality = "unknown"
                confidence = 0.20

            return {
                "valid": True,
                "file_name": Path(file_path).name,
                "file_format": extension.lstrip("."),
                "width": int(width),
                "height": int(height),
                "band_count": len(image.getbands()),
                "bands": list(image.getbands()),
                "mode": image.mode,
                "crs": None,
                "bounds_native": None,
                "bounds_wgs84": None,
                "resolution": None,
                "transform": None,
                "modality": modality,
                "modality_confidence": confidence,
                "georeferenced": False,
            }

    except Exception as exc:
        return {
            "valid": False,
            "error": f"Failed to read image: {exc}",
        }


def inspect_raster(file_path: str) -> Dict[str, Any]:
    """
    Unified raster inspection entry point.

    Automatically chooses GeoTIFF or PNG/JPEG metadata extraction.
    """
    validation = validate_file_format(file_path)

    if not validation["valid"]:
        return validation

    extension = Path(file_path).suffix.lower()

    if extension in {".tif", ".tiff"}:
        return extract_geotiff_metadata(file_path)

    return extract_standard_image_metadata(file_path)


def verify_band_configuration(
    file_path: str,
    expected_modality: Optional[str] = None,
    expected_polarizations: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """
    Verify the band configuration of a raster.

    expected_modality:
        optical, sar, unknown

    expected_polarizations:
        Example: ["VV", "VH"]
    """
    metadata = inspect_raster(file_path)

    if not metadata.get("valid"):
        return {
            "valid": False,
            "verified": False,
            "error": metadata.get("error"),
        }

    detected_modality = metadata.get("modality", "unknown")

    result = {
        "valid": True,
        "verified": True,
        "detected_modality": detected_modality,
        "modality_confidence": metadata.get("modality_confidence"),
        "band_count": metadata.get("band_count"),
        "band_descriptions": metadata.get("band_descriptions", []),
        "polarizations": metadata.get("polarizations", []),
    }

    if expected_modality:
        result["modality_match"] = (
            detected_modality == expected_modality.lower()
        )

    if expected_polarizations:
        detected = {
            polarization.upper()
            for polarization in metadata.get("polarizations", [])
        }

        expected = {
            polarization.upper()
            for polarization in expected_polarizations
        }

        result["polarization_match"] = expected.issubset(detected)

    return result


def validate_image_pair_alignment(
    first_path: str,
    second_path: str,
    tolerance: float = 1e-6,
) -> Dict[str, Any]:
    """
    Validate spatial alignment between two raster images.

    Checks:
    - dimensions
    - CRS
    - spatial resolution
    - bounding extents
    - affine transform

    This is suitable for bi-temporal and cross-modal pair validation.
    """
    first = inspect_raster(first_path)
    second = inspect_raster(second_path)

    if not first.get("valid"):
        return {
            "valid": False,
            "aligned": False,
            "error": f"First image: {first.get('error')}",
        }

    if not second.get("valid"):
        return {
            "valid": False,
            "aligned": False,
            "error": f"Second image: {second.get('error')}",
        }

    comparison = {
        "dimensions_match": (
            first.get("width") == second.get("width")
            and first.get("height") == second.get("height")
        ),
        "crs_match": first.get("crs") == second.get("crs"),
        "resolution_match": _values_close(
            first.get("resolution"),
            second.get("resolution"),
            tolerance,
        ),
        "bounds_match": _values_close(
            first.get("bounds_native"),
            second.get("bounds_native"),
            tolerance,
        ),
        "transform_match": _values_close(
            first.get("transform"),
            second.get("transform"),
            tolerance,
        ),
    }

    aligned = all(comparison.values())

    return {
        "valid": True,
        "aligned": aligned,
        "checks": comparison,
        "first_image": {
            "width": first.get("width"),
            "height": first.get("height"),
            "crs": first.get("crs"),
            "resolution": first.get("resolution"),
            "bounds": first.get("bounds_native"),
        },
        "second_image": {
            "width": second.get("width"),
            "height": second.get("height"),
            "crs": second.get("crs"),
            "resolution": second.get("resolution"),
            "bounds": second.get("bounds_native"),
        },
    }


def _values_close(
    first: Any,
    second: Any,
    tolerance: float,
) -> bool:
    """Compare scalars/lists with numerical tolerance."""
    if first is None or second is None:
        return first == second

    try:
        first_array = np.asarray(first, dtype=float)
        second_array = np.asarray(second, dtype=float)

        if first_array.shape != second_array.shape:
            return False

        return bool(
            np.allclose(
                first_array,
                second_array,
                rtol=tolerance,
                atol=tolerance,
            )
        )

    except (TypeError, ValueError):
        return first == second


def geotiff_to_png_tile(
    input_path: str,
    output_path: str,
    bands: Tuple[int, int, int] = (1, 2, 3),
) -> bool:
    """
    Normalize a multi-band raster into an 8-bit RGB PNG.

    Uses the 2nd-98th percentile for contrast stretching.
    Handles:
    - 8-bit imagery
    - 16-bit imagery
    - single-band imagery
    - two-band imagery
    """
    if not RASTERIO_AVAILABLE or not PIL_AVAILABLE:
        print("Error: rasterio and Pillow are required.")
        return False

    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return False

    try:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with rasterio.open(input_path) as src:
            read_bands = []

            for band in bands:
                if 1 <= band <= src.count:
                    read_bands.append(band)
                else:
                    read_bands.append(1)

            image_data = src.read(read_bands).astype(np.float32)

            normalized_channels = []

            for channel in image_data:
                valid_pixels = channel[np.isfinite(channel)]

                if src.nodata is not None:
                    valid_pixels = valid_pixels[
                        valid_pixels != src.nodata
                    ]

                if valid_pixels.size == 0:
                    normalized_channels.append(
                        np.zeros(channel.shape, dtype=np.uint8)
                    )
                    continue

                p2, p98 = np.percentile(
                    valid_pixels,
                    (2, 98),
                )

                if np.isclose(p98, p2):
                    normalized = np.zeros_like(channel)
                else:
                    normalized = np.clip(
                        (channel - p2) / (p98 - p2),
                        0,
                        1,
                    )

                normalized_channels.append(
                    (normalized * 255).astype(np.uint8)
                )

            rgb_array = np.dstack(normalized_channels)

            if rgb_array.shape[2] == 1:
                rgb_array = np.repeat(
                    rgb_array,
                    3,
                    axis=2,
                )
            elif rgb_array.shape[2] == 2:
                zeros = np.zeros(
                    (
                        rgb_array.shape[0],
                        rgb_array.shape[1],
                        1,
                    ),
                    dtype=np.uint8,
                )

                rgb_array = np.concatenate(
                    [rgb_array, zeros],
                    axis=2,
                )

            image = Image.fromarray(rgb_array, mode="RGB")
            image.save(output, "PNG")

            return True

    except Exception as exc:
        print(f"Failed to convert GeoTIFF to PNG: {exc}")
        return False