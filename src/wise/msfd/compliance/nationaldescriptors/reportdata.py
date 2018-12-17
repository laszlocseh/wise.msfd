import logging
import time
from collections import namedtuple
from datetime import datetime
from io import BytesIO

from lxml.etree import fromstring
from six import string_types
from zope.schema import Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

import xlsxwriter
from eea.cache import cache
from persistent.list import PersistentList
from plone.memoize import volatile
from Products.Five.browser.pagetemplatefile import \
    ViewPageTemplateFile as Template
from wise.msfd import db, sql, sql2018
from wise.msfd.base import BaseUtil
from wise.msfd.data import (get_factsheet_url, get_report_data,
                            get_report_file_url, get_report_filename)
from wise.msfd.gescomponents import (LABELS, get_descriptor, get_features,
                                     get_parameters)
from wise.msfd.utils import (ItemLabel, ItemList, change_orientation,
                             filter_duplicates)
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form

from ..base import BaseComplianceView
from .a8 import Article8 as Article8
from .a9 import Article9
from .a10 import Article10
from .utils import get_sorted_fields_2018, row_to_dict, REPORT_2018

logger = logging.getLogger('wise.msfd')

NSMAP = {"w": "http://water.eionet.europa.eu/schemas/dir200856ec"}


def get_reportdata_key(func, self, *args, **kwargs):
    """ Reportdata template rendering cache key generation
    """

    if 'nocache' in self.request.form:
        raise volatile.DontCache

    muids = ",".join(self.muids)
    region = getattr(self, 'country_region_code', ''.join(self.regions))

    res = '_cache_' + '_'.join([self.report_year, self.country_code,
                                region,
                                self.descriptor, self.article, muids])
    res = res.replace('.', '').replace('-', '')

    return res


class ReportData2012(BaseComplianceView, BaseUtil):
    """ WIP on compliance tables
    """

    report_year = '2012'
    section = 'national-descriptors'

    @property
    def article_implementations(self):
        res = {
            'Art8': Article8,
            'Art9': Article9,
            'Art10': Article10,
        }

        return res

    def get_criterias_list(self, descriptor):
        """ Get the list of criterias for the specified descriptor

        :param descriptor: 'D5'
        :return: (('D5', 'Eutrophication'),
                  ('5.1.1', 'D5C1'),
                  ('5.2.1', 'D5C2'), ... )

        # TODO: the results here need to be augumented by L_GESComponents
        """

        result = [
            (descriptor, self.descriptor_label)
        ]

        criterions = get_descriptor(descriptor).criterions

        for crit in criterions:
            for alt in crit.alternatives:
                title = '{} ({}) {}'.format(crit._id or '', alt[0], alt[1])
                indicator = alt[0]

                result.append((indicator, title))

        return result

    @property
    def muids(self):
        """ Get all Marine Units for a country

        :return: ['BAL- LV- AA- 001', 'BAL- LV- AA- 002', ...]
        """
        t = sql.t_MSFD4_GegraphicalAreasID
        count, res = db.get_all_records(
            t,
            t.c.MemberState == self.country_code,
            t.c.RegionSubRegions == self.country_region_code,
        )

        res = [row_to_dict(t, r) for r in res]
        muids = set([x['MarineUnitID'] for x in res])

        return sorted(muids)

    # @cache(get_reportdata_key, dependencies=['translation'])
    def get_report_data(self):
        logger.info("Rendering 2012 report for: %s %s %s %s",
                    self.country_code, self.descriptor, self.article,
                    ",".join(self.muids)
                    )
        klass = self.article_implementations[self.article]

        view = klass(self, self.request, self.country_code, self.descriptor,
                     self.article, self.muids)

        return view()

    def get_report_filename(self):
        # needed in article report data implementations, to retrieve the file

        return get_report_filename('2012',
                                   self.country_code,
                                   self.country_region_code,
                                   self.article,
                                   self.descriptor)

    @db.use_db_session('2012')
    def __call__(self):

        if self.descriptor.startswith('D1.'):       # map to old descriptor
            self._descriptor = 'D1'
            assert self.descriptor == 'D1'

        print "Will render report for ", self.article
        self.filename = filename = self.get_report_filename()

        factsheet = None

        if filename:
            url = get_report_file_url(filename)
            try:
                factsheet = get_factsheet_url(url)
            except:
                logger.exception("Error in getting HTML Factsheet URL %s", url)
            source_file = (filename, url + '/manage_document')
        else:
            source_file = ('File not found', None)

        rep_info = self.get_reporting_information()

        report_header = self.report_header_template(
            title="{}'s 2012 Member State Report for {} / {} / {}".format(
                self.country_name,
                self.country_region_code,
                self.descriptor,
                self.article
            ),
            report_by=rep_info.reporters,
            source_file=source_file,
            # TODO: do the report_due by a mapping with article: date
            report_due='2012-10-15',
            report_date=rep_info.report_date,
            factsheet=factsheet,
        )

        report_data = self.get_report_data()
        self.report_html = report_header + report_data

        return self.index()

    def get_reporting_information(self):
        # The MSFD<ArtN>_ReportingInformation tables are not reliable (8b is
        # empty), so we try to get the information from the reported XML files.

        default = ReportingInformation('Member State', '2013-04-30')

        if not self.filename:
            return default

        text = get_report_data(self.filename)
        root = fromstring(text)

        reporters = root.xpath('//w:ReportingInformation/w:Name/text()',
                               namespaces=NSMAP)
        date = root.xpath('//w:ReportingInformation/w:ReportingDate/text()',
                          namespaces=NSMAP)

        try:
            res = ReportingInformation(date[0], ', '.join(set(reporters)))
        except Exception:
            logger.exception('Could not get reporting info for %s, %s, %s',
                             self.article, self.descriptor, self.country_code
                             )
            res = default

        return res


ReportingInformation = namedtuple('ReportingInformation',
                                  ['report_date', 'reporters'])


class SnapshotSelectForm(Form):
    template = Template('../pt/inline-form.pt')
    _updated = False

    @property
    def fields(self):
        snaps = getattr(self.context.context, 'snapshots', [])

        if snaps:
            default = snaps[-1][0]
        else:
            default = None

        dates = [SimpleTerm(x[0], x[0].isoformat(), x[0]) for x in snaps]

        field = Choice(
            title=u'Date of harvest',
            __name__='sd',
            vocabulary=SimpleVocabulary(dates),
            required=False,
            default=default
        )

        return Fields(field)

    def update(self):
        if not self._updated:
            Form.update(self)
            self._updated = True

    @buttonAndHandler(u'View snapshot', name='view')
    def apply(self, action):
        return

    # TODO: make a condition for this button
    @buttonAndHandler(u'Harvest new data', name='harvest')
    def harvest(self, action):
        data = self.context.get_data_from_db()

        self.context.context.snapshots.append((datetime.now(), data))
        print "harvesting data"

        self.request.response.redirect('./@@view-report-data-2018')


class Proxy2018(object):
    def __init__(self, obj, article, extra=None):
        self.__o = obj       # the proxied object
        self.nodes = REPORT_2018.get_article_childrens(article)
        if not extra:
            extra = {}

        self.extra = extra

        for node in self.nodes:
            name = node.tag
            value = getattr(self.__o, name, extra.get(name, None))
            if not value:
                continue

            attrs = node.attrib
            label_name = attrs.get('labelName', None)
            if not label_name:
                continue

            as_list = attrs.get('asList', 'false')
            if as_list == 'true':
                vals = set(value.split(','))

                res = [
                    ItemLabel(
                        v,
                        LABELS.get(label_name, v),
                    )
                    for v in vals
                ]

                setattr(self, name, ItemList(rows=res))
            else:
                title = LABELS.get(label_name, value)
                setattr(self, name, ItemLabel(value, title))

    def __getattr__(self, name):
        return getattr(self.__o, name, self.extra.get(name))

    def __iter__(self):
        return iter(self.__o)


# class A8Proxy(object):
#     def __init__(self, obj):
#         self.__o = obj       # the proxied object
#
#         # we try to translate shortcodes into labels
#         simple_labels = [
#             ('Feature', 'feature_labels'),
#             ('Parameter', 'parameter_labels'),
#             ('IntegrationRuleTypeParameter', 'parameter_labels'),
#             ('ThresholdValueSource', 'threshold_sources_labels'),
#             ('ValueUnit', 'units_labels'),
#             ('ElementCodeSource', 'elementcode_sources_labels'),
#             ('Element2CodeSource', 'elementcode_sources_labels'),
#         ]
#
#         for (name, collection_name) in simple_labels:
#             value = getattr(self.__o, name)
#
#             if isinstance(value, string_types):
#                 value = value.strip()
#
#             if not value:       # don't overwrite empty values
#                 continue
#
#             title = LABELS.get(collection_name, value)
#             setattr(self, name, ItemLabel(value, title))
#
#         # if self.__o.PressureCode:
#         #     s = self.__o.PressureCode.strip()
#         #     res = [(LABELS.get('pressure_labels', s), s)]
#         #
#         #     self.PressureCode = ItemList(rows=res)
#
#     def __getattr__(self, name):
#         return getattr(self.__o, name)
#
#     def __iter__(self):
#         return iter(self.__o)
#
#
# class A10Proxy(object):     # Proxy
#     def __init__(self, obj):
#         self.__o = obj       # original object
#
#         simple_labels = [
#             ('Parameter', 'parameter_labels'),
#             ('ValueUnit', 'units_labels'),
#         ]
#
#         for (name, collection_name) in simple_labels:
#             value = getattr(self.__o, name)
#
#             if isinstance(value, string_types):
#                 value = value.strip()
#
#             if not value:       # don't overwrite empty values
#                 continue
#
#             title = LABELS.get(collection_name, value)
#             setattr(self, name, ItemLabel(value, title))
#
#         if self.__o.Features:
#             s = set(self.__o.Features.split(','))
#             res = [
#                 ItemLabel(
#                     x,
#                     LABELS.get('feature_labels', x),
#                 )
#
#                 for x in s
#             ]
#             self.Features = ItemList(rows=res)
#
#     def __getattr__(self, name):
#         return getattr(self.__o, name)
#
#     def __iter__(self):
#         return iter(self.__o)
#
#
# class A9Proxy(object):     # Proxy
#     def __init__(self, obj):
#         self.__o = obj       # original object
#
#         if self.__o.Features:
#             s = set(self.__o.Features.split(','))
#             res = [
#                 ItemLabel(
#                     x,
#                     LABELS.get('feature_labels', x),
#                 )
#
#                 for x in s
#             ]
#             self.Features = ItemList(rows=res)
#
#     def __getattr__(self, name):
#         v = getattr(self.__o, name)
#         logger.info("getting attribute %s: %r", name, v)
#
#         return v
#
#     def __iter__(self):
#         return iter(self.__o)


class ReportData2018(BaseComplianceView):

    report_year = '2018'        # used by cache key
    section = 'national-descriptors'

    BLACKLIST = (       # used in templates to filter fields
        'CountryCode',
        'ReportingDate',
        'ReportedFileLink',
        'Region',
        'MarineReportingUnit'
    )

    Art8 = Template('pt/nat-desc-report-data-multiple-muid.pt')
    Art9 = Template('pt/nat-desc-report-data-single-muid.pt')
    Art10 = Template('pt/nat-desc-report-data-multiple-muid.pt')

    group_by_fields = {
        'Art8': (),  # 'TargetCode', 'PressureCode'
        'Art9': (),
        'Art10': ()
    }

    subform = None

    def get_data_from_view_Art8(self):
        fields = REPORT_2018.get_article_childrens(self.article)
        exclude = [
            x.tag
            for x in fields
            if x.attrib.get('exclude', 'false') == 'true'
        ]
        # TODO: the data here should be filtered by muids in region

        t = sql2018.t_V_ART8_GES_2018

        descr_class = get_descriptor(self.descriptor)
        all_ids = list(descr_class.all_ids())

        if self.descriptor.startswith('D1.'):
            all_ids.append('D1')

        conditions = [t.c.GESComponent.in_(all_ids)]

        exclude_data, res = db.get_all_records_distinct_ordered(
            t,
            'Criteria',
            exclude,
            t.c.CountryCode == self.country_code,
            *conditions
        )

        data = [Proxy2018(row, self.article, exclude_data) for row in res]

        return data

    def get_data_from_view_Art10(self):
        descr_class = get_descriptor(self.descriptor)
        all_ids = list(descr_class.all_ids())

        if self.descriptor.startswith('D1.'):
            all_ids.append('D1')

        t = sql2018.t_V_ART10_Targets_2018

        # TODO check conditions for other countries beside NL
        # conditions = [t.c.GESComponents.in_(all_ids)]

        conditions = []
        params = get_parameters(self.descriptor)
        p_codes = [p.name for p in params]
        conditions.append(t.c.Parameter.in_(p_codes))

        features = set([f.name for f in get_features(self.descriptor)])

        count, res = db.get_all_records_ordered(
            t,
            'GESComponents',
            t.c.CountryCode == self.country_code,
            *conditions
        )

        out = []

        for row in res:
            feats = set(row.Features.split(','))

            if feats.intersection(features):
                out.append(row)

        data = [Proxy2018(row, self.article) for row in out]

        return data

    def get_data_from_view_Art9(self):

        t = sql2018.t_V_ART9_GES_2018

        descr_class = get_descriptor(self.descriptor)
        all_ids = list(descr_class.all_ids())

        # TODO: this needs to be analysed, what to do about D1?

        if self.descriptor.startswith('D1.'):
            all_ids.append('D1')

        conditions = [t.c.GESComponent.in_(all_ids)]

        count, r = db.get_all_records_ordered(
            t,
            'GESComponent',
            t.c.CountryCode == self.country_code,
            *conditions
        )

        data = [Proxy2018(row, self.article) for row in r]

        return data

    @db.use_db_session('2018')
    def get_data_from_db(self):
        get_data_method = getattr(
            self,
            'get_data_from_view_' + self.article
        )

        data = get_data_method()

        # this consolidates the data, filtering duplicates
        # list of ((name, label), values)
        good_data = filter_duplicates(data, self.group_by_fields[self.article])
        # good_data = data

        res = []

        for mru, rows in good_data.items():
            _fields = rows[0]._fields
            sorted_fields = get_sorted_fields_2018(_fields, self.article)
            _data = change_orientation(rows, sorted_fields)

            for row in _data:
                (fieldname, label), row_data = row
                row[0] = label

                # if fieldname not in self.group_by_fields[self.article]:
                #     continue
                #
                # # rewrite some rows with list of all possible values
                # all_values = set([
                #     getattr(x, fieldname)
                #
                #     for x in data
                #
                #     if (x.MarineReportingUnit == mru) and
                #     (getattr(x, fieldname) is not None)
                # ])
                #
                # row[1] = [', '.join(all_values)] * len(row_data)

            res.append((mru, _data))

        return sorted(res, key=lambda r: r[0])      # sort by MarineUnitiD

    def get_snapshots(self):
        """ Returns all snapshots, in the chronological order they were created
        """

        # snapshots = getattr(self.context, 'snapshots', None)
        snapshots = None
        # TODO: fix this. I'm hardcoding it now to always use generated data

        if snapshots is None:
            self.context.snapshots = PersistentList()

            db_data = self.get_data_from_db()
            snapshot = (datetime.now(), db_data)

            self.context.snapshots.append(snapshot)
            self.context.snapshots._p_changed = True

            self.context._p_changed = True

            return self.context.snapshots

        return snapshots

    def get_form(self):

        if not self.subform:
            form = SnapshotSelectForm(self, self.request)
            self.subform = form

        return self.subform

    def get_report_data(self):
        """ Returns the data to display in the template
        """

        snapshots = self.get_snapshots()
        self.subform.update()
        fd, errors = self.subform.extractData()
        date_selected = fd['sd']

        data = snapshots[-1][1]

        if date_selected:
            # print date_selected
            filtered = [x for x in snapshots if x[0] == date_selected]

            if filtered:
                date, data = filtered[0]
            else:
                raise ValueError("Snapshot doesn't exist at this date")

        return data

    def get_muids_from_data(self, data):
        muids = sorted(set([x[0] for x in data]))

        return ', '.join(muids)

    # @cache(get_reportdata_key, dependencies=['translation'])
    def render_reportdata(self):
        logger.info("Quering database for 2018 report data: %s %s %s %s",
                    self.country_code, self.country_region_code, self.article,
                    self.descriptor)
        data = self.get_report_data()

        report_date = ''
        source_file = ['To be addedd...', '.']

        if data and data[0][1]:
            for row in data[0][1]:
                if row[0] == 'ReportingDate':
                    report_date = row[1][0]

                if row[0] == 'ReportedFileLink':
                    source_file[1] = row[1][0] + '/manage_document'
                    source_file[0] = row[1][0].split('/')[-1]

        report_header = self.report_header_template(
            title="{}'s 2018 Member State Report for {} / {} / {}".format(
                self.country_name,
                self.country_region_code,
                self.descriptor,
                self.article
            ),
            factsheet=None,
            # TODO: find out how to get info about who reported
            report_by='Member State',
            source_file=source_file,
            report_due='2018-10-15',
            report_date=report_date
        )

        template = getattr(self, self.article, None)

        return template(data=data, report_header=report_header)

    def data_to_xls(self, data):
        # Create a workbook and add a worksheet.
        out = BytesIO()
        workbook = xlsxwriter.Workbook(out, {'in_memory': True})

        for wtitle, wdata in data:
            worksheet = workbook.add_worksheet(wtitle)

            for i, (row_label, row_values) in enumerate(wdata):
                worksheet.write(i, 0, row_label)

                for j, v in enumerate(row_values):
                    worksheet.write(i, j+1, unicode(v or ''))

        workbook.close()
        out.seek(0)

        return out

    def download(self):
        xlsdata = self.get_report_data()

        # if self.article == 'Art9':
        #     xlsdata = [
        #         ('Reported Data', data),
        #     ]
        # else:
        #     # use marine unit ids as worksheet titles
        #     xlsdata = data

        xlsio = self.data_to_xls(xlsdata)
        sh = self.request.response.setHeader

        sh('Content-Type', 'application/vnd.openxmlformats-officedocument.'
           'spreadsheetml.sheet')
        fname = "-".join([self.country_code,
                          self.country_region_code,
                          self.article,
                          self.descriptor])
        sh('Content-Disposition',
           'attachment; filename=%s.xlsx' % fname)

        return xlsio.read()

    def __call__(self):

        self.content = ''
        template = getattr(self, self.article, None)

        if not template:
            return self.index()

        self.subform = self.get_form()

        if 'download' in self.request.form:
            return self.download()

        trans_edit_html = self.translate_view()()

        t = time.time()
        logger.debug("Started rendering of report data")

        self.muids = []
        report_html = self.render_reportdata()

        delta = time.time() - t
        logger.info("Rendering report data took: %s, %s/%s/%s/%s",
                    delta, self.article, self.descriptor,
                    self.country_region_code, self.country_code)

        self.report_html = report_html + trans_edit_html

        return self.index()
