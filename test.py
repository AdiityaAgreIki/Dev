import cv2
import pytesseract
import re
from PIL import Image
import json


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image_path):
    """
    Loads and preprocesses the image for better OCR accuracy.
    Includes grayscaling, deskewing, and binarization.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    return img, gray  # Return original img and the preprocessed binary for OCR

def ocr_region(image_cv, x, y, w, h, config='--psm 6'):
    """
    Performs OCR on a specified region of the image.
    :param image_cv: OpenCV image (binary preprocessed).
    :param x, y, w, h: Coordinates and dimensions of the region.
    :param config: Tesseract configuration string (e.g., PSM modes).
                   --psm 6: Assume a single uniform block of text.
                   --psm 7: Treat the image as a single text line.
                   --psm 8: Treat the image as a single word.
    :return: Extracted text.
    """
    cropped_img = image_cv[y:y + h, x:x + w]
    # Convert OpenCV image (NumPy array) to PIL Image for pytesseract
    pil_img = Image.fromarray(cropped_img)
    text = pytesseract.image_to_string(pil_img, config=config)
    return text.strip()

def extract_header(processed_img):
    """Extracts title and date from the header."""
    header_data = {}
    # Coordinates for the header area (approximate, adjust as needed)
    # Title
    title_text = ocr_region(processed_img, 100, 30, 800, 70, config='--psm 6')
    header_data["report_title"] = title_text if "report" in title_text.lower() else "Body composition analysis report"
    # # Date and Time
    date_time_text = ocr_region(processed_img, 100, 80, 800, 50, config='--psm 7')
    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', date_time_text)
    if match:
        header_data["report_date"] = match.group(0)
    else:
        header_data["report_date"] = date_time_text  # Keep raw text if not perfectly matched

    return header_data


def extract_basic_data(processed_img):
    """Extracts data from the 'Basic data' section."""
    basic_data = {}
    # Name, Gender, Height, Age
    user_info_text = ocr_region(processed_img, 70, 150, 800, 70, config='--psm 6')
    # print("user_info_text:", user_info_text)
    name_match = re.search(r'Name:(\w+)', user_info_text)
    if name_match: basic_data["name"] = name_match.group(1)
    gender_match = re.search(r'Gender:(\w+)', user_info_text)
    if gender_match: basic_data["gender"] = gender_match.group(1)
    height_match = re.search(r'height: (\d+)cm', user_info_text)
    if height_match: basic_data["height_cm"] = int(height_match.group(1))
    age_match = re.search(r'Age:(\d+)', user_info_text)
    if age_match: basic_data["age"] = int(age_match.group(1))

    # Current Weight and Change
    weight_text_area = ocr_region(processed_img, 25, 290, 200, 100, config='--psm 6')
    basic_data["current_weight"] = weight_text_area.strip()

    change_text = ocr_region(processed_img, 240, 340, 200, 50, config='--psm 6')

    match = re.search(r'(increase|decrease)(\d+\.\d+)kg', change_text, re.IGNORECASE)
    if match:
        direction = match.group(1).lower()  # "increase" or "decrease"
        value = float(match.group(2))  # Numeric value

        basic_data["weight_change"] = {"direction": direction, "value": value}


    # BMI, Body Fat, Muscle Rate
    indicators = ["BMI", "Body fat perc", "Muscle rate"]
    y_offset = 420  # Starting Y coordinate for these indicators
    for i, indicator in enumerate(indicators):
        row_text = ocr_region(processed_img, 30, y_offset + i * 35, 500, 35, config='--psm 6')

        value_match = re.search(r'(\d+\.\d+)', row_text)
        # print(value_match)
        # status_match = re.search(r'(Standard|Little high|Little low|Excellent|Insufficient)', row_text, re.IGNORECASE)
        value = float(value_match.group(1)) if value_match else None

        key_name = indicator.lower().replace(" ", "_").replace("perc", "percentage")
        basic_data[key_name] = {"value": value}

    return basic_data

def extract_body_composition_analysis(processed_img):
    """Extracts data from the 'Body composition analysis' section (top right)."""
    analysis_data = {}
    rows = ["Fat Mass", "Moisture", "Protein a", "Bone mass"]
    y_offset = 300
    for i, row_name in enumerate(rows):
        row_text = ocr_region(processed_img, 600, y_offset + i * 50, 180, 50, config='--psm 7')

        value_match = re.search(r'(\d+\.\d+)(%|kg)', row_text)
        # status_match = re.search(r'(Standard|Excellent|Insufficient|Little high|Little low)', row_text, re.IGNORECASE)
        #
        value = float(value_match.group(1)) if value_match else None
        unit = value_match.group(2) if value_match else None
        # status = status_match.group(1) if status_match else None
        #
        key_name = row_name.lower().replace(" ", "_") # protein alpha
        analysis_data[key_name] = {"value": value, "unit": unit}

    return analysis_data


def extract_weight_control(processed_img):
    """Extracts data from the 'Weight control' section (middle left)."""
    weight_control_data = {}
    rows = ["Current weight", "Standard weight", "Muscle mass", "Lean body mass", "Weight control"]
    y_offset = 650
    for i, row_name in enumerate(rows):
        row_text = ocr_region(processed_img, 20, y_offset + i * 35, 400, 40, config='--psm 7')
        value_match = re.search(r'(\d+\.\d+)\s*kg', row_text)
        value = float(value_match.group(1)) if value_match else None
        weight_control_data[row_name.lower().replace(" ", "_") + "_kg"] = value

    return weight_control_data


def extract_body_type(processed_img):
    """Extracts data from the 'Body type' section (middle right)."""
    body_type_data = {}

    # Overall type (e.g., Overweight)
    overall_type_text = ocr_region(processed_img, 620, 580, 200, 40,config='--psm 6')

    body_type_data["overall"] = overall_type_text


    return body_type_data

def extract_other_indicators(processed_img):
    """Extracts data from the 'Other indicators' sections (bottom left and right)."""
    other_indicators_data = {}

    # Left table
    left_indicators = [
        ("BMR", r'(\d+)', r'(\d+-\d+)'),
        ("Visceral fat level", r'(\d+)', r'(\d+-\d+)'),
        ("Subcutaneous fat level", r'(\d+)', r'(\d+-\d+)'),
    ]
    y_offset = 960
    for i, (name, val_regex, ref_regex) in enumerate(left_indicators):
        row_text = ocr_region(processed_img, 20, y_offset + i * 40, 250, 50, config='--psm 7')
        value = None
        val_match =re.search(r'(\d+\.\d+|\d+|Biased|Standard)', row_text)
        if val_match:
            try:
                value =  val_match.group(1)
            except ValueError:
                pass  # Keep as None if conversion fails
        key_name = name.lower().replace(" ", "_")
        other_indicators_data[key_name] = {"value": value}


    # # Right table
    right_indicators = [
        ("Body age", r'(\d+)', r'(\d+-\d+)'),
        ("Obesity rating", r'(Biased|Standard)', r'(Biased|Standard)'),  # OCR might pick "Standard" from Reference
        ("Protein rate", r'(\d+\.\d+)%', r'(\d+\.\d+-\d+\.\d+)')
    ]
    y_offset = 960
    for i, (name, val_regex, ref_regex) in enumerate(right_indicators):
        row_text = ocr_region(processed_img, 450, y_offset + i * 40, 250, 50, config='--psm 7')
        value = None
        val_match = re.search(r'(\d+\.\d+|\d+|Biased|Standard)', row_text)
        if val_match:
            try:
                value = val_match.group(1)
            except ValueError:
                pass

        key_name = name.lower().replace(" ", "_")
        other_indicators_data[key_name] = {"value": value}
    return other_indicators_data

# Load the image using PIL
def main(image_path="diet.jpg"):
    """
    Main function to orchestrate the image extraction.
    """
    try:
        original_img, processed_img = preprocess_image(image_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure 'image.png' is in the same directory as the script.")
        return {}

    full_report_data = {}

    print("Extracting Header...")
    full_report_data.update(extract_header(processed_img))
    print("Extracting Basic Data...")
    full_report_data["basic_data"] = extract_basic_data(processed_img)
    print("Extracting Body Composition Analysis...")
    full_report_data["body_composition_analysis"] = extract_body_composition_analysis(processed_img)
    print("Extracting Weight Control Data...")
    full_report_data["weight_control"] = extract_weight_control(processed_img)
    print("Extracting Body Type Data...")
    full_report_data["body_type"] = extract_body_type(processed_img)
    print("Extracting Other Indicators...")
    full_report_data["other_indicators"] = extract_other_indicators(processed_img)



    return full_report_data


if __name__ == "__main__":
    extracted_json_data = main("diet.jpg")
    if extracted_json_data:
        print("\n--- Extracted JSON Data ---")
        print(json.dumps(extracted_json_data, indent=2, ensure_ascii=False))

        # You can save this to a file
        with open("extracted_report.json", "w", encoding="utf-8") as f:
            json.dump(extracted_json_data, f, indent=2, ensure_ascii=False)
        print("\nData saved to extracted_report.json")