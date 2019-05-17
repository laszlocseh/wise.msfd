import datetime
import logging

from zope.schema import Choice, Text
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.security import checkPermission

from AccessControl import Unauthorized
from persistent.list import PersistentList
from plone.api import user
from plone.api.user import get_roles
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import (PageTemplateFile,
                                                    ViewPageTemplateFile)
from wise.msfd.base import EmbeddedForm, MainFormWrapper
from wise.msfd.compliance.assessment import (additional_fields, summary_fields,
                                             render_assessment_help, PHASES)
from wise.msfd.compliance.base import get_questions
from wise.msfd.compliance.content import AssessmentData
from wise.msfd.gescomponents import get_descriptor  # get_descriptor_elements

from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form

from .base import BaseView

logger = logging.getLogger('wise.msfd')


class EditAssessmentDataForm(Form, BaseView):
    """ Edit the assessment for a national descriptor, for a specific article
    """
    name = 'art-view'
    section = 'national-descriptors'

    subforms = None
    year = session_name = '2018'
    template = ViewPageTemplateFile("./pt/edit-assessment-data.pt")
    _questions = get_questions()

    @property
    def criterias(self):
        return self.descriptor_obj.sorted_criterions()      # criterions

    @property
    def help(self):
        return render_assessment_help(self.criterias, self.descriptor)

    @property
    def title(self):
        return "Edit {}'s Assessment for {}/{}/{}".format(
            self.country_title,
            self.descriptor,
            self.country_region_code,
            self.article,
        )

    def _can_comment(self, folder_id):
        folder = self.context[folder_id]

        return checkPermission('zope2.View', folder)

    @property
    def can_comment_tl(self):
        return self._can_comment('tl')

    @property
    def can_comment_ec(self):
        return self._can_comment('ec')

    @buttonAndHandler(u'Save', name='save')
    def handle_save(self, action):

        roles = get_roles(obj=self.context)

        if 'Contributor' not in roles and ('Manager' not in roles):
            raise Unauthorized

        data, errors = self.extractData()
        # if not errors:
        # TODO: check for errors

        for question in self.questions:
            elements = question.get_assessed_elements(self.descriptor_obj,
                                                      muids=self.muids)

            values = []
            score = None

            if question.use_criteria == 'none':
                field_name = '{}_{}'.format(self.article, question.id)
                values.append(data.get(field_name, None))

            for element in elements:
                field_name = '{}_{}_{}'.format(
                    self.article, question.id, element.id
                )
                values.append(data.get(field_name, None))

            # score is updated if ALL of the fields have been answered

            if values and None not in values:
                score = question.calculate_score(self.descriptor, values)

            name = '{}_{}_Score'.format(self.article, question.id)
            logger.info("Set score: %s - %s", name, score)
            data[name] = score

            # name = '{}_{}_RawScore'.format(self.article, question.id)
            # data[name] = raw_score

            # name = '{}_{}_Conclusion'.format(self.article, question.id)
            # logger.info("Set conclusion: %s - %s", name, conclusion)
            # data[name] = conclusion

        # TODO: update the overall score
        overall_score = 0

        for k, v in data.items():
            if not k.endswith('_Score'):
                continue
            else:
                overall_score += getattr(v, 'weighted_score', 0)

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

    # TODO: use memoize
    @property
    def questions(self):
        qs = self._questions[self.article]

        return qs

    def get_subforms(self):
        """ Build a form of options from a tree of options

        TODO: this method does too much, should be refactored
        """
        assessment_data = {}

        if hasattr(self.context, 'saved_assessment_data'):
            assessment_data = self.context.saved_assessment_data.last()

        forms = []

        is_ec_user = not self.can_comment_tl
        is_other_tl = not (self.can_comment_tl or self.can_comment_tl)

        for question in self.questions:
            phase = [
                k

                for k, v in PHASES.items()

                if question.klass in v
            ][0]

            elements = question.get_assessed_elements(
                self.descriptor_obj, muids=self.muids
            )

            form = EmbeddedForm(self, self.request)
            form.title = question.definition
            form._question_type = question.klass
            form._question_phase = phase
            form._question = question
            form._elements = elements
            form._disabled = self.is_disabled(
                question) or is_other_tl or is_ec_user

            fields = []

            if not elements:  # and question.use_criteria == 'none'
                field_title = u'All criteria'
                field_name = '{}_{}'.format(self.article, question.id)
                choices = question.answers

                terms = [SimpleTerm(token=i, value=i, title=c)
                         for i, c in enumerate(choices)]

                # Add 'Not relevant' to choices list
                # terms.extend([
                #     SimpleTerm(token=len(terms) + 1,
                #                value=None,
                #                title=u'Not relevant')
                # ])

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
                # terms.extend([
                #     SimpleTerm(token=len(terms) + 1,
                #                value=None,
                #                title=u'Not relevant')
                # ])
                default = assessment_data.get(field_name, None)
                field = Choice(
                    title=unicode(field_title),
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
        assessment_summary_form._disabled = not self.can_comment_tl
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
