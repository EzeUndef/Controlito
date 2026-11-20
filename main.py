"""Entry point for Controlito."""
import sys
import os

# Add project root directory to sys.path so modules are resolved cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app import ControlitoApp

def main():
    app = ControlitoApp()
    app.mainloop()

if __name__ == "__main__":
    main()
