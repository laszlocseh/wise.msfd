import logging
import os
import tempfile
from collections import defaultdict

import requests

import sparql
from eea.cache import cache
from wise.msfd import db, sql, sql_extra

from .utils import timeit

logger = logging.getLogger('wise.msfd')


@db.use_db_session('2012')
def all_regions():
    """ Return a list of region ids
    """

    return db.get_unique_from_mapper(
        sql_extra.MSFD4GeographicalAreaID,
        'RegionSubRegions'
    )


@db.use_db_session('2012')
def countries_in_region(regionid):
    """ Return a list of (<countryid>, <marineunitids>) pairs
    """
    t = sql_extra.MSFD4GeographicalAreaID

    return db.get_unique_from_mapper(
        t,
        'MemberState',
        t.RegionSubRegions == regionid
    )


@db.use_db_session('2012')
def muids_by_country():
    t = sql_extra.MSFD4GeographicalAreaID
    count, records = db.get_all_records(t)
    res = defaultdict(list)

    for rec in records:
        res[rec.MemberState].append(rec.MarineUnitID)

    return dict(**res)


@db.use_db_session('2012')
def _get_report_filename_art10_2012(country, region, article, descriptor):
    mc = sql.MSFD10Import

    count, item = db.get_item_by_conditions(
        mc,
        'MSFD10_Import_ID',
        mc.MSFD10_Import_ReportingCountry == country,
        mc.MSFD10_Import_ReportingRegion == region
    )

    # TODO: analyse cases when it returns more then one file

    if count != 1:
        logger.warning("Could not find precise report (count %s) "
                       "filename for %s %s %s", country, region, article,)

        raise ValueError

        # return None

    return item.MSFD10_Import_FileName


@db.use_db_session('2012')
def _get_report_filename_art9_2012(country, region, article, descriptor):
    mc = sql.MSFD9Import

    count, item = db.get_item_by_conditions(
        mc,
        'MSFD9_Import_ID',
        mc.MSFD9_Import_ReportingCountry == country,
        mc.MSFD9_Import_ReportingRegion == region
    )

    # TODO: analyse cases when it returns more then one file

    if count != 1:
        logger.warning("Could not find report filename for %s %s %s",
                       country, region, article,)

        return None

    return item.MSFD9_Import_FileName


def _get_report_filename_art8_2012(country, region, article, descriptor):
    d = descriptor.split('.')[0]

    if d in ['D1', 'D4', 'D6']:
        base = 'MSFD8a'
    else:
        base = 'MSFD8b'

    mc = getattr(sql, base + 'Import')
    idcol = base + '_Import_ID'
    filecol = base + '_Import_FileName'
    countrycol = getattr(mc, base + '_Import_ReportingCountry')
    regcol = getattr(mc, base + '_Import_ReportingRegion')

    count, item = db.get_item_by_conditions(
        mc,
        idcol,
        countrycol == country,
        regcol == region
    )

    # TODO: analyse cases when it returns more then one file

    if count != 1:
        logger.warning("Could not find report filename for %s %s %s",
                       country, region, article,)

        return None

    return getattr(item, filecol)


def get_report_filename(report_version,
                        country, region, article, descriptor):
    """ Return the filename for imported information

    :param report_version: report "version" year: 2012 or 2018
    :param country: country code, like: 'LV'
    :param region: region code, like: 'ANS'
    :param article: article code, like: 'art9'
    :param descriptor: descriptor code, like: 'D5'
    """

    # 'Art8': '8b',       # TODO: this needs to be redone for descriptor
    mapping = {
        '2012': {
            'Art8': _get_report_filename_art8_2012,
            'Art9': _get_report_filename_art9_2012,
            'Art10': _get_report_filename_art10_2012,
        }
    }

    handler = mapping[report_version][article]

    return handler(country, region, article, descriptor)


@cache(lambda func, filename: func.__name__ + filename)
@timeit
def get_report_file_url(filename):
    """ Retrieve the CDR url based on query in ContentRegistry
    """

#     q = """
# PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# PREFIX cr: <http://cr.eionet.europa.eu/ontologies/contreg.rdf#>
# PREFIX dc: <http://purl.org/dc/dcmitype/>
# PREFIX dcterms: <http://purl.org/dc/terms/>
#
# SELECT ?file
# WHERE {
# ?file a dc:Dataset .
# ?file dcterms:date ?date .
# FILTER regex(str(?file), '%s')
# }
# ORDER BY DESC(?date)
# LIMIT 1""" % filename

    q = """
PREFIX cr: <http://cr.eionet.europa.eu/ontologies/contreg.rdf#>
PREFIX terms: <http://purl.org/dc/terms/>

SELECT ?file
WHERE {
?file terms:date ?date .
?file cr:mediaType 'text/xml'.
FILTER regex(str(?file), '%s')
}
ORDER BY DESC(?date)
LIMIT 1""" % filename

    service = sparql.Service('https://cr.eionet.europa.eu/sparql')

    logger.info("Getting filename with SPARQL: %s", filename)
    try:
        req = service.query(q)
        rows = req.fetchall()

        urls = []

        for row in rows:
            url = row[0].value
            splitted = url.split('/')

            filename_from_url = splitted[-1]

            if filename == filename_from_url:
                urls.append(url)

        assert len(urls) == 1
    except:
        logger.exception('Got an error in querying SPARQL endpoint for '
                         'filename url: %s', filename)

        raise

    return urls[0]


@cache(lambda func, url: func.__name__ + url)
def get_factsheet_url(url):
    """ Returns the URL for the conversion that gets the "HTML Factsheet"
    """
    cdr = "http://cdr.eionet.europa.eu/Converters/run_conversion"\
        "?source=remote&file="

    base = url.replace('http://cdr.eionet.europa.eu/', '')
    base = base.replace('https://cdr.eionet.europa.eu/', '')

    resp = requests.get(url + '/get_possible_conversions')
    j = resp.json()
    ids = [x
           for x in j['remote_converters']

           if x['description'] == 'HTML Factsheet']

    if ids:
        return '{}{}&conv={}'.format(cdr, base, ids[0]['convert_id'])


@timeit
def get_xml_report_data(filename):
    if not filename:
        return ""

    xmldir = os.environ.get("MSFDXML")

    if not xmldir:
        xmldir = tempfile.gettempdir()

    assert '..' not in filename     # need better security?

    fpath = os.path.join(xmldir, filename)

    text = ''

    if filename in os.listdir(xmldir):
        with open(fpath) as f:
            text = f.read()

    if not text:
        # TODO: handle this problem:
        # https://cr.eionet.europa.eu/factsheet.action?uri=http%3A%2F%2Fcdr.eionet.europa.eu%2Fro%2Feu%2Fmsfd8910%2Fblkro%2Fenvux97qw%2FRO_MSFD10TI_20130430.xml&page1=http%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23type
        url = get_report_file_url(filename)
        req = requests.get(url)
        text = req.content
        logger.info("Requesting XML file: %s", fpath)

        with open(fpath, 'wb') as f:
            f.write(text)
    else:
        logger.info("Using cached XML file: %s", fpath)

    assert text, "Report data could not be fetched %s" % url

    return text


@db.use_db_session('2012')
def country_ges_components(country_code):
    """ Get the assigned ges components for a country
    """

    t = sql.t_MSFD_19a_10DescriptiorsCriteriaIndicators
    count, res = db.get_all_records(
        t,
        t.c.MemberState == country_code,
    )

    cols = t.c.keys()
    recs = [
        {
            k: v for k, v in zip(cols, row)
        } for row in res
    ]

    return list(set([c['Descriptors Criterion Indicators'] for c in recs]))
