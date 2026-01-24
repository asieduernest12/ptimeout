#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "ptimeout"))

# Import the ptimeout module
import ptimeout

if __name__ == "__main__":
    print("Debug: sys.argv =", sys.argv)
    print("Debug: Before main()")
    try:
        ptimeout.main()
    except Exception as e:
        print(f"Exception: {e}")
        import traceback

        traceback.print_exc()
    print("Debug: After main()")
