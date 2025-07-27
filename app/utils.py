import cv2
import pytesseract
import re
from PIL import Image

class ReportExtractor:
    def __init__(self):
        pass

    def preprocess_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img, gray

    def ocr_region(self, image_cv, x, y, w, h, config='--psm 6'):
        cropped_img = image_cv[y:y + h, x:x + w]
        pil_img = Image.fromarray(cropped_img)
        text = pytesseract.image_to_string(pil_img, config=config)
        return text.strip()

    def extract_header(self, processed_img):
        header_data = {}
        title_text = self.ocr_region(processed_img, 100, 30, 800, 70, config='--psm 6')
        header_data["report_title"] = title_text if "report" in title_text.lower() else "Body composition analysis report"
        date_time_text = self.ocr_region(processed_img, 100, 80, 800, 50, config='--psm 7')
        match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', date_time_text)
        if match:
            header_data["report_date"] = match.group(0)
        else:
            header_data["report_date"] = date_time_text
        return header_data

    def extract_basic_data(self, processed_img):
        basic_data = {}
        user_info_text = self.ocr_region(processed_img, 70, 150, 800, 70, config='--psm 6')
        name_match = re.search(r'Name:(\w+)', user_info_text)
        if name_match: basic_data["name"] = name_match.group(1)
        gender_match = re.search(r'Gender:(\w+)', user_info_text)
        if gender_match: basic_data["gender"] = gender_match.group(1)
        height_match = re.search(r'height: (\d+)cm', user_info_text)
        if height_match: basic_data["height_cm"] = int(height_match.group(1))
        age_match = re.search(r'Age:(\d+)', user_info_text)
        if age_match: basic_data["age"] = int(age_match.group(1))
        weight_text_area = self.ocr_region(processed_img, 25, 290, 200, 100, config='--psm 6')
        basic_data["current_weight"] = weight_text_area.strip()
        change_text = self.ocr_region(processed_img, 240, 340, 200, 50, config='--psm 6')
        match = re.search(r'(increase|decrease)(\d+\.\d+)kg', change_text, re.IGNORECASE)
        if match:
            direction = match.group(1).lower()
            value = float(match.group(2))
            basic_data["weight_change"] = {"direction": direction, "value": value}
        indicators = ["BMI", "Body fat perc", "Muscle rate"]
        y_offset = 420
        for i, indicator in enumerate(indicators):
            row_text = self.ocr_region(processed_img, 30, y_offset + i * 35, 500, 35, config='--psm 6')
            value_match = re.search(r'(\d+\.\d+)', row_text)
            value = float(value_match.group(1)) if value_match else None
            key_name = indicator.lower().replace(" ", "_").replace("perc", "percentage")
            basic_data[key_name] = {"value": value}
        return basic_data

    def extract_body_composition_analysis(self, processed_img):
        analysis_data = {}
        rows = ["Fat Mass", "Moisture", "Protein a", "Bone mass"]
        y_offset = 300
        for i, row_name in enumerate(rows):
            row_text = self.ocr_region(processed_img, 600, y_offset + i * 50, 180, 50, config='--psm 7')
            value_match = re.search(r'(\d+\.\d+)(%|kg)', row_text)
            value = float(value_match.group(1)) if value_match else None
            unit = value_match.group(2) if value_match else None
            key_name = row_name.lower().replace(" ", "_")
            analysis_data[key_name] = {"value": value, "unit": unit}
        return analysis_data

    def extract_weight_control(self, processed_img):
        weight_control_data = {}
        rows = ["Current weight", "Standard weight", "Muscle mass", "Lean body mass", "Weight control"]
        y_offset = 650
        for i, row_name in enumerate(rows):
            row_text = self.ocr_region(processed_img, 20, y_offset + i * 35, 400, 40, config='--psm 7')
            value_match = re.search(r'(\d+\.\d+)\s*kg', row_text)
            value = float(value_match.group(1)) if value_match else None
            weight_control_data[row_name.lower().replace(" ", "_") + "_kg"] = value
        return weight_control_data

    def extract_body_type(self, processed_img):
        body_type_data = {}
        overall_type_text = self.ocr_region(processed_img, 620, 580, 200, 40, config='--psm 6')
        body_type_data["overall"] = overall_type_text
        return body_type_data

    def extract_other_indicators(self, processed_img):
        other_indicators_data = {}
        left_indicators = [
            ("BMR", r'(\d+)', r'(\d+-\d+)'),
            ("Visceral fat level", r'(\d+)', r'(\d+-\d+)'),
            ("Subcutaneous fat level", r'(\d+)', r'(\d+-\d+)'),
        ]
        y_offset = 960
        for i, (name, val_regex, ref_regex) in enumerate(left_indicators):
            row_text = self.ocr_region(processed_img, 20, y_offset + i * 40, 250, 50, config='--psm 7')
            value = None
            val_match = re.search(r'(\d+\.\d+|\d+|Biased|Standard)', row_text)
            if val_match:
                try:
                    value = val_match.group(1)
                except ValueError:
                    pass
            key_name = name.lower().replace(" ", "_")
            other_indicators_data[key_name] = {"value": value}
        right_indicators = [
            ("Body age", r'(\d+)', r'(\d+-\d+)'),
            ("Obesity rating", r'(Biased|Standard)', r'(Biased|Standard)'),
            ("Protein rate", r'(\d+\.\d+)%', r'(\d+\.\d+-\d+\.\d+)')
        ]
        y_offset = 960
        for i, (name, val_regex, ref_regex) in enumerate(right_indicators):
            row_text = self.ocr_region(processed_img, 450, y_offset + i * 40, 250, 50, config='--psm 7')
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

    def extract_report(self, image_path):
        try:
            original_img, processed_img = self.preprocess_image(image_path)
        except FileNotFoundError as e:
            raise Exception(str(e))
        full_report_data = {}
        full_report_data.update(self.extract_header(processed_img))
        full_report_data["basic_data"] = self.extract_basic_data(processed_img)
        full_report_data["body_composition_analysis"] = self.extract_body_composition_analysis(processed_img)
        full_report_data["weight_control"] = self.extract_weight_control(processed_img)
        full_report_data["body_type"] = self.extract_body_type(processed_img)
        full_report_data["other_indicators"] = self.extract_other_indicators(processed_img)
        return full_report_data


# Convenience function for easy import and use
def extract_report(image_path):
    """
    Convenience function to extract report data from an image.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Extracted report data
    """
    extractor = ReportExtractor()
    return extractor.extract_report(image_path)