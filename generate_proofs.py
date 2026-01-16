import time
import os
import cv2
import pyautogui
import numpy as np
from src.detector import IconDetector
import sys

def main():
    print("=========================================")
    print("   Generating Proof Screenshots (3x)     ")
    print("=========================================")
    
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    template_paths = [
        os.path.join(assets_dir, "notepad_icon_dark.png"),
        os.path.join(assets_dir, "notepad_icon_light.png")
    ]
    
    try:
        detector = IconDetector(template_paths)
    except Exception as e:
        print(f"[ERROR] Init failed: {e}")
        return

    print("Instructions:")
    print("This script will run 3 times to capture the icon in different locations.")
    print("Between each capture, you will have 8 seconds to move the icon.")
    
    for i in range(1, 4):
        print(f"\n--- Proof #{i} ---")
        print("Please move the Notepad icon to a new location now!")
        for k in range(8, 0, -1):
            print(f"{k}...", end=" ")
            sys.stdout.flush()
            time.sleep(1)
        print("\nCapturing...")
        
        # Capture
        screenshot = pyautogui.screenshot()
        img_np = np.array(screenshot)
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR) # OpenCV uses BGR
        
        # Detect
        best_match = None
        highest_val = -1
        
        for template in detector.templates:
            # We access protected member _multi_scale_match for annotation purposes
            try:
                match_val, match_loc, scale = detector._multi_scale_match(img_gray, template)
                if match_val > highest_val:
                    highest_val = match_val
                    best_match = (match_loc, scale, template.shape)
            except Exception as e:
                print(f"[WARN] Detection error: {e}")

        # Annotate & Save
        if best_match and highest_val > 0.8:
            (loc, scale, t_shape) = best_match
            t_h, t_w = t_shape
            
            top_left = loc
            bottom_right = (int(loc[0] + t_w * scale), int(loc[1] + t_h * scale))
            
            # Draw Red Box
            cv2.rectangle(img_bgr, top_left, bottom_right, (0, 0, 255), 3)
            # Draw Label
            label = f"Notepad ({highest_val:.2f})"
            cv2.putText(img_bgr, label, (top_left[0], top_left[1]-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            save_path = os.path.join(output_dir, f"proof_{i}.png")
            cv2.imwrite(save_path, img_bgr)
            print(f"[SUCCESS] Saved: {save_path}")
        else:
            print(f"[FAIL] Icon not found (Confidence: {highest_val:.2f})")

    print("\nAll proofs generated in 'output/' folder.")

if __name__ == "__main__":
    main()
