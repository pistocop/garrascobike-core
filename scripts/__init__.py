import sys
import pathlib
from os.path import join

#  Used to import `garrascobike` code
working_dir = pathlib.Path().absolute()
src_dir = join(working_dir, "garrascobike")
sys.path.insert(0, src_dir)
