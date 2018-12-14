import hashlib
import logging
import time
from collections import defaultdict, namedtuple
from datetime import datetime
from io import BytesIO

from lxml.etree import fromstring
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
from wise.msfd.gescomponents import (LabelCollection, get_descriptor,
                                     get_features, get_parameters)

from wise.msfd.utils import ItemList
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form

from ..base import BaseComplianceView
from .a8 import Article8
from .a8_new import Article8 as Article8New
from .a9 import Article9
from .a10 import Article10
from .utils import get_sorted_fields_2018, row_to_dict

logger = logging.getLogger('wise.msfd')

NSMAP = {"w": "http://water.eionet.europa.eu/schemas/dir200856ec"}


def get_reportdata_key(func, self, *args, **kwargs):
    """ Reportdata template rendering cache key generation
    """

    if 'refresh' in self.request.form:
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
            'Art8': Article8New,
            'Art9': Article9,
            'Art10': Article10,
        }

        if 'alter' in self.request.form:
            res['Art8'] = Article8

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

    @cache(get_reportdata_key, dependencies=['translation'])
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
        # emptt), so we try to get the information from the reported XML files.

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


# class Proxy(object):
#
#     def __init__(self, obj):
#         self.__o = obj       # original object
#
#     def __getattr__(self, name):
#         return getattr(self.__o, name)
#
#     def __iter__(self):
#         return iter(self.__o)


LabelCollection = LabelCollection()


class A8Proxy(object):     # Proxy
    def __init__(self, obj):
        self.__o = obj       # original object

    def __getattr__(self, name):
        return getattr(self.__o, name)

    def __iter__(self):
        return iter(self.__o)

    @property
    def Feature(self):
        s = self.__o.Feature.strip()
        label_name = 'feature_labels'
        res = [(LabelCollection.get_label(label_name, s), s)]

        return ItemList(rows=res)

    @property
    def Parameter(self):
        s = self.__o.Parameter.strip()
        label_name = 'parameter_labels'
        res = [(LabelCollection.get_label(label_name, s), s)]

        return ItemList(rows=res)

    @property
    def IntegrationRuleTypeParameter(self):
        s = self.__o.IntegrationRuleTypeParameter.strip()
        label_name = 'parameter_labels'
        res = [(LabelCollection.get_label(label_name, s), s)]

        return ItemList(rows=res)

    @property
    def ThresholdValueSource(self):
        s = self.__o.ThresholdValueSource.strip()
        label_name = 'threshold_sources_labels'
        res = [(LabelCollection.get_label(label_name, s), s)]

        return ItemList(rows=res)

    @property
    def ValueUnit(self):
        s = self.__o.ValueUnit.strip()
        label_name = 'units_labels'
        res = [(LabelCollection.get_label(label_name, s), s)]

        return ItemList(rows=res)

    @property
    def ElementCodeSource(self):
        s = self.__o.ElementCodeSource.strip()
        label_name = 'elementcode_sources_labels'
        res = [
            (LabelCollection.get_label(label_name, s), s)
        ]

        return ItemList(rows=res)

    @property
    def Element2CodeSource(self):
        s = self.__o.Element2CodeSource.strip()
        label_name = 'elementcode_sources_labels'
        res = [
            (LabelCollection.get_label(label_name, s), s)
        ]

        return ItemList(rows=res)

    # TODO make this work
    # @property
    # def PressureCode(self):
    #     s = self.__o.PressureCode.strip()
    #     label_name = 'pressure_labels'
    #     res = [(LabelCollection.get_pressure_label(label_name, s), s)]
    #
    #     return ItemList(rows=res)


class A10Proxy(object):     # Proxy
    def __init__(self, obj):
        self.__o = obj       # original object

    def __getattr__(self, name):
        return getattr(self.__o, name)

    def __iter__(self):
        return iter(self.__o)

    @property
    def Features(self):
        s = set(self.__o.Features.split(','))
        label_name = 'feature_labels'
        res = [
            (LabelCollection.get_label(label_name, x), x)
            for x in s
        ]

        return ItemList(rows=res)

    @property
    def Parameter(self):
        s = self.__o.Parameter.strip()
        label_name = 'parameter_labels'
        res = [(LabelCollection.get_label(label_name, s), s)]

        return ItemList(rows=res)

    @property
    def ValueUnit(self):
        s = self.__o.ValueUnit.strip()
        label_name = 'units_labels'
        res = [(LabelCollection.get_label(label_name, s), s)]

        return ItemList(rows=res)


class A9Proxy(object):     # Proxy
    def __init__(self, obj):
        self.__o = obj       # original object

    def __getattr__(self, name):
        return getattr(self.__o, name)

    def __iter__(self):
        return iter(self.__o)

    @property
    def Features(self):
        s = set(self.__o.Features.split(','))
        label_name = 'feature_labels'
        res = [
            (LabelCollection.get_label(label_name, x), x)
            for x in s
        ]

        return ItemList(rows=res)


class ReportData2018(BaseComplianceView):

    report_year = '2018'
    section = 'national-descriptors'

    BLACKLIST = (
        'CountryCode',
        'ReportingDate',
        'ReportedFileLink',
        'Region',
        'MarineReportingUnit'
    )

    Art8 = Template('pt/nat-desc-report-data-multiple-muid.pt')
    Art9 = Template('pt/nat-desc-report-data-single-muid.pt')
    Art10 = Template('pt/nat-desc-report-data-multiple-muid.pt')

    view_names = {
        'Art8': 't_V_ART8_GES_2018',
        'Art9': 't_V_ART9_GES_2018',
        'Art10': 't_V_ART10_Targets_2018'
    }

    subform = None

    def get_data_from_view_art8(self):

        # TODO: the data here should be filtered by muids in region

        view_name = self.view_names[self.article]
        t = getattr(sql2018, view_name)

        descr_class = get_descriptor(self.descriptor)
        all_ids = list(descr_class.all_ids())

        if self.descriptor.startswith('D1.'):
            all_ids.append('D1')

        conditions = [t.c.GESComponent.in_(all_ids)]

        count, res = db.get_all_records_ordered(
            t,
            'Criteria',
            t.c.CountryCode == self.country_code,
            *conditions
        )

        data = [A8Proxy(row) for row in res]

        return data

    def get_data_from_view_art10(self):
        descr_class = get_descriptor(self.descriptor)
        all_ids = list(descr_class.all_ids())

        if self.descriptor.startswith('D1.'):
            all_ids.append('D1')

        view_name = self.view_names[self.article]
        t = getattr(sql2018, view_name)

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

        data = [A10Proxy(row) for row in out]

        return data

    def get_data_from_view_art9(self):

        view_name = self.view_names[self.article]
        t = getattr(sql2018, view_name)

        descr_class = get_descriptor(self.descriptor)
        all_ids = list(descr_class.all_ids())

        if self.descriptor.startswith('D1.'):
            all_ids.append('D1')
        conditions = [t.c.GESComponent.in_(all_ids)]

        count, r = db.get_all_records_ordered(
            t,
            'GESComponent',
            t.c.CountryCode == self.country_code,
            *conditions
        )

        data = [A9Proxy(row) for row in r]

        return data

    def change_orientation(self, data):
        """ From a set of results, create labeled list of rows
        """

        # def make_distinct(col_name, col_data):
        #     """ Features come as a list of comma separated values, with
        #     duplicated values among them. We make those values distinct
        #     """
        #
        #     if col_name not in ('Features', ):
        #         return col_data
        #
        #     if not col_data:
        #         return ''
        #
        #     splitted = col_data.split(',')
        #     distinct = ', '.join(sorted(set(splitted)))
        #
        #     return distinct

        res = []
        row0 = data[0]

        sorted_fields = get_sorted_fields_2018(row0._fields, self.article)

        for fname, label in sorted_fields:
            values = [
                getattr(row, fname)
                # make_distinct(fname, getattr(row, fname))

                for row in data
            ]

            res.append([(fname, label), values])

        return res

    @db.use_db_session('2018')
    def get_data_from_db(self):
        article = self.article.lower()

        get_data_method = getattr(
            self,
            'get_data_from_view_' + article
        )

        data = get_data_method()

        grouped_data = defaultdict(list)

        # Ignore the following fields when hashing the rows
        ignores = {
            'art8': ('TargetCode', 'PressureCode'),
            'art9': (),
            'art10': ()
        }
        ignore = [data[0]._fields.index(x) for x in ignores[article]]

        seen = []

        for row in data:
            # without the ignored fields create a hash to exclude
            # duplicate rows

            # TODO: this needs to be redone
            as_list = [x for ind, x in enumerate(row) if ind not in ignore]
            hash = hashlib.md5(''.join(unicode(as_list))).hexdigest()

            if hash in seen:
                continue

            seen.append(hash)

            if not row.MarineReportingUnit:
                # skip rows without muid, they can't help us

                continue

            grouped_data[row.MarineReportingUnit].append(row)

        res = []

        # change the orientation of the data

        for mru, filtered_data in grouped_data.items():
            changed = (mru, self.change_orientation(filtered_data))

            for row in changed[1]:
                # field = db_name/title ('TargetCode', 'RelatedTargets')
                field = row[0]
                row_data = row[1]

                if field[0] not in ignores[article]:
                    row[0] = field[1]

                    continue

                # override the values for the ignored fields
                # with all the values from DB
                all_values = [
                    getattr(x, field[0])

                    for x in data

                    if x.MarineReportingUnit == mru
                ]
                row[0] = field[1]

                all_values = filter(lambda _: _ is not None, all_values)

                if all_values:
                    all_values = set(all_values)

                new_row_data = [', '.join(all_values)] * len(row_data)

                row[1] = new_row_data

            res.append(changed)

        res = sorted(res, key=lambda r: r[0])
        # import pdb; pdb.set_trace()

        return res

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

    def get_data(self):
        """ Returns the data to display in the template
        """

        snapshots = self.get_snapshots()
        self.subform.update()
        fd, errors = self.subform.extractData()
        date_selected = fd['sd']

        data = snapshots[-1][1]

        if date_selected:
            print date_selected
            filtered = [x for x in snapshots if x[0] == date_selected]

            if filtered:
                date, data = filtered[0]
            else:
                raise ValueError("Snapshot doesn't exist at this date")

        return data

    def get_muids_from_data(self, data):
        muids = sorted(set([x[0] for x in data]))

        return ', '.join(muids)

    @cache(get_reportdata_key, dependencies=['translation'])
    def render_reportdata(self):
        logger.info("Quering database for 2018 report data: %s %s %s %s",
                    self.country_code, self.country_region_code, self.article,
                    self.descriptor)
        print "rendering data"

        data = self.get_data()

        report_date = ''
        source_file = ['To be addedd...', '.']

        # TODO: check validity of data

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
        xlsdata = self.get_data()

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
