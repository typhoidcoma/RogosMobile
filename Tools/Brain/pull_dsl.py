import sys, os, json
sys.path.insert(0, os.path.expanduser("~"))
import mcp_ue
graph_ref, out = sys.argv[1], sys.argv[2]
res = mcp_ue.rpc("tools/call", {"name":"call_tool","arguments":{
    "toolset_name":"editor_toolset.toolsets.blueprint.BlueprintTools",
    "tool_name":"read_graph_dsl","arguments":{"graph":{"refPath":graph_ref}}}})
inner = res.get("result", res)["content"][0]["text"]
dsl = json.loads(inner)["returnValue"] if inner.lstrip().startswith("{") else inner
open(out,"w",encoding="utf-8").write(dsl)
print("wrote", out, len(dsl), "chars")
