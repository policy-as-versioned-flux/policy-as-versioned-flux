import sys, shutil
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
import engine_compatibility as ec
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
shutil.copytree(src, dst)
# run _matrix with a stub "binary" that does nothing; it rewrites files in place
for fam in ec.FAMILIES:
    ec._matrix(dst, '5.0.0', fam, '/usr/bin/true')
print('prepared', dst)
