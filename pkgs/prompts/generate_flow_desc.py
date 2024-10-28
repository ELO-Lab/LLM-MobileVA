generate_flow_desc_tmpl = {
    "model_input": """
        create a 100-word summary of the flow based on the given properties:

        1. **Request**: The user request that needs to be completed.
        Example: 
        ```
        "Complete the registration process."
        ```
        2. **Steps**: The steps that need to be completed to fulfill the user request(in csv format). 
        Example: 
        ```
        screen_desc,user_guide,element_content_desc,action
        Registration screen,Enter name,name_field,input
        Confirmation screen,Click submit button,submit_button,tap
        ```

        ### Return only a string description:
        "A 100-word summary of the flow"
""",
    "user_input": []
}
