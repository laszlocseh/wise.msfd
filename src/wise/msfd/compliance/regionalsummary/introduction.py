
from sqlalchemy import or_

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from wise.msfd import db
from wise.msfd.data import get_text_reports_2018
from wise.msfd.sql2018 import (MarineReportingUnit, ReportingHistory,
                               t_MarineWaters)
from wise.msfd.utils import ItemList

from ..nationalsummary.introduction import Introduction
from .base import BaseRegSummaryView
from .utils import SimpleTable


class RegionalIntroduction(BaseRegSummaryView, Introduction):
    """ Make National summary code compatible for Regional summary """

    template = ViewPageTemplateFile('pt/introduction.pt')
    rep_date_tpl = u'<a href="{}">{}</a>'

    def default(self):
        return ['-' for _ in self.available_countries]

    @property
    def information_memberstate(self):
        text = u"""
By October 2018, the Member States were due to submit updates of the assessment
 of their marine waters (Article 8), the determination of GES (Article 9) and 
 the setting of environmental targets (Article 10), in accordance with 
 Article 17 of the Marine Strategy Framework Directive (MSFD, Directive 2008/56/EC).
<br/>The table gives details of when the Member States submitted their reports, in text (usually pdf) and elecronic (xml) format. E-reporting was undertaken in relation to specific geographic areas (Marine Reporting Units) which are specifed in an xml file (4geo.xml) and accompanied by geographic information system (GIS) shapefiles which allow the reported information to be displayed as maps. In cases where the Member State uploaded reports in stages (text reports) or modified previous versions (e-reports), multiple dates are shown.        
"""
        return text

    def _get_memberstate_reports(self, data, obligation):
        res = []

        for country_code, country_name in self.available_countries:
            values = []
            for row in data:
                if row.ReportingObligation != obligation:
                    continue

                if row.CountryCode != country_code:
                    continue

                date_received = row.DateReceived.date()
                envelope_url = row.LocationURL.replace(row.FileName, '')

                values.append((envelope_url, date_received))

            values = sorted(set(values), key=lambda i: i[1], reverse=True)
            unique_values = [
                self.rep_date_tpl.format(v[0], v[1])

                for v in values
            ]

            res.append(ItemList(unique_values, sort=False))

        return res

    def get_text_reports(self):
        res = []

        for country_code, country_name in self.available_countries:
            text_reports = get_text_reports_2018(country_code)
            values = []

            for row in text_reports:
                file_url = row[0]
                release_date = row[1].date()
                envelope_url = '/'.join(file_url.split('/')[:-1])

                values.append((envelope_url, release_date))

            values = sorted(set(values), key=lambda i: i[1], reverse=True)
            unique_values = [
                self.rep_date_tpl.format(v[0], v[1])

                for v in values
            ]

            res.append(ItemList(unique_values, sort=False))

        return res

    @db.use_db_session('2018')
    def memberstate_reports(self):
        header = u"Dates of Member State's reports for 2018 updates of " \
                u"Articles 8, 9 and 10"
        mc = ReportingHistory
        _, data = db.get_all_records(
            mc,
            # mc.EnvelopeStatus == 'End',
        )

        rows = [
            ("", [x[1] for x in self.available_countries]),
            ("Text reports (pdf)", self.get_text_reports()),
            ("Electronic reports (xml)", self._get_memberstate_reports(
                data, 'MSFD - Articles 8, 9 and 10 - XML data')),
            ("Geographic data (4geo.xml; GIS shapefiles)",
             self._get_memberstate_reports(
                 data, 'MSFD - Article 4 - Spatial data')
             )
        ]
        view = SimpleTable(self, self.request, header, rows)

        return view()

    def _get_marine_water_by_type(self, data, types):
        res = []

        for country_id, country_name in self.available_countries:
            values = [
                int(row.Area_km2)
                for row in data
                if (row.Country == country_id and
                    row.Type in types and
                    row.Subregion in self.available_subregions)
            ]

            res.append("{:,}".format(sum(values)))

        return res

    def get_water_seabed_row(self, data):
        types = ['Water column & seabed/subsoil', 'Marine waters']

        return self._get_marine_water_by_type(data, types)

    def get_seabed_only_row(self, data):
        types = ['Seabed/subsoil']

        return self._get_marine_water_by_type(data, types)

    def get_proportion_row(self, data):
        types = ['Water column & seabed/subsoil', 'Marine waters']
        res = []
        total = sum([
            float(row.Area_km2)
            for row in data
            if (row.Type in types and
                row.Subregion in self.available_subregions)
        ])

        for country_id, country_name in self.available_countries:
            values = [
                float(row.Area_km2)
                for row in data
                if (row.Country == country_id and
                    row.Type in types and
                    row.Subregion in self.available_subregions)
            ]
            country_total = sum(values)
            res.append("{:.1f}%".format(country_total/total * 100))

        return res

    @db.use_db_session('2018')
    def marine_waters(self):
        header = u"Length of coastline and area of marine waters per Member " \
                u"State (based on GIS data reported for MSFD by each Member " \
                u"State)"

        column_names = ['Country', 'Subregion', 'Area_km2', 'Type']

        cnt, data = db.get_all_specific_columns(
            [getattr(t_MarineWaters.c, c) for c in column_names]
        )

        rows = [
            ("", [x[1] for x in self.available_countries]),
            ("Length of coastline (km)", self.default()),
            ("Area of marine waters (water column and seabed) (km2)",
             self.get_water_seabed_row(data)),
            ("Area of marine waters (seabed only - beyond EEZ or quivalent) "
             "(km2)", self.get_seabed_only_row(data)),
            ("Proportion of Baltic Sea region per Member State (areal %)",
             self.get_proportion_row(data))
        ]
        view = SimpleTable(self, self.request, header, rows)

        return view()

    @db.use_db_session('2018')
    def get_number_of_mrus(self):
        columns = ['CountryCode', 'MarineReportingUnitId', 'desigBegin',
                   '_4geo']
        cnt, data = db.get_all_specific_columns(
            [getattr(MarineReportingUnit, c)
             for c in columns],
            or_(MarineReportingUnit.desigBegin.isnot(None),
                MarineReportingUnit._4geo.isnot(None))
        )

        res = []

        for country_code, country_name in self.available_countries:
            cnt = [
                x
                for x in data
                if x.CountryCode == country_code
            ]

            res.append(len(cnt))

        return res

    def assessment_areas(self):
        header = u"Reporting areas of the Member States"
        title = u"The table gives details about the Marine Reporting Units " \
                u"used for the 2018 reporting on updates of Articles 8, 9 " \
                u"and 10."

        rows = [
            ("", [x[1] for x in self.available_countries]),
            ("Number of Marine Reporting Units used",
             self.get_number_of_mrus()),
            ("Range of extent of Marine Reporting Units (km2)",
             self.default()),
            ("Average extent of Marine Reporting Units (km2)", self.default())
        ]
        view = SimpleTable(self, self.request, header, rows, title)

        return view()

