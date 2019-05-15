from collections import defaultdict
from sqlalchemy import or_

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from wise.msfd import db, sql, sql_extra
from wise.msfd.data import countries_in_region, muids_by_country
from wise.msfd.utils import CompoundRow, ItemList, Row, TableHeader

from ..base import BaseComplianceView
from .base import BaseRegDescRow
from .utils import compoundrow


class RegDescA102018Row(BaseRegDescRow):
    """"""
    @compoundrow
    def get_target_row(self):
        rows = []
        values = []
        for country_code, country_name in self.countries:
            data = set([
                row.TargetCode
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.TargetCode
            ])
            value = self.not_rep
            if data:
                value = len(data)

            values.append(value)

        rows.append(('Number defined', values))

        return rows

    @compoundrow
    def get_indicators_row(self):
        rows = []
        values = []
        for country_code, country_name in self.countries:
            data = set([
                row.Indicators
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.Indicators
            ])
            value = self.not_rep
            if data:
                value = len(data)

            values.append(value)

        rows.append(('Number defined', values))

        return rows

    @compoundrow
    def get_timescale_row(self):
        rows = []
        values = []
        for country_code, country_name in self.countries:
            data = set([
                row.TimeScale
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.TimeScale
            ])
            value = self.not_rep
            if data:
                value = self.rep

            values.append(value)

        rows.append(('', values))

        return rows

    @compoundrow
    def get_updatedate_row(self):
        rows = []
        values = []
        for country_code, country_name in self.countries:
            data = set([
                row.UpdateDate
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.UpdateDate
            ])
            value = self.not_rep
            if data:
                value = max(data)

            values.append(value)

        rows.append(('', values))

        return rows

    @compoundrow
    def get_updatetype_row(self):
        rows = []
        values = []
        for country_code, country_name in self.countries:
            data = set([
                row.UpdateType
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.UpdateType
            ])
            value = self.not_rep
            if data:
                value = self.rep

            values.append(value)

        rows.append(('', values))

        return rows

    @compoundrow
    def get_measures_row(self):
        rows = []
        values = []
        for country_code, country_name in self.countries:
            data = set([
                row.Measures
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.Measures
            ])
            value = self.not_rep
            if data:
                value = len(data)

            values.append(value)

        rows.append(('Number reported', values))

        return rows

    # TODO needs to be finished
    @compoundrow
    def get_targetvalue_row(self):
        rows = []
        values = []

        indics = self.get_unique_values('Indicators')

        for country_code, country_name in self.countries:
            count_target_values = len(set([
                row.TargetCode
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.TargetCode
                   and row.TargetValue
            ]))
            count_total_targets = len(set([
                row.TargetCode
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.TargetCode
            ]))
            value_target = "Targets ({} of {})".format(count_target_values,
                                                       count_total_targets)

            count_indics_values = len(set([
                row.Indicators
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.Indicators
                   and row.TargetValue
            ]))
            count_total_indics = len(set([
                row.Indicators
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.Indicators
            ]))
            value_indic = "Indicators ({} of {})".format(count_indics_values,
                                                         count_total_indics)

            values.append("; ".join((value_target, value_indic)))

        rows.append(('Quantitative values provided', values))

        return rows

    @compoundrow
    def get_targetstatus_row(self):
        rows = []
        values = []

        for country_code, country_name in self.countries:
            tar_status_counter = defaultdict(int)

            data = set([
                (row.TargetCode, row.TargetStatus)
                for row in self.db_data
                if row.CountryCode == country_code
            ])
            for item in data:
                target_status = item[1]
                if not target_status:
                    tar_status_counter['Status not reported'] += 1
                    continue

                tar_status_counter[target_status] += 1

            count_vals = [
                "{} - {}".format(k, v)
                for k, v in sorted(tar_status_counter.items(),
                                   key=lambda i: i[1], reverse=True)
            ]
            values.append("; ".join(count_vals))

        rows.append(('', values))

        return rows

    @compoundrow
    def get_assessmentperiod_row(self):
        rows = []
        values = []
        for country_code, country_name in self.countries:
            data = set([
                row.AssessmentPeriod
                for row in self.db_data
                if row.CountryCode == country_code
                   and row.AssessmentPeriod
            ])
            value = self.not_rep
            if data:
                value = max(data)

            values.append(value)

        rows.append(('', values))

        return rows


class RegDescA10(BaseComplianceView):
    # TODO: this is hard to implement
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
        self.muids_in_region = []

        for c in self.countries:
            self.muids_in_region.extend(self.all_countries[c])

        self.import_data, self.target_data = self.get_base_data()
        self.features_data = self.get_features_data()

        allrows = [
            self.get_countries_row(),
            self.get_marine_unit_id_nrs(),
            self.get_threshold_value(),
            self.get_reference_point_type(),
            self.get_baseline(),
            self.get_proportion(),
            self.get_type_of_target(),
            self.get_timescale(),
            self.get_interim_of_ges(),
            self.get_compatibility(),
            self.get_physical_features(),
            self.get_predominant_habitats(),
            self.get_functional_groups(),
            self.get_pressures(),
        ]

        return self.template(rows=allrows)

    def get_import_id(self, country):
        for imp in self.import_data:
            if imp.MSFD10_Import_ReportingCountry == country:
                import_id = imp.MSFD10_Import_ID

                return import_id

        return 0

    def get_base_data(self):
        imp = sql.MSFD10Import
        target = sql.MSFD10Target
        des_crit = sql_extra.MSFD10DESCrit

        descriptor = self.descriptor
        descriptor_code = descriptor[1:]

        count, import_data = db.get_all_records(
            imp,
            imp.MSFD10_Import_ReportingCountry.in_(self.countries),
            imp.MSFD10_Import_ReportingRegion == self.region
        )
        import_ids = [x.MSFD10_Import_ID for x in import_data]

        dc_indicator = getattr(des_crit, 'GESDescriptorsCriteriaIndicators')
        count, target_data = db.get_all_records_outerjoin(
            target,
            des_crit,
            target.MSFD10_Targets_Import.in_(import_ids),
            target.Topic == 'EnvironmentalTarget',
            or_(dc_indicator == descriptor,
                dc_indicator.like('{}.%'.format(descriptor_code)))
        )

        return import_data, target_data

    def create_base_row(self, label_name, attr_name):
        results = []

        for country in self.countries:
            import_id = self.get_import_id(country)

            value = ''

            if not import_id:
                results.append(value)

                continue

            for tar in self.target_data:
                if tar.MSFD10_Targets_Import == import_id:
                    value = getattr(tar, attr_name, '')

                    break

            results.append(value)

        row = Row('', results)

        return CompoundRow(label_name, [row])

    def get_features_data(self):
        feat = sql_extra.MSFD10FeaturePressures
        target_ids = [x.MSFD10_Target_ID for x in self.target_data]

        count, feat_res = db.get_all_records(
            feat,
            feat.MSFD10_Target.in_(target_ids),
        )

        return feat_res

    def create_feature_row(self, label_name):
        rows = []

        features = []

        for row in self.features_data:
            if row.FeatureType == label_name:
                val = row.PhysicalChemicalHabitatsFunctionalPressures
                features.append(val)

                val_other = row.Other

                if val_other:
                    features.append(val_other)

        features = sorted(set(features))

        for feature in features:
            results = []

            for country in self.countries:
                import_id = self.get_import_id(country)

                value = ''

                if not import_id:
                    import pdb; pdb.set_trace()
                    # results.append(value)
                    # continue

                target_ids = []

                for tar in self.target_data:
                    if tar.MSFD10_Targets_Import == import_id:
                        target_ids.append(tar.MSFD10_Target_ID)

                for r in self.features_data:
                    if r.MSFD10_Target not in target_ids:
                        continue

                    if r.FeatureType != label_name:
                        continue

                    feat = r.PhysicalChemicalHabitatsFunctionalPressures

                    if feat == feature or r.Other == feature:
                        value = 'Reported'

                        break

                results.append(value)

            row = Row(feature, results)
            rows.append(row)

        return CompoundRow(label_name, rows)

    def get_countries_row(self):
        return TableHeader('Member state', self.countries)

    def get_marine_unit_id_nrs(self):
        row = Row('Number used',
                  [len(self.all_countries[c]) for c in self.countries])

        return CompoundRow('MarineUnitID', [row])

    # TODO how to implement this
    def get_threshold_value(self):
        results = ['Not implemented'] * len(self.countries)
        row = Row('Quantitative values provided', results)

        return CompoundRow(
            'Threshold value [TargetValue]',
            [row]
        )

    def get_reference_point_type(self):
        label = 'Reference point type'
        attr = 'ReferencePointType'

        return self.create_base_row(label, attr)

    def get_baseline(self):
        label = 'Baseline'
        attr = 'Baseline'

        return self.create_base_row(label, attr)

    def get_proportion(self):
        label = 'Proportion'
        attr = 'Proportion'

        return self.create_base_row(label, attr)

    def get_type_of_target(self):
        label = 'Type of target/indicator'
        attr = 'TypeTargetIndicator'

        return self.create_base_row(label, attr)

    def get_timescale(self):
        label = 'Timescale'
        attr = 'TimeScale'

        return self.create_base_row(label, attr)

    def get_interim_of_ges(self):
        label = 'Interim or GES target'
        attr = 'InterimGESTarget'

        return self.create_base_row(label, attr)

    def get_compatibility(self):
        label = 'Compatibility with existing targets/indicators'
        attr = 'CompatibilityExistingTargets'

        return self.create_base_row(label, attr)

    def get_physical_features(self):
        label = 'Physical/chemical features'

        return self.create_feature_row(label)

    def get_predominant_habitats(self):
        label = 'Predominant habitats'

        return self.create_feature_row(label)

    def get_functional_groups(self):
        label = 'Functional group'

        return self.create_feature_row(label)

    def get_pressures(self):
        label = 'Pressures'

        return self.create_feature_row(label)
