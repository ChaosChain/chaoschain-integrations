"""Configuration management using pydantic-settings."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdapterConfig(BaseSettings):
    """Base configuration for all adapters."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or console")
    adapter_health_check_interval: int = Field(
        default=30, description="Health check interval in seconds"
    )


class ZeroGConfig(BaseSettings):
    """Configuration for ZeroG adapters."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ZEROG_",
        case_sensitive=False,
        extra="ignore",
    )

    grpc_url: str = Field(default="localhost:50051", description="gRPC endpoint URL")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    timeout_seconds: int = Field(default=60, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class EigenConfig(BaseSettings):
    """Configuration for Eigen compute adapter."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EIGEN_",
        case_sensitive=False,
        extra="ignore",
    )

    api_url: str = Field(
        default="http://localhost:8082", description="API endpoint URL (HTTP or gRPC)"
    )
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    use_grpc: bool = Field(default=True, description="Use gRPC instead of HTTP")
    timeout_seconds: int = Field(default=600, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class PinataConfig(BaseSettings):
    """Configuration for Pinata (IPFS) storage adapter."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PINATA_",
        case_sensitive=False,
        extra="ignore",
    )

    api_url: str = Field(default="https://api.pinata.cloud", description="Pinata API URL")
    api_key: Optional[str] = Field(default=None, description="Pinata API key")
    api_secret: Optional[str] = Field(default=None, description="Pinata API secret")
    jwt: Optional[str] = Field(default=None, description="Pinata JWT token")
    timeout_seconds: int = Field(default=60, description="Request timeout in seconds")


class ChainlinkCREConfig(BaseSettings):
    """Configuration for Chainlink CRE adapter."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CRE_",
        case_sensitive=False,
        extra="ignore",
    )

    api_url: str = Field(
        default="https://cre-api.chainlink.com", description="Chainlink CRE API URL"
    )
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

