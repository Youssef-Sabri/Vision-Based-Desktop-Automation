import os
import time
from src.api import ContentFetcher
from src.detector import IconDetector
from src.bot import AutomationBot

def main():
    print("=========================================")
    print(" Vision-Based Desktop Automation System  ")
    print("=========================================")
    
    # 1. Configuration
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    output_base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "tjm-project")
    
    # Ensure output directory exists
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Load Templates (Light & Dark)
    template_paths = [
        os.path.join(assets_dir, "notepad_icon_dark.png"),
        os.path.join(assets_dir, "notepad_icon_light.png")
    ]
    
    # 2. Initialize Components
    try:
        # Using standard timeout (5s) for real API
        api = ContentFetcher()
        detector = IconDetector(template_paths)
        bot = AutomationBot()
        print("[INIT] System initialized successfully.")
        
        # 3. Setup Environment
        bot.minimize_all_windows()
    except Exception as e:
        print(f"[FATAL] Initialization failed: {e}")
        return

    # 3. Main Loop (10 Iterations)
    for i in range(1, 11):
        print(f"\n--- Processing Post #{i} ---")
        
        try:
            # A. Fetch Data
            post = api.get_post(i)
            if not post:
                print(f"[WARN] API failed. Using MOCK data for iteration {i} to verify automation.")
                post = {
                    "title": f"Mock Title {i} (Offline)",
                    "body": f"This is a mock body for post {i} because the API was unreachable.\nAutomation logic is still being verified."
                }
                
            title = post.get("title", "No Title")
            body = post.get("body", "No Body")
            
            # B. Grounding (Find Notepad)
            # Minimizing windows? Ideally user keeps desktop visible. 
            # We can't easily "minimize all" without potentially hiding our own console if not careful.
            # Assuming user keeps Notepad icon visible as per instructions.
            
            coords = detector.find_icon()
            if not coords:
                print(f"[FAIL] Could not locate Notepad icon for iteration {i}.")
                continue
            
            # C. Interact
            bot.double_click(coords)
            
            # D. Write Content
            bot.type_content(title, body)
            
            # E. Save and Close
            filename = os.path.join(output_base_dir, f"post_{i}.txt")
            bot.save_and_close(filename)
            
            print(f"[SUCCESS] Completed Post {i}.")
            
            # Small pause before next iteration to let windows close/animations finish
            time.sleep(2)
            
        except Exception as e:
            print(f"[ERROR] Exception during iteration {i}: {e}")
            # Failsafe: Try to close app if stuck?
            # bot.close_app() # Risky if focus lost
            
    print("\n=========================================")
    print("           Workflow Complete             ")
    print("=========================================")

if __name__ == "__main__":
    main()
