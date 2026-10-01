import json
import time
import uuid
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from app.agent.state import InvestigationState
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.llm import get_llm_client
from app.config import settings

from app.tools.metrics import query_metrics
from app.tools.logs import query_logs
from app.tools.deployments import get_deployment_history
from app.tools.service_catalog import get_service
from app.tools.runbooks import search_runbooks
from app.tools.incidents import search_incidents

from app.api.schemas import InvestigationResult, Evidence

class TracePilotAgent:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_client()
        self.max_steps = settings.max_agent_steps
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_service",
                    "description": "Get service metadata like dependencies and owner.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service": {"type": "string"}
                        },
                        "required": ["service"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_metrics",
                    "description": "Query metrics for a service within a time range.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service": {"type": "string"},
                            "metric_name": {"type": "string"},
                            "start_time": {"type": "string", "description": "ISO format"},
                            "end_time": {"type": "string", "description": "ISO format"}
                        },
                        "required": ["service", "metric_name", "start_time", "end_time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_deployment_history",
                    "description": "Get deployment history for a service.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service": {"type": "string"},
                            "start_time": {"type": "string", "description": "ISO format"},
                            "end_time": {"type": "string", "description": "ISO format"}
                        },
                        "required": ["service", "start_time", "end_time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_logs",
                    "description": "Query logs for a service.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service": {"type": "string"},
                            "start_time": {"type": "string", "description": "ISO format"},
                            "end_time": {"type": "string", "description": "ISO format"},
                            "level": {"type": "string"},
                            "search_term": {"type": "string"}
                        },
                        "required": ["service", "start_time", "end_time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_runbooks",
                    "description": "Search runbooks for matching errors or terms.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "service": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_incidents",
                    "description": "Search past incidents and postmortems.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "service": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def _execute_tool(self, name: str, args: Dict[str, Any]) -> str:
        try:
            if name == "get_service":
                res = get_service(self.db, args["service"])
                return json.dumps(res) if res else "Service not found."
            elif name == "query_metrics":
                st = datetime.fromisoformat(args["start_time"])
                et = datetime.fromisoformat(args["end_time"])
                res = query_metrics(self.db, args["service"], args["metric_name"], st, et)
                return json.dumps(res)
            elif name == "get_deployment_history":
                st = datetime.fromisoformat(args["start_time"])
                et = datetime.fromisoformat(args["end_time"])
                res = get_deployment_history(self.db, args["service"], st, et)
                return json.dumps(res)
            elif name == "query_logs":
                st = datetime.fromisoformat(args["start_time"])
                et = datetime.fromisoformat(args["end_time"])
                res = query_logs(self.db, args["service"], st, et, args.get("level"), args.get("search_term"))
                return json.dumps(res)
            elif name == "search_runbooks":
                res = search_runbooks(self.db, args["query"], args.get("service"))
                return json.dumps(res)
            elif name == "search_incidents":
                res = search_incidents(self.db, args["query"], args.get("service"))
                return json.dumps(res)
            else:
                return f"Tool {name} not found."
        except Exception as e:
            return f"Error executing tool: {str(e)}"

    def investigate(self, query: str) -> InvestigationResult:
        start_time_ms = time.time() * 1000
        trace_id = str(uuid.uuid4())
        
        # We start by forcing a deterministic mock response if LLM is mocked
        if hasattr(self.llm, "call_count"):
            # It's a Mock LLM
            # Just do a manual quick simulation of tools for the demo scenario
            now = datetime.now(timezone.utc)
            st = (now - timedelta(hours=3)).isoformat()
            et = now.isoformat()
            
            _ = self._execute_tool("get_service", {"service": "checkout-api"})
            metrics_resp = self._execute_tool("query_metrics", {"service": "checkout-api", "metric_name": "error_rate_percent", "start_time": st, "end_time": et})
            deps_resp = self._execute_tool("get_deployment_history", {"service": "checkout-api", "start_time": st, "end_time": et})
            logs_resp = self._execute_tool("query_logs", {"service": "checkout-api", "start_time": st, "end_time": et, "level": "ERROR"})
            runbooks_resp = self._execute_tool("search_runbooks", {"query": "PaymentClientTimeout", "service": "checkout-api"})
            
            evidence = [
                Evidence(
                    evidence_id="ev-1",
                    source_type="metric",
                    source_name="error_rate_percent",
                    source_reference="checkout-api",
                    excerpt="Spike in 5xx errors from 1.1% to 11.8%",
                    relevance="Shows the incident impact"
                ),
                Evidence(
                    evidence_id="ev-2",
                    source_type="deployment",
                    source_name="d-8472",
                    source_reference="checkout-api v2.8.1",
                    excerpt="Update PaymentClient timeout configuration",
                    relevance="Correlates with error spike"
                ),
                Evidence(
                    evidence_id="ev-3",
                    source_type="log",
                    source_name="PaymentClientTimeout",
                    source_reference="checkout-api",
                    excerpt="PaymentClientTimeout: request exceeded 100ms",
                    relevance="Shows actual error mechanism"
                )
            ]
            
            return InvestigationResult(
                incident_summary=query,
                affected_services=["checkout-api", "payment-service"],
                timeline=[],
                observations=["5xx spike detected", "Deployment d-8472 occurred just before spike", "PaymentClientTimeout errors in logs"],
                hypotheses=["Deployment d-8472 introduced a bad timeout config"],
                likely_root_cause="PaymentClient timeout configuration is too aggressive (100ms), causing false timeouts when payment gateway latency spikes.",
                confidence="High",
                evidence=evidence,
                recommended_next_step="Revert checkout-api deployment or adjust timeout configuration to 500ms.",
                limitations="This is a mocked response since LLM_API_KEY was not provided.",
                trace_id=trace_id,
                latency_ms=int((time.time() * 1000) - start_time_ms)
            )

        # Real LLM ReAct Loop
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Investigate this incident: {query}\nThe current time is: {datetime.now(timezone.utc).isoformat()}"}
        ]
        
        state = InvestigationState(incident_description=query)
        
        while state.iterations < self.max_steps:
            state.iterations += 1
            
            response = self.llm.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            messages.append(message)
            
            if not message.tool_calls:
                # Agent concluded
                break
                
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                tool_result = self._execute_tool(function_name, arguments)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": tool_result
                })
        
        # After loop, ask for final structured output
        messages.append({
            "role": "user", 
            "content": "You have gathered all necessary information. Please output the final investigation result in JSON format matching the expected schema. Include detailed evidence."
        })
        
        final_response = self.llm.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        try:
            result_dict = json.loads(final_response.choices[0].message.content)
            result_dict["trace_id"] = trace_id
            result_dict["latency_ms"] = int((time.time() * 1000) - start_time_ms)
            return InvestigationResult(**result_dict)
        except Exception as e:
            # Fallback if json parsing fails
            return InvestigationResult(
                incident_summary=query,
                affected_services=[],
                timeline=[],
                observations=[],
                hypotheses=[],
                likely_root_cause=f"Failed to parse final output: {str(e)}\nRaw: {final_response.choices[0].message.content}",
                confidence="Low",
                evidence=[],
                recommended_next_step="Check logs.",
                limitations="Parsing error.",
                trace_id=trace_id,
                latency_ms=int((time.time() * 1000) - start_time_ms)
            )
