""" Classes and views to implement the National Descriptors compliance page
"""

import re
from collections import namedtuple
from logging import getLogger

from sqlalchemy import or_

from persistent.list import PersistentList
from Products.Five.browser.pagetemplatefile import \
    ViewPageTemplateFile as Template
from wise.msfd import db, sql2018
from wise.msfd.compliance.base import get_descriptor_elements, get_questions
from wise.msfd.compliance.scoring import get_overall_conclusion
from wise.msfd.compliance.vocabulary import SUBREGIONS_TO_REGIONS
from wise.msfd.gescomponents import get_descriptor
from wise.msfd.utils import t2rt

from ..base import BaseComplianceView

CountryStatus = namedtuple('CountryStatus',
                           ['name', 'status', 'state_id', 'url'])

logger = getLogger('wise.msfd')


@db.use_db_session('2018')
def get_assessment_data_2012_db(*args):
    """ Returns the 2012 assessment data, from COM_Assessments_2012 table
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

    return res


class NationalDescriptorsOverview(BaseComplianceView):
    section = 'national-descriptors'

    def countries(self):
        countries = self.context.contentValues()
        res = []

        for country in countries:
            state_id, state_label = self.process_phase(country)
            info = CountryStatus(country.Title(), state_label, state_id,
                                 country.absolute_url())

            res.append(info)

        return res


class NationalDescriptorCountryOverview(BaseComplianceView):
    section = 'national-descriptors'

    def get_articles(self):
        return ['Art8', 'Art9', 'Art10']

    def get_regions(self):
        return self.context.contentValues()


Assessment = namedtuple('Assessment',
                        [
                            'gescomponents',
                            'answers',
                            'assessment_summary',
                            'recommendations',
                            'overall_score',
                            'overall_conclusion'
                         ])
AssessmentRow = namedtuple(
    'AssessmentRow',
    [
        'question',
        'summary',
        'conclusion',
        'conclusion_color',
        'score',
        'values'
     ]
)


# This somehow translates the real value in a color, to be able to compress the
# displayed information in the assessment table

# TODO: this needs to be redone, according to new scoring rules
COLOR_TABLE = {
    2: [1, 4],
    3: [1, 3, 4],
    4: [1, 2, 3, 4],
    5: [1, 2, 3, 4, 5],
    6: [1, 2, 3, 4, 5, 0]      # TODO: this needs to be removed
}


# get the criteria value to be shown in the assessment data 2018 table
def get_crit_val(question, criteria):
    use_crit = question.use_criteria
    is_prim = criteria.is_primary
    crit = criteria.id

    if use_crit == 'all':
        return crit

    if is_prim and use_crit == 'primary':
        return crit

    if not is_prim and use_crit == 'secondary':
        return crit

    return ''


def get_assessment_data(article, criterias, questions, data):
    """ Builds a data structure suitable for display in a template

    This is used to generate the assessment data overview table for 2018
    """

    answers = []
    gescomponents = [c.id for c in criterias]
    overall_score = 0

    for question in questions:
        values = []
        choices = dict(enumerate(question.answers))

        if question.use_criteria == 'none':
            field_name = '{}_{}'.format(article, question.id)
            v = data.get(field_name, None)

            if v is not None:
                label = choices[v]
                color_index = COLOR_TABLE[len(choices)][v]
            else:
                color_index = 0
                label = 'Not filled in'

            value = (label, color_index, u'All criterias')
            values.append(value)
        else:
            for criteria in criterias:
                for element in criteria.elements:
                    field_name = '{}_{}_{}_{}'.format(
                        article, question.id, criteria.id, element.id
                    )
                    v = data.get(field_name, None)

                    if v is not None:
                        label = choices[v]
                        color_index = COLOR_TABLE[len(choices)][v]
                    else:
                        color_index = 0
                        label = 'Not filled in'

                    value = (
                        label,
                        color_index,
                        get_crit_val(question, criteria)
                    )

                    values.append(value)

        summary_title = '{}_{}_Summary'.format(article, question.id)
        summary = data.get(summary_title) or ''

        sn = '{}_{}_Score'.format(article, question.id)
        score = data.get(sn, 0)

        cn = '{}_{}_Conclusion'.format(article, question.id)
        conclusion = data.get(cn, '')
        conclusion_color = 5 - data.get(
            '{}_{}_RawScore'.format(article, question.id), 5
        )
        overall_score += score     # use raw score or score?

        qr = AssessmentRow(question.definition, summary, conclusion,
                           conclusion_color, score, values)
        answers.append(qr)

    # Add to answers 2 more rows: assessment summary and recommendations
    assess_sum = data.get('{}_assessment_summary'.format(article), '-') or '-'
    recommendations = data.get(
        '{}_recommendations'.format(article), '-') or '-'

    # overall_score = overall_score * 100 / len(questions)
    try:
        overall_conclusion = get_overall_conclusion(overall_score)
    except:
        logger.exception("Error in getting overall conclusion")
        overall_conclusion = (1, 'error')

    assessment = Assessment(
        gescomponents,
        answers,
        assess_sum,
        recommendations,
        overall_score,
        overall_conclusion
    )

    return assessment


@db.use_db_session('2018')
def get_assessment_head_data_2012(data):
    if not data:
        return ['Not found'] * 3 + [('Not found', '')]

    ids = [x.COM_General_Id for x in data]
    ids = tuple(set(ids))

    t = sql2018.COMGeneral
    count, res = db.get_all_records(
        t,
        t.Id.in_(ids)
    )

    if count:
        report_by = res[0].ReportBy
        assessors = res[0].Assessors
        assess_date = res[0].DateAssessed
        com_report = res[0].CommissionReport

        return (report_by,
                assessors,
                assess_date,
                (com_report.split('/')[-1], com_report))

    return ['Not found'] * 3 + [('Not found', '')]


# TODO: use memoization for old data, needs to be called again to get the
# score, to allow delta compute for 2018
#
# @memoize

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

REGION_RE = re.compile('.+\s\((?P<region>.+)\)$')


def filter_assessment_data_2012(data, region_code, descriptor_criterions):
    gescomponents = [c.id for c in descriptor_criterions]

    assessments = {}

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

            if SUBREGIONS_TO_REGIONS[region_code] != region:
                continue

        summary = col('Conclusions')
        score = col('OverallScore')
        overall_ass = col('OverallAssessment')
        criteria = Criteria(
            col('AssessmentCriteria'),
            t2rt(col('Assessment'))
        )

        if country not in assessments:
            assessment = Assessment2012(
                gescomponents,
                [criteria],
                summary,
                overall_ass,
                score,
            )
            assessments[country] = assessment
        else:
            assessments[country].criteria.append(criteria)

    return assessments


class AssessmentData(PersistentList):

    data = []

    @property
    def assessors(self):
        assessors = []

        for data in self.data:
            assessor = data.get('assessor')

            if assessor is None:
                continue
                raise ValueError, 'No assessor in data'

            if assessor not in assessors:
                assessors.append(assessor)

        if not assessors:
            return 'Not assessed'

        return ', '.join(assessors)

    def append(self, data):
        self.data.append(data)

        self._p_changed = True

    def last(self):
        if not self.data:
            return {}

        return self.data[-1]


class NationalDescriptorRegionView(BaseComplianceView):
    section = 'national-descriptors'


class NationalDescriptorArticleView(BaseComplianceView):
    section = 'national-descriptors'

    assessment_data_2012_tpl = Template('./pt/assessment-data-2012.pt')
    assessment_data_2018_tpl = Template('./pt/assessment-data-2018.pt')

    @property
    def title(self):
        return "{}'s assessment overview for {}/{}/{}".format(
            self.country_title,
            self.descriptor,
            self.country_region_code,
            self.article
        )

    @property
    def criterias(self):
        # TODO: unify descriptor handling, should also see ges_components.py
        els = get_descriptor_elements(
            'compliance/nationaldescriptors/data'
        )

        if self.descriptor not in els:
            logger.warning("Descriptor elements not defined: %s",
                           self.descriptor)

            desc = self.descriptor.split('.')[0]

            return els[desc]

        return els[self.descriptor]

    @property
    def questions(self):
        qs = get_questions(
            'compliance/nationaldescriptors/data'
        )

        return qs[self.article]

    def __init__(self, context, request):
        super(NationalDescriptorArticleView, self).__init__(context, request)

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
            else:       # fallback
                ctry = assessments_2012.keys()[0]
                score_2012 = assessments_2012[ctry].score

            report_by, assessors, assess_date, source_file = \
                get_assessment_head_data_2012(db_data_2012)
        except:
            logger.exception("Could not get assessment data for 2012")
            self.assessment_data_2012 = ''
            score_2012 = 100
            report_by, assessors, assess_date, source_file = [
                'Not found'] * 3 + [('Not found', '')]

        # Assessment header 2012

        self.assessment_header_2012 = self.assessment_header_template(
            report_by=report_by,
            assessors=assessors,
            assess_date=assess_date,
            source_file=source_file
        )

        # Assessment data 2018
        data = self.context.saved_assessment_data.last()

        assessment = get_assessment_data(
            self.article,
            self.criterias,
            self.questions,
            data
        )

        self.assessment_data_2018 = self.assessment_data_2018_tpl(
            assessment=assessment,
            score_2012=score_2012
        )

        # Assessment header 2018
        report_by_2018 = u'Commission'
        assessors_2018 = self.context.saved_assessment_data.assessors
        assess_date_2018 = data.get('assess_date', u'Not assessed')
        source_file_2018 = ('To be addedd...', '.')

        self.assessment_header_2018 = self.assessment_header_template(
            report_by=report_by_2018,
            assessors=assessors_2018,
            assess_date=assess_date_2018,
            source_file=source_file_2018,
        )
