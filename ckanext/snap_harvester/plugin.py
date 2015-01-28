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
            "gml": "http://www.opengis.net/gml/3.2",
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
        credits = tree.xpath('//gmd:credit/gco:CharacterString/text()', namespaces=namespaces)

        package_dict['extras'].append(
            {'key': 'credits', 'value': json.dumps(credits)}
        )
        package_dict['extras'].append(
            {'key': 'temporal-extent-begin', 'value': iso_values.get('temporal-extent-begin')}
        )
        package_dict['extras'].append(
            {'key': 'temporal-extent-end', 'value': iso_values.get('temporal-extent-end')}
        )

        return package_dict

