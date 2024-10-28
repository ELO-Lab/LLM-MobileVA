# AI-phone-assistant

## Project Overview

**AI-phone-assistant** is an intelligent automation system developed to interact with and test mobile applications. This system leverages the power of large language models (LLM) such as OpenAI's GPT and Google's Gemini to perform various automation tasks, including:

- **Remote Control of Android Devices**: Perform actions such as swiping, tapping, text input, and controlling applications based on the user interface.
- **Application Identification**: Use LLMs to identify applications and determine the appropriate actions based on user requests.
- **Workflow Memory and Description**: Create and store memory for application workflows, optimizing the automation and testing process.
- **User Interface Analysis and Interaction**: Process and extract information from the user interface to perform automated tasks.
- **Integration with LLM APIs**: Send requests and process results from APIs to support automation and testing tasks.

## Installation Instructions

To install and run this project, follow these steps:

1. **Clone the Repository**
```bash
git clone git@github.com:pkna-2407/LLM-MobileVA.git
```

2. **Install Dependencies**

Ensure you have Python 3.7 or higher installed. Run the following command to install the necessary libraries from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

3. **Setup adb**

Make sure you have `adb` installed. Then add the adb platform-tools path to the end of the virtual environment's active.bat file. The path structure is as follows:

```text
@set PATH=%PATH%;{Disk}:path\to\platform-tools
```
## Usage Examples

Here are some examples of how to use the **AI-phone-assistant** for various automation tasks:

### Example: Automating Application Launch and Interaction

This example demonstrates how to automate the process of launching an application, performing actions, and capturing the results.

1. **Start the API Server**

   Before running the automation script, start the FastAPI server:
   
```python
python api.py
```
2. **Run the run_excecutor.py**

After the server is running, you can execute the automation script. For example, to open the settings application and perform a series of interactions:

```bash
python run_excecutor.py
```
<h3>Check the api server </h3>

`check_health` function will check if the api server is up and running. If not, you have to go back to step `1. Start the API Server`.

Example: 
```python
# check health of the system
    if not check_health():
        print("System is not healthy")
        return 
    
## None: if api-server turned on
## end process: if api-server turned off
```

<h3> Find app fit for user's request </h3>

`identify_app` function takes a user request. For example: "Watch tiktok". The result is the app that matches the user's request.

Example:
```python
apps = identify_app(user_request)
print(apps)

## ['Tiktok']
```

<h3> Find similar flow </h3>

After finding the app name. We need to map them with the name of the package containing the flows of that app. Then we find the json containing the corresponding flows based on the function `similar_flows`.

Example:
```python
app = map_app_name_to_package[apps[0]]
    # get similar flows  
    similar_flows_ids = similar_flows(app, request)
    print(similar_flows_ids)

##  ['0322a58f-18b3-4f26-85ce-d08606c4f722', '5f89e49d-b2af-4748-9bbb-7c6130b8eee9']
```

<h3> Interact with the app </h3>

Interact with the app by performing different actions (typing, tapping, swiping, etc.) based on the app's current state and previous actions

1. **Open the specified app**

```python
open_app(app)
```

This line opens the application specified by the app variable. The open_app function can be used to launch the application on the device or on the emulator.

2.**Get action information**

```python
element_position, action, completed, additional_data, element_content_desc = get_action(
    app, 
    request, 
    similar_flows_ids, 
    previous_action)
```

This line calls the `get_action` function, which analyzes the current state of the app and returns the next action to take. The return values ​​include:

- **element_position**: The coordinate on the screen where the action (such as a touch) will be performed.

- **action**: The type of action to take (e.g. "input", "tap", "swipe").

- **completed**: A flag indicating whether the action is complete.

- **additional_data**: Additional data required for the action.

- **element_content_desc**: A description of the UI element associated with the action.

3. **Take action**

```python
if action == "input":
    data = input(f"Input {additional_data}: ")
    tap(element_position[0], element_position[1])
    time.sleep(0.5)
    input_text(data)
if action == "tap" or action == "click":
    tap(element_position[0], element_position[1])
if action == "swipe_up":
    swipe_up()
if action == "swipe_down":
    swipe_down()
if action == "swipe_left":
    swipe_left()
if action == "swipe_right":
    swipe_right()
if action == "return":
    break
```

Depending on the type of action returned from `get_action`, different blocks of code will be executed:

- If the action is "input", the script will ask the user for input.
- The script will then tap a specified location on the screen, wait half a second, and then enter text.
- If the action is "tap" or "click", the script will tap a specified location on the screen.
- Depending on the action, the script will perform a swipe in the specified direction.
- If the action is "return", the script will exit the loop, ending the interaction.


4. **Sumary full loop action**

```python
open_app(app)
    while True:
        # take screen shot and get screen description 
        # get next action
        element_position, action, completed, additional_data, element_content_desc = get_action(
            app, 
            request, 
            similar_flows_ids, 
            previous_action)
        data = ""
        if action == "input":
            data = input(f"Input {additional_data}: ")
            tap(element_position[0], element_position[1])
            time.sleep(0.5)
            input_text(data)
        if action == "tap" or action == "click":
            tap(element_position[0], element_position[1])
        if action == "swipe_up":
            swipe_up()
        if action == "swipe_down":
            swipe_down()
        if action == "swipe_left":
            swipe_left()
        if action == "swipe_right":
            swipe_right()
        if action == "return":
            break

        previous_action += f"{element_content_desc},{action},{data}\n"
        if completed:
            break

        step_count += 1 
        if step_count > 5:
            break
        # wait for the action to complete
        time.sleep(2)
```

<h4> Code Summary </h4>

The automation code interacts with an app by performing actions based on the current state:

1. **Open the app** using the `open_app(app)` function.

2. **Main loop** checks and performs actions:

- Calls the `get_action` function to determine the next action.

- Performs an action such as input, tap, swipe, or ends the loop if the action is "return" or the number of steps exceeds 5.

3. **Updates the state** after each action and pauses for 2 seconds to let the app respond.

The loop ends when the action completes or the step limit is exceeded.
