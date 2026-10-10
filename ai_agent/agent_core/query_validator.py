"""
Stellar AI - Query Quality & Input Validation Module
Detects empty, gibberish, keyboard mash, nonsensical, or invalid user queries.
Prevents model hallucination on invalid inputs.
"""

import re
from typing import Tuple

# Recognized Earth Observation, spatial, technical, space science, and general conversational vocabulary
COMMON_VALID_TOKENS = {
    # Question & Conversational Words
    "what", "where", "how", "which", "who", "why", "is", "are", "was", "were", "can", "could",
    "would", "should", "do", "does", "did", "find", "show", "detect", "locate", "identify",
    "describe", "classify", "analyze", "analyse", "check", "tell", "give", "many", "much",
    "there", "this", "that", "these", "those", "the", "a", "an", "in", "on", "at", "of", "to",
    "for", "with", "and", "or", "not", "from", "by", "between", "before", "after", "new", "old",
    "about", "any", "all", "some", "it", "its", "has", "have", "had", "been", "get", "got",
    "please", "help", "view", "see", "map", "area", "region", "zone", "location", "spot", "point",
    "predict", "estimate", "calculate", "compute", "measure", "monitor", "track", "trace",
    "compare", "contrast", "evaluate", "assess", "report", "generate", "create", "produce",
    "show", "display", "visualize", "render", "plot", "chart", "list", "summarize", "explain",
    "over", "under", "above", "below", "near", "far", "around", "within", "across", "through",

    # Satellite & Remote Sensing Domain Terms
    "satellite", "sat", "query", "imagery", "image", "images", "scene", "scenes", "photo", "picture",
    "raster", "band", "bands", "optical", "sar", "radar", "multispectral", "water", "river", "lake",
    "ocean", "sea", "pond", "reservoir", "flood", "flooding", "wetland", "forest", "tree", "trees",
    "greenery", "vegetation", "plant", "plants", "crop", "crops", "farm", "farmland", "field", "fields",
    "agriculture", "agricultural", "urban", "building", "buildings", "city", "house", "houses",
    "road", "roads", "structure", "structures", "construction", "bare", "soil", "desert", "sand",
    "rock", "cloud", "clouds", "haze", "snow", "ice", "glacier", "change", "changes", "difference",
    "differences", "built", "deforestation", "ndvi", "ndwi", "ndbi", "geotiff", "cog", "tiff",
    "sentinel", "sentinel1", "sentinel2", "landsat", "landsat8", "landsat9", "cartosat", "cartosat3",
    "resourcesat", "risat", "isro", "eo", "vqa", "bbox", "bounding", "box", "coordinates", "lat",
    "lon", "latitude", "longitude", "iss", "orbit", "norad", "tle", "polarization", "reflectance",
    "nir", "swir", "rgb", "pixel", "resolution", "spatial", "temporal", "modality", "fusion",
    "active", "tosat", "stellar", "analysis", "evidence", "terrain", "surface", "elevation",
    "dem", "lidar", "backscatter", "coherence", "interferometry", "insar", "displacement",
    "land", "cover", "type", "types", "segment", "segmentation", "classification",
    "fire", "burn", "drought", "erosion", "sedimentation", "coastal", "shoreline", "wetlands",

    # Space Science & Mission Terms
    "chandrayaan", "mangalyaan", "aditya", "pslv", "gslv", "gaganyaan", "astrosat",
    "trajectory", "decay", "orbital", "altitude", "inclination", "apogee", "perigee",
    "launch", "mission", "spacecraft", "probe", "lander", "rover", "capsule", "payload",
    "telemetry", "position", "velocity", "speed", "direction", "course",
    "moon", "lunar", "mars", "martian", "solar", "space", "cosmos", "galaxy", "planet",
    "asteroid", "comet", "debris", "constellation", "gps", "glonass", "galileo", "navic",
    "geosynchronous", "geostationary", "leo", "meo", "geo", "sun", "earth", "ground",
    "tracking", "pass", "coverage", "visibility", "eclipse", "transit", "conjunction",
    "maneuver", "burn", "thrust", "propulsion", "attitude", "control", "stabilization",
    "communication", "downlink", "uplink", "signal", "frequency", "power", "thermal",
    "pressure", "temperature", "radiation", "magnetosphere", "atmosphere", "ionosphere",

    # Technical & Analytical Terms
    "index", "value", "score", "percentage", "ratio", "density", "concentration",
    "rate", "speed", "magnitude", "intensity", "severity", "distribution",
    "pattern", "trend", "anomaly", "anomalies", "outlier", "hotspot",
    "boundary", "extent", "area", "perimeter", "volume", "depth", "width", "height",
    "accuracy", "precision", "confidence", "probability", "likelihood", "uncertainty",
    "threshold", "baseline", "reference", "benchmark", "calibration",
    "pre", "post", "event", "before", "after", "historical", "current", "future",
    "annual", "seasonal", "monthly", "weekly", "daily", "hourly",
    "global", "regional", "local", "national", "district", "state", "country",
    "india", "indian", "isro", "nasa", "esa", "jaxa", "cnsa", "roscosmos",
}

# Keyboard mash patterns
KEYBOARD_MASH_PATTERNS = [
    r"^[asdfghjkl]+$", r"^[qwertyuiop]+$", r"^[zxcvbnm]+$",
    r"^[dfghjkl]+$", r"^[fghjkl]+$", r"^[hjkl]+$", r"^[asdf]+$",
    r"^[ghjk]+$", r"^[dfgh]+$", r"^[zxcv]+$"
]

# Sub-string patterns that always indicate a valid satellite/space query
VALID_SUBSTRINGS = [
    "sat", "sentinel", "landsat", "cartosat", "ndvi", "isro", "nasa", "esa",
    "water", "change", "land", "orbit", "lunar", "mars", "space", "mission",
    "chandrayaan", "mangalyaan", "aditya", "pslv", "gslv", "track", "trajectory",
    "telemetry", "ground", "detection", "vegetation", "flood", "fire", "glacier",
    "urban", "coast", "deforest", "agri", "crop", "forest", "desert", "snow",
    "sar", "radar", "optical", "infrared", "spectrum", "band", "pixel", "raster",
    "geotiff", "geospatial", "coordinate", "bbox", "bounding", "segment",
]

def is_meaningful_query(query: str) -> Tuple[bool, str]:
    """
    Evaluates whether a user query is meaningful and valid for satellite analysis.
    Returns (is_valid: bool, suggestion_or_reason: str).
    """
    if not query or not str(query).strip():
        return False, "Query cannot be empty. Please provide a clear question or prompt."

    cleaned = str(query).strip()

    # Allow hashtags (e.g. #Sentinel-2) or satellite identifiers
    if cleaned.startswith("#") and len(cleaned) > 2:
        return True, "Valid query tag."

    # Remove non-alphanumeric characters for alpha checks
    alpha_chars = re.sub(r'[^a-zA-Z]', '', cleaned)
    
    # Check minimum length of alphabetic content unless float coordinates present
    if len(alpha_chars) < 2 and not re.search(r'\d+\.\d+', cleaned):
        return False, f"Query '{cleaned}' is too short or contains no valid words."

    lower_clean = cleaned.lower()
    
    # Check keyboard mash patterns
    for pat in KEYBOARD_MASH_PATTERNS:
        if re.match(pat, lower_clean) and len(lower_clean) > 3:
            return False, f"Query '{query}' appears to be random keyboard mash."

    # Check repeating single character e.g. "aaaaaa" or "11111"
    if len(set(lower_clean)) <= 2 and len(lower_clean) > 4:
        return False, f"Query '{query}' contains repetitive characters without clear meaning."

    # Quick pass: if query is long enough and contains mostly alphabetic words,
    # it's likely a valid natural-language question — be permissive.
    words = [w for w in re.split(r'\s+', lower_clean) if w]
    if len(words) >= 3 and len(alpha_chars) >= 10:
        # Multi-word query with substantial alphabetic content → likely valid
        return True, "Valid query (natural language)."

    # Extract words/tokens
    raw_tokens = [re.sub(r'^[#@!?,.]+|[#@!?,.]+$', '', t).lower() for t in re.split(r'\s+', cleaned) if t]
    tokens = [t for t in raw_tokens if len(t) > 0]

    if not tokens:
        return False, "Query does not contain valid text tokens."

    # Count recognized valid tokens or coordinates
    valid_count = 0
    for token in tokens:
        # Check float coordinates e.g. 12.34
        if re.match(r'^\d+\.\d+$', token):
            valid_count += 1
            continue
        
        # Split hyphenated words e.g. sentinel-2 -> sentinel, 2
        parts = token.split('-')
        if any(part in COMMON_VALID_TOKENS for part in parts if not part.isdigit()):
            valid_count += 1
            continue
        
        if token in COMMON_VALID_TOKENS:
            valid_count += 1
            continue

        # Check sub-words for compound query terms
        if any(term in token for term in VALID_SUBSTRINGS):
            valid_count += 1
            continue

    if valid_count == 0:
        return False, (
            f"Unrecognized or ambiguous query: '{query}'. "
            "Please ask a valid satellite intelligence question, such as: "
            "'Detect land cover types', 'Locate water bodies in the image', "
            "'Analyze vegetation index (NDVI)', or 'What changed between these images?'"
        )

    return True, "Valid query."
