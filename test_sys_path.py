import os
import sys
from pprint import pprint

from pylint import modify_sys_path

print(f"PYTHONPATH: '{os.environ.get('PYTHONPATH')}'")
pprint(sys.path)
print("--")
modify_sys_path()
pprint(sys.path)
