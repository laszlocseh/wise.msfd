import logging
from collections import namedtuple

import lxml.etree
from sqlalchemy.orm import aliased
from zope.component import getMultiAdapter
from zope.dottedname.resolve import resolve
from zope.interface import implements

from Acquisition import aq_inner
from plone.api.content import get_state
from plone.api.portal import get_tool
from plone.memoize import ram
from plone.memoize.view import memoize
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from wise.msfd import db, sql
from wise.msfd.compliance.scoring import compute_score
from wise.msfd.compliance.vocabulary import ASSESSED_ARTICLES, REGIONS
from wise.msfd.gescomponents import (get_descriptor, get_marine_units,
                                     sorted_criterions)
from wise.msfd.translation.interfaces import ITranslationContext
from wise.msfd.utils import Tab, _parse_files_in_location, row_to_dict

from . import interfaces
from .interfaces import ICountryDescriptorsFolder
from .utils import REPORT_DEFS

# from zope.annotation.interfaces import IAnnotations

logger = logging.getLogger('wise.msfd')
edw_logger = logging.getLogger('edw.logger')
edw_logger.setLevel('WARNING')


MAIN_FORMS = [Tab(*x) for x in [
    # view name, (title, explanation)
    ('@@comp-start',
     'compliance-start',    # section name
     'Assessment Module',
     'Start Page',
     ),
    ('national-descriptors-assessments/@@nat-desc-start',
     'national-descriptors',
     'Descriptor - national',
     'Member states reports and Commission assessments',
     ),
    ('regional-descriptors-assessments/@@reg-desc-start',
     'regional-descriptors',
     'Descriptor - regional',
     'Member states reports and Commission assessments',
     ),
    ('@@comp-national-overviews',
     'national-overviews',
     'Overview - national',
     'Overview for a Member state',
     ),
    ('@@comp-regional-overviews',
     'regional-overviews',
     'Overview - regional',
     'Overview for all Member states in a region',
     ),
]
]


class Container(object):
    """ A container can render its children forms and views
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.children = []

    def __call__(self):
        self.update()

        return self.render()

    def update(self):
        pass

    def render(self):
        lines = []

        for child in self.children:
            lines.append(child())

        # TODO: maybe use a template for this?

        return u'\n'.join(lines)


class BaseComplianceView(BrowserView):
    """ Base class for compliance views
    """

    tabs_type = 'tab'
    main_forms = MAIN_FORMS
    _translatables = None

    @property
    def json_map_url(self):
        return self.root_url() + '/@@json-map'

    @property
    def TRANSLATABLES(self):
        # for 2018, returns a list of field names that are translatable

        if self._translatables:
            return self._translatables

        year = REPORT_DEFS[self.year]

        if self.article in year:
            return year[self.article].get_translatable_fields()

        self._translatables = []

        return self._translatables

    @TRANSLATABLES.setter
    def set_translatables(self, v):
        self._translatables = v

    report_header_template = ViewPageTemplateFile(
        'nationaldescriptors/pt/report-data-header.pt'
    )

    assessment_header_template = ViewPageTemplateFile(
        'nationaldescriptors/pt/assessment-header.pt'
    )
    _descriptor = None      # can be overriden

    @property
    def colspan(self):
        return 42

    @property
    def country_name(self):
        """ Get country name based on country code

        :return: 'Latvia'
        """

        name = self._country_folder.Title()

        return name

    @property
    def desc_label(self):
        """ Get the label(text) for a descriptor

        :return: 'D5 Eutrophication'
        """

        res = self._descriptor_folder.Title()

        return res

    @property
    def descriptor_label(self):
        # same as desc_label

        return self._descriptor_folder.Title()

    @property
    @db.use_db_session('2012')
    def regions(self):
        """ Get all regions and subregions for a country

        :return: ['BAL', 'ANS']
        """

        t = sql.t_MSFD4_GegraphicalAreasID
        count, res = db.get_all_records(
            t,
            t.c.MemberState == self.country_code
        )

        res = [row_to_dict(t, r) for r in res]
        regions = set([x['RegionSubRegions'] for x in res])

        return regions

    @property
    def muids(self):
        """ Get all Marine Units for a country

        :return: ['BAL- LV- AA- 001', 'BAL- LV- AA- 002', ...]
        """

        return get_marine_units(self.country_code,
                                self.country_region_code,
                                self.year)

    def get_parent_by_iface(self, iface):
        for parent in self.request.other['PARENTS']:
            if iface.providedBy(parent):
                return parent

        raise ValueError('Parent not found: {}'.format(iface))

    def root_url(self):
        root = self.get_parent_by_iface(interfaces.IComplianceModuleFolder)

        return root and root.absolute_url() or ''

    @property
    def _article_assessment(self):
        return self.get_parent_by_iface(
            interfaces.INationalDescriptorAssessment
        )

    @property
    def article(self):
        return self._article_assessment.getId().capitalize()

    @property
    def _descriptor_folder(self):
        return self.get_parent_by_iface(
            interfaces.IDescriptorFolder
        )

    @property
    def descriptor(self):
        if self._descriptor:        # can be bypassed for D1
            return self._descriptor

        return self._descriptor_folder.getId().upper()

    @property
    def _country_folder(self):
        return self.get_parent_by_iface(
            interfaces.ICountryDescriptorsFolder
        )

    @property
    def country_code(self):
        return self._country_folder.getId().upper()

    @property
    def country_title(self):
        return self._country_folder.title

    @property
    def _countryregion_folder(self):
        return self.get_parent_by_iface(
            interfaces.INationalRegionDescriptorFolder
        )

    @property
    def country_region_code(self):
        return self._countryregion_folder.getId().upper()

    @property
    def country_region_name(self):
        return REGIONS[self.country_region_code]

    @property
    def article_name(self):
        art_name = [x[1] for x in ASSESSED_ARTICLES if x[0] == self.article]

        if art_name:
            return art_name[0]

        return self.article

    @property       # TODO: memoize
    def descriptor_obj(self):
        return get_descriptor(self.descriptor)

    @property
    def _national_descriptors_folder(self):
        return self.get_parent_by_iface(
            interfaces.INationalDescriptorsFolder
        )

    @property
    def _compliance_folder(self):
        return self.get_parent_by_iface(
            interfaces.IComplianceModuleFolder
        )

    def process_phase(self, context=None):
        if context is None:
            context = self.context

        state = get_state(context)
        wftool = get_tool('portal_workflow')
        wf = wftool.getWorkflowsFor(context)[0]        # assumes one wf
        wf_state = wf.states[state]
        title = wf_state.title.strip() or state

        return state, title

    def get_status(self, context=None):
        if context is None:
            context = self.context

        state = get_state(context)
        wftool = get_tool('portal_workflow')
        wf = wftool.getWorkflowsFor(context)[0]        # assumes one wf
        wf_state = wf.states[state]
        title = wf_state.title.strip() or state

        return title

    def get_transitions(self):
        wftool = get_tool('portal_workflow')
        transitions = wftool.listActionInfos(object=self.context)

        return [t for t in transitions if t['allowed']]

    def check_permission(self, permission, context=None):

        tool = get_tool('portal_membership')

        if context is None:
            context = self.context

        return bool(tool.checkPermission(permission, aq_inner(context)))

    @memoize
    def translate_view(self):
        return getMultiAdapter((self.context, self.request),
                               name="translation-view")

    def translate_value(self, fieldname, value):
        is_translatable = fieldname in self.TRANSLATABLES

        v = self.translate_view()

        source_lang = self.country_code

        return v.translate(source_lang=source_lang,
                           value=value,
                           is_translatable=is_translatable)


Target = namedtuple('Target', ['id', 'title', 'definition'])


def _a10_ids_cachekey(method, self, descriptor, **kwargs):
    muids = [m.id for m in kwargs['muids']]

    return '{}-{}'.format(descriptor.id, ','.join(muids))


class AssessmentQuestionDefinition:
    """ A definition for a single assessment question.

    Pass an <assessment-question> node to initialize it
    """

    def __init__(self, article, node, root, position):
        self.article = article
        self.id = node.get('id')
        self.klass = node.get('class')
        self.use_criteria = node.get('use-criteria')
        self.definition = u"Q{}: {}".format(
            position + 1, node.find('definition').text.strip())
        self.answers = [x.strip()
                        for x in node.xpath('answers/option/text()')]

        self.score_weights = {}

        for wn in node.iterchildren('score-weight'):
            desc = wn.get('descriptor')
            weight = wn.get('value')
            self.score_weights[desc] = weight

        sn = node.find('scoring')
        self.score_method_factory = resolve(sn.get('determination-method'))
        self.score_method_args = sn.get('determination-method-args')

        factory_method = self.score_method_factory
        method = factory_method(self.score_method_args)
        self.score_method = method

        self.scores = []

        # TODO: why do we need scoring and options as well?

        for onode in sn.iterchildren('option'):
            try:
                si = (int(onode.get('score')), onode.text.strip())
            except:
                import pdb
                pdb.set_trace()
            self.scores.append(si)

    def calculate_score(self, descriptor, values):
        return compute_score(self, descriptor, values)

    def _art_89_ids(self, descriptor, **kwargs):
        return sorted_criterions(descriptor.criterions)

    @ram.cache(_a10_ids_cachekey)
    @db.use_db_session('2012')
    def _art_10_ids(self, descriptor, **kwargs):
        muids = [x.id for x in kwargs['muids']]
        ok_ges_ids = descriptor.all_ids()

        sess = db.session()
        T = sql.MSFD10Target
        dt = sql.t_MSFD10_DESCrit

        D_q = sess.query(dt).join(T)
        D_a = aliased(dt, alias=D_q.subquery())

        targets = sess\
            .query(T)\
            .order_by(T.ReportingFeature)\
            .filter(T.MarineUnitID.in_(muids))\
            .filter(T.Topic == 'EnvironmentalTarget')\
            .join(D_a)\
            .filter(D_a.c.GESDescriptorsCriteriaIndicators.in_(ok_ges_ids))\
            .distinct()\
            .all()
        print 'Resulting targets: ', len(targets)

        # TODO: also get 2012 targets here

        return [Target(r.ReportingFeature.replace(' ', '_').lower(),
                       r.ReportingFeature,
                       r.Description) for r in targets]

    def get_assessed_elements(self, descriptor, **kwargs):
        """ Get a list of filtered assessed elements for this question.
        """

        res = self.get_all_assessed_elements(descriptor, **kwargs)

        if self.article in ['Art8', 'Art9']:
            res = filtered_criterias(res, self)

        return sorted_criterions(res)

    def get_all_assessed_elements(self, descriptor, **kwargs):
        """ Get a list of unfiltered assessed elements for this question.

        For Articles 8, 9 it returns a list of criteria elements
        For Article 10 it returns a list of targets

        Return a list of identifiable elements that need to be assessed.
        """
        impl = {
            'Art8': self._art_89_ids,
            'Art9': self._art_89_ids,
            'Art10': self._art_10_ids,
        }

        return impl[self.article](descriptor, **kwargs)


def filtered_questions(questions, phase):
    """ Get the questions appropriate for the phase
    """

    if phase == 'phase3':
        res = [q for q in questions if q.klass == 'coherence']
    else:
        res = [q for q in questions if q.klass != 'coherence']

    return res


def filtered_criterias(criterias, question):

    if question.use_criteria == 'primary':
        crits = [c for c in criterias if c.is_primary is True]

    if question.use_criteria == 'secondary':
        crits = [c for c in criterias if c.is_primary is False]

    # TODO what to return

    if question.use_criteria == 'none':
        crits = []

    return sorted_criterions(crits)


def parse_question_file(fpath):
    res = []

    root = lxml.etree.parse(fpath).getroot()
    article_id = root.get('article')

    for i, qn in enumerate(root.iterchildren('assessment-question')):
        q = AssessmentQuestionDefinition(article_id, qn, root, i)
        res.append(q)

    return article_id, res


def get_questions(location):
    def check_filename(fname):
        return fname.startswith('questions_')

    return _parse_files_in_location(location,
                                    check_filename, parse_question_file)


class BaseArticle2012(BrowserView):

    def __init__(self, context, request, country_code, region_code,
                 descriptor, article,  muids):

        BrowserView.__init__(self, context, request)

        self.country_code = country_code
        self.region_code = region_code
        self.descriptor = descriptor
        self.article = article
        self.muids = muids


class TranslationContext(object):
    implements(ITranslationContext)

    def __init__(self, context):
        self.context = context

    @property
    def language(self):
        for context in self.context.REQUEST.PARENTS:
            if ICountryDescriptorsFolder.providedBy(context):
                return context.getId().upper()

        return 'EN'
