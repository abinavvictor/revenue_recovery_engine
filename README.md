# Sentinel Recover: REVENUE RECOVERY ENGINE 

Sentinel Recover is an autonomous SELF CORRECTING agentic workflow designed for banking and fintech sectors to investigate transaction disputes. 

# Mission: 
Deploying an autonomous multi-agent system that reconciles e-commerce disputes by cross-referencing real-time logistics data against internal transaction records to automate "Compelling Evidence" generation to resolve a claim.



Using LangGraph for orchestration and Groq (Llama-3) for high-speed reasoning, the engine automatically verifies shipping evidence against customer claims to detect contradictions.

# Core Features
Autonomous Investigation: Automatically retrieves tracking numbers from a PostgreSQL "Source of Truth."

Live Evidence Harvesting: Uses Tavily AI to perform real-time web searches for shipping carrier statuses (UPS, FedEx, etc.).

Intelligent Audit: A Groq-powered LLM node performs a skeptical logical audit to verify if a claim (e.g., "Item not received") contradicts physical evidence ("Delivered to Front Door").

Persistence Layer: Saves every investigation result and logical trail back to a database for human-in-the-loop (HIL) review.

# Tech Stack
Orchestration: LangGraph

LLM Engine: Groq (Llama 3.3 70B)

RAG Pipelines

Multi Context Protocol (MCP)

Search Tool: Tavily AI

Database: PostgreSQL 

Environment: Python 3.11+ / uv package manager


# Getting Started
1. Prerequisites
Ensure you have a PostgreSQL instance running and a Groq API key.
Also secure Tavily API Key to secure shipping information

# Environment Setup
Create a .env file in the root directory:

Plaintext

GROQ_API_KEY=gsk_your_key_here
TAVILY_API_KEY=tvly_your_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/sentinel_db



# Install dependencies
uv sync

# Run the engine
uv run python -m main
⚖️ Safety & Guardrails

# Future Enhancements
Incorporate MultiContext Protocol(MCP) to find and read through the DB sources without SQL Alchemy

Building the future of autonomous resolution of charge disputes with self correcting intelligent agents

Conceieved , designed and developed by Abhinav K Victor
