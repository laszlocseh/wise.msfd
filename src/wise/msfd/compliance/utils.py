import lxml.etree
from pkg_resources import resource_filename


definition_files = {
    '2018': 'data/report_2018_def.xml',
    '2012': 'data/report_2012_def.xml',
}


class ReportDefinition(object):
    """ Parser class for a XML report definition file.

    For 2018, use report_2018_def.xml, for 2012 use report_2012_def.xml
    """

    def __init__(self, year, article):
        labels_file = resource_filename(
            'wise.msfd',
            definition_files[year]
        )
        self.article = article
        self.doc = lxml.etree.parse(labels_file)
        self.nodes = self.doc.find(self.article).getchildren()

    def get_elements(self):
        return self.nodes

    def get_group_by_fields(self):
        res = [
            x.get('name')

            for x in self.nodes

            if x.attrib.get('exclude', 'false') == 'true'
        ]

        return res

    def get_translatable_fields(self):
        res = [
            x.get('name')

            for x in self.nodes

            if x.attrib.get('translate', 'false') == 'true'
        ]

        return res


REPORT_DEFS = {
    '2018': {
        'Art8': ReportDefinition('2018', 'Art8'),
        'Art9': ReportDefinition('2018', 'Art9'),
        'Art10': ReportDefinition('2018', 'Art10'),
    },
    '2012': {
        'Art8a': ReportDefinition('2012', 'Art8a'),
        'Art8b': ReportDefinition('2012', 'Art8b'),
        'Art9': ReportDefinition('2012', 'Art9'),
        'Art10': ReportDefinition('2012', 'Art10'),
    }
}


def get_sorted_fields(year, article, fields):
    """ field = name from DB
        title = title/label showed in the template

    :param fields: ['Feature', 'GESComponents', 'Element', 'TargetCode', ...]
    :param article: 'Art8'
    :return: [('<fieldname>', <title'), ...
              ('Feature', 'Feature'), ('GESComponents', ''GESComponents),
        ... , ('TargetCode', 'RelatedTargets')]
    """

    elements = REPORT_DEFS[year][article].get_elements()

    labels = [
        (x.get('name'), x.text.strip())

        for x in elements

        if x.attrib.get('skip', 'false') == 'false'
    ]

    if not labels:
        final = [(x, x) for x in fields]

        return final

    diff = set(fields) - set([x.get('name') for x in elements])
    final = [(x, x) for x in diff]

    final.extend(labels)

    return final
