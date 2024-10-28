import os
import time
import xml.etree.ElementTree as ET

def swipe(x1, y1, x2, y2, duration=200):
    os.system("adb shell input swipe %d %d %d %d %d" % (x1, y1, x2, y2, duration))

def swipe_up():
    width, height = get_screen_size()
    swipe(width//2, height*3//4, width//2, height//4)

def swipe_down():
    width, height = get_screen_size()
    swipe(width//2, height//4, width//2, height*3//4)

def swipe_left():
    width, height = get_screen_size()
    swipe(width*3//4, height//2, width//4, height//2)

def swipe_right():
    width, height = get_screen_size()
    swipe(width//4, height//2, width*3//4, height//2)

def tap(x, y):
    print(f"tapping {x} {y}")
    os.system("adb shell input tap %d %d" % (x, y))

def keyevent(key):
    os.system("adb shell input keyevent %d" % key)

viet_char_map = {
    'à': 'af', 'á': 'as', 'ả': 'ar', 'ã': 'ax', 'ạ': 'aj',
    'â': 'aa', 'ầ': 'aaf', 'ấ': 'aas', 'ẩ': 'aar', 'ẫ': 'aax', 'ậ': 'aaj',
    'ă': 'aw', 'ằ': 'awf', 'ắ': 'aws', 'ẳ': 'awr', 'ẵ': 'awx', 'ặ': 'awj',
    'è': 'ef', 'é': 'es', 'ẻ': 'er', 'ẽ': 'ex', 'ẹ': 'ej',
    'ê': 'ee', 'ề': 'eef', 'ế': 'ees', 'ể': 'eer', 'ễ': 'eex', 'ệ': 'eej',
    'ì': 'if', 'í': 'is', 'ỉ': 'ir', 'ĩ': 'ix', 'ị': 'ij',
    'ò': 'of', 'ó': 'os', 'ỏ': 'or', 'õ': 'ox', 'ọ': 'oj',
    'ô': 'oo', 'ồ': 'oof', 'ố': 'oos', 'ổ': 'oor', 'ỗ': 'oox', 'ộ': 'ooj',
    'ơ': 'ow', 'ờ': 'owf', 'ớ': 'ows', 'ở': 'owr', 'ỡ': 'owx', 'ợ': 'owj',
    'ù': 'uf', 'ú': 'us', 'ủ': 'ur', 'ũ': 'ux', 'ụ': 'uj',
    'ư': 'uw', 'ừ': 'uwf', 'ứ': 'uws', 'ử': 'uwr', 'ữ': 'uwx', 'ự': 'uwj',
    'ỳ': 'yf', 'ý': 'ys', 'ỷ': 'yr', 'ỹ': 'yx', 'ỵ': 'yj',
    'đ': 'dd',
    'À': 'Af', 'Á': 'As', 'Ả': 'Ar', 'Ã': 'Ax', 'Ạ': 'Aj',
    'Â': 'Aa', 'Ầ': 'Aaf', 'Ấ': 'Aas', 'Ẩ': 'Aar', 'Ẫ': 'Aax', 'Ậ': 'Aaj',
    'Ă': 'Aw', 'Ằ': 'Awf', 'Ắ': 'Aws', 'Ẳ': 'Awr', 'Ẵ': 'Awx', 'Ặ': 'Awj',
    'È': 'Ef', 'É': 'Es', 'Ẻ': 'Er', 'Ẽ': 'Ex', 'Ẹ': 'Ej',
    'Ê': 'Ee', 'Ề': 'Eef', 'Ế': 'Ees', 'Ể': 'Eer', 'Ễ': 'Eex', 'Ệ': 'Eej',
    'Ì': 'If', 'Í': 'Is', 'Ỉ': 'Ir', 'Ĩ': 'Ix', 'Ị': 'Ij',
    'Ò': 'Of', 'Ó': 'Os', 'Ỏ': 'Or', 'Õ': 'Ox', 'Ọ': 'Oj',
    'Ô': 'Oo', 'Ồ': 'Oof', 'Ố': 'Oos', 'Ổ': 'Oor', 'Ỗ': 'Oox', 'Ộ': 'Ooj',
    'Ơ': 'Ow', 'Ờ': 'Owf', 'Ớ': 'Ows', 'Ở': 'Owr', 'Ỡ': 'Owx', 'Ợ': 'Owj',
    'Ù': 'Uf', 'Ú': 'Us', 'Ủ': 'Ur', 'Ũ': 'Ux', 'Ụ': 'Uj',
    'Ư': 'Uw', 'Ừ': 'Uwf', 'Ứ': 'Uws', 'Ử': 'Uwr', 'Ữ': 'Uwx', 'Ự': 'Uwj',
    'Ỳ': 'Yf', 'Ý': 'Ys', 'Ỷ': 'Yr', 'Ỹ': 'Yx', 'Ỵ': 'Yj',
    'Đ': 'Dd'
}

def convert_vietnamese(text):
    result = []
    for char in text:
        if char in viet_char_map:
            result.append(viet_char_map[char])
        else:
            result.append(char)
    return ''.join(result)

def input_text(text):
    text = convert_vietnamese(text)
    words = text.split()
    space = " "
    for word in words:
        os.system(f"""adb shell "input text '{word}'" """)
        os.system(f"""adb shell "input text '{space}'" """)
    os.system("adb shell input keyevent 23")  # ok key event

def screen_on():
    os.system("adb shell input keyevent 26")

def screen_off():
    os.system("adb shell input keyevent 26")

def get_screen_size():
    result = os.popen("adb shell wm size").read()
    result = result.strip().split(":")[-1].strip()
    width, height = result.split("x")
    return int(width), int(height)

def list_apps():
    result = os.popen("adb shell pm list packages").read()
    return result.split()

def close_app(app):
    os.system(f"adb shell am force-stop {app}")

def open_app(app):
    os.system(f"adb shell monkey -p {app} -c android.intent.category.LAUNCHER 1")

def take_screenshot(output_file="screen.png"):
    os.system("adb shell screencap -p /sdcard/screen.png")
    os.system(f"adb pull /sdcard/screen.png {output_file}")

def generate_unique_id(element, id_prefix="elem", start_id=1):
    """Generate unique ID for each element in the XML tree."""
    for i, elem in enumerate(element.iter(), start=start_id):
        elem.set("id", f"{id_prefix}_{i}")
    return element

def dump_ui(output_file="window_dump.xml"):
    os.system("adb shell uiautomator dump")
    os.system(f"adb pull /sdcard/window_dump.xml {output_file}")
    
    # Read and parse the XML file
    tree = ET.parse(output_file)
    root = tree.getroot()
    
    # Generate unique IDs for each element
    generate_unique_id(root)
    
    # Write the updated XML back to the file
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    
    # Read the output file and return its content
    with open(output_file, "r", encoding="utf-8") as f:
        return str(f.read())


def main():
    # input_text("xin chào các bạn")
    # print(get_bounds())
    # print(get_screen_size()) # (1080, 2340) /
    # tap(870.0, 198.0)
    # 870.0 198.0
    # time.sleep(2)
    # time.sleep(2)
    # take_screenshot("zalo.png")
    print(list_apps())

if __name__ == "__main__":
    main()
