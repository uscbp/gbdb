from __future__ import unicode_literals
import math
from .conf import settings

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^geoposition\.fields\.GeopositionField"])
except ImportError:
    pass

#def compute_distance(lat1, lon1, lat2, lon2, unit):
#    radlat1=math.pi*lat1/180.0
#    radlat2=math.pi*lat2/180.0
#    theta=lon1-lon2
#    radtheta=math.pi*theta/180.0
#    dist=math.sin(radlat1)*math.sin(radlat2)+math.cos(radlat1)+math.cos(radlat2)*math.cos(radtheta)
#    dist=math.acos(dist)
#    dist=dist*180/math.pi
#    dist=dist*60*1.515
#    if unit=='K':
#        dist *= 1.609344
#    return dist

def compute_distance(lat1, lon1, lat2, lon2):
    r = 6371; # km
    phi1 = math.pi*lat1/180.0
    phi2 = math.pi*lat2/180.0
    delta_phi = math.pi*(lat2-lat1)/180.0
    delta_lambda = math.pi*(lon2-lon1)/180.0

    a = math.sin(delta_phi/2.0) * math.sin(delta_phi/2.0) + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2.0) * math.sin(delta_lambda/2.0)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1-a));
    return r * c