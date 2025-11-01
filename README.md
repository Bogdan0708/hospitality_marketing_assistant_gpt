# Mitch AI Monorepo

This repository provides a multi-service stack for social analytics, data processing, content automation, and operator tooling. It follows an MCP-style layout with small, focused services communicating over HTTP and sharing a common docker-compose environment.

## Getting Started

1. Copy the environment template and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
2. Build and start the stack:
   ```bash
   docker compose up --build
   ```
3. Access the dashboard at [http://localhost:8501](http://localhost:8501).

## Services Overview

- **mcp-social-analytics**: Platform-specific ingestion services, starting with Instagram.
- **mcp-data-processor**: NLP services for sentiment analysis, trend detection, and insight aggregation.
- **mcp-content-automation**: Caption generation, scheduling, and publishing utilities.
- **ui**: API gateway and Streamlit dashboard for operators.
- **infra**: Supporting infrastructure such as Postgres and optional Nginx reverse proxy.
- **libs/common**: Shared utilities and DTOs (placeholder for now).

Extend each service as you iterate through the roadmap in the project brief.
