"""Push a .dsl file into a BP graph via the UE MCP server.
Usage: python push_dsl.py <graph_refPath> <dsl_file>"""
import sys, os
sys.path.insert(0, os.path.expanduser("~"))
import mcp_ue
graph_ref, dsl_file = sys.argv[1], sys.argv[2]
code = open(dsl_file, encoding="utf-8").read()
res = mcp_ue.rpc("tools/call", {"name":"call_tool","arguments":{
    "toolset_name":"editor_toolset.toolsets.blueprint.BlueprintTools",
    "tool_name":"write_graph_dsl",
    "arguments":{"graph":{"refPath":graph_ref},"code":code}}})
import json
print(json.dumps(res)[:3000])
