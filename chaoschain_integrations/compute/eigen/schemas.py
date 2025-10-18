"""Pydantic schemas for Eigen compute API."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EigenComputeTask(BaseModel):
    """Task specification for Eigen compute."""

    task: str = Field(..., description="Task type (e.g., 'inference', 'training')")
    model: Optional[str] = Field(default=None, description="Model identifier")
    prompt: Optional[str] = Field(default=None, description="Prompt for inference")
    inputs: Optional[Dict[str, Any]] = Field(default=None, description="Task inputs")
    verification: str = Field(default="tee-ml", description="Verification method")
    image_digest: Optional[str] = Field(default=None, description="Docker image digest")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Additional config")


class EigenSubmitResponse(BaseModel):
    """Response from job submission."""

    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Initial status")
    created_at: int = Field(..., description="Creation timestamp")


class EigenStatusResponse(BaseModel):
    """Response from status query."""

    job_id: str
    status: str = Field(
        ..., description="Job status: pending, running, completed, failed"
    )
    progress: Optional[int] = Field(default=None, description="Progress percentage")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    updated_at: int = Field(..., description="Last update timestamp")


class EigenResultResponse(BaseModel):
    """Response with job result."""

    job_id: str
    status: str
    output: Any = Field(..., description="Computation output")
    attestation: Optional[Dict[str, Any]] = Field(
        default=None, description="TEE attestation data"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata including proof, hashes, signatures",
    )
    completed_at: Optional[int] = Field(default=None, description="Completion timestamp")


class EigenCancelResponse(BaseModel):
    """Response from cancel request."""

    job_id: str
    cancelled: bool
    message: Optional[str] = None

