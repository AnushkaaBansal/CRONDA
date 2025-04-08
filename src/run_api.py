import sys
from pathlib import Path

# Add the project root to Python path
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)