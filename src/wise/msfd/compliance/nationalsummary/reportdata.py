import logging
from collections import defaultdict, namedtuple

from plone.api.portal import get_tool

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from wise.msfd import db, sql2018
# from wise.msfd.compliance.base import BaseComplianceView
from wise.msfd.compliance.interfaces import (IDescriptorFolder,
                                             INationalDescriptorAssessment,
                                             INationalDescriptorsFolder,
                                             INationalRegionDescriptorFolder)
from wise.msfd.compliance.scoring import (CONCLUSIONS, get_range_index,
                                          OverallScores)
from wise.msfd.data import get_report_filename
from wise.msfd.utils import (ItemList, TemplateMixin,  # RawRow,
                             db_objects_to_dict, timeit)

from ..nationaldescriptors.a7 import Article7
from ..nationaldescriptors.a34 import Article34
from ..nationaldescriptors.base import BaseView
from ..nationaldescriptors.main import (ARTICLE_WEIGHTS,
                                        CONCLUSION_COLOR_TABLE,
                                        get_assessment_data_2012_db,
                                        filter_assessment_data_2012)
from .base import BaseNatSummaryView
# from .download import download

logger = logging.getLogger('wise.msfd')


DESCRIPTOR_SUMMARY = namedtuple(
    'DescriptorSummary',
    ['assessment_summary', 'progress_assessment', 'recommendations',
     'adequacy', 'consistency', 'coherence', 'overall_score_2018',
     'overall_score_2012', 'change_since_2012']
)


def compoundrow(self, title, rows):
    """ Function to return a compound row for 2012 report"""

    FIELD = namedtuple("Field", ["name", "title"])
    field = FIELD(title, title)

    return CompoundRow(self, self.request, field, rows)


class CompoundRow(TemplateMixin):
    template = ViewPageTemplateFile('pt/compound-row.pt')

    def __init__(self, context, request, field, rows):
        self.context = context
        self.request = request
        self.field = field
        self.rows = rows
        self.rowspan = len(rows)


class NatSummaryTable(BaseNatSummaryView):
    """ Base class for tables """


class Article34Copy(Article34):
    """ Class to override the template """
    template = ViewPageTemplateFile('pt/report-data-secondary.pt')
    title = "Articles 3 & 4 Marine regions"


class Article7Copy(Article7):
    """ Class to override the template """
    template = ViewPageTemplateFile('pt/report-data-secondary.pt')
    title = "Article 7 Competent authorities"


class ArticleTable(BaseView):
    impl = {
        'Art3-4': Article34Copy,
        'Art7': Article7Copy,
    }

    is_translatable = True

    def __init__(self, context, request, article):
        super(ArticleTable, self).__init__(context, request)

        self._article = article
        self.klass = self.impl[article]

    year = '2012'

    @property
    def article(self):
        return self._article

    @property
    def descriptor(self):
        return 'Not linked'

    @property
    def muids(self):
        return []

    @property
    def country_region_code(self):
        return 'No region'

    def get_article_title(self, klass):
        tmpl = u"<h4>{}</h4>"
        title = klass.title

        return tmpl.format(title)

    def get_report_filename(self, art=None):
        # needed in article report data implementations, to retrieve the file

        return get_report_filename(
            self.year, self.country_code, self.country_region_code,
            art or self.article, self.descriptor
        )

    def __call__(self):
        try:
            self.view = self.klass(
                self, self.request, self.country_code,
                self.country_region_code, self.descriptor, self.article,
                self.muids
            )
            rendered_view = self.view()
        except:
            rendered_view = 'Error getting report'

        return self.get_article_title(self.klass) + rendered_view


class ReportingHistoryTable(BaseNatSummaryView):
    """ Reporting history and performance
    """

    template = ViewPageTemplateFile('pt/report-history-compound-table.pt')

    def __init__(self, context, request):
        super(ReportingHistoryTable, self).__init__(context, request)

        self.data = self.get_reporting_history_data()

    @db.use_db_session('2018')
    def get_reporting_history_data(self):
        mc = sql2018.ReportingHistory

        _, res = db.get_all_records(
            mc,
            mc.CountryCode == self.country_code
        )

        res = db_objects_to_dict(res)

        return res

    def location_url(self, location, filename):
        tmpl = "<a href={} target='_blank'>{}</a>"
        location = location.replace(filename, '')

        return tmpl.format(location, location)

    def format_date(self, date):
        if not date:
            return date

        # formatted = date.strftime('%m/%d/%Y')
        formatted = date.date()

        return formatted

    def headers(self):
        headers = (
            'Report format', 'Files available', 'Access to reports',
            'Report due', 'Report received', 'Reporting delay (days)'
        )

        return headers

    def get_article_row(self, obligation):
        # Group the data by report type, envelope, report due, report date
        # and report delay
        data = [
            row for row in self.data

            if row.get('ReportingObligation') == obligation

        ]
        rows = []

        groups = defaultdict(list)

        for row in data:
            filename = row.get('FileName')
            report_type = row.get('ReportType')
            envelope = self.location_url(row.get('LocationURL'), filename)
            report_due = self.format_date(row.get('DateDue'))
            report_date = self.format_date(row.get('DateReceived'))
            report_delay = row.get('ReportingDelay')
            k = (report_type, envelope, report_due, report_date, report_delay)

            groups[k].append(filename)

        for _k, filenames in groups.items():
            values = [
                _k[0],  # Report type
                ItemList(rows=filenames),  # Filenames
                _k[1],  # Envelope url
                _k[2],  # Report due
                _k[3],  # Report date
                _k[4]  # Report delay
            ]
            rows.append(values)

        sorted_rows = sorted(rows,
                             key=lambda _row: (_row[4], _row[2], _row[0]),
                             reverse=True)

        return sorted_rows

    def __call__(self):
        data = self.data

        obligations = set([x.get('ReportingObligation') for x in data])

        self.allrows = [
            compoundrow(self, obligation, self.get_article_row(obligation))

            for obligation in obligations
        ]

        return self.template(rows=self.allrows)


class DescriptorLevelAssessments(BaseView):

    template = ViewPageTemplateFile('pt/descriptor-level-assessments.pt')

    @property
    def rdas(self):
        catalog = get_tool('portal_catalog')
        brains = catalog.searchResults(
            portal_type='wise.msfd.regionaldescriptorassessment',
        )

        for brain in brains:
            obj = brain.getObject()

            yield obj

    def get_coherence_data(self, region_code, descriptor, article):
        """
        :return: {'color': 5, 'score': 0, 'max_score': 0,
                'conclusion': (1, 'Very poor')
            }
        """

        article_folder = None

        for obj in self.rdas:
            descr = obj.aq_parent.id.upper()

            if descr != descriptor:
                continue

            region = obj.aq_parent.aq_parent.id.upper()

            if region != region_code:
                continue

            art = obj.title

            if art != article:
                continue

            article_folder = obj

            break

        assess_data = self._get_assessment_data(article_folder)

        res = {
            'score': 0,
            'max_score': 0,
            'color': 0,
            'conclusion': (1, 'Very poor')
        }

        for k, score in assess_data.items():
            if '_Score' not in k:
                continue

            if not score:
                continue

            is_not_relevant = getattr(score, 'is_not_relevant', False)
            weighted_score = getattr(score, 'weighted_score', 0)
            max_weighted_score = getattr(score, 'max_weighted_score', 0)

            if not is_not_relevant:
                res['score'] += weighted_score
                res['max_score'] += max_weighted_score

        score_percent = int(round(res['max_score'] and (res['score'] * 100)
                                  / res['max_score'] or 0))
        score_val = get_range_index(score_percent)
        res['color'] = self.get_color_for_score(score_val)
        res['conclusion'] = (score_val, self.get_conclusion(score_val))

        return res

    def get_assessment_data_2012(self, region_code, country_name,
                                 descriptor, article):
        try:
            db_data_2012 = get_assessment_data_2012_db(
                country_name,
                descriptor,
                article
            )
            assessments_2012 = filter_assessment_data_2012(
                db_data_2012,
                region_code,
                []  # descriptor_criterions,
            )

            if assessments_2012.get(country_name):
                score_2012 = assessments_2012[country_name].score
                conclusion_2012 = assessments_2012[country_name].overall_ass
            else:       # fallback
                ctry = assessments_2012.keys()[0]
                score_2012 = assessments_2012[ctry].score
                conclusion_2012 = assessments_2012[ctry].overall_ass

        except:
            logger.exception("Could not get assessment data for 2012")
            score_2012 = 0
            conclusion_2012 = 'Not found'

        return int(round(score_2012)), conclusion_2012

    def get_color_for_score(self, score_value):
        return CONCLUSION_COLOR_TABLE[score_value]

    def get_conclusion(self, score_value):
        concl = list(reversed(CONCLUSIONS))[score_value]

        return concl

    def _get_assessment_data(self, article_folder):
        if not hasattr(article_folder, 'saved_assessment_data'):
            return {}

        return article_folder.saved_assessment_data.last()

    def _setup_phase_overall_scores(self, phase_overall_scores, assess_data,
                                    article):

        for k, score in assess_data.items():
            if '_Score' not in k:
                continue

            if not score:
                continue

            is_not_relevant = getattr(score, 'is_not_relevant', False)
            q_klass = score.question.klass
            weighted_score = getattr(score, 'weighted_score', 0)
            max_weighted_score = getattr(score, 'max_weighted_score', 0)

            if not is_not_relevant:
                p_score = getattr(phase_overall_scores, q_klass)
                p_score['score'] += weighted_score
                p_score['max_score'] += max_weighted_score

        phases = phase_overall_scores.article_weights[article].keys()

        for phase in phases:
            # set the conclusion and color based on the score for each phase
            phase_scores = getattr(phase_overall_scores, phase)
            score_val = phase_overall_scores.get_range_index_for_phase(phase)

            if phase == 'consistency' and article == 'Art9':
                phase_scores['conclusion'] = ('-', 'Not relevant')
                phase_scores['color'] = 0
            else:
                phase_scores['conclusion'] = (score_val,
                                              self.get_conclusion(score_val))
                phase_scores['color'] = self.get_color_for_score(score_val)

        return phase_overall_scores

    def _get_article_data(self, region_code, country_name, descriptor,
                          assess_data, article):
        phase_overall_scores = OverallScores(ARTICLE_WEIGHTS)

        # Get the adequacy, consistency scores from national descriptors
        phase_overall_scores = self._setup_phase_overall_scores(
            phase_overall_scores, assess_data, article)

        # Get the coherence scores from regional descriptors
        phase_overall_scores.coherence = self.get_coherence_data(
            region_code, descriptor, article
        )

        # if assess_data:
        #     import pdb; pdb.set_trace()

        adequacy_score_val, conclusion = \
            phase_overall_scores.adequacy['conclusion']
        score = phase_overall_scores.get_score_for_phase('adequacy')
        adequacy = ("{} ({}, {})".format(score, conclusion, adequacy_score_val),
                    phase_overall_scores.adequacy['color'])

        score_val, conclusion = phase_overall_scores.consistency['conclusion']
        score = phase_overall_scores.get_score_for_phase('consistency')
        consistency = ("{} ({}, {})".format(score, conclusion, score_val),
                       phase_overall_scores.consistency['color'])

        score_val, conclusion = phase_overall_scores.coherence['conclusion']
        score = phase_overall_scores.get_score_for_phase('coherence')
        coherence = ("{} ({}, {})".format(score, conclusion, score_val),
                     phase_overall_scores.coherence['color'])

        score_val, score = phase_overall_scores.get_overall_score(article)
        conclusion = self.get_conclusion(score_val)
        overall_score_2018 = (
            "{} ({}, {})".format(score, conclusion, score_val),
            self.get_color_for_score(score_val)
        )

        assessment_summary = assess_data.get(
            '{}_assessment_summary'.format(article)
        )
        progress_assessment = assess_data.get('{}_progress'.format(article))
        recommendations = assess_data.get('{}_recommendations'.format(article))

        score_2012, conclusion_2012 = self.get_assessment_data_2012(
            region_code, country_name, descriptor, article
        )
        overall_score_2012 = ("{} ({})".format(conclusion_2012, score_2012),
                              self.get_color_for_score(score_2012))

        change_since_2012 = int(adequacy_score_val - score_2012)

        res = DESCRIPTOR_SUMMARY(
            assessment_summary, progress_assessment, recommendations,
            adequacy, consistency, coherence, overall_score_2018,
            overall_score_2012, change_since_2012
        )

        return res

    def __call__(self):
        """
        :return: res =  [("Baltic Sea", [
                ("D7 - Hydrographical changes", [
                        ("Art8", DESCRIPTOR_SUMMARY),
                        ("Art9", DESCRIPTOR_SUMMARY),
                        ("Art10", DESCRIPTOR_SUMMARY),
                    ]
                ),
                ("D1.4 - Birds", [
                        ("Art8", DESCRIPTOR_SUMMARY),
                        ("Art9", DESCRIPTOR_SUMMARY),
                        ("Art10", DESCRIPTOR_SUMMARY),
                    ]
                ),
            ]
        )]
        """

        res = []

        portal_catalog = self.context.context.portal_catalog
        brains = portal_catalog.searchResults(
            object_provides=INationalDescriptorsFolder.__identifier__
        )
        nat_desc_folder = brains[0].getObject()
        country_folder = [
            country
            for country in nat_desc_folder.contentValues()
            if country.id == self.country_code.lower()
        ][0]

        for region_folder in country_folder.contentValues():
            if not INationalRegionDescriptorFolder.providedBy(region_folder):
                continue
            region_code = region_folder.id
            region_name = region_folder.title
            descriptor_data = []

            for descriptor_folder in region_folder.contentValues():
                if not IDescriptorFolder.providedBy(descriptor_folder):
                    continue

                desc_id = descriptor_folder.id
                desc_name = descriptor_folder.title
                articles = []

                for article_folder in descriptor_folder.contentValues():
                    if not INationalDescriptorAssessment.providedBy(
                            article_folder):
                        continue

                    article = article_folder.title

                    assess_data = self._get_assessment_data(article_folder)
                    article_data = self._get_article_data(
                        region_code.upper(), country_folder.title,
                        desc_id.upper(), assess_data, article
                    )
                    articles.append((article, article_data))

                descriptor_data.append(
                    (desc_name, articles)
                )

            res.append((region_name, descriptor_data))

        return self.template(data=res)


class NationalSummaryView(BaseNatSummaryView):
    help_text = "HELP TEXT"
    template = ViewPageTemplateFile('pt/report-data.pt')
    year = "2012"

    # def download(self):
    #     doc = download()
    #     sh = self.request.response.setHeader
    #
    #     sh('Content-Type', 'application/vnd.oasis.opendocument.text.')
    #     fname = "test-test"
    #     sh('Content-Disposition',
    #        'attachment; filename=%s.odt' % fname)
    #
    #     return doc

    # @cache(get_reportdata_key, dependencies=['translation'])
    def render_reportdata(self):
        report_header = self.report_header_template(
            title="National summary report: {}".format(
                self.country_name,
            )
        )
        # trans_edit_html = self.translate_view()()

        self.tables = [
            report_header,
            DescriptorLevelAssessments(self, self.request)
            # ArticleTable(self, self.request, 'Art7'),
            # ArticleTable(self, self.request, 'Art3-4'),
            # ReportingHistoryTable(self, self.request),
            # trans_edit_html,
        ]

        template = self.template

        return template(tables=self.tables)

    def __call__(self):
        report_html = self.render_reportdata()
        self.report_html = report_html

        # if 'download' in self.request.form:
        #     return self.download()

        if 'translate' in self.request.form:
            for table in self.tables:
                if (hasattr(table, 'is_translatable')
                        and table.is_translatable):
                    view = table.view
                    view.auto_translate()

            messages = IStatusMessage(self.request)
            messages.add(u"Auto-translation initiated, please refresh "
                         u"in a couple of minutes", type=u"info")

        @timeit
        def render_html():
            return self.index()

        return render_html()