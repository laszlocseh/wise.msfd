""" Classes and views to implement the National Descriptors compliance page
"""

import re
from collections import namedtuple
from logging import getLogger

from sqlalchemy import or_
from zope.interface import implements

from persistent.list import PersistentList
from plone.api.content import transition
from plone.api.portal import get_tool
from plone.protect import CheckAuthenticator  # , protect
from Products.Five.browser.pagetemplatefile import \
    ViewPageTemplateFile as Template
from Products.statusmessages.interfaces import IStatusMessage
from wise.msfd import db, sql2018
from wise.msfd.compliance.assessment import (ANSWERS_COLOR_TABLE,
                                             CONCLUSION_COLOR_TABLE,
                                             AssessmentDataMixin)
from wise.msfd.compliance.base import NAT_DESC_QUESTIONS
from wise.msfd.compliance.content import AssessmentData
from wise.msfd.compliance.scoring import (CONCLUSIONS, get_overall_conclusion,
                                          get_range_index, OverallScores)
from wise.msfd.compliance.utils import ordered_regions_sortkey
from wise.msfd.compliance.vocabulary import (REGIONAL_DESCRIPTORS_REGIONS,
                                             SUBREGIONS_TO_REGIONS)
from wise.msfd.data import _extract_pdf_assessments
from wise.msfd.gescomponents import get_descriptor
from wise.msfd.utils import t2rt

from .base import BaseView
from ..interfaces import ICountryStartAssessments, ICountryStartReports
from .interfaces import (INationaldescriptorArticleView,
                         INationaldescriptorSecondaryArticleView)

logger = getLogger('wise.msfd')

REGION_RE = re.compile('.+\s\((?P<region>.+)\)$')


ARTICLE_WEIGHTS = {
    'Art9': {
        'adequacy': 3/5.0,
        'consistency': 0.0,
        'coherence': 2/5.0
    },
    'Art8': {
        'adequacy': 3/5.0,
        'consistency': 1/5.0,
        'coherence': 1/5.0
    },
    'Art10': {
        'adequacy': 3/5.0,
        'consistency': 1/5.0,
        'coherence': 1/5.0
    },
    'Art3': {
        'adequacy': 1.0,
        'consistency': 0,
        'coherence': 0
    },
    'Art4': {
        'adequacy': 1.0,
        'consistency': 0,
        'coherence': 0
    },
    'Art7': {
        'adequacy': 1.0,
        'consistency': 0,
        'coherence': 0
    },
    'Art8esa': {
        'adequacy': 1.0,
        'consistency': 0,
        'coherence': 0
    }
}

Assessment2012 = namedtuple(
    'Assessment2012', [
        'gescomponents',
        'criteria',
        'summary',
        'overall_ass',
        'score'
    ]
)

Criteria = namedtuple(
    'Criteria', ['crit_name', 'answer']
)


Assessment = namedtuple('Assessment',
                        [
                            'gescomponents',
                            'answers',
                            'assessment_summary',
                            'recommendations',
                            'phase_overall_scores',
                            'overall_score',
                            'overall_conclusion',
                            'overall_conclusion_color'
                        ])
AssessmentRow = namedtuple('AssessmentRow',
                           [
                               'question',
                               'summary',
                               'conclusion',
                               'conclusion_color',
                               'score',
                               'values'
                           ])

CountryStatus = namedtuple('CountryStatus',
                           ['code', 'name', 'status', 'state_id', 'url'])


@db.use_db_session('2018')
def get_assessment_data_2012_db(*args):
    """ Returns the assessment for 2012, from COM_Assessments_2012 table
    """

    articles = {
        'Art8': 'Initial assessment (Article 8)',
        'Art9': 'GES (Article 9)',
        'Art10': 'Targets (Article 10)',
    }

    country, descriptor, article = args
    art = articles.get(article)
    descriptor = descriptor.split('.')[0]

    t = sql2018.t_COM_Assessments_2012
    count, res = db.get_all_records(
        t,
        t.c.Country.like('%{}%'.format(country)),
        t.c.Descriptor == descriptor,
        or_(t.c.MSFDArticle == art,
            t.c.MSFDArticle.is_(None))
    )

    # look for rows where OverallAssessment looks like 'see D1'
    # replace these rows with data for the descriptor mentioned in the
    # OverallAssessment
    res_final = []
    descr_reg = re.compile('see\s(d\d{1,2})', flags=re.I)

    for row in res:
        overall_text = row.OverallAssessment
        assess = row.Assessment

        if 'see' in overall_text.lower() or (not overall_text and
                                             'see d' in assess.lower()):
            descr_match = (descr_reg.match(overall_text)
                            or descr_reg.match(assess))
            descriptor = descr_match.groups()[0]

            _, r = db.get_all_records(
                t,
                t.c.Country == row.Country,
                t.c.Descriptor == descriptor,
                t.c.AssessmentCriteria == row.AssessmentCriteria,
                t.c.MSFDArticle == row.MSFDArticle
            )

            res_final.append(r[0])

            continue

        if not overall_text:
            res_final.append(row)

            continue

        res_final.append(row)

    return res_final


@db.use_db_session('2018')
def get_assessment_head_data_2012(article, region, country_code):

    t = sql2018.COMGeneral
    count, res = db.get_all_records(
        t,
        t.CountryCode == country_code,
        t.MSFDArticle == article,
        t.RegionSubregion.startswith(region),
        # t.RegionSubregion == region + country_code,
        t.AssessmentTopic == 'GES Descriptor'
    )

    assert count == 1

    if count:
        # report_by = res[0].ReportBy
        report_by = 'Commission'
        assessors = res[0].Assessors
        assess_date = res[0].DateAssessed
        com_report = res[0].CommissionReport

        return (report_by,
                assessors,
                assess_date,
                (com_report.split('/')[-1], com_report))

    return ['Not found'] * 3 + [('Not found', '')]


class NationalDescriptorsOverview(BaseView):
    section = 'national-descriptors'

    def countries(self):
        countries = self.context.contentValues()
        res = []

        for country in countries:
            state_id, state_label = self.process_phase(country)
            info = CountryStatus(country.id.upper(), country.Title(),
                                 state_label, state_id, country.absolute_url())

            res.append(info)

        return res


class NationalDescriptorCountryOverview(BaseView):
    section = 'national-descriptors'

    def get_regions(self, context=None):
        if not context:
            context = self.context

        regions = [
            x for x in context.contentValues()
            if x.portal_type == 'Folder'
        ]

        sorted_regions = sorted(
            regions, key=lambda i: ordered_regions_sortkey(i.id.upper())
        )

        return sorted_regions

    # @protect(CheckAuthenticator)
    def send_to_tl(self):
        regions = self.get_regions()

        for region in regions:
            descriptors = self.get_descriptors(region)

            for desc in descriptors:
                assessments = self.get_articles(desc)

                for assessment in assessments:
                    state_id = self.get_wf_state_id(assessment)

                    if state_id == 'approved':
                        transition(obj=assessment, to_state='in_work')

        IStatusMessage(self.request).add(u'Sent to TL', type='info')

        url = self.context.absolute_url()

        return self.request.response.redirect(url)

    def ready_phase2(self, regions=None):
        # roles = self.get_current_user_roles(self.context)

        if not self.can_view_edit_assessment_data(self.context):
            return False

        if not regions:
            regions = self.get_regions()

        for region in regions:
            descriptors = self.get_descriptors(region)

            for desc in descriptors:
                assessments = self.get_articles(desc)

                for assessment in assessments:
                    state_id = self.get_wf_state_id(assessment)

                    if state_id != 'approved':
                        return False

        return True

    def get_descriptors(self, region):
        order = [
            'd1.1', 'd1.2', 'd1.3', 'd1.4', 'd1.5', 'd1.6', 'd2', 'd3', 'd4',
            'd5', 'd6', 'd7', 'd8', 'd9', 'd10', 'd11',
        ]

        return [region[d] for d in order]

    def descriptor_for_code(self, code):
        desc = get_descriptor(code.upper())

        return desc

    def get_secondary_articles(self, country):
        order = ['art7', 'art3', 'art4']

        return [country[a] for a in order]

    def __call__(self):

        return self.index()


class NatDescCountryOverviewReports(NationalDescriptorCountryOverview):
    """ Class declaration needed to be able to override HTML head title """

    implements(ICountryStartReports)


class NatDescCountryOverviewAssessments(NationalDescriptorCountryOverview):
    """ Class declaration needed to be able to override HTML head title """

    implements(ICountryStartAssessments)

def get_crit_val(question, element, descriptor):
    """ Get the criteria value to be shown in the assessment data 2018 table
    """
    use_crit = question.use_criteria

    if 'targets' in use_crit:
        if use_crit == 'all-targets':
            return element.title

        if use_crit == '2018-targets' and element.year == '2018':
            return element.title

        return ''

    is_prim = element.is_primary(descriptor)
    crit = element.id

    # special case for D1.4 A09Ad2 we need to show all crits excluding D1C2
    if question.id == 'A09Ad2' and descriptor.id == 'D1.4' and crit != 'D1C2':
        return crit

    if use_crit == 'all':
        return crit

    if is_prim and use_crit == 'primary':
        return crit

    if not is_prim and use_crit == 'secondary':
        return crit

    return ''


def format_assessment_data(article, elements, questions, muids, data,
                           descriptor, article_weights, self):
    """ Builds a data structure suitable for display in a template

    This is used to generate the assessment data overview table for 2018

    TODO: this is doing too much. Need to be simplified and refactored.
    """
    answers = []
    phases = article_weights.values()[0].keys()
    phase_overall_scores = OverallScores(article_weights)

    for question in questions:
        values = []
        choices = dict(enumerate(question.answers))
        q_scores = question.scores
        q_klass = question.klass

        if question.use_criteria == 'none':
            field_name = '{}_{}'.format(article, question.id)
            color_index = 0
            label = 'Not filled in'
            v = data.get(field_name, None)

            if v is not None:
                label = choices[v]
                color_index = ANSWERS_COLOR_TABLE[q_scores[v]]

            value = (label, color_index, u'All criteria')
            values.append(value)
        else:
            for element in elements:
                field_name = '{}_{}_{}'.format(
                    article, question.id, element.id
                )

                color_index = 0
                label = u'{}: Not filled in'.format(element.title)

                v = data.get(field_name, None)

                if v is not None:
                    label = u'{}: {}'.format(element.title, choices[v])
                    try:
                        color_index = ANSWERS_COLOR_TABLE[q_scores[v]]
                    except Exception:
                        logger.exception('Invalid color table')
                        color_index = 0
                        # label = 'Invalid color table'

                value = (
                    label,
                    color_index,
                    get_crit_val(question, element, descriptor)
                )

                values.append(value)

        summary_title = '{}_{}_Summary'.format(article, question.id)
        summary = data.get(summary_title) or ''

        sn = '{}_{}_Score'.format(article, question.id)
        score = data.get(sn, {})

        conclusion = getattr(score, 'conclusion', '')
        score_value = getattr(score, 'score_value', 0)

        conclusion_color = CONCLUSION_COLOR_TABLE[score_value]

        weighted_score = getattr(score, 'weighted_score', 0)
        max_weighted_score = getattr(score, 'max_weighted_score', 0)
        is_not_relevant = getattr(score, 'is_not_relevant', False)
        # q_weight = float(question.score_weights.get(descriptor.id, 10.0))

        # is_not_relevant is True if all answered options are 'Not relevant'
        # maximum overall score is incremented if the is_not_relevant is False

        if not is_not_relevant:
            p_score = getattr(phase_overall_scores, q_klass)
            p_score['score'] += weighted_score
            p_score['max_score'] += max_weighted_score

        qr = AssessmentRow(question.definition, summary, conclusion,
                           conclusion_color, score, values)
        answers.append(qr)

    # assessment summary and recommendations
    assess_sum = data.get('%s_assessment_summary' % article)
    recommend = data.get('%s_recommendations' % article)

    for phase in phases:
        # set the conclusion and color based on the score for each phase
        phase_scores = getattr(phase_overall_scores, phase)
        phase_score = phase_overall_scores.get_score_for_phase(phase)

        if phase == 'consistency' and article == 'Art9':
            phase_scores['conclusion'] = ('-', 'Not relevant')
            phase_scores['color'] = 0
            continue

        phase_scores['conclusion'] = get_overall_conclusion(phase_score)
        phase_scores['color'] = \
            CONCLUSION_COLOR_TABLE[get_range_index(phase_score)]

    # for national descriptors override the coherence score with the score
    # from regional descriptors
    if self.section == 'national-descriptors':
        phase_overall_scores.coherence = self.get_coherence_data(
            self.country_region_code, self.descriptor, article
        )

    # the overall score and conclusion for the whole article 2018
    overall_score_val, overall_score = phase_overall_scores.\
        get_overall_score(article)
    overall_conclusion = get_overall_conclusion(overall_score)
    overall_conclusion_color = CONCLUSION_COLOR_TABLE[overall_score_val]

    assessment = Assessment(
        elements,
        answers,
        assess_sum or '-',
        recommend or '-',
        phase_overall_scores,
        overall_score,
        overall_conclusion,
        overall_conclusion_color
    )

    return assessment


# TODO: use memoization for old data, needs to be called again to get the
# score, to allow delta compute for 2018
#
# @memoize


def filter_assessment_data_2012(data, region_code, descriptor_criterions):
    """ Filters and formats the raw db data for 2012 assessment data
    """
    gescomponents = [c.id for c in descriptor_criterions]

    assessments = {}
    criterias = []

    for row in data:
        fields = row._fields

        def col(col):
            return row[fields.index(col)]

        country = col('Country')

        # The 2012 assessment data have the region in the country name
        # For example: United Kingdom (North East Atlantic)
        # When we display the assessment data (which we do, right now, based on
        # subregion), we want to match the data according to the "big" region

        if '(' in country:
            region = REGION_RE.match(country).groupdict()['region']

            if region not in SUBREGIONS_TO_REGIONS[region_code]:
                continue

        summary = col('Conclusions')
        score = col('OverallScore')
        overall_ass = col('OverallAssessment')
        criteria = Criteria(
            col('AssessmentCriteria'),
            t2rt(col('Assessment'))
        )

        # TODO test for other countries beside LV
        # Condition changed because of LV report, where score is 0

        # if not score:

        if score is None:
            criterias.append(criteria)
        elif country not in assessments:
            criterias.insert(0, criteria)
            assessment = Assessment2012(
                gescomponents,
                criterias,
                summary,
                overall_ass,
                score,
            )
            assessments[country] = assessment
        else:
            assessments[country].criteria.append(criteria)

        # if country not in assessments:
        #     assessment = Assessment2012(
        #         gescomponents,
        #         [criteria],
        #         summary,
        #         overall_ass,
        #         score,
        #     )
        #     assessments[country] = assessment
        # else:
        #     assessments[country].criteria.append(criteria)

    if not assessments:
        assessment = Assessment2012(
            gescomponents,
            criterias,
            summary,
            overall_ass,
            score,
        )
        assessments[country] = assessment

    return assessments


class NationalDescriptorRegionView(BaseView):
    section = 'national-descriptors'


class NationalDescriptorArticleView(BaseView, AssessmentDataMixin):
    implements(INationaldescriptorArticleView)
    section = 'national-descriptors'

    assessment_data_2012_tpl = Template('./pt/assessment-data-2012.pt')
    assessment_data_2018_tpl = Template('./pt/assessment-data-2018.pt')

    year = '2018'       # used by self.muids
    _questions = NAT_DESC_QUESTIONS

    @property
    def title(self):
        return u"Commission assessment / {} / 2018 / {} / {} / {} ".format(
            self.article,
            self.descriptor_title,
            self.country_title,
            self.country_region_name,
        )

    @property
    def criterias(self):
        return self.descriptor_obj.sorted_criterions()      # criterions

    @property
    def questions(self):
        qs = self._questions.get(self.article, [])

        return qs

    def __call__(self):

        if 'assessor' in self.request.form:
            assessors = self.request.form['assessor']

            if isinstance(assessors, list):
                assessors = ', '.join(assessors)
            self.context.saved_assessment_data.ass_new = assessors

        # BBB:

        context = self.context

        if not hasattr(context, 'saved_assessment_data') or \
                not isinstance(context.saved_assessment_data, PersistentList):
            context.saved_assessment_data = AssessmentData()

        # Assessment data 2012
        descriptor_criterions = get_descriptor(self.descriptor).criterions

        country_name = self._country_folder.title

        try:
            db_data_2012 = get_assessment_data_2012_db(
                country_name,
                self.descriptor,
                self.article
            )
            assessments_2012 = filter_assessment_data_2012(
                db_data_2012,
                self.country_region_code,       # TODO: this will need refactor
                descriptor_criterions,
            )

            self.assessment_data_2012 = self.assessment_data_2012_tpl(
                data=assessments_2012
            )

            if assessments_2012.get(country_name):
                score_2012 = assessments_2012[country_name].score
                conclusion_2012 = assessments_2012[country_name].overall_ass
            else:       # fallback
                ctry = assessments_2012.keys()[0]
                score_2012 = assessments_2012[ctry].score
                conclusion_2012 = assessments_2012[ctry].overall_ass

            report_by, assessors, assess_date, source_file = \
                get_assessment_head_data_2012(self.article,
                                              self.country_region_code,
                                              self._country_folder.id)
        except:
            logger.exception("Could not get assessment data for 2012")
            self.assessment_data_2012 = ''
            score_2012 = 100
            conclusion_2012 = 'Not found'
            report_by, assessors, assess_date, source_file = [
                'Not found'] * 3 + [('Not found', '')]

        # Assessment header 2012

        self.assessment_header_2012 = self.assessment_header_template(
            report_by=report_by,
            assessor_list=[],
            assessors=assessors,
            assess_date=assess_date,
            source_file=source_file,
            show_edit_assessors=False,
        )

        # Assessment data 2018
        data = self.context.saved_assessment_data.last()
        elements = self.questions[0].get_all_assessed_elements(
            self.descriptor_obj,
            muids=self.muids
        )
        article_weights = ARTICLE_WEIGHTS
        assessment = format_assessment_data(
            self.article,
            elements,
            self.questions,
            self.muids,
            data,
            self.descriptor_obj,
            article_weights,
            self
        )
        assessment.phase_overall_scores.coherence = self.get_coherence_data(
            self.country_region_code, self.descriptor, self.article
        )

        score_2012 = int(round(score_2012))
        conclusion_2012_color = CONCLUSION_COLOR_TABLE.get(score_2012, 0)
        change = int(
            assessment.phase_overall_scores
            .get_range_index_for_phase('adequacy') - score_2012
        )

        self.assessment_data_2018_html = self.assessment_data_2018_tpl(
            assessment=assessment,
            score_2012=score_2012,
            conclusion_2012=conclusion_2012,
            conclusion_2012_color=conclusion_2012_color,
            change_since_2012=change,
            can_comment=self.can_comment
        )

        # Assessment header 2018
        report_by_2018 = u'Commission'
        # assessors_2018 = self.context.saved_assessment_data.assessors
        assessors_2018 = getattr(
            self.context.saved_assessment_data, 'ass_new', 'Not assessed'
        )
        assess_date_2018 = data.get('assess_date', u'Not assessed')
        source_file_2018 = ('To be addedd...', '.')

        can_edit = self.check_permission('wise.msfd: Edit Assessment')
        show_edit_assessors = self.assessor_list and can_edit

        self.assessment_header_2018_html = self.assessment_header_template(
            report_by=report_by_2018,
            assessor_list=self.assessor_list,
            assessors=assessors_2018,
            assess_date=assess_date_2018,
            source_file=source_file_2018,
            show_edit_assessors=show_edit_assessors,
        )

        return self.index()


class NationalDescriptorSecondaryArticleView(NationalDescriptorArticleView):
    """"""

    assessment_data_2018_tpl = Template(
        './pt/assessment-data-2018-secondary.pt'
    )
    assessment_header_template = Template(
        '../pt/assessment-header-secondary.pt'
    )

    pdf_assessments = _extract_pdf_assessments()

    implements(INationaldescriptorSecondaryArticleView)
    _descriptor = 'Not linked'

    @property
    def country_region_code(self):
        return 'No region'

    @property
    def descriptor_obj(self):
        return 'Not linked'

    @property
    def has_assessment(self):
        """ Article 7 will be not assessed, we do not show the 2018 and
        2012 assessment tables
        """

        if self.article == 'Art7':
            return False

        return True

    def source_pdf_assessment(self):
        for row in self.pdf_assessments:
            country = row[0]
            if country != self.country_code:
                continue

            article = row[1]
            if article != self.article:
                continue

            url = row[2]

            return url

        return None

    def __call__(self):

        if 'assessor' in self.request.form:
            assessors = self.request.form['assessor']

            if isinstance(assessors, list):
                assessors = ', '.join(assessors)
            self.context.saved_assessment_data.ass_new = assessors

        # BBB:

        context = self.context

        if not hasattr(context, 'saved_assessment_data') or \
                not isinstance(context.saved_assessment_data, PersistentList):
            context.saved_assessment_data = AssessmentData()

        # Assessment data 2012
        # descriptor_criterions = get_descriptor(self.descriptor).criterions
        descriptor_criterions = []

        country_name = self._country_folder.title

        try:
            db_data_2012 = get_assessment_data_2012_db(
                country_name,
                self.descriptor,
                self.article
            )
            assessments_2012 = filter_assessment_data_2012(
                db_data_2012,
                self.country_region_code,
                descriptor_criterions,
            )
            self.assessment_data_2012 = self.assessment_data_2012_tpl(
                data=assessments_2012
            )

            if assessments_2012.get(country_name):
                score_2012 = assessments_2012[country_name].score
                conclusion_2012 = assessments_2012[country_name].overall_ass
            else:       # fallback
                ctry = assessments_2012.keys()[0]
                score_2012 = assessments_2012[ctry].score
                conclusion_2012 = assessments_2012[ctry].overall_ass

            report_by, assessors, assess_date, source_file = \
                get_assessment_head_data_2012(self.article,
                                              self.country_region_code,
                                              self._country_folder.id)
        except:
            logger.exception("Could not get assessment data for 2012")
            self.assessment_data_2012 = ''
            score_2012 = 100
            conclusion_2012 = 'Not found'
            report_by, assessors, assess_date, source_file = [
                'Not found'] * 3 + [('Not found', '')]

        # Assessment header 2012

        self.assessment_header_2012 = self.assessment_header_template(
            report_by=report_by,
            assessor_list=[],
            assessors=assessors,
            assess_date=assess_date,
            source_file=source_file,
            show_edit_assessors=False,
        )

        # Assessment data 2018
        data = self.context.saved_assessment_data.last()
        elements = self.questions[0].get_all_assessed_elements(
            self.descriptor_obj,
            country_name=self.country_name,
            country_code=self.country_code
        )
        article_weights = ARTICLE_WEIGHTS
        assessment = format_assessment_data(
            self.article,
            elements,
            self.questions,
            self.muids,
            data,
            self.descriptor_obj,
            article_weights,
            self
        )

        score_2012 = int(round(score_2012))
        conclusion_2012_color = CONCLUSION_COLOR_TABLE.get(score_2012, 0)
        change = int(
            assessment.phase_overall_scores
            .get_range_index_for_phase('adequacy') - score_2012
        )

        self.assessment_data_2018_html = self.assessment_data_2018_tpl(
            assessment=assessment,
            score_2012=score_2012,
            conclusion_2012=conclusion_2012,
            conclusion_2012_color=conclusion_2012_color,
            change_since_2012=change,
            can_comment=self.can_comment
        )

        # Assessment header 2018
        report_by_2018 = u'Commission'
        # assessors_2018 = self.context.saved_assessment_data.assessors
        assessors_2018 = getattr(
            self.context.saved_assessment_data, 'ass_new', 'Not assessed'
        )
        assess_date_2018 = data.get('assess_date', u'Not assessed')
        source_file_2018 = ('To be addedd...', '.')

        can_edit = self.check_permission('wise.msfd: Edit Assessment')
        show_edit_assessors = self.assessor_list and can_edit

        self.assessment_header_2018_html = self.assessment_header_template(
            report_by=report_by_2018,
            assessor_list=self.assessor_list,
            assessors=assessors_2018,
            assess_date=assess_date_2018,
            source_file=source_file_2018,
            show_edit_assessors=show_edit_assessors,
        )

        return self.index()

    @property
    def title(self):
        return u"Commission assessment: {} / {} / 2018".format(
            self.country_title,
            self.article,
        )
