import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from src.graph import create_graph

load_dotenv()

async def run_revenuerecovery_engine():
    print("\n" + "="*40)
    user_order_id = input("🔎 Enter the ORDER ID to investigate: ").strip()
    print("="*40 + "\n")

    if not user_order_id:
        print(" Error: Order ID cannot be empty.")
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, "src", "mcpserver.py")

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", script_path],
        env=os.environ.copy()
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                #Loading MCP tools and passing into state ..to avoid task group error triggered from async workflow of stimulating three engines namely postgresdb,stripe,resend
                tools = await load_mcp_tools(session)
                print(f" Loaded {len(tools)} MCP tools.")
                print(f"Systems Online. Beginning flow for: {user_order_id}")

                app = create_graph()

                initial_state = {
                    "order_id": user_order_id,
                    "mcp_session": session,
                    "stripe_session": session,
                    "db_session": session,
                    "mcp_tools": tools,          # ✅ pre-loaded tools
                    "history": [],
                    "messages": [],
                    "retry_count": 0,
                    "resolution_status": "pending"
                }

                 
                final_state = await app.ainvoke(initial_state)

                print(f"\n✨ Workflow Finished. Final Verdict: {final_state.get('resolution_status')}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f" System Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_revenuerecovery_engine())