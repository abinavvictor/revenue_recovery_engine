# Sentinel Recover: REVENUE RECOVERY ENGINE 

Revenue Recovery Engine is an autonomous SELF CORRECTING multi agentic workflow designed for remediating charge back conflicts with a resolve to recover revenue for Large Financial Institutions(LFI)

# Mission: 
Deploying an autonomous multi-agent system that reconciles e-commerce disputes intelligently through a two way determinisic approach.It brings out verdict through set of rules  to automate "Compelling Evidence" in resolving a claim.

Using LangGraph for orchestration and Groq (Llama-3) for blazing fast reasoning, the engine essentially verifies shipping evidence against customer claims to detect anamolies.

# Core Features
Autonomous Investigation: Developing Decision framework that is self correcting using both sources as in,the cross validation of internal db records  and the live tracker of delivered item using shipping status in flagging fraudulent claims

Live Evidence Harvesting: Uses Shippo AI to perform real-time web searches for shipping carrier statuses from different shipping labels(UPS, FedEx,USPS etc.).

Intelligent Audit: A Groq-powered LLM node performs a skeptical logical audit to verify if a claim (e.g., "Item not received") contradicts physical evidence ("Delivered to Front Door").

Refund Initiation: Mitigating revenue loss by minimizing false claims and in case of genuine claim,initiating refund using Stripe payment gateway is the main objective of this node

Notifier: This Agent essentially notifies the verdict for all cases to end customer based on template automated using RESEND

MCP TOOLING: Biggest flex of this project is the development of MCP server , instead of just leveraging the MCP client utility to let AI(in our case Groq LLM) to communicate with the DB.MCP Client miserably at transactional writes.so in order to get the inserts going MCP server had to be established

Dispute History: Maintaining a history of disputes related to a customer corroborates the discrepancy without additonal steps for harvesting evidence thereby ensuring swift and sustainable resolutions

Triple Engine: Managing the asynchronous workflows of three different engines namely Postgres DB, Payment Engine, Notification Engine within a single MCP session using State is remarkable

# Tech Stack
Orchestration: LangGraph

LLM Engine: Groq (Llama 3.3 70B)

RAG Pipelines

Multi Context Protocol (MCP)

Search Tool: Shippo API

Database: PostgreSQL 

Payment Gateway: Stripe API

Email Notification: Resend API

Environment: Python 3.11+ / uv package manager


# Getting Started
1. Prerequisites
Ensure you have a PostgreSQL instance running and a Groq API key.
Also secure Shippo API Key for secure shipping information
For Refund remediance,ensure Stripe Payment Gateway is established


# Environment Setup
Create a .env file in the root directory:

Plaintext

GROQ_API_KEY=gsk_your_key_here
STRIPE_API_KEY=tvly_your_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/sentinel_db



# Install dependencies
uv sync

# Run the engine
uv run python -m main

#Safety & Guardrails
I have employed retry count within state and used that as circuit breaker to ensure the safety of AI from hallucinating..

# Future Enhancements
Wrapping the Engine using a fastWEB API to depict distributed dashboards for the total revenue recovered by successful autonomous remediation of charge back conflicts using AI Agents

Conceieved , designed and developed by Abhinav K Victor
