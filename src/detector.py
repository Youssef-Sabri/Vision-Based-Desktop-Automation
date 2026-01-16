import cv2
import numpy as np
import pyautogui
import time
from typing import Optional, Tuple, List
import os

class IconDetector:
    """
    Implements a robust computer vision system to locate icons on the desktop.
    Uses a 'ReGround' strategy (Coarse-to-Fine) and Multi-Scale Matching.
    """
    
    def __init__(self, template_paths: List[str]):
        """
        Args:
            template_paths: List of absolute paths to icon template images (Light/Dark).
        """
        self.templates = []
        for path in template_paths:
            if os.path.exists(path):
                # Read as grayscale
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    self.templates.append(img)
                else:
                    print(f"[WARN] Failed to load template: {path}")
            else:
                print(f"[WARN] Template not found: {path}")
                
        if not self.templates:
            raise ValueError("No valid icon templates loaded. Check 'assets/' folder.")

    def find_icon(self, retries: int = 3) -> Optional[Tuple[int, int]]:
        """
        Locates the icon on the screen.
        
        Returns:
            (x, y) center coordinates or None if not found.
        """
        for attempt in range(1, retries + 1):
            try:
                # 1. Capture Screenshot
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
                
                # 2. ReGround Strategy: Coarse -> Fine
                # Since we don't have a neural network "Global Planner" like the paper,
                # we treat the Global Search as a standard multi-scale match on a 
                # downscaled image to find the ROI quickly.
                
                # However, for a single icon on a 1080p screen, a direct optimized 
                # multi-template match is often fast enough. 
                # To stick to the "ReGround" spirit, we will implement the robust
                # multi-scale match which essentially searches everywhere.
                
                best_match = None
                highest_val = -1
                
                # Iterate through all loaded templates (Light/Dark)
                for template in self.templates:
                    match_val, match_loc, scale = self._multi_scale_match(screenshot, template)
                    if match_val > highest_val:
                        highest_val = match_val
                        best_match = (match_loc, scale, template.shape)
                
                # Threshold
                if best_match and highest_val > 0.8:
                    (loc, scale, t_shape) = best_match
                    t_h, t_w = t_shape
                    
                    # Calculate Center
                    # loc is topleft
                    center_x = int(loc[0] + (t_w * scale) / 2)
                    center_y = int(loc[1] + (t_h * scale) / 2)
                    
                    print(f"[VISION] Found icon! Conf: {highest_val:.2f} at ({center_x}, {center_y})")
                    return (center_x, center_y)
                
            except Exception as e:
                print(f"[VISION] Error during detection: {e}")
            
            print(f"[VISION] Icon not found. Retrying ({attempt}/{retries})...")
            time.sleep(1)
            
        return None

    def _multi_scale_match(self, image, template):
        """
        Performs template matching at multiple scales.
        Returns (best_val, best_loc, best_scale)
        """
        best_val = -1
        best_loc = (0, 0)
        best_scale = 1.0
        
        img_h, img_w = image.shape
        t_h, t_w = template.shape
        
        # Scales to check: 80% to 120% size
        scales = np.linspace(0.8, 1.2, 10)
        
        for scale in scales:
            # Resize template (better than resizing large image)
            # OR Resize image? Resizing template is faster but less accurate if upscaling too much.
            # Usually resizing image is safer for "finding varied sizes". 
            # Let's resize the template for speed if scale is close to 1.
            
            new_w = int(t_w * scale)
            new_h = int(t_h * scale)
            
            if new_w > img_w or new_h > img_h:
                continue
                
            resized_template = cv2.resize(template, (new_w, new_h))
            
            # Match
            res = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_scale = scale
                
        return best_val, best_loc, best_scale
