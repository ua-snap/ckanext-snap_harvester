import logging
log = logging.getLogger(__name__)

from lxml import etree
import json

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.harvest.interfaces import IHarvester

from ckanext.spatial.harvesters.csw import CSWHarvester, text_traceback
from pprint import pprint

class SnapHarvester(CSWHarvester, SingletonPlugin):

    implements(IHarvester)

    def info(self):
        return {
            'name': 'SNAP',
            'title': 'SNAP GeoNetwork instance',
            'description': 'Imports from GeoNetwork via CSW, pulling in more fields than default'
        }

    def get_package_dict(self, iso_values, harvest_object):

        namespaces = {
            "gts": "http://www.isotc211.org/2005/gts",
            "gml": "http://www.opengis.net/gml",
            "gmx": "http://www.isotc211.org/2005/gmx",
            "gsr": "http://www.isotc211.org/2005/gsr",
            "gss": "http://www.isotc211.org/2005/gss",
            "gco": "http://www.isotc211.org/2005/gco",
            "gmd": "http://www.isotc211.org/2005/gmd",
            "srv": "http://www.isotc211.org/2005/srv",
            "xlink": "http://www.w3.org/1999/xlink",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }

        package_dict = super(SnapHarvester, self).get_package_dict(iso_values, harvest_object)

        tree = etree.fromstring(harvest_object.content)

        # Will be a list of names.
        credits = tree.xpath('//gmd:credit/gco:CharacterString/text()', namespaces=namespaces)

        # Will get two values, one for x and one for y; we can assume square pixels for the moment.
        spatial_resolution = tree.xpath('//gmd:spatialRepresentationInfo/gmd:MD_Georectified/gmd:axisDimensionProperties/gmd:MD_Dimension/gmd:resolution/gco:Angle/text()', namespaces=namespaces)[0]
        spatial_resolution_units = tree.xpath('//gmd:spatialRepresentationInfo/gmd:MD_Georectified/gmd:axisDimensionProperties/gmd:MD_Dimension/gmd:resolution/gco:Angle/@uom', namespaces=namespaces)[0]

        package_dict['extras'].append(
            {'key': 'credits', 'value': json.dumps(credits)}
        )
        package_dict['extras'].append(
            {'key': 'spatial-resolution', 'value': spatial_resolution}
        )
        package_dict['extras'].append(
            {'key': 'spatial-resolution-units', 'value': spatial_resolution_units}
        )

        return package_dict

