identify_app_tmpl = {
"model_input": """
Input:
App List: A list of available apps (e.g., "Tiktok, Shopee, Youtube, XanhSM, Facebook").
Request: The user's request (e.g., "I want to watch a video.").
Task: Identify the relevant app(s) from the list based on the user's request. Return the result in JSON format:
{
    "apps": ["Youtube", "Tiktok"]
}
No additional information should be included in the response.
""",
    "user_input": []
}
