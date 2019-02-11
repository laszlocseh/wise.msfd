import datetime
import logging
from collections import namedtuple

from zope.schema import Choice, Text
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from persistent.list import PersistentList
from plone.api import user
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import (PageTemplateFile,
                                                    ViewPageTemplateFile)
from wise.msfd.base import EmbeddedForm, MainFormWrapper
from wise.msfd.compliance.base import get_questions
from wise.msfd.compliance.content import AssessmentData
from wise.msfd.compliance.interfaces import ICountryDescriptorsFolder
from wise.msfd.gescomponents import get_descriptor  # , get_descriptor_elements
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form

from ..base import BaseComplianceView

logger = logging.getLogger('wise.msfd')

# TODO which question type belongs to which phase?
PHASES = {
    'phase1': ('adequacy', 'consistency'),
    'phase2': ('coherence', ),
    'phase3': (),
}

# mapping of title: field_name
additional_fields = {
    'Summary': u'Summary',
}

summary_fields = (
    ('assessment_summary', u'Assessment summary'),
    ('recommendations', u'Recommendations for Member State'),
)

progress_fields = (
    ('progress', u'Progress assessment'),
)


class EditAssessmentSummaryForm(Form, BaseComplianceView):
    """ Edit the assessment summary

    Fields are: summary, recommendations, progress assessment
    """

    title = u"Edit progress assessment"
    template = ViewPageTemplateFile("../pt/inline-form.pt")
    _saved = False

    @property
    def fields(self):
        saved_data = self.context.saved_assessment_data.last()

        _fields = []

        for name, title in progress_fields:
            _name = '{}_{}'.format(
                self.article, name
            )

            default = saved_data.get(_name, None)
            _field = Text(title=u'',
                          __name__=_name, required=False, default=default)
            _fields.append(_field)

        print "fields"

        return Fields(*_fields)

    @buttonAndHandler(u'Save', name='save')
    def handle_save(self, action):
        data, errors = self.extractData()

        if errors:
            return

        context = self.context

        # BBB code, useful in development

        if not hasattr(context, 'saved_assessment_data') or \
                not isinstance(context.saved_assessment_data, PersistentList):
            context.saved_assessment_data = AssessmentData()

        saved_data = self.context.saved_assessment_data.last()

        if not saved_data:
            self.context.saved_assessment_data.append(data)
        else:
            saved_data.update(data)
        self.context.saved_assessment_data._p_changed = True

        print "handle save"

    def nextURL(self):
        print 'nexturl'

        return self.context.absolute_url()

    @property
    def action(self):

        print 'action'

        return self.context.absolute_url() + '/@@edit-assessment-summary'

    def render(self):

        if self.request.method == 'POST':
            Form.render(self)
            print "Done render"

            return self.request.response.redirect(self.nextURL())

        return Form.render(self)


class EditAssessmentDataForm(Form, BaseComplianceView):
    """ Edit the assessment for a national descriptor, for a specific article
    """
    name = 'art-view'

    subforms = None
    session_name = '2018'
    template = ViewPageTemplateFile("./pt/edit-assessment-data.pt")

    @property
    def help(self):
        return render_assessment_help(self.criterias)

    @property
    def title(self):
        return "Edit {}'s Assessment for {}/{}/{}".format(
            self.country_title,
            self.descriptor,
            self.country_region_code,
            self.article,
        )

    # @property
    # def process_phase_title(self):
    #     _, title = self.current_phase
    #
    #     return 'Current process phase: {}'.format(title)

    @buttonAndHandler(u'Save', name='save')
    def handle_save(self, action):
        data, errors = self.extractData()
        # if not errors:
        # TODO: check for errors

        for question in self.questions:
            # criterias = filtered_criterias(self.criterias, question)
            elements = question.get_assessed_elements(self.descriptor_obj)

            values = []

            if question.use_criteria == 'none':
                field_name = '{}_{}'.format(self.article, question.id)
                values.append(data.get(field_name, None))

            for element in elements:
                field_name = '{}_{}_{}'.format(
                    self.article, question.id, element.id
                )
                values.append(data.get(field_name, None))

            # TODO update the score if all fields have been answered
            # score is updated if one of the fields has been answered
            values = [x for x in values if x is not None]

            if values:
                conclusion, raw_score, score = question.calculate_score(
                    self.descriptor, values)

                name = '{}_{}_Score'.format(self.article, question.id)
                logger.info("Set score: %s - %s", name, score)
                data[name] = score

                name = '{}_{}_RawScore'.format(self.article, question.id)
                data[name] = raw_score

                name = '{}_{}_Conclusion'.format(self.article, question.id)
                logger.info("Set conclusion: %s - %s", name, conclusion)
                data[name] = conclusion

        # TODO: update the overall score
        overall_score = 0

        for k, v in data.items():
            if not k.endswith('_Score'):
                continue
            else:
                overall_score += v

        data['OverallScore'] = overall_score

        try:
            data['assessor'] = user.get_current().getId()
        except:
            data['assessor'] = 'system'

        data['assess_date'] = datetime.date.today()

        # BBB code, useful for development
        context = self.context

        if not hasattr(context, 'saved_assessment_data') or \
                not isinstance(context.saved_assessment_data, PersistentList):
            context.saved_assessment_data = AssessmentData()
        last = self.context.saved_assessment_data.last()

        if last != data:
            last.update(data)
            self.context.saved_assessment_data.append(last)

    @property
    def current_phase(self):
        country_folder = self.get_parent_by_iface(ICountryDescriptorsFolder)
        state, title = self.process_phase(country_folder)

        return state, title

    def is_disabled(self, question):
        state, _ = self.current_phase
        disabled = question.klass not in PHASES.get(state, ())

        return disabled

    @property
    def fields(self):
        if not self.subforms:
            self.subforms = self.get_subforms()

        fields = []

        for subform in self.subforms:
            fields.extend(subform.fields._data_values)

        return Fields(*fields)

    @property       # TODO: memoize
    def descriptor_obj(self):
        return get_descriptor(self.descriptor)

    # @property
    # def criterias(self):
    #     return self.descriptor_obj.criterions

    # TODO: use memoize
    @property
    def questions(self):
        qs = get_questions(
            'compliance/nationaldescriptors/data'
        )

        return qs[self.article]

    def get_subforms(self):
        """ Build a form of options from a tree of options

        TODO: this method does too much, should be refactored
        """

        assessment_data = {}

        if hasattr(self.context, 'saved_assessment_data'):
            assessment_data = self.context.saved_assessment_data.last()

        forms = []

        for question in self.questions:
            phase = [
                k

                for k, v in PHASES.items()

                if question.klass in v
            ][0]

            elements = question.get_assessed_elements(
                self.descriptor_obj
            )

            form = EmbeddedForm(self, self.request)
            form.title = question.definition
            form._question_type = question.klass
            form._question_phase = phase
            form._question = question
            form._elements = elements
            form._disabled = self.is_disabled(question)
            fields = []

            if not elements:       # when use-criteria == 'none'
                field_title = u'All criterias'
                field_name = '{}_{}'.format(self.article, question.id)
                choices = question.answers

                terms = [SimpleTerm(token=i, value=i, title=c)
                         for i, c in enumerate(choices)]

                # Add 'Not relevant' to choices list
                terms.extend([
                    SimpleTerm(token=len(terms) + 1,
                               value=None,
                               title=u'Not relevant')
                ])

                default = assessment_data.get(field_name, None)
                field = Choice(
                    title=field_title,
                    __name__=field_name,
                    vocabulary=SimpleVocabulary(terms),
                    required=False,
                    default=default,
                )
                # field._criteria = criteria
                fields.append(field)

            for element in elements:
                field_title = element.title
                field_name = '{}_{}_{}'.format(
                    self.article, question.id, element.id       # , element
                )
                choices = question.answers
                terms = [SimpleTerm(token=i, value=i, title=c)
                         for i, c in enumerate(choices)]
                # Add 'Not relevant' to choices list
                terms.extend([
                    SimpleTerm(token=len(terms) + 1,
                               value=None,
                               title=u'Not relevant')
                ])
                default = assessment_data.get(field_name, None)
                field = Choice(
                    title=field_title,
                    __name__=field_name,
                    vocabulary=SimpleVocabulary(terms),
                    required=False,
                    default=default,
                )
                field._element = element
                fields.append(field)

            for name, title in additional_fields.items():
                _name = '{}_{}_{}'.format(self.article, question.id, name)

                default = assessment_data.get(_name, None)
                _field = Text(title=title,
                              __name__=_name, required=False, default=default)

                fields.append(_field)

            form.fields = Fields(*fields)
            forms.append(form)

        assessment_summary_form = EmbeddedForm(self, self.request)
        assessment_summary_form.title = u"Assessment summary"
        assessment_summary_form.subtitle = u''
        assessment_summary_form._disabled = False
        asf_fields = []

        for name, title in summary_fields:
            _name = '{}_{}'.format(
                self.article, name
            )

            default = assessment_data.get(_name, None)
            _field = Text(title=title,
                          __name__=_name, required=False, default=default)
            asf_fields.append(_field)

        assessment_summary_form.fields = Fields(*asf_fields)

        forms.append(assessment_summary_form)

        return forms


EditAssessmentDataView = wrap_form(EditAssessmentDataForm, MainFormWrapper)

Cell = namedtuple('Cell', ['text', 'rowspan'])


help_template = PageTemplateFile('./pt/assessment-question-help.pt')


def render_assessment_help(criterias):
    elements = []
    methods = []

    for c in criterias:
        elements.extend([e.id for e in c.elements])
        methods.append(c.methodological_standard.id)

    element_count = {}

    for k in elements:
        element_count[k] = elements.count(k)

    method_count = {}

    for k in methods:
        method_count[k] = methods.count(k)

    rows = []
    seen = []

    for c in criterias:
        row = []

        if not c.elements:
            logger.info("Skipping %r from help rendering", c)

            continue
        cel = c.elements[0]     # TODO: also support multiple elements

        if cel.id not in seen:
            seen.append(cel.id)
            rowspan = element_count[cel.id]
            cell = Cell(cel.definition, rowspan)
            row.append(cell)

        prim_label = c.is_primary and 'primary' or 'secondary'
        cdef = u"<strong>{} ({})</strong><br/>{}".format(
            c.id, prim_label, c.definition
        )

        cell = Cell(cdef, 1)
        row.append(cell)

        meth = c.methodological_standard

        if meth.id not in seen:
            seen.append(meth.id)
            rowspan = method_count[meth.id]
            cell = Cell(meth.definition, rowspan)
            row.append(cell)

        rows.append(row)

    return help_template(rows=rows)
