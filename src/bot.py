import pyautogui
import time
import os
import ctypes

class AutomationBot:
    """
    Handles all desktop interactions: mouse movement, clicking, typing.
    Includes robust safety mechanisms and focus validation.
    """
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1  # Optimized for speed (was 0.5)

    def _get_active_window_title(self):
        """Helper to get the active window title safely."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            return buff.value
        except Exception as e:
            print(f"[WARN] Error getting window title: {e}")
            return ""

    def _wait_for_window(self, title_part: str, timeout: int = 5) -> bool:
        """Waits for a window with the given title part to become active."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            active_title = self._get_active_window_title()
            if title_part in active_title:
                return True
            time.sleep(0.1) # Faster polling
        print(f"[WARN] Timeout waiting for window containing '{title_part}'")
        return False

    def minimize_all_windows(self):
        """Minimizes all windows to show the desktop."""
        print("[BOT] Minimizing all windows to reveal desktop...")
        pyautogui.hotkey('win', 'd')
        time.sleep(1.0)  # Faster animation wait

    def double_click(self, coords):
        """Moves to coordinates and double clicks."""
        x, y = coords
        print(f"[BOT] Double clicking at ({x}, {y})")

        pyautogui.moveTo(x, y, duration=0.2) # Faster Move
        pyautogui.doubleClick()
        
        # Verify it opened
        print("[BOT] Waiting for Notepad to open...")
        if self._wait_for_window("Notepad", timeout=5):
            print("[BOT] Notepad verified open.")
        else:
            print("[WARN] Notepad might not have opened correctly.")
        
        # No extra sleep needed if verified

    def type_content(self, title: str, body: str):
        """
        Types the formatted content into the active window.
        Verifies window focus first.
        """
        # Strict Verification
        if not self._wait_for_window("Notepad", timeout=3):
             print(f"[WARN] Notepad not focus! Typing might be unsafe. Aborting type.")
             return

        print("[BOT] Typing content...")
        
        # Type Title
        pyautogui.write(f"Title: {title}", interval=0.005) # Super fast typing
        pyautogui.press('enter')
        pyautogui.press('enter')
        
        # Type Body
        pyautogui.write(body, interval=0.005)
        
    def save_and_close(self, filename: str):
        """
        Saves the file to specific path and closes Notepad.
        Strategy: Try to delete existing file first to force a 'Clean Save'.
        """
        print(f"[BOT] Saving as: {filename}")
        
        # Verify focus before starting save sequence
        if not self._wait_for_window("Notepad", timeout=3):
            print("[ERROR] Lost focus before saving! Aborting save action for safety.")
            return
        
        # 0. Pre-Cleanup: Delete file if it strictly exists to avoid "Overwrite?" dialog
        need_ui_overwrite = False
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print("[BOT] Removed existing file to ensure clean save.")
            except Exception as e:
                print(f"[WARN] Could not delete existing file ({e}). Will handle overwrite in UI.")
                need_ui_overwrite = True
        
        # 1. Trigger Save Dialog
        pyautogui.hotkey('ctrl', 's')
        time.sleep(0.5)  # Fast wait for dialog
        
        # 2. Type full path
        pyautogui.write(filename, interval=0.005)
        time.sleep(0.2)
        
        # 3. Confirm Save (First Enter)
        pyautogui.press('enter')
        time.sleep(0.5) # Fast save
        
        # 4. Close Application (Safely)
        print("[BOT] Closing application...")
        
        # Try to close up to 3 times for robustness
        for attempt in range(3):
            # Check for Notepad OR "Save As" (stuck dialog)
            if self._wait_for_window("Notepad", timeout=0.5) or self._wait_for_window("Save As", timeout=0.5):
                 # Explicit Key Press (More reliable than hotkey sometimes)
                pyautogui.keyDown('alt')
                pyautogui.press('f4')
                pyautogui.keyUp('alt')
                time.sleep(0.5) # Fast Wait for reaction
            else:
                 print("[BOT] Notepad does not appear to be active. Assuming closed.")
                 break
            
            # Verify if gone
            time.sleep(0.2)
            active_title = self._get_active_window_title()
            if "Notepad" not in active_title and "Save As" not in active_title:
                print("[BOT] Application closed successfully.")
                break
            else:
                print(f"[BOT] Window still open (Attempt {attempt+1}/3)... retrying.")
        
        # 5. Reset Mouse (Prevent occlusion for next run)
        self.move_mouse_to_safe_zone()

    def move_mouse_to_safe_zone(self):
        """Moves mouse to the right side of the screen to avoid obscuring icons."""
        screen_w, screen_h = pyautogui.size()
        safe_x = screen_w - 50
        safe_y = screen_h // 2
        print(f"[BOT] Moving mouse to safe zone ({safe_x}, {safe_y})...")
        pyautogui.moveTo(safe_x, safe_y, duration=0.5)
