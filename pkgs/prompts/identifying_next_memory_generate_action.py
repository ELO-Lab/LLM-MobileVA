identifying_next_memory_generate_action_tmpl = {
    "model_input": """
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
3. **User's Guide**: A string that guides how to complete the next action.
    Example: 
    ```
    "Enter password"
    ```
4. **Previous Actions**: A CSV list of previous executed actions:
    - `content_desc`: The content description of the UI element acted upon
    - `action`: The action performed (e.g., `click`, `input`)
    - `data`: Any data associated with the action
    Example:
    ```
    content_desc,action,data
    name_field,input,John Doe
    email_field,input,john.doe@example.com
    ```
Based on the inputs, determine the next action to take and return the result in JSON format with the following structure. Don't add any additional information to the response.:
```json
{
    "index": "<index of the UI element to act on, if need to action on sreen then index will be -1 >",
    "action": "<action to perform (tap, input, swipe_up, swipe_down, swipe_left, swipe_right, answer, return)>",
    "additional_data": "<additional data required for the action>"
}
```
**Notes:
    1.If action is "input", the additional_data field should contain the information required for the input action. 
    2.If the action is "answer", the additional_data field should contain the answer to the question from request.
""",
    "user_input": []
}
