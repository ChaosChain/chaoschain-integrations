"""
ChaosChain Integrations - Partner Adapters for ChaosChain SDK.

This package provides adapters for various partner services including:
- Storage providers (ZeroG, IPFS/Pinata)
- Compute providers (ZeroG, Eigen)
- Attestation services (Chainlink CRE)

Each adapter implements the corresponding protocol from chaoschain-sdk.
"""

from chaoschain_integrations.common.version import __version__

__all__ = ["__version__"]

