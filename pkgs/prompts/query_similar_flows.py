query_similar_flows_tmpl = {
    "model_input": """
Given the following inputs:
1. **Request**: The user request that needs to be completed.
    Example: 
    ```
    "Complete the registration process."
    ```
2. **Flows**: A CSV list with the following properties:
    - `flow_desc`: The description of the flow 
    - `user_request`: The user request that the flow fulfills 
    Each row represents a flow.
    Example:
    ```
    flow_desc,user_request
    Registration process,Complete the registration process
    ```
Based on the input request, determine flows index that could match the user request(maximum 10 index) and return the result in csv format with the following structure. 
If there are no similar flows, return -1.
Don't add any additional information to the response. 
Example response that have similar flows: 
```csv
0,3,5
```
Example response that have no flows:
```csv
-1 
```
    """,
    "user_input": []
}
