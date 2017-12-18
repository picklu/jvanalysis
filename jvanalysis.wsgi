import sys
sys.stdout = sys.stderr
sys.path.insert(0, '/home/ubuntu/jvanalysis')

import envvar
from jvanalysis import app as application
