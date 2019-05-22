import logging
from sqlalchemy import or_

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from wise.msfd import db, sql2018
from wise.msfd.translation import retrieve_translation
from wise.msfd.utils import (CompoundRow, ItemList, items_to_rows, timeit,
                             natural_sort_key, Row)

from .a8 import RegDescA82018Row, RegDescA82012
from .a9 import RegDescA92018Row, RegDescA92012
from .a10 import RegDescA102018Row, RegDescA102012
from .base import BaseRegComplianceView
from .data import get_report_definition

logger = logging.getLogger('wise.msfd')


class RegReportData2012(BaseRegComplianceView):
    help_text = "HELP TEXT"
    template = ViewPageTemplateFile('pt/report-data.pt')
    year = "2012"

    Art8 = RegDescA82012
    Art9 = RegDescA92012
    Art10 = RegDescA102012

    @db.use_db_session('2012')
    def get_report_data(self):
        impl_class = getattr(self, self.article)
        result = impl_class(self, self.request)

        # import pdb; pdb.set_trace()

        return result.allrows

    # @cache(get_reportdata_key, dependencies=['translation'])
    def render_reportdata(self):
        logger.info("Quering database for 2012 report data: %s %s %s",
                    self.country_region_code, self.article,
                    self.descriptor)

        data = self.get_report_data()

        report_header = self.report_header_template(
            title="Member State report: {} / {} / {} / 2012".format(
                self.country_region_name,
                self.descriptor_title,
                self.article
            ),
            factsheet=None,
            # TODO: find out how to get info about who reported
            report_by='Report by',
            report_due='2018-10-15',
            help_text=self.help_text,
            use_translation=False
        )

        template = self.template

        return template(data=data, report_header=report_header)

    def __call__(self):
        report_html = self.render_reportdata()
        self.report_html = report_html

        @timeit
        def render_html():
            return self.index()

        return render_html()


class RegReportData2018(BaseRegComplianceView):
    # implements(IReportDataView)

    help_text = "HELP TEXT"
    template = ViewPageTemplateFile('pt/report-data.pt')
    year = "2018"

    # Art8 = ViewPageTemplateFile('pt/report-data.pt')
    # Art9 = ViewPageTemplateFile('pt/report-data.pt')
    # Art10 = ViewPageTemplateFile('pt/report-data.pt')

    Art8 = RegDescA82018Row
    Art9 = RegDescA92018Row
    Art10 = RegDescA102018Row

    @property
    def all_descriptor_ids(self):
        all_ids = list(self.descriptor_obj.all_ids())

        if self.descriptor.startswith('D1.'):
            all_ids.append('D1')

        all_ids = set(all_ids)

        return all_ids

    @property
    def get_data_from_view_Art9(self):
        t = sql2018.t_V_ART9_GES_2018

        count, q = db.get_all_records_ordered(
            t,
            ('GESComponent',),
            or_(t.c.Region == self.country_region_code,
                t.c.Region.is_(None)),
            t.c.GESComponent.in_(self.all_descriptor_ids),
        )

        return q

    @property
    def get_data_from_view_Art8(self):
        sess = db.session()
        t = sql2018.t_V_ART8_GES_2018

        conditions = [
            t.c.Region == self.country_region_code,
            t.c.GESComponent.in_(self.all_descriptor_ids),
            or_(t.c.Element.isnot(None),
                t.c.Criteria.isnot(None)),
        ]

        # groupby IndicatorCode
        q = sess\
            .query(t)\
            .filter(*conditions)\
            .distinct()

        res = [row for row in q]

        return res

    @property
    def get_data_from_view_Art10(self):
        t = sql2018.t_V_ART10_Targets_2018

        # TODO check conditions for other countries beside NL
        # conditions = [t.c.GESComponents.in_(all_ids)]

        count, res = db.get_all_records_ordered(
            t,
            ('Features', 'TargetCode', 'Element'),
            t.c.Region == self.country_region_code,
            # *conditions
        )

        out = []

        # GESComponents contains multiple values separated by comma
        # filter rows by splitting GESComponents
        for row in res:
            ges_comps = getattr(row, 'GESComponents', ())
            ges_comps = set([g.strip() for g in ges_comps.split(',')])

            if ges_comps.intersection(self.all_descriptor_ids):
                out.append(row)

        return out

    @db.use_db_session('2018')
    def get_report_data(self):
        # TODO check if data is filtered by features for D1
        db_data = getattr(self, 'get_data_from_view_' + self.article, None)

        countries = self.available_countries
        region = self.country_region_code
        descriptor_obj = self.descriptor_obj

        fields = get_report_definition('2018', self.article).get_fields()

        impl_class = getattr(self, self.article)
        result = []

        for field in fields:
            row_class = impl_class(self, self.request, db_data, descriptor_obj,
                                   region, countries, field)
            field_data_method = getattr(row_class, field.getrowdata, None)
            if not field_data_method:
                continue

            result.append(field_data_method())

        return result

    def auto_translate(self):
        data = self.get_report_data()
        translatables = self.TRANSLATABLES
        seen = set()

        for compoundrow in data:
            rows =  compoundrow.rows

            for row in rows:
                sub_title, values = row
                if compoundrow.field.name in translatables:
                    for indx, value in enumerate(values):
                        if not value:
                            continue

                        if value not in seen:
                            country_code = self.available_countries[indx][0]
                            retrieve_translation(country_code, value)
                            seen.add(value)

        messages = IStatusMessage(self.request)
        messages.add(u"Auto-translation initiated, please refresh "
                     u"in a couple of minutes", type=u"info")

        url = self.context.absolute_url() + '/@@view-report-data-2018'
        return self.request.response.redirect(url)

    # @cache(get_reportdata_key, dependencies=['translation'])
    def render_reportdata(self):
        logger.info("Quering database for 2018 report data: %s %s %s",
                    self.country_region_code, self.article,
                    self.descriptor)

        data = self.get_report_data()

        report_header = self.report_header_template(
            title="Member State report: {} / {} / {} / 2018".format(
                self.country_region_name,
                self.descriptor_title,
                self.article
            ),
            factsheet=None,
            # TODO: find out how to get info about who reported
            report_by='Report by',
            report_due='2018-10-15',
            help_text=self.help_text,
            use_translation=True
        )

        # template = getattr(self, self.article, None)
        template = self.template

        return template(data=data, report_header=report_header)

    def __call__(self):
        if 'translate' in self.request.form:
            return self.auto_translate()

        report_html = self.render_reportdata()
        trans_edit_html = self.translate_view()()
        self.report_html = report_html + trans_edit_html

        @timeit
        def render_html():
            return self.index()

        return render_html()