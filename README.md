# Agent Traffic Logging

This repository provides a minimal, self-contained example of an
instrumented web-based LLM agent that logs network-level behavior
during agent execution.

The goal is to support evaluation and analysis of agentic AI systems
by capturing structured behavioral metadata rather than content.

## What is Logged
- Visited domains
- Request and response sizes
- HTTP methods and status codes
- Navigation events
- LLM API request metadata

## Design Goals
- Agent-agnostic instrumentation
- Minimal coupling to task logic
- Async, non-blocking logging
- Logs suitable for downstream evaluation, auditing, and risk analysis

## Structure
- `logging_websurfer.py` instruments a web-browsing agent via Playwright hooks
- `logging_openai_client.py` logs LLM API request metadata
- `isp_logger.py` provides a shared structured logger
- `run_example.py` demonstrates a simple end-to-end agent run

This code was extracted and simplified from a larger research prototype
to highlight the core infrastructure component.
