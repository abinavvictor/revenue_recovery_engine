import os
import stripe
import psycopg
import resend 
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()
#Three asynchronous Engines managed by single MCP session preloaded and passed via state to prevent collision from aysnc task group calls cos of concurrent laod_mcp_tools
mcp = FastMCP("Revenue-Recovery-Engine")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  #Using Secret key because i use drestricted key and failed because of permissions
DB_URL = os.getenv("DATABASE_URL")
resend.api_key = os.getenv("RESEND_API_KEY")

#Database tooling here

@mcp.tool()
async def access_database(sql_command: str) -> str:
    """
    Execute SQL commands on the Postgres database.
    Use this for reading customer history or writing/updating dispute records.
    """
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_command)
                if cur.description:
                    columns = [desc[0] for desc in cur.description]
                    results = cur.fetchall()
                    return str([dict(zip(columns, row)) for row in results])
                conn.commit()
                return "Database command executed successfully."
    except Exception as e:
        return f"Database Error: {str(e)}"

#Stripe Engine tooling

@mcp.tool()
async def get_payment_details(payment_intent_id: str) -> str:
    """Fetch status and amount of a payment intent to verify refund eligibility."""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return f"Payment Status: {intent.status}, Amount: ${intent.amount / 100:.2f}, Currency: {intent.currency}"
    except stripe.error.StripeError as e:
        return f"Stripe Error: {e.user_message}"

@mcp.tool()
async def process_refund(payment_intent_id: str, amount_cents: int = 0) -> str:
    """
    Executes a refund in Stripe.
    Pass payment_intent_id. Set amount_cents to 0 for a full refund,
    or specify a partial amount in cents (e.g. 5000 = $50.00).
    """
    try:
        refund_params = {"payment_intent": payment_intent_id}
        if amount_cents > 0:
            refund_params["amount"] = amount_cents

        refund = stripe.Refund.create(**refund_params)
        return f"Refund successful. ID: {refund.id}, Status: {refund.status}"
    except stripe.error.StripeError as e:
        return f"Stripe Refund Error: {e.user_message}"

# Email?notification engine tooling

@mcp.tool()
async def send_email(email: str, subject: str, body: str) -> str:
    """
    Sends a customer notification email via Resend.
    Use for refund confirmations, updates, or manual review escalations.
    """
    try:
        params = {
            "from": os.getenv("EMAIL_FROM", "abinav.korati@gmail.com"),
            "to": [email],
            "subject": subject,
            "text": body,
        }
        email_response = resend.Emails.send(params)
        print(f" [LOG]: Email sent to {email} | Subject: {subject} | ID: {email_response['id']}")
        return f"Success: Email sent to {email}, ID: {email_response['id']}"
    except Exception as e:
        return f"Email Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
