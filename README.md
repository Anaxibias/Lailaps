Lailaps
Live Application: lailaps.app

Overview
Lailaps is an automated job tracking application and data extraction pipeline. It utilizes an AI-driven backend to parse complex, unstandardized web payloads and convert them into structured relational database records.

Architecture
Backend: Python, Flask REST API, PostgreSQL

AI Orchestration: Gemini API, Serper search tools (leveraging structured tool use for dynamic parsing)

Deployment: Containerized with Docker and deployed on Azure

Active Development: Frontend Refactor
The application's frontend is currently undergoing a structural refactor. The initial build utilized server-side rendered HTML and Jinja templates. This is actively being migrated to a decoupled Single-Page Application (SPA) architecture using Mithril.js to interface with the Flask REST API.

Local Setup
Clone the repository.

Configure environment variables for PostgreSQL, Gemini API, and Serper API in a .env file.

Build and run the Docker containers.