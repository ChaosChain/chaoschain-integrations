"""Pydantic schemas for Pinata API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PinataMetadata(BaseModel):
    """Metadata for pinned content."""

    name: Optional[str] = Field(default=None, description="Pin name")
    keyvalues: Optional[Dict[str, Any]] = Field(
        default=None, description="Custom key-value metadata"
    )


class PinataOptions(BaseModel):
    """Options for pinning."""

    cidVersion: int = Field(default=1, description="CID version (0 or 1)")
    wrapWithDirectory: bool = Field(default=False, description="Wrap in directory")


class PinFileRequest(BaseModel):
    """Request to pin file to IPFS via Pinata."""

    content: bytes = Field(..., description="Content to pin")
    metadata: Optional[PinataMetadata] = Field(default=None, description="Pin metadata")
    options: Optional[PinataOptions] = Field(default=None, description="Pin options")


class PinFileResponse(BaseModel):
    """Response from Pinata pin operation."""

    IpfsHash: str = Field(..., description="IPFS CID")
    PinSize: int = Field(..., description="Pin size in bytes")
    Timestamp: str = Field(..., description="Pin timestamp (ISO)")
    isDuplicate: Optional[bool] = Field(default=None, description="Whether pin is duplicate")


class UnpinRequest(BaseModel):
    """Request to unpin from Pinata."""

    ipfs_hash: str = Field(..., description="IPFS CID to unpin")


class PinListQuery(BaseModel):
    """Query parameters for listing pins."""

    hashContains: Optional[str] = None
    pinStart: Optional[str] = None
    pinEnd: Optional[str] = None
    status: Optional[str] = Field(default="pinned", description="Pin status filter")


class PinListItem(BaseModel):
    """Single pin list item."""

    ipfs_pin_hash: str
    size: int
    date_pinned: str
    metadata: Optional[Dict[str, Any]] = None


class PinListResponse(BaseModel):
    """Response from pin list query."""

    count: int
    rows: List[PinListItem]

