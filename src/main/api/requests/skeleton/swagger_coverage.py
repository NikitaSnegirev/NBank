from urllib.parse import urlparse

from swagger_coverage_tool import SwaggerCoverageTracker

from src.main.api.configs.config import Config
from src.main.api.requests.skeleton.endpoint import Endpoint

_tracker: SwaggerCoverageTracker | None = None


def get_tracker() -> SwaggerCoverageTracker:
    global _tracker
    if _tracker is None:
        _tracker = SwaggerCoverageTracker(service="nbank")
        if _tracker.settings.history_file:
            _tracker.settings.history_file.parent.mkdir(parents=True, exist_ok=True)
    return _tracker


def coverage_path_for(endpoint: Endpoint, id_in_path: bool = False) -> str:
    base_url = f"{Config.get('server')}{Config.get('api_version')}"
    api_prefix = urlparse(base_url).path.rstrip("/")
    endpoint_path = endpoint.value.swagger_path or endpoint.value.url
    if id_in_path and endpoint.value.swagger_path is None:
        endpoint_path = f"{endpoint_path}/{{id}}"

    return f"{api_prefix}/{endpoint_path.lstrip('/')}"
