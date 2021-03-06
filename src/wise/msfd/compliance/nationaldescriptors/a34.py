import logging

from collections import defaultdict
from lxml.etree import fromstring

from Products.Five.browser.pagetemplatefile import \
    ViewPageTemplateFile as Template
from wise.msfd.data import get_xml_report_data
from wise.msfd.translation import retrieve_translation
from wise.msfd.utils import (Item, ItemLabel, ItemList, Node, RawRow,  # Row,
                             RelaxedNode, natural_sort_key, to_html)

from ..base import BaseArticle2012

# from .data import REPORT_DEFS

logger = logging.getLogger('wise.msfd')


NSMAP = {
    "w": "http://water.eionet.europa.eu/schemas/dir200856ec",
    "c": "http://water.eionet.europa.eu/schemas/dir200856ec/mscommon",
}


def xp(xpath, node):
    return node.xpath(xpath, namespaces=NSMAP)


class A34Item(Item):
    def __init__(self, parent, node, description):

        super(A34Item, self).__init__([])

        self.parent = parent
        self.node = node
        self.description = description
        self.g = RelaxedNode(node, NSMAP)

        # self.id = node.find('w:ReportingFeature', namespaces=NSMAP).text

        attrs = [
            ('Member state description', self.member_state_descr),
            ('Region / subregion description', self.region_subregion),
            ('Subdivisions', self.subdivisions),
            ('Marine reporting units description', self.assessment_areas),
            ('Region or subregion', self.region_or_subregion),
            ('Member state', self.member_state),
            ('Area type', self.area_type),
            ('Marine Reporting Unit', self.mru_id),
            ('MRU Name', self.marine_reporting_unit),
        ]

        for title, getter in attrs:
            self[title] = getter()
            setattr(self, title, getter())

    def member_state_descr(self):
        text = xp('w:MemberState/text()', self.description)

        return text and text[0] or ''

    def region_subregion(self):
        text = xp('w:RegionSubregion/text()', self.description)

        return text and text[0] or ''

    def subdivisions(self):
        text = xp('w:Subdivisions/text()', self.description)

        return text and text[0] or ''

    def assessment_areas(self):
        text = xp('w:AssessmentAreas/text()', self.description)

        return text and text[0] or ''

    def region_or_subregion(self):
        v = self.g['w:RegionSubRegions/text()']

        return v and v[0] or ''

    def member_state(self):
        v = self.g['w:MemberState/text()']

        return v and v[0] or ''

    def area_type(self):
        v = self.g['w:AreaType/text()']

        return v and v[0] or ''

    def mru_id(self):
        v = self.g['w:MarineUnitID/text()']

        return v and v[0] or ''

    def marine_reporting_unit(self):
        v = self.g['w:MarineUnits_ReportingAreas/text()']

        return v and v[0] or ''


class Article34(BaseArticle2012):
    """ Article 3 & 4 implementation

    klass(self, self.request, self.country_code, self.country_region_code,
            self.descriptor, self.article, self.muids)
    """

    root = None
    year = '2012'

    template = Template('pt/report-data-secondary.pt')
    help_text = ""

    def __init__(self, context, request, country_code, region_code,
                 descriptor, article,  muids, filename):

        super(Article34, self).__init__(context, request, country_code,
                                        region_code, descriptor, article,
                                        muids)

        self.filename = filename

    def sort_cols(self, cols):
        sorted_cols = sorted(
            cols, key=lambda _r: (
                _r['Region / subregion description'],
                _r['Area type'],
                _r['Marine Reporting Unit']
            )
        )

        return sorted_cols

    def setup_data(self):
        filename = self.filename
        text = get_xml_report_data(filename)
        self.root = fromstring(text)

        nodes = xp('//w:GeographicalBoundariesID', self.root)
        description = xp('//w:Description', self.root)[0]

        cols = []

        for node in nodes:
            item = A34Item(self, node, description)
            cols.append(item)

        sorted_cols = self.sort_cols(cols)

        self.rows = []

        for col in sorted_cols:
            for name in col.keys():
                values = []

                for inner in sorted_cols:
                    values.append(inner[name])

                raw_values = []
                vals = []

                for v in values:
                    raw_values.append(v)
                    vals.append(self.context.translate_value(
                        name, v, self.country_code))

                row = RawRow(name, vals, raw_values)
                self.rows.append(row)

            break       # only need the "first" row

        self.cols = sorted_cols

    def __call__(self):
        if self.root is None:
            self.setup_data()

        return self.template()


class A34Item_2018_mru(Item):
    def __init__(self, node):

        super(A34Item_2018_mru, self).__init__([])

        self.node = node
        self.g = RelaxedNode(node, NSMAP)

        attrs = [
            ('Region or subregion', self.region_or_subregion()),
            ('Member state', self.member_state()),
            ('Area type', self.area_type()),
            ('Marine Reporting Unit', self.mru_id()),
            ('MRU Name', self.marine_reporting_unit()),
        ]

        for title, value in attrs:
            self[title] = value
            setattr(self, title, value)

    def region_or_subregion(self):
        v = self.g['w:RegionSubRegions/text()']

        return v and v[0] or ''

    def member_state(self):
        v = self.g['w:MemberState/text()']

        return v and v[0] or ''

    def area_type(self):
        v = self.g['w:AreaType/text()']

        return v and v[0] or ''

    def mru_id(self):
        v = self.g['w:MarineUnitID/text()']

        return v and v[0] or ''

    def marine_reporting_unit(self):
        v = self.g['w:MarineUnits_ReportingAreas/text()']

        return v and v[0] or ''


class A34Item_2018_main(Item):
    mrus_template = Template('pt/mrus-table-art34.pt')
    TRANSLATABLES_EXTRA = ['MRU Name']

    def __init__(self, context, request, description,
                 mru_nodes, previous_mrus=None):

        super(A34Item_2018_main, self).__init__([])
        self.description = description
        self.context = context
        self.request = request

        attrs = [
            ('Member state description', self.member_state_descr),
            ('Region / subregion description', self.region_subregion),
            ('Subdivisions', self.subdivisions),
            ('Marine reporting units description', self.assessment_areas),
        ]

        for title, getter in attrs:
            self[title] = getter()
            setattr(self, title, getter())

        mrus = []

        for node in mru_nodes:
            item = A34Item_2018_mru(node)
            mrus.append(item)

        sorted_mrus = sorted(mrus, key=lambda x: x['Marine Reporting Unit'])
        self._mrus = sorted_mrus
        self.available_mrus = [x['Marine Reporting Unit'] for x in sorted_mrus]
        self.available_regions = set(
            [x['Region or subregion'] for x in sorted_mrus]
        )
        self.previous_mrus = previous_mrus or []
        item_labels = sorted_mrus and sorted_mrus[0].keys() or ""

        sorted_mrus = self.mrus_template(
            item_labels=item_labels,
            item_values=sorted_mrus,
            previous_mrus=self.previous_mrus,
            country_code=self.context.country_code,
            translate_value=self.translate_value
        )

        self['MRUs'] = sorted_mrus
        setattr(self, 'MRUs', sorted_mrus)

        # Region or subregion Member state    Area type   MRU ID  Marine
        # reporting unit  Marine reporting unit

    def get_translatable_extra_data(self):
        """ Get the translatable fields from the MRU nodes

        :return: a list of values to translate
        """
        res = []

        for row in self._mrus:
            for field in self.TRANSLATABLES_EXTRA:
                value = getattr(row, field, None)
                if not value:
                    continue

                res.append(value)

        return set(res)

    def translate_value(self, fieldname, value, source_lang):
        is_translatable = fieldname in self.TRANSLATABLES_EXTRA
        v = self.context.context.translate_view()

        return v.translate(source_lang=source_lang,
                           value=value,
                           is_translatable=is_translatable)

    def sort_mrus(self, cols):
        sorted_cols = sorted(
            cols, key=lambda _r: (
                _r['Member state'],
                _r['Region or subregion'],
                _r['Marine Reporting Unit'],
                _r['MRU Name']
            )
        )

        return sorted_cols

    def member_state_descr(self):
        text = xp('w:MemberState/text()', self.description)

        return text and text[0] or ''

    def region_subregion(self):
        text = xp('w:RegionSubregion/text()', self.description)

        return text and text[0] or ''

    def subdivisions(self):
        text = xp('w:Subdivisions/text()', self.description)

        return text and text[0] or ''

    def assessment_areas(self):
        text = xp('w:AssessmentAreas/text()', self.description)

        return text and text[0] or ''


class Article34_2018(BaseArticle2012):
    """ Implementation for Article 3/4 2018 reported data
    """

    year = '2012'
    root = None

    template = Template('pt/report-data-secondary.pt')
    help_text = ""

    def __init__(self, context, request, country_code, region_code,
                 descriptor, article, muids, filename=None,
                 previous_mrus=None):

        # TODO: use previous_mrus to highlight this file MRUs according to edit
        # status: added or deleted
        super(Article34_2018, self).__init__(context, request, country_code,
                                             region_code, descriptor, article,
                                             muids)

        self.filename = filename
        self.previous_mrus = previous_mrus

    def get_report_file_root(self, filename=None):
        if self.root is None:
            self.setup_data()

        return self.root

    def setup_data(self):
        filename = self.filename
        text = get_xml_report_data(filename)
        self.root = fromstring(text)

        mru_nodes = xp('//w:GeographicalBoundariesID', self.root)
        description = xp('//w:Description', self.root)[0]

        # TODO: also send the previous file data
        main_node = A34Item_2018_main(
            self, self.request, description, mru_nodes, self.previous_mrus
        )
        self.translatable_extra_data = main_node.get_translatable_extra_data()
        self.available_mrus = main_node.available_mrus
        self.available_regions = main_node.available_regions
        self.rows = []

        # TODO: this code needs to be explained. It's hard to understand what
        # its purpose is

        for name in main_node.keys():
            values = []

            for inner in [main_node]:
                values.append(inner[name])

            raw_values = []
            vals = []

            for v in values:
                raw_values.append(v)
                vals.append(self.context.translate_value(
                    name, v, self.country_code))

            row = RawRow(name, vals, raw_values)
            self.rows.append(row)

        self.cols = [main_node]

    def __call__(self):
        if self.root is None:
            self.setup_data()

        return self.template()
