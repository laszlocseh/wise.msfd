""" Forms and views for Article 13-14 search
"""
from sqlalchemy import and_

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.field import Fields

from . import interfaces
from .. import db, sql
from ..base import EmbeddedForm
from ..db import get_all_records, get_all_records_join
from ..interfaces import IMarineUnitIDsSelect
from .. labels import COMMON_LABELS
from ..utils import default_value_from_field
from .base import ItemDisplayForm, MainForm
from .utils import data_to_xls

# all_values_from_field,#


class StartArticle1314Form(MainForm):
    """
    """
    fields = Fields(interfaces.IStartArticles1314)
    fields['region_subregions'].widgetFactory = CheckBoxFieldWidget

    name = 'msfd-c3'
    record_title = 'Articles 13 & 14'
    session_name = '2012'

    def get_subform(self):
        return MemberStatesForm(self, self.request)

    # This is needed because of metatype weirdness. Would be nice to have an
    # explanation of why this happens, only for this MainForm
    def default_report_type(self):
        return default_value_from_field(self, self.fields['report_type'])


class MemberStatesForm(EmbeddedForm):
    """ Select the member states based on region
    """
    # fields = Fields(interfaces.IMemberStates)
    fields = Fields(interfaces.IA1314MemberStates)

    fields['member_states'].widgetFactory = CheckBoxFieldWidget

    def get_subform(self):
        return MarineUnitIDsForm(self, self.request)

    def get_available_marine_unit_ids(self):
        # TODO: use available marine unit ids from t_MSFD4_GegraphicalAreasID
        mc = sql.MSFD13ReportingInfo

        ms = self.get_selected_member_states()
        report_type = self.context.data['report_type']

        count, res = db.get_all_records_join(
            [mc.MarineUnitID],
            sql.MSFD13ReportingInfoMemberState,
            and_(sql.MSFD13ReportingInfoMemberState.MemberState.in_(ms),
                 mc.ReportType == report_type),
        )

        return [count, [x[0] for x in res]]


class MarineUnitIDsForm(EmbeddedForm):
    """ Select the MarineUnitID based on MemberState, Region and Area
    """

    # TODO: properly show only available marine unit ids
    fields = Fields(IMarineUnitIDsSelect)
    fields['marine_unit_ids'].widgetFactory = CheckBoxFieldWidget

    def get_subform(self):
        mc = sql.MSFD13ReportingInfo
        report_type = self.context.context.data['report_type']

        count, res = db.get_all_records(
            mc.ID,
            and_(mc.MarineUnitID.in_(self.data.get('marine_unit_ids', [])),
                 mc.ReportType == report_type)
        )
        self.data['report_ids'] = [x[0] for x in res]

        mc = sql.MSFD13Measure

        count, res = db.get_all_records(
            mc,
            mc.ReportID.in_(self.data['report_ids'])
        )
        res = set([(x.UniqueCode, x.Name) for x in set(res)])
        self.data['unique_codes'] = sorted(res)

        return UniqueCodesForm(self, self.request)


class UniqueCodesForm(EmbeddedForm):
    """ Select the unique codes
    """

    fields = Fields(interfaces.IA1314UniqueCodes)

    fields['unique_codes'].widgetFactory = CheckBoxFieldWidget

    def get_subform(self):
        return A1314ItemDisplay(self, self.request)


class A1314ItemDisplay(ItemDisplayForm):
    """ The implementation for the Article 9 (GES determination) form
    """
    extra_data_template = ViewPageTemplateFile('pt/extra-data-item.pt')
    pivot_template = ViewPageTemplateFile('pt/extra-data-pivot-notselect.pt')

    css_class = "left-side-form"

    mapper_class = sql.MSFD13MeasuresInfo
    order_field = 'ID'

    def get_current_country(self):
        if not self.item:
            return

        mc = sql.MSFD13ReportingInfoMemberState
        report_id = self.item.ReportID

        count, data = get_all_records(
            mc,
            mc.ReportID == report_id
        )
        country_code = data[0].MemberState
        print_value = self.print_value(country_code)

        return print_value

    def download_results(self):
        mc_join = sql.MSFD13ReportingInfoMemberState

        mc_fields = self.get_obj_fields(self.mapper_class, False)
        fields = [mc_join.MemberState] + \
                 [getattr(self.mapper_class, field) for field in mc_fields]

        muids = self.context.data.get('unique_codes', [])

        sess = db.session()
        q = sess.query(*fields).\
            join(mc_join, self.mapper_class.ReportID == mc_join.ReportID).\
            filter(self.mapper_class.UniqueCode.in_(muids))
        data = [x for x in q]

        report_ids = [row.ReportID for row in data]
        mc_report = sql.MSFD13ReportInfoFurtherInfo
        count, data_report = get_all_records(
            mc_report,
            mc_report.ReportID.in_(report_ids)
        )

        xlsdata = [
            ('MSFD13MeasuresInfo', data),  # worksheet title, row data
            ('MSFD13ReportInfoFurtherInfo', data_report),
        ]

        return data_to_xls(xlsdata)

    def get_db_results(self):
        page = self.get_page()
        mc = self.mapper_class

        count, item, extra_data = db.get_collapsed_item(
            mc,
            self.order_field,
            [{'InfoType': ['InfoText']}],
            mc.UniqueCode.in_(self.context.data.get('unique_codes', [])),
            page=page,
        )
        self.extra_data = extra_data.items()

        return [count, item]

    def get_extra_data(self):
        if not self.item:
            return {}

        report_id = self.item.ReportID
        mc = sql.MSFD13ReportInfoFurtherInfo

        count, item = db.get_related_record(mc, 'ReportID', report_id)

        return ('Report info', item)

    def extras(self):
        html = self.pivot_template(extra_data=self.extra_data)

        return self.extra_data_template() + html

    def custom_print_value(self, row_label, val):
        """ Used to create a customized print value, like adding the
            descriptor code into the label
            for a specific data section(row_label)

        :param row_label: 'RelevantGESDescriptors'
        :param val: 'D5'
        :return:
        """

        row_labels = ('RelevantGESDescriptors', )

        if row_label in row_labels:
            label = COMMON_LABELS.get(val, val)
            value = '<span title="{0}">({0}) {1}</span>'.format(val, label)

            return value

        return self.print_value(val)
