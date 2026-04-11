"""Route normalized execution requests into the execution layer.

This module owns the thin CLI-to-execution routing boundary after request
construction has completed. It should remain free of workflow compilation,
simulation execution, and presentation logic.
"""

from __future__ import annotations

from engine_build.app.service_models.service_request_container import ServiceRequest
from engine_build.app.execution.orchestrator import orchestrate


def dispatch(service_request: ServiceRequest) -> int:
    """ Thin layer to keep separation clean"""
    return orchestrate(service_request=service_request)




if __name__ == "__main__":
    pass
