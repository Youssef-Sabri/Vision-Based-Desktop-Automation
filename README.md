# Vision-Based Desktop Automation 🤖

A robust, computer-vision powered automation agent designed to dynamically locate and interact with desktop applications (Notepad). This project demonstrates advanced techniques in GUI grounding, resilience engineering, and screen parsing without relying on hardcoded coordinates.

## 🚀 Key Features

*   **Dynamic Grounding ("ReGround" Strategy)**: Implements a two-stage detection pipeline (Coarse-to-Fine) inspired by the *ScreenSpot-Pro* research paper to locate icons anywhere on the screen with high precision.
*   **Theme & Resolution Agnostic**: Capable of detecting icons in both **Light** and **Dark** modes and varying screen resolutions using Multi-Scale Template Matching.
*   **Resilience First**: Built with self-healing capabilities:
    *   **Network Fallback**: Automatically switches to mock data if the API is unreachable (Offline Mode).
    *   **Visual Retry Logic**: Exponential backoff detection if the screen is actively changing.
*   **High-Speed Performance**: Optimized for low-latency execution (0.1s input delay) with dynamic polling to eliminate unnecessary waits.
*   **Advanced Safety Gates**:
    *   **Strict Focus Control**: Aborts actions immediately if window focus is lost.
    *   **Clean Saving Strategy**: Uses a "Delete-First" approach to ensure idempotent file saving without "Overwrite?" popups.
    *   **Auto-Minimization**: Clears the desktop (`Win+D`) at startup to ensure a clean visual field.
*   **Modern Python Stack**: Managed efficiently with `uv` for lightning-fast dependency resolution.

## 🛠️ Architecture

The system operates on a closed-loop control cycle:
1.  **Sense**: Captures the desktop state and analyzes it using OpenCV.
2.  **Plan**: Identifies the target application (Notepad) using the ReGround logic.
3.  **Act**: Executes precise mouse and keyboard events to launch the app and input data.
4.  **Verify**: Validates actions and handles external API data fetching.

## 📦 Installation

This project uses `uv` for dependency management.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd TJM_Labs
    ```

2.  **Install dependencies:**
    ```bash
    # This will create a virtual environment and install all locked packages
    uv sync
    ```

3.  **Asset Setup:**
    Ensure your `assets/` folder contains the reference templates:
    *   `notepad_icon_light.png`
    *   `notepad_icon_dark.png`

## 💻 Usage

### Run the Automation
To execute the primary workflow (Fetch 10 posts -> Type into Notepad -> Save):

```bash
uv run main.py
```

### Generate Proof of Concept
To verify the computer vision system separately (generates 3 annotated screenshots):

```bash
uv run generate_proofs.py
```

## 📂 Project Structure

```
TJM_Labs/
├── src/
│   ├── detector.py       # Core Vision Logic (ReGround implementation)
│   ├── bot.py            # Automation & Interaction Logic
│   └── api.py            # Data Fetching & Error Handling
├── assets/               # Reference Icon Templates
├── output/               # Generated Proofs & Logs (Ignored by Git)
├── main.py               # Application Entry Point
├── pyproject.toml        # Dependency Configuration
└── README.md             # Documentation
```

## 🔬 Technical Details

**The "ReGround" Approach:** 
Instead of scanning the entire high-resolution desktop for every frame which is computationally expensive and prone to false positives, specific "Region of Interest" (ROI) proposal techniques are adaptable. In this implementation, we utilize optimized multi-scale matching to simulating the robust visual grounding agents described in state-of-the-art UI navigation literature.

