common_input = """
Given the following inputs:
1. **Request**: The user request that needs to be completed.
    Example: 
    ```
    "Complete the registration process."
    ```
2. **Current UI Elements**: A CSV list with the following properties:
    - `index`: The index of the UI element
    - `android_class`: The Android class of the UI element (e.g., `Button`, `TextView`)
    - `resource_id`: The unique identifier for the UI element
    - `text`: The text displayed on the UI element
    - `content_desc`: The content description of the UI element
    - `x1`, `y1`: The coordinates of the top-left corner of the UI element
    - `x2`, `y2`: The coordinates of the bottom-right corner of the UI element
    Example:
    ```
    index,android_class,text,content_desc,x1,y1,x2,y2
    0,Button,Submit,submit_button,100,200,300,400
    1,TextView,Welcome,description_welcome,50,100,200,150
    ```
3. **Previous Actions**: A CSV list of previous executed actions:
    - `screen_desc`: The screen description of the screen acted upon 
    - `content_desc`: The content description of the UI element acted upon
    - `action`: The action performed (e.g., `click`, `input`)
    - `data`: Any data associated with the action
    Example:
    ```
    screen_desc,content_desc,action,data
    register screen,name_field,input,John Doe
    register screen,email_field,input,john.doe@example.com
    ```
"""

result_description = """
Based on the inputs, determine the next action to take and return the result in JSON format with the following structure. Don't add any additional information to the response.:
```json
{
    "index": "<index of the UI element to act on, if need to action on sreen then index will be -1 >",
    "action": "<action to perform (tap, input, swipe_up, swipe_down, swipe_left, swipe_right, answer, return)>",
    "additional_data": "<additional data required for the action>"
    "completed": "boolean to indicate if the flow is completed or not after this action"
}
```
**Notes:
    1.If action is "input", the additional_data field should contain the information required for the input action. 
    2.If the flow is completed after the action, the completed field should be set to true. 
    3.If the flow is completed and no action is required to be performed, the action field should be set to "return". 
    4.If the action is "answer", the additional_data field should contain the answer to the question from request.
"""

identifying_next_execute_action_tmpl = {
    "model_input": common_input + """
4. **Similar flow guide**: A list of similar flows with the following properties: 
    - `flow description`: The description of the flow
    - `steps`: The steps to complete the flow in csv format with the following properties:
        - `screen_desc`: The description of the screen
        - `user_guide`: The user guide to complete the step
        - `element_content_desc`: The description of the element content
        - `action`: The action to perform
    Example: 
    ```
    [
        {
            "flow_description": "Complete the registration process.",
            "steps": [
                "Registration screen,Enter name,name_field,input",
                "Confirmation screen,Click submit button,submit_button,tap",
            ]
        }
    ]
    ```
""" + result_description,
    "user_input": []
}


identifying_next_execute_action_with_only_user_guide_tmpl = {
    "model_input": common_input + """
4. **User guide**: The user guides from similar flows that can be used to complete the request. 
    Example: 
    ```
    [ 
        ["Enter name","Click submit button"],
        ["Enter name","Click submit button"]
    ]
    ```
""" + result_description,
    "user_input": []
}

identifying_next_execute_action_with_only_similar_flow_tmpl = {
    "model_input": common_input + """
4. **Similar flow guide**: A list of similar flows with the following properties: 
    - `flow description`: The description of the flow
    - `steps`: The steps to complete the flow in csv format with the following properties:
        - `screen_desc`: The description of the screen
        - `element_content_desc`: The description of the element content
        - `action`: The action to perform
    Example: 
    ```
    [
        {
            "flow_description": "Complete the registration process.",
            "steps": [
                "Registration screen,name_field,input",
                "Confirmation screen,submit_button,tap",
            ]
        }
    ]
    ```
""" + result_description,
    "user_input": []
}

indentifying_next_execute_action_with_only_current_screen_tmpl = {
    "model_input": common_input + result_description,
    "user_input": []
}
