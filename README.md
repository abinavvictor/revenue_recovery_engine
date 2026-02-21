# Sentinel Recover: REVENUE RECOVERY ENGINE 

Revenue Recovery Engine is an autonomous SELF CORRECTING multi agentic workflow designed for remediating charge back conflicts with a resolve to recover revenue for Large Financial Institutions(LFI)

# Mission: 
Deploying an autonomous multi-agent system that reconciles e-commerce disputes intelligently through a two way determinisic approach.It brings out verdict through set of rules  to automate "Compelling Evidence"  to resolve a claim.



Using LangGraph for orchestration and Groq (Llama-3) for high-speed reasoning, the engine automatically verifies shipping evidence against customer claims to detect contradictions.

# Core Features
Autonomous Investigation: Developing Decision framework that is self correcting using both sources as in,the internal db records  and the live tracker of shippingstatus  in flagging fraudulent claims

Live Evidence Harvesting: Uses Shippo AI to perform real-time web searches for shipping carrier statuses (UPS, FedEx, etc.).

Intelligent Audit: A Groq-powered LLM node performs a skeptical logical audit to verify if a claim (e.g., "Item not received") contradicts physical evidence ("Delivered to Front Door").

Refund Initiation: Mitigating revenue loss by minimizing false claims and in case of genuine claim,initaiing refund.

Notifier: this Agent essentially notifies the verdict for any case based on template using RESEND

MCP TOOLING: Biggest flex of this project is the development of MCP server , instead of just MCP client to let AI communicat DB.MCP Client fails purely in transactional write

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

Safety & Guardrails

# Future Enhancements
Wrapping the Engine using a fastWEB API

Building the future of autonomous resolution of charge disputes with self correcting intelligent agents

Conceieved , designed and developed by Abhinav K Victor
