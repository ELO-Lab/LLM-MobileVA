from pkgs.flow import Flow
import json

with open('flows_data.json', 'r', encoding="utf-8") as file:
    json_data = json.load(file)

flows = Flow.load_flows_json(json_data)

for flow in flows:
    print(f"Flow: {flow.user_request}, {flow.flow_desc}\n")