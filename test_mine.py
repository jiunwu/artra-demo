import sys
sys.path.append('backend')
from pmc import mine_pmc_text

try:
    print(mine_pmc_text())
except Exception as e:
    print("Exception:", e)
