# mcp_server.py
"""
MCP server for the Multi-Agent Customer Service System.
Implements 5 required MCP tools and exposes them via JSON-RPC + SSE.
Extracted from notebook lg_multi_agent_customer_service_system_with_a2a_and_mcp.py
"""

import sqlite3
import json
import threading
import time
from typing import Dict, Any, List

from flask import Flask, request, Response, jsonify
from flask_cors import CORS

DB_PATH = "support.db"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

app = Flask(__name__)
CORS(app)

# -------------------------------------------------------
# DB helper
# -------------------------------------------------------

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------------------------------
# MCP Tool Implementations
# -------------------------------------------------------

def get_customer(customer_id: int) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "error": f"Customer {customer_id} not found"}
        return {"success": True, "customer": dict(row)}
    finally:
        conn.close()


def list_customers(status: str = None, limit: int = 10) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if status:
            cursor.execute(
                "SELECT * FROM customers WHERE status = ? ORDER BY id LIMIT ?",
                (status, limit),
            )
        else:
            cursor.execute("SELECT * FROM customers ORDER BY id LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return {"success": True, "customers": [dict(r) for r in rows]}
    finally:
        conn.close()


def update_customer(customer_id: int, data: Dict[str, Any]):
    if not data:
        return {"success": False, "error": "No fields provided to update"}

    allowed = {"name", "email", "phone", "status"}
    updates = []
    values = []
    for k, v in data.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            values.append(v)

    if not updates:
        return {"success": False, "error": "No valid fields to update"}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        values.append(customer_id)
        cursor.execute(
            f"UPDATE customers SET {', '.join(updates)}, updated_at=CURRENT_TIMESTAMP WHERE id = ?",
            values,
        )
        conn.commit()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "error": "Customer not found after update"}
        return {"success": True, "customer": dict(row)}
    finally:
        conn.close()


def create_ticket(customer_id: int, issue: str, priority: str = "medium"):
    if priority not in ("low", "medium", "high"):
        return {"success": False, "error": "Invalid priority"}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
        if not cursor.fetchone():
            return {"success": False, "error": "Customer does not exist"}

        cursor.execute(
            """
            INSERT INTO tickets (customer_id, issue, status, priority)
            VALUES (?, ?, 'open', ?)
            """,
            (customer_id, issue, priority),
        )
        conn.commit()
        ticket_id = cursor.lastrowid

        cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cursor.fetchone()
        return {"success": True, "ticket": dict(row)}
    finally:
        conn.close()


def get_customer_history(customer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        cust = cursor.fetchone()
        if not cust:
            return {"success": False, "error": "Customer not found"}

        cursor.execute(
            "SELECT * FROM tickets WHERE customer_id = ? ORDER BY created_at DESC",
            (customer_id,),
        )
        tickets = cursor.fetchall()

        return {
            "success": True,
            "customer": dict(cust),
            "tickets": [dict(t) for t in tickets],
        }
    finally:
        conn.close()


# -------------------------------------------------------
# MCP Tool Schema
# -------------------------------------------------------

MCP_TOOLS = [
    {
        "name": "get_customer",
        "description": "Get customer by ID",
        "inputSchema": {
            "type": "object",
            "properties": {"customer_id": {"type": "integer"}},
            "required": ["customer_id"],
        },
    },
    {
        "name": "list_customers",
        "description": "List customers",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
            },
        },
    },
    {
        "name": "update_customer",
        "description": "Update a customer's fields",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer"},
                "data": {"type": "object"},
            },
            "required": ["customer_id", "data"],
        },
    },
    {
        "name": "create_ticket",
        "description": "Create a support ticket",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer"},
                "issue": {"type": "string"},
                "priority": {"type": "string"},
            },
            "required": ["customer_id", "issue"],
        },
    },
    {
        "name": "get_customer_history",
        "description": "Return customer + all tickets",
        "inputSchema": {
            "type": "object",
            "properties": {"customer_id": {"type": "integer"}},
            "required": ["customer_id"],
        },
    },
]

# -------------------------------------------------------
# JSON-RPC dispatcher
# -------------------------------------------------------

def handle_initialize(msg):
    return {
        "jsonrpc": "2.0",
        "id": msg.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "customer-support-mcp-server", "version": "1.0.0"},
        },
    }


def handle_tools_list(msg):
    return {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"tools": MCP_TOOLS}}


def handle_tools_call(msg):
    params = msg.get("params", {})
    name = params.get("name")
    args = params.get("arguments", {}) or {}

    fn = {
        "get_customer": get_customer,
        "list_customers": list_customers,
        "update_customer": update_customer,
        "create_ticket": create_ticket,
        "get_customer_history": get_customer_history,
    }.get(name)

    if fn is None:
        return {
            "jsonrpc": "2.0",
            "id": msg.get("id"),
            "error": {"code": -32601, "message": f"Unknown tool {name}"},
        }
    try:
        result = fn(**args)
        return {
            "jsonrpc": "2.0",
            "id": msg.get("id"),
            "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": msg.get("id"),
            "error": {"code": -32000, "message": str(e)},
        }


def dispatch(msg):
    method = msg.get("method")
    if method == "initialize":
        return handle_initialize(msg)
    if method == "tools/list":
        return handle_tools_list(msg)
    if method == "tools/call":
        return handle_tools_call(msg)
    return {
        "jsonrpc": "2.0",
        "id": msg.get("id"),
        "error": {"code": -32601, "message": f"Unsupported method: {method}"},
    }

# -------------------------------------------------------
# Flask routes (SSE)
# -------------------------------------------------------

def sse_message(payload):
    return f"data: {json.dumps(payload)}\n\n"


@app.route("/mcp", methods=["POST"])
def mcp_endpoint():
    msg = request.get_json()

    def generate():
        try:
            response = dispatch(msg)
            yield sse_message(response)
        except Exception as e:
            yield sse_message(
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            )

    return Response(generate(), mimetype="text/event-stream")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "server": "customer-support-mcp-server"})

# -------------------------------------------------------
# Boot
# -------------------------------------------------------

def start_server():
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    print("Starting MCP server at", SERVER_URL)
    start_server()
