from zope.interface import implements

from plone.dexterity.content import Container

from .interfaces import (ICountryDescriptorsFolder,
                         INationalDescriptorAssessment)


class CountryDescriptorsFolder(Container):
    """ Assessment implementation for national descriptor assessments
    """
    implements(ICountryDescriptorsFolder)


class NationalDescriptorAssessment(Container):
    """ Assessment implementation for national descriptor assessments
    """

    implements(INationalDescriptorAssessment)
    _data = None

    def _get_assessment_data(self):
        return self._data or {}

    def _set_assessment_data(self, value):
        self._data = value
        self._p_changed = True

    assessment_data = property(_get_assessment_data, _set_assessment_data)
