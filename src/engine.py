import re
import cv2
import numpy as np
from PIL import Image

class TriageEngine:
    def __init__(self):
        # Heuristic keywords for categorization
        self.categories = {
            'Medical': ['bleeding', 'blood', 'hurt', 'injury', 'injured', 'pain', 'dying', 'death', 'unconscious', 'fainted', 'broke', 'broken', 'wound', 'heart attack', 'stroke', 'seizure'],
            'Rescue': ['trapped', 'stuck', 'flood', 'water rising', 'fire', 'burning', 'collapse', 'collapsed', 'rubble', 'buried', 'roof', 'sinking', 'stranded'],
            'Logistics': ['food', 'water', 'thirsty', 'hungry', 'shelter', 'blanket', 'cold', 'clothes', 'supplies', 'medicine', 'battery', 'power']
        }
        
        # Keywords specifically for high priority
        self.critical_keywords = ['dying', 'heavy bleeding', 'unconscious', 'trapped', 'fire', 'rising', 'now', 'immediately', 'emergency', 'critical']
        
        # Vulnerability flags
        self.vulnerable_keywords = ['pregnant', 'baby', 'child', 'infant', 'kid', 'elderly', 'senior', 'diabetic', 'insulin', 'injured', 'wheelchair', 'disabled', 'handicapped']

    def _analyze_text(self, text):
        if not text:
             return {
                'category': 'General',
                'priority': 'Low',
                'confidence': 0.0,
                'explanation': "No text provided.",
                'matched_keywords': [],
                'keyword_count': 0,
                'risk_flags': []
            }

        text_lower = text.lower()
        matched_keywords = []
        risk_flags = []
        
        for word in self.vulnerable_keywords:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                risk_flags.append(word)
        
        detected_categories = []
        for category, keywords in self.categories.items():
            for word in keywords:
                if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                    detected_categories.append(category)
                    matched_keywords.append(word)
                    
        final_category = detected_categories[0] if detected_categories else "General"
        if len(detected_categories) > 1:
            if 'Medical' in detected_categories:
                final_category = 'Medical'
            elif 'Rescue' in detected_categories:
                final_category = 'Rescue'

        hero_score = 0
        priority = 'Low'
        
        for word in self.critical_keywords:
             if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                 hero_score += 2
                 matched_keywords.append(word)
        
        # Count matched keywords
        detected_keywords_count = len(matched_keywords)
        hero_score += detected_keywords_count * 0.5

        if hero_score >= 2 or 'Medical' in detected_categories or 'Rescue' in detected_categories:
             priority = 'High'
        elif hero_score >= 1 or 'Logistics' in detected_categories:
             priority = 'Medium'
        
        if risk_flags:
            if priority == 'Low': priority = 'Medium'
            elif priority == 'Medium': priority = 'High'
            
        return {
            'category': final_category,
            'priority': priority,
            'confidence': 0.85 if priority == 'High' else 0.6,
            'explanation': f"Detected keywords: {', '.join(matched_keywords)}." if matched_keywords else "No specific keywords detected.",
            'matched_keywords': list(set(matched_keywords)),
            'keyword_count': len(set(matched_keywords)),
            'risk_flags': list(set(risk_flags))
        }

    def _analyze_image(self, image):
        # Convert PIL Image to OpenCV
        open_cv_image = np.array(image.convert('RGB')) 
        open_cv_image = open_cv_image[:, :, ::-1].copy() # BGR

        # 1. Darkness / Visibility
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        visibility = 'Daylight' if avg_brightness > 80 else 'Low Visibility (Night/Dark)'

        # 2. Flood Detection (HSV)
        hsv = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2HSV)
        
        # Muddy/Brown
        lower_mud = np.array([10, 40, 40])
        upper_mud = np.array([30, 255, 255])
        # Murky/Blue
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])

        mask_mud = cv2.inRange(hsv, lower_mud, upper_mud)
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        combined_mask = cv2.bitwise_or(mask_mud, mask_blue)
        
        height, width = combined_mask.shape
        total_pixels = height * width
        water_pixels = cv2.countNonZero(combined_mask)
        water_coverage = (water_pixels / total_pixels) * 100

        if water_coverage >= 35:
            flood_severity = 'Severe'
            image_priority = 'High'
        elif water_coverage >= 18:
            flood_severity = 'Moderate'
            image_priority = 'Medium'
        else:
            flood_severity = 'Low'
            image_priority = 'Low'

        # 3. Fire-like Region Detection
        # Red/Orange ranges
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        fire_mask = cv2.bitwise_or(mask_red1, mask_red2)
        
        fire_pixels = cv2.countNonZero(fire_mask)
        fire_ratio = (fire_pixels / total_pixels) * 100
        fire_risk = 'Detected' if fire_ratio > 2.0 else 'None'
        if fire_risk == 'Detected':
             image_priority = 'High' # Fire escalates priority

        # 4. Debris/Clutter (Edge Density)
        edges = cv2.Canny(gray, 100, 200)
        edge_pixels = cv2.countNonZero(edges)
        edge_density = (edge_pixels / total_pixels) * 100
        debris_risk = 'High' if edge_density > 15.0 else 'Low'

        return {
            'water_coverage': water_coverage,
            'flood_severity': flood_severity,
            'image_priority': image_priority,
            'visibility': visibility,
            'fire_risk': fire_risk,
            'debris_risk': debris_risk
        }

    def generate_serious_suggestions(self, result, text):
        immediate = []
        not_to_do = []
        checklist = []
        
        text_lower = text.lower() if text else ""
        
        # --- INPUTS ---
        priority = result.get('final_priority')
        category = result.get('final_category')
        img_res = result.get('image_result') or {}
        
        flood_sev = img_res.get('flood_severity', 'Low')
        vis = img_res.get('visibility', 'Daylight')
        fire = img_res.get('fire_risk', 'None')
        debris = img_res.get('debris_risk', 'Low')
        risk_flags = result.get('risk_flags', [])

        # --- LOGIC ---
        
        # 1. Fire
        if 'fire' in text_lower or fire == 'Detected':
            immediate.append("EVACUATE area immediately if safe paths exist.")
            immediate.append("Stay low to ground (crawl) to avoid smoke inhalation.")
            immediate.append("Check doors for heat before opening.")
            not_to_do.append("Do NOT use elevators.")
            not_to_do.append("Do NOT re-enter a burning building.")
            checklist.extend(['Wet cloth (for breathing)', 'Flashlight'])

        # 2. Flood
        elif 'flood' in text_lower or 'rising' in text_lower or flood_sev in ['Severe', 'Moderate']:
            immediate.append("Move to highest floor or roof immediately.")
            immediate.append("Disconnect gas and electricity mains if dry to do so.")
            not_to_do.append("Do NOT walk/drive through flood water (6 inches can knock you down).")
            not_to_do.append("Do NOT touch electrical equipment if wet.")
            checklist.extend(['Floatation devices', 'Waterproof bags for electronics', 'Whistle'])

        # 3. Medical / Injury
        elif category == 'Medical' or 'bleeding' in text_lower:
             immediate.append("Control bleeding with direct pressure.")
             immediate.append("Keep patient warm to prevent shock.")
             not_to_do.append("Do NOT remove objects impaled in wounds (stabilize them instead).")
             not_to_do.append("Do NOT give food/water to unconscious persons.")
             checklist.extend(['Clean bandages', 'Antiseptic', 'Thermal blanket'])

        # 4. Debris / Earthquake
        elif debris == 'High' or 'trapped' in text_lower or 'rubble' in text_lower:
             immediate.append("Protect head/neck with arms or pillows.")
             immediate.append("Signal presence with tapping (3 taps) or whistle.")
             not_to_do.append("Do NOT light matches (gas leak risk).")
             not_to_do.append("Do NOT shout continuously (conserves oxygen/dust inhalation).")

        # 5. Visibility
        if vis.startswith('Low'):
             immediate.append("Use flashlight or phone light sparingly.")
             not_to_do.append("Do NOT move blindly in dark debris-filled areas.")

        # 6. Vulernable Groups
        if risk_flags:
             immediate.append(f"Prioritize assistance for: {', '.join(risk_flags)}.")
             
        # General / Logistics
        if category == 'Logistics' and priority != 'High':
             immediate.append("Secure drinking water source.")
             immediate.append("Inventory food and warm clothing.")
             checklist.extend(['Water (1 gallon/person)', 'Canned food', 'Can opener'])

        # Defaults
        if not immediate:
             immediate.append("Stay calm and assess immediate surroundings.")
             immediate.append("Listen to battery-operated radio for news.")
        if not not_to_do:
             not_to_do.append("Do NOT rely on rumors.")
        if not checklist:
             checklist.extend(['Flashlight', 'Batteries', 'First Aid Kit', 'Water'])
             
        return {
            'immediate': list(set(immediate))[:5],
            'not_to_do': list(set(not_to_do))[:4],
            'checklist': list(set(checklist))[:5]
        }

    def predict(self, text, image=None):
        text_result = self._analyze_text(text)
        
        final_priority = text_result['priority']
        final_category = text_result['category']
        
        image_result = None
        if image:
            image_result = self._analyze_image(image)
            
            # Priority Escalation Logic
            priorities = ['Low', 'Medium', 'High']
            p_text_idx = priorities.index(text_result['priority'])
            p_img_idx = priorities.index(image_result['image_priority'])
            
            if p_img_idx > p_text_idx:
                final_priority = image_result['image_priority']
            
            # Category overrides
            if image_result['flood_severity'] == 'Severe':
                final_category = 'Rescue'
            elif image_result['fire_risk'] == 'Detected':
                final_category = 'Rescue'

        # Structure for generating suggestions
        combined_result = {
            'final_priority': final_priority,
            'final_category': final_category,
            'image_result': image_result,
            'risk_flags': text_result['risk_flags']
        }
        
        action_cards = self.generate_serious_suggestions(combined_result, text)

        return {
            'text_result': text_result,
            'image_result': image_result,
            'final_priority': final_priority,
            'final_category': final_category,
            'action_cards': action_cards,
            'risk_flags': text_result['risk_flags']
        }

