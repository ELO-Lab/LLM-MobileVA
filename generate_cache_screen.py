import os
from pkgs import NewLLMExecutor, Executor,  screen_from_api_data
import argparse
import os
from dotenv import load_dotenv
import jsonpickle

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--dataset", help="Dataset folder")
parser.add_argument("-f", "--force", help="Force to generate cache", type=bool, default=False)

args = parser.parse_args()

load_dotenv()
llm_executor = NewLLMExecutor(os.getenv("LLM_MODEL"))
args = parser.parse_args()

def generate_cache_screen(dataset_folder):
    for app in os.listdir(dataset_folder):
        app_folder = os.path.join(dataset_folder, app)
        if os.path.isdir(app_folder):
            for flow_name in os.listdir(app_folder):
                flow_folder = os.path.join(app_folder, flow_name)
                if os.path.isdir(flow_folder):
                    # for each xml file in the flow folder
                    for xml_file in os.listdir(flow_folder):
                        if xml_file.endswith(".xml"):
                            # extract id 
                            id = xml_file.split("_")[2].split(".")[0]
                            if not os.path.exists(flow_folder + f"/screen_{id}.json") or args.force:
                                # generate cache description 
                                screen = screen_from_api_data(
                                    app,
                                    flow_folder + f"/screen_{id}.png", 
                                    flow_folder + f"/window_dump_{id}.xml", 
                                    llm_executor )
                                save_path = flow_folder + f"/screen_{id}.json"
                                with open(save_path, "w") as f:
                                    f.write(jsonpickle.encode(screen))
                                    print(f"screen saved to file: {save_path}")

if __name__ == "__main__":
    generate_cache_screen(args.dataset)

