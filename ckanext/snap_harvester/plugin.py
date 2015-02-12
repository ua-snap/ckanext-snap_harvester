import logging
log = logging.getLogger(__name__)

from lxml import etree
import json

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.harvest.interfaces import IHarvester

from ckanext.spatial.harvesters.csw import CSWHarvester, text_traceback

import logging

from pprint import pprint

log = logging.getLogger(__name__)

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

        # Convert package extras to a dictionary to ease manipulation
        extras = {}
        for extra in package_dict['extras']:
            extras[extra['key']] = extra['value']

        # Will be a list of names.
        credits = tree.xpath('//gmd:credit/gco:CharacterString/text()', namespaces=namespaces)
        extras['credits'] = json.dumps(credits)

        # Will get two values, one for x and one for y; we can assume square pixels for the moment.
        spatial_resolution = tree.xpath('//gmd:spatialRepresentationInfo/gmd:MD_Georectified/gmd:axisDimensionProperties/gmd:MD_Dimension/gmd:resolution/gco:Angle/text()', namespaces=namespaces)[0]
        spatial_resolution_units = tree.xpath('//gmd:spatialRepresentationInfo/gmd:MD_Georectified/gmd:axisDimensionProperties/gmd:MD_Dimension/gmd:resolution/gco:Angle/@uom', namespaces=namespaces)[0]
        extras['spatial-resolution'] = spatial_resolution
        extras['spatial-resolution-units'] = spatial_resolution_units

        # The way we fetch temporal-start and temporal-end can be different from what the built-in xpath uses.
        temporal_extent_begin = tree.xpath('//gml:TimePeriod/gml:begin//gml:timePosition/text()', namespaces=namespaces)
        temporal_extent_end = tree.xpath('//gml:TimePeriod/gml:end//gml:timePosition/text()', namespaces=namespaces)
        if(temporal_extent_begin and temporal_extent_end):
            extras['temporal-extent-begin'] = temporal_extent_begin[0]
            extras['temporal-extent-end'] = temporal_extent_end = temporal_extent_end[0]

        # Rebuild the package extras as a list
        package_dict['extras'] = []
        for key, value in extras.iteritems():
            package_dict['extras'].append({'key': key, 'value': value})
        
        # Attach our CC license directly to package
        package_dict['license_title'] = 'Creative Commons Attribution'
        package_dict['license_id'] = 'CC-BY-NC-SA-3.0' # corresponds to licenses.json file
        package_dict['license_url'] = 'http://www.opendefinition.org/licenses/cc-by'
        package_dict['extras'].append({'key':'license', 'value':'Attribution-NonCommercial-ShareAlike 3.0 Unported'})
        package_dict['extras'].append({'key':'license_url', 'value':'http://creativecommons.org/licenses/by-nc-sa/3.0/'})

        return package_dict
