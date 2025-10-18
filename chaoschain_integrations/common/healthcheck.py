"""Health check utilities for sidecar services."""

import time
from typing import Dict, Optional

import httpx

from chaoschain_integrations.common.errors import ConnectionError, TimeoutError
from chaoschain_integrations.common.logging import get_logger

logger = get_logger(__name__)


async def check_http_health(
    url: str,
    timeout_seconds: int = 5,
    expected_status: int = 200,
) -> Dict[str, any]:
    """
    Check health of an HTTP service.

    Args:
        url: Health check endpoint URL
        timeout_seconds: Request timeout
        expected_status: Expected HTTP status code

    Returns:
        Dictionary with health status information

    Raises:
        ConnectionError: If connection fails
        TimeoutError: If request times out
    """
    start_time = time.time()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout_seconds)
            elapsed = time.time() - start_time

            is_healthy = response.status_code == expected_status

            result = {
                "healthy": is_healthy,
                "status_code": response.status_code,
                "response_time_ms": round(elapsed * 1000, 2),
                "url": url,
            }

            if is_healthy:
                logger.info("health_check_success", **result)
            else:
                logger.warning("health_check_failed", **result)

            return result

    except httpx.TimeoutException as e:
        elapsed = time.time() - start_time
        logger.error("health_check_timeout", url=url, elapsed_ms=round(elapsed * 1000, 2))
        raise TimeoutError(
            f"Health check timed out after {timeout_seconds}s",
            adapter_name="healthcheck",
            details={"url": url, "timeout": timeout_seconds},
        ) from e

    except httpx.RequestError as e:
        elapsed = time.time() - start_time
        logger.error(
            "health_check_error",
            url=url,
            error=str(e),
            elapsed_ms=round(elapsed * 1000, 2),
        )
        raise ConnectionError(
            f"Failed to connect to {url}: {e}",
            adapter_name="healthcheck",
            details={"url": url, "error": str(e)},
        ) from e


def check_grpc_health(
    host: str,
    port: int,
    timeout_seconds: int = 5,
    service_name: Optional[str] = None,
) -> Dict[str, any]:
    """
    Check health of a gRPC service.

    Args:
        host: gRPC service host
        port: gRPC service port
        timeout_seconds: Request timeout
        service_name: Optional service name to check

    Returns:
        Dictionary with health status information

    Raises:
        ConnectionError: If connection fails
        TimeoutError: If request times out
    """
    # TODO: Implement gRPC health check using grpc.health.v1.Health
    # This requires grpcio-health-checking package
    logger.warning(
        "grpc_health_check_not_implemented",
        host=host,
        port=port,
        message="gRPC health checks not yet implemented",
    )

    return {
        "healthy": False,
        "message": "gRPC health check not implemented",
        "host": host,
        "port": port,
    }

