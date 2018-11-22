
from eea.cache import cache

from wise.msfd import db, sql, sql_extra
from wise.msfd.gescomponents import get_ges_criterions
from Products.Five.browser.pagetemplatefile import (PageTemplateFile,
                                                    ViewPageTemplateFile)

from ..base import BaseComplianceView
from .a8_utils import UtilsArticle8
from .utils import (Row, CompoundRow, TableHeader, List,
                    countries_in_region, muids_by_country, get_key,
                    get_percentage)


class RegDescA8(BaseComplianceView):
    session_name = '2012'
    template = ViewPageTemplateFile('pt/report-data-table.pt')

    @property
    def descriptor(self):
        return 'D5'

    def __call__(self):
        db.threadlocals.session_name = self.session_name

        self.region = 'BAL'

        self.countries = countries_in_region(self.region)
        self.all_countries = muids_by_country()

        self.utils_art8 = UtilsArticle8(self.descriptor)

        self.import_data = self.get_import_data()
        self.base_data = self.get_base_data()
        self.suminfo2_data = self.get_suminfo2_data()
        self.status_data = self.get_status_data()

        allrows = [
            self.get_countries(),
            self.get_marine_unit_id_nrs(),
            # TODO show the reported value, or Reported/Not reported ??
            self.get_suminfo1_row(),
            self.get_suminfo2_row(),
            self.get_criteria_status_row(),
            self.get_activity_type_row(),
            self.get_assessment_date_row()
        ]

        return self.template(rows=allrows)

    def get_status_data(self):
        tables = self.utils_art8.tables

        results = {}
        for table in tables:
            suffix = 'Assesment'

            # if table.startswith('MSFD8a'):
            #     suffix = 'StatusAssessment'

            mc_name = '{}{}'.format(table.replace('_', ''), suffix)
            mc = getattr(sql, mc_name, None)

            if not mc:
                continue

            col_id = '{}_ID'.format(table)
            base_ids = [getattr(x, col_id) for x in self.base_data[table]]

            _, res = db.get_all_records(
                mc,
                getattr(mc, table).in_(base_ids)
            )

            results[table] = res

        return results

    def get_import_data(self):
        tables = self.utils_art8.tables
        import_res = {}

        for table in tables:
            if table.startswith('MSFD8a'):
                prefix = 'MSFD8a'
            else:
                prefix = 'MSFD8b'

            mc = getattr(sql, '{}Import'.format(prefix))
            region = '{}_Import_ReportingRegion'.format(prefix)
            country = '{}_Import_ReportingCountry'.format(prefix)
            id_ = '{}_Import_ID'.format(prefix)

            col_region = getattr(mc, region)
            count, res = db.get_all_records(
                mc,
                col_region == self.region
            )

            result = {}

            for row in res:
                c = getattr(row, country)
                i = getattr(row, id_)
                result[c] = i

            import_res[table] = result

        return import_res

    def get_base_data(self):
        tables = self.utils_art8.tables

        results = {}
        for table in tables:
            mc = self.utils_art8.get_base_mc(table)
            conditions = []

            # topics_needed = self.utils_art8.get_topic_conditions(table)
            # if topics_needed:
            #     conditions.append(mc.Topic.in_(topics_needed))

            col_id = getattr(mc, '{}_Import'.format(table))

            conditions.append(col_id.in_(self.import_data[table].values()))

            _, res = db.get_all_records(
                mc,
                *conditions
            )

            results[table] = res

        return results

    def get_suminfo2_data(self):
        tables = self.utils_art8.tables

        results = {}
        for table in tables:
            suffix = 'SumInfo2ImpactedElement'

            # if table.startswith('MSFD8a'):
            #     suffix = 'Summary2'

            mc_name = '{}{}'.format(table.replace('_', ''), suffix)
            mc = getattr(sql, mc_name, None)

            if not mc:
                continue

            col_id = '{}_ID'.format(table)
            base_ids = [getattr(x, col_id) for x in self.base_data[table]]

            _, res = db.get_all_records(
                mc,
                getattr(mc, table).in_(base_ids)
            )

            results[table] = res

        return results

    def get_suminfo2_elements(self):
        # Summary2 for MSFD8a
        result = []

        for table, res in self.suminfo2_data.items():
            elements = [x.SumInfo2 for x in res]

            result.extend(elements)

        result = sorted(set(result))

        return result

    def get_topics(self):
        result = []

        for table, res in self.base_data.items():
            topics_needed = self.utils_art8.get_topic_conditions(table)

            topics = [x.Topic for x in res]

            topics = list(set(topics_needed) & set(topics))

            result.extend(topics)

        result = sorted(result)

        return result

    def get_base_value(self, country, topic, col_name):
        for table, res in self.base_data.items():
            for row in res:
                if row.Topic != topic:
                    continue

                import_id = self.import_data[table][country]
                import_col = '{}_Import'.format(table)

                if import_id != getattr(row, import_col, 0):
                    continue

                return getattr(row, col_name, '')

        return ''

    def get_countries(self):
        return TableHeader('Member state', self.countries)

    def get_marine_unit_id_nrs(self):
        row = Row('Number used',
                  [len(self.all_countries[c]) for c in self.countries])

        return CompoundRow('MarineUnitID [Reporting area]', [row])

    def get_suminfo1_row(self):
        col_name = 'SumInfo1'

        rows = []

        self.topics = self.get_topics()

        for topic in self.topics:
            results = []
            for country in self.countries:
                value = self.get_base_value(country, topic, col_name)
                results.append(value)

            row = Row(topic, results)
            rows.append(row)

        label = 'PressureLevelN/P/Oconcentration/' \
                'ImpactsPressureWater/Seabed: ' \
                'SumInfo1 ' \
                '[ProportionValueAchieved]'

        return CompoundRow(label, rows)

    def get_suminfo2_row(self):
        rows = []

        elements = self.get_suminfo2_elements()

        for element in elements:
            results = []

            for country in self.countries:
                for table, res in self.suminfo2_data.items():
                    value = ''
                    base_import_id = self.import_data[table][country]

                    col_id = '{}_ID'.format(table)
                    col_import_id = '{}_Import'.format(table)
                    data = self.base_data[table]

                    base_ids = [
                        getattr(x, col_id)
                        for x in data
                        if getattr(x, col_import_id) == base_import_id
                    ]

                    suminfo_ids = [
                        getattr(x, table)
                        for x in res
                        if x.SumInfo2 == element
                    ]

                    intersect = set(suminfo_ids) & set(base_ids)

                    if intersect:
                        value = 'Reported'
                        break

                results.append(value)

            row = Row(element, results)
            rows.append(row)

        label = 'ImpactsPressureWater/Seabed: ' \
                'SumInfo2'

        return CompoundRow(label, rows)

    def get_criteria_status_row(self):
        # MSFD8b_Nutrients_Assesment
        # MSFD8a_Species_StatusAssessment
        rows = []

        for topic in self.topics:
            topic_alt = self.utils_art8.get_proper_topic(topic)
            results = []
            for country in self.countries:
                value = ''
                for table, res in self.base_data.items():
                    base_import_id = self.import_data[table][country]
                    col_id = '{}_ID'.format(table)
                    col_import_id = '{}_Import'.format(table)

                    for row in res:
                        top = row.Topic
                        imp_id_ = getattr(row, col_import_id)

                        if base_import_id != imp_id_:
                            continue

                        if top != topic_alt:
                            continue

                        id_ = getattr(row, col_id)

                        status = [
                            x.Status
                            for x in self.status_data[table]
                            if getattr(x, table) == id_
                        ]

                        if status:
                            value = status[0]
                            break

                    if value:
                        break

                results.append(value)

            row = Row(topic, results)
            rows.append(row)

        label = 'Status [CriteriaStatus]'

        return CompoundRow(label, rows)

    def get_activity_type_row(self):
        # MSFD8b_Nutrients_Activity
        
        pass

    def get_assessment_date_row(self):
        pass