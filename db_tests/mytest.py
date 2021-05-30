
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from website.models import Metrics

estac = Metrics.query.filter_by(name="Estacionamentos")
wifi = Metrics.query.filter_by(name="Wifi Users")
print(estac)
print(wifi)