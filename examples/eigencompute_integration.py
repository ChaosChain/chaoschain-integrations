#!/usr/bin/env python3
"""
EigenCompute Integration Example for ChaosChain Genesis Studio.

This demonstrates how to integrate EigenCloud's TEE-based compute
with ChaosChain's Triple-Verified Stack (Layer 2: Process Integrity).

Usage:
    python examples/eigencompute_integration.py

Environment Variables Required:
    EIGEN_API_URL - EigenCloud API endpoint (e.g., https://api.eigencloud.xyz)
    EIGEN_API_KEY - Your EigenCloud API key
"""

import os
import sys
import time
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table

# Add parent directory to path for local SDK imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from chaoschain_integrations.compute.eigen import EigenComputeAdapter
from chaoschain_integrations.common.logging import configure_logging

# Load environment variables
load_dotenv()


class EigenComputeDemo:
    """Demo class for EigenCompute integration with ChaosChain."""

    def __init__(self):
        """Initialize EigenCompute adapter."""
        # Configure logging
        configure_logging(log_level="INFO", log_format="console")

        # Initialize Eigen adapter
        self.eigen = EigenComputeAdapter(
            api_url=os.getenv("EIGEN_API_URL"),
            api_key=os.getenv("EIGEN_API_KEY"),
            use_grpc=False,  # EigenCloud uses HTTP REST
        )

        rprint("[green]✅ EigenCompute adapter initialized[/green]")

    def run_smart_shopping_demo(self) -> None:
        """
        Run smart shopping analysis demo (mirrors genesis_studio.py workflow).

        This is the same type of task used in the Triple-Verified Stack demo.
        """
        rprint("\n[bold blue]🛒 Smart Shopping Analysis with EigenCompute[/bold blue]")
        rprint("=" * 80)

        # Create shopping analysis task (same as genesis_studio.py)
        task = {
            "model": "llama-3-8b",  # or your preferred model
            "prompt": """Analyze this shopping request and provide recommendations:

User Request: "Find me the best winter jacket in green, budget $150"

Provide:
1. Best product recommendation with price
2. Alternative options if green not available
3. Quality assessment (1-100)
4. Value score (1-100)
5. Confidence in recommendation (percentage)

Respond in JSON format with fields: product_name, price, color, quality_score, value_score, confidence, alternatives.""",
            "max_tokens": 600,
            "temperature": 0.4,
            "verification": "tee",  # Request TEE attestation
        }

        try:
            # Submit job to EigenCloud
            rprint("\n[cyan]📤 Submitting job to EigenCloud...[/cyan]")
            job_id = self.eigen.submit(task)
            rprint(f"[green]✅ Job submitted: {job_id}[/green]")

            # Poll for completion
            rprint("[yellow]⏳ Waiting for TEE-verified AI inference...[/yellow]")
            max_wait = 120  # 2 minutes max
            start_time = time.time()

            while time.time() - start_time < max_wait:
                status = self.eigen.status(job_id)
                rprint(f"   Status: {status['status']}", end="\r")

                if status["status"] == "completed":
                    rprint("\n[green]✅ Analysis completed in TEE![/green]")
                    break
                elif status["status"] == "failed":
                    rprint(f"\n[red]❌ Job failed: {status.get('error')}[/red]")
                    return

                time.sleep(3)

            # Get result with attestation
            result = self.eigen.result(job_id, wait=False)

            # Display results
            self._display_results(result)

            # Display TEE proof
            self._display_tee_proof(result)

        except Exception as e:
            rprint(f"[red]❌ Error: {e}[/red]")
            import traceback
            traceback.print_exc()

    def run_validation_demo(self) -> None:
        """
        Run validation demo (Bob's validator role in genesis_studio.py).
        """
        rprint("\n[bold blue]🔍 Quality Validation with EigenCompute[/bold blue]")
        rprint("=" * 80)

        # Mock analysis data to validate
        analysis_data = {
            "product_name": "Alpine Pro Winter Jacket",
            "price": 129.99,
            "color": "Forest Green",
            "quality_score": 85,
            "value_score": 90,
            "confidence": 0.89,
        }

        # Create validation task
        task = {
            "model": "llama-3-8b",
            "prompt": f"""As a validator, analyze this shopping recommendation:

Analysis to validate: {analysis_data}

Evaluate:
1. Completeness: Does it address all requirements? (1-100)
2. Accuracy: Are price and quality realistic? (1-100)
3. Value: Is it a good deal? (1-100)
4. Overall Score: (1-100)

Provide validation in JSON format with fields: completeness_score, accuracy_score, value_score, overall_score.""",
            "max_tokens": 500,
            "temperature": 0.3,
            "verification": "tee",
        }

        try:
            # Submit validation job
            rprint("\n[cyan]📤 Submitting validation to EigenCloud...[/cyan]")
            job_id = self.eigen.submit(task)
            rprint(f"[green]✅ Validation job: {job_id}[/green]")

            # Poll for completion
            rprint("[yellow]⏳ Waiting for validation...[/yellow]")
            for _ in range(40):
                status = self.eigen.status(job_id)
                if status["status"] == "completed":
                    break
                time.sleep(3)

            # Get validation result
            result = self.eigen.result(job_id)

            # Display validation
            self._display_validation_results(result)

        except Exception as e:
            rprint(f"[red]❌ Error: {e}[/red]")
            import traceback
            traceback.print_exc()

    def _display_results(self, result: Any) -> None:
        """Display smart shopping analysis results."""
        rprint("\n[bold]🛒 Shopping Analysis Results:[/bold]")

        try:
            import json

            output_str = result.output
            if isinstance(output_str, dict):
                output_str = output_str.get("output", "{}")

            # Parse JSON from output
            if "```json" in str(output_str):
                json_start = str(output_str).find("```json") + 7
                json_end = str(output_str).find("```", json_start)
                output_str = str(output_str)[json_start:json_end].strip()

            analysis = json.loads(str(output_str))

            # Create results table
            table = Table(title="Analysis Results", show_header=True)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Product", analysis.get("product_name", "N/A"))
            table.add_row("Price", f"${analysis.get('price', 0)}")
            table.add_row("Color", analysis.get("color", "N/A"))
            table.add_row("Quality Score", f"{analysis.get('quality_score', 0)}/100")
            table.add_row("Value Score", f"{analysis.get('value_score', 0)}/100")
            table.add_row("Confidence", f"{analysis.get('confidence', 0)}%")

            rprint(table)

        except Exception as e:
            rprint(f"[yellow]Raw output: {str(result.output)[:500]}...[/yellow]")
            rprint(f"[yellow]Parse error: {e}[/yellow]")

    def _display_validation_results(self, result: Any) -> None:
        """Display validation results."""
        rprint("\n[bold]🔍 Validation Results:[/bold]")

        try:
            import json

            output_str = result.output
            if isinstance(output_str, dict):
                output_str = output_str.get("output", "{}")

            if "```json" in str(output_str):
                json_start = str(output_str).find("```json") + 7
                json_end = str(output_str).find("```", json_start)
                output_str = str(output_str)[json_start:json_end].strip()

            validation = json.loads(str(output_str))

            rprint(f"   Overall Score: [green]{validation.get('overall_score', 0)}/100[/green]")
            rprint(f"   Completeness: {validation.get('completeness_score', 0)}/100")
            rprint(f"   Accuracy: {validation.get('accuracy_score', 0)}/100")
            rprint(f"   Value: {validation.get('value_score', 0)}/100")

        except Exception as e:
            rprint(f"[yellow]Raw output: {str(result.output)[:500]}...[/yellow]")

    def _display_tee_proof(self, result: Any) -> None:
        """Display TEE attestation proof."""
        rprint("\n[bold cyan]🔐 TEE Attestation Proof (Process Integrity - Layer 2):[/bold cyan]")

        proof_panel = f"""[yellow]Proof Method:[/yellow] {result.proof.method}
[yellow]Docker Digest:[/yellow] {result.proof.docker_digest or 'N/A'}
[yellow]Enclave Public Key:[/yellow] {result.proof.enclave_pubkey or 'N/A'}
[yellow]Execution Hash:[/yellow] {result.proof.execution_hash or 'N/A'}
[yellow]Signature:[/yellow] {result.proof.signature[:40] if result.proof.signature else 'N/A'}...

[green]✅ TEE Attestation Verified[/green]
This proof can be stored on-chain for Layer 3 (Adjudication/Accountability)."""

        panel = Panel(
            proof_panel,
            title="[bold green]Process Integrity Proof[/bold green]",
            border_style="green",
        )
        rprint(panel)

    def list_available_models(self) -> None:
        """List available models on EigenCloud."""
        rprint("\n[bold blue]📋 Available EigenCloud Models[/bold blue]")
        rprint("=" * 80)

        try:
            models = self.eigen.client.list_models_sync()

            table = Table(title="Available Models", show_header=True)
            table.add_column("Model Name", style="cyan")
            table.add_column("Capabilities", style="yellow")
            table.add_column("TEE Support", style="green")

            for model in models:
                table.add_row(
                    model.get("name", "Unknown"),
                    model.get("capabilities", "N/A"),
                    "✅" if model.get("tee_enabled") else "❌",
                )

            rprint(table)

        except Exception as e:
            rprint(f"[yellow]Could not list models: {e}[/yellow]")


def main():
    """Main entry point."""
    banner = """
[bold cyan]🔐 EigenCompute Integration for ChaosChain[/bold cyan]
[yellow]Triple-Verified Stack - Layer 2: Process Integrity[/yellow]

This demo shows how to integrate EigenCloud's TEE-based compute
with ChaosChain's verification stack.
    """

    panel = Panel(
        banner,
        title="[bold green]EigenCompute Demo[/bold green]",
        border_style="cyan",
    )
    rprint(panel)

    # Check environment variables
    if not os.getenv("EIGEN_API_KEY"):
        rprint("[red]❌ Error: EIGEN_API_KEY environment variable not set[/red]")
        rprint("[yellow]Please set your EigenCloud API key:[/yellow]")
        rprint("   export EIGEN_API_KEY=your_key_here")
        sys.exit(1)

    if not os.getenv("EIGEN_API_URL"):
        rprint("[yellow]⚠️  EIGEN_API_URL not set, using default[/yellow]")

    # Initialize demo
    demo = EigenComputeDemo()

    # Run demos
    demo.list_available_models()
    demo.run_smart_shopping_demo()
    demo.run_validation_demo()

    rprint("\n[bold green]✅ EigenCompute Integration Demo Complete![/bold green]")


if __name__ == "__main__":
    main()

