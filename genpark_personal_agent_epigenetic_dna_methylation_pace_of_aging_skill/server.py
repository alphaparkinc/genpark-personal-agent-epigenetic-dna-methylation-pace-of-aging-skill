# -*- coding: utf-8 -*-
"""MCP Server for Epigenetic DNA Methylation & DunedinPACE Biological Aging Tracker Skill."""
import sys
import json
import logging
from typing import Dict, Any

from .core import EpigeneticDNAMethylationPaceOfAgingTracker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOOLS_SCHEMA = [
    {
        "name": "audit_dunedin_pace_of_aging",
        "description": "Evaluate DunedinPACE epigenetic pace of aging, GrimAge acceleration delta, and mortality hazard ratio against standard chronological baseline.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dunedin_pace": {
                    "type": "number",
                    "description": "e.g. 0.85 years of biological aging per calendar year"
                },
                "chronological_age": {
                    "type": "integer"
                },
                "grim_age_years": {
                    "type": "number"
                },
                "telomere_percentile": {
                    "type": "number"
                }
            },
            "required": [
                "dunedin_pace",
                "chronological_age",
                "grim_age_years"
            ]
        }
    },
    {
        "name": "synthesize_epigenetic_rejuvenation_protocol",
        "description": "Synthesize personalized methyl-donor nutrition, NAD+ replenishment, and circadian fasting protocol to decelerate epigenetic drift.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pace_tier": {
                    "type": "string",
                    "enum": [
                        "slow_aging",
                        "average_aging",
                        "accelerated_aging",
                        "hyper_accelerated_aging"
                    ]
                },
                "primary_epigenetic_target": {
                    "type": "string",
                    "enum": [
                        "dna_repair_nad",
                        "homocysteine_methylation",
                        "autophagy_mTOR",
                        "mitochondrial_biogenesis"
                    ]
                }
            },
            "required": [
                "pace_tier",
                "primary_epigenetic_target"
            ]
        }
    }
]

def handle_rpc(line: str) -> str:
    try:
        req = json.loads(line)
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-personal-agent-epigenetic-dna-methylation-pace-of-aging-skill", "version": "1.0.0"}
            }
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": res})

        elif method == "tools/list":
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SCHEMA}})

        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})

            target_func = getattr(EpigeneticDNAMethylationPaceOfAgingTracker, tool_name, None)
            if not target_func:
                return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {tool_name}"}})

            result = target_func(**args)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            })

        else:
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": req.get("id") if "req" in locals() else None, "error": {"code": -32000, "message": str(e)}})

def run_test():
    print("[TEST] Running internal RPC self-test for genpark-personal-agent-epigenetic-dna-methylation-pace-of-aging-skill...")
    init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    init_res = json.loads(handle_rpc(init_req))
    assert init_res.get("result", {}).get("serverInfo", {}).get("name") == "genpark-personal-agent-epigenetic-dna-methylation-pace-of-aging-skill"

    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    list_res = json.loads(handle_rpc(list_req))
    assert len(list_res.get("result", {}).get("tools", [])) == 2
    print(f"[TEST] SUCCESS: {len(list_res['result']['tools'])} tools verified.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        if run_test():
            sys.exit(0)
        sys.exit(1)

    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
