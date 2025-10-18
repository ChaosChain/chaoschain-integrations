"""Pydantic schemas for ZeroG storage API."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ZeroGPutRequest(BaseModel):
    """Request to store data in ZeroG."""

    content: bytes = Field(..., description="Content to store")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")
    compression: bool = Field(default=False, description="Enable compression")


class ZeroGPutResponse(BaseModel):
    """Response from ZeroG put operation."""

    file_id: str = Field(..., description="ZeroG file identifier")
    root_hash: str = Field(..., description="Merkle root hash")
    merkle_proof: Optional[Dict[str, Any]] = Field(default=None, description="Merkle proof")
    size_bytes: int = Field(..., description="Stored content size")
    timestamp: int = Field(..., description="Storage timestamp (Unix)")


class ZeroGGetRequest(BaseModel):
    """Request to retrieve data from ZeroG."""

    file_id: str = Field(..., description="ZeroG file identifier")


class ZeroGGetResponse(BaseModel):
    """Response from ZeroG get operation."""

    content: bytes = Field(..., description="Retrieved content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Associated metadata")
    size_bytes: int = Field(..., description="Content size")


class ZeroGExistsRequest(BaseModel):
    """Request to check if file exists in ZeroG."""

    file_id: str = Field(..., description="ZeroG file identifier")


class ZeroGExistsResponse(BaseModel):
    """Response from ZeroG exists check."""

    exists: bool = Field(..., description="Whether file exists")
    size_bytes: Optional[int] = Field(default=None, description="File size if exists")


class ZeroGProofRequest(BaseModel):
    """Request to get proof for stored file."""

    file_id: str = Field(..., description="ZeroG file identifier")


class ZeroGProofResponse(BaseModel):
    """Response with storage proof."""

    file_id: str = Field(..., description="ZeroG file identifier")
    root_hash: str = Field(..., description="Merkle root hash")
    merkle_proof: Dict[str, Any] = Field(..., description="Merkle proof data")
    timestamp: int = Field(..., description="Storage timestamp")

