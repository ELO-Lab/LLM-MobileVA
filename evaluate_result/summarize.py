import argparse
import json

def print_result_app(result):
    for app in result:
        print(f"App: {app}")
        print(f"Total action: {result[app]['total_action']}")
        print(f"Total correct action: {result[app]['total_correct_action']}")
        print(f"Total tap action: {result[app]['total_tap_action']}")
        print(f"Total correct tap action: {result[app]['total_correct_tap_action']}")
        print(f"Total input action: {result[app]['total_input_action']}")
        print(f"Total correct input action: {result[app]['total_correct_input_action']}")
        print(f"Total swipe action: {result[app]['total_swipe_action']}")
        print(f"Total correct swipe action: {result[app]['total_correct_swipe_action']}")
        print(f"Overall accuracy: {result[app]['total_correct_action'] / result[app]['total_action']}")
        print(f"Tap accuracy: {result[app]['total_correct_tap_action'] / result[app]['total_tap_action']}")
        print(f"Input accuracy: {result[app]['total_correct_input_action'] / result[app]['total_input_action']}")
        print(f"Swipe accuracy: {result[app]['total_correct_swipe_action'] / result[app]['total_swipe_action']}")
    print("=====================================\n")


def print_result_all(result):
    total_action = 0
    total_correct_action = 0
    total_tap_action = 0
    total_correct_tap_action = 0
    total_input_action = 0
    total_correct_input_action = 0
    total_swipe_action = 0
    total_correct_swipe_action = 0
    for app in result:
        total_action += result[app]['total_action']
        total_correct_action += result[app]['total_correct_action']
        total_tap_action += result[app]['total_tap_action']
        total_correct_tap_action += result[app]['total_correct_tap_action']
        total_input_action += result[app]['total_input_action']
        total_correct_input_action += result[app]['total_correct_input_action']
        total_swipe_action += result[app]['total_swipe_action']
        total_correct_swipe_action += result[app]['total_correct_swipe_action']
        total_flow = result[app]['total_flows']
        total_success_flow = result[app]['total_sucessful_flows']

    print(f"Total action: {total_action}")
    print(f"Total correct action: {total_correct_action}")
    print(f"Total tap action: {total_tap_action}")
    print(f"Total correct tap action: {total_correct_tap_action}")
    print(f"Total input action: {total_input_action}")
    print(f"Total correct input action: {total_correct_input_action}")
    print(f"Total swipe action: {total_swipe_action}")
    print(f"Total correct swipe action: {total_correct_swipe_action}")
    print(f"Overall accuracy: {total_correct_action / total_action}")
    print(f"Tap accuracy: {total_correct_tap_action / total_tap_action}")
    print(f"Input accuracy: {total_correct_input_action / total_input_action}")
    print(f"FRC: {total_success_flow / total_flow }")
    if total_swipe_action == 0:
        print(f"Swipe accuracy: 0")
    else:
        print(f"Swipe accuracy: {total_correct_swipe_action / total_swipe_action}")
    print("=====================================\n")

def main():
    # Parse arguments
    # models = ["gpt-4o", "gpt-4o-mini", "gemini-flash"]
    models = ["gpt-4o","gpt-4o-mini"]
    for model_name in models:
        # Load result
        # _no_user_guide_no_memory =  json.load(open(f"result_{model_name}_no_user_guide_no_memory.json"))
        # _no_user_guide =  json.load(open(f"result_{model_name}_no_user_guide.json"))
        # _no_memory =  json.load(open(f"result_{model_name}_no_memory.json"))
        full =  json.load(open(f"result_{model_name}.json"))

    #     # Summarize
    #     print("Summary")
    #     print("=====================================")
    #     print("Without memory and user guide")
    #     print_result_app(_no_user_guide_no_memory)
    #     
    #     print("=====================================")
    #     print("Without memory")
    #     print_result_app(_no_memory)
    # 
    #     print("=====================================")
    #     print("Without user guide")
    #     print_result_app(_no_user_guide)
    # 
    #     print("=====================================")
    #     print("With memory and user guide")
    #     print_result_app(full)
    
        # summarize sum app
    #     print(f"Summary for model {model_name}")
    #     print("=====================================")
    #     print("Without memory and user guide")
    #     print_result_all(_no_user_guide_no_memory)
    # 
    #     print("=====================================")
    #     print("Without memory")
    #     print_result_all(_no_memory)
    # 
    #     print("=====================================")
    #     print("Without user guide")
    #     print_result_all(_no_user_guide)
    
        print("=====================================")
        print("With memory and user guide")
        print_result_all(full)


if __name__ == "__main__":
    main()
