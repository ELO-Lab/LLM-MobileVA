generate_element_content_desc_tmpl = {
    "model_input": """
    You will be provided with a UI element image and csv properties including android_class, text, content_desc . Your task is to generate a description for the content_desc.
    ### Return only a string description 
    ### Example Usage:
    **UI element**
    android_class,text,content_desc
    android.widget.Button,Like,
    **Response:**
    "Like button"
""",
    "user_input": []
}
