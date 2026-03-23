#!/usr/bin/env python3
"""
engi.py — Launcher for 縁起 ENGI: Feudal Japan Roguelike
"""
import sys
import os

# Ensure the game directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_requirements():
    import curses
    if sys.platform == "win32":
        try:
            import _curses
        except ImportError:
            print("ERROR: On Windows, install 'windows-curses':")
            print("  pip install windows-curses")
            sys.exit(1)
    # Check terminal size
    try:
        import shutil
        cols, rows = shutil.get_terminal_size()
        if cols < 100 or rows < 35:
            print(f"WARNING: Terminal is {cols}×{rows}.")
            print("Recommended minimum: 120×40 for best experience.")
            print("Press Enter to continue anyway, or Ctrl+C to resize first.")
            input()
    except:
        pass

def run():
    check_requirements()
    import curses
    from game import main
    curses.wrapper(main)

if __name__ == "__main__":
    run()
