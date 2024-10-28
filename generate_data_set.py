from control_phone import take_screenshot, dump_ui
import uuid

if __name__ == "__main__":
    save_path = input("Enter save path: \n")
    while True:
        input("Press enter to take screenshot and dump UI")
        id = str(uuid.uuid4())
        print(id)
        take_screenshot(save_path + f"/screen_{id}.png")
        dump_ui(save_path + f"/window_dump_{id}.xml")
        print("Screenshot and UI dump saved")
