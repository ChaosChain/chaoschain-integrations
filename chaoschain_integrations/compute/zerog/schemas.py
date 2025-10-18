"""Pydantic schemas for ZeroG compute API."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ZeroGComputeTask(BaseModel):
    """Task specification for ZeroG compute."""

    task_type: str = Field(..., description="Task type (e.g., 'inference', 'training')")
    model: Optional[str] = Field(default=None, description="Model identifier")
    inputs: Dict[str, Any] = Field(..., description="Task inputs")
    verification: str = Field(default="tee-ml", description="Verification method")
    docker_image: Optional[str] = Field(default=None, description="Custom docker image")
    resources: Optional[Dict[str, Any]] = Field(default=None, description="Resource requirements")


class ZeroGSubmitResponse(BaseModel):
    """Response from job submission."""

    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Initial status")
    submitted_at: int = Field(..., description="Submission timestamp")


class ZeroGStatusResponse(BaseModel):
    """Response from status query."""

    job_id: str
    status: str = Field(..., description="Job status: pending, running, completed, failed")
    progress: Optional[float] = Field(default=None, description="Progress percentage (0-100)")
    message: Optional[str] = Field(default=None, description="Status message")
    updated_at: int = Field(..., description="Last update timestamp")


class ZeroGResultResponse(BaseModel):
    """Response with job result."""

    job_id: str
    status: str
    output: Any = Field(..., description="Computation output")
    attestation: Optional[Dict[str, Any]] = Field(default=None, description="TEE attestation")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata (proof, hashes, etc.)"
    )
    completed_at: Optional[int] = Field(default=None, description="Completion timestamp")


class ZeroGCancelResponse(BaseModel):
    """Response from cancel request."""

    job_id: str
    cancelled: bool = Field(..., description="Whether job was cancelled")
    message: Optional[str] = None

