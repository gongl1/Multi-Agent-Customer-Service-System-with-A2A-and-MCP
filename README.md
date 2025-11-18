# Multi-Agent-Customer-Service-System-with-A2A-and-MCP
Build a multi-agent customer service system where specialized agents coordinate using Agent-to-Agent (A2A) communication and access customer data through the Model Context Protocol (MCP). 

# Multi-Agent Customer Service System with A2A and MCP

This project implements a **multi-agent customer service automation system** using:

- **Agent-to-Agent (A2A) communication**
- **Model Context Protocol (MCP)**
- **SQLite-based database**
- **Google ADK Agents (LlmAgent)**
- **ngrok** for exposing the MCP server in Colab

It includes:
- A Router/Orchestrator Agent
- A Customer Data Agent (uses MCP tools)
- A Support Agent (handles general support)
- A fully working MCP server with 5 required tools
- All 3 assignment scenarios implemented with A2A coordination

---

## 📌 System Architecture

### Agents
1. **Router Agent**
   - Determines intent
   - Allocates tasks to other agents
   - Coordinates multi-step workflows

2. **Customer Data Agent**
   - Uses MCP tools to access/update the database:
     - `get_customer`
     - `list_customers`
     - `update_customer`
     - `create_ticket`
     - `get_customer_history`

3. **Support Agent**
   - Handles general support queries
   - Requires context from Router
   - Produces responses, escalates if needed

### MCP Server Tools
- `get_customer(customer_id)`
- `list_customers(status, limit)`
- `update_customer(customer_id, data)`
- `create_ticket(customer_id, issue, priority)`
- `get_customer_history(customer_id)`

---

## ⚙️ Installation

```bash
git clone https://github.com/<your-username>/multi-agent-customer-service-system.git
cd multi-agent-customer-service-system
pip install -r requirements.txt
