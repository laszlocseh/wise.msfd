from collections import defaultdict
from itertools import chain
from operator import attrgetter

from Products.Five.browser import BrowserView
from wise.msfd.labels import GES_LABELS
from wise.msfd.utils import ItemLabel, ItemList, LabeledItemList, timeit

from .proxy import proxy_cmp


def consolidate_date_by_mru(data):
    """ Takes data (proxies of data) organized by mru and groups them according
    to similarity of data (while ignoring the mru of that proxied row)

    This is used by the A9 2018 report.
    """

    groups = []

    # Rows without MRU reported
    # This case applies for Art9, when justification for delay is reported
    rows_without_mru = []

    for obj in chain(*data.values()):
        found = False

        for group in groups:
            # compare only with the first object from a group because
            # all objects from a group should contain the same data
            first_from_group = group[0]

            if proxy_cmp(obj, first_from_group):
                group.append(obj)
                found = True

        if not found:
            groups.append([obj])

    # regroup the data by mru, now that we found identical rows
    regroup = defaultdict(list)

    for batch in groups:
        # TODO: get a proper MarineUnitID object
        mrus = tuple(sorted(set([r.MarineReportingUnit for r in batch])))

        if mrus[0] is None:
            rows_without_mru.append(batch[0])

            continue

        regroup[mrus].append(batch[0])

    out = {}

    # rewrite the result keys to list of MRUs

    for mrus, rows in regroup.items():
        mrus_labeled = tuple([
            ItemLabel(row, u'{} ({})'.format(GES_LABELS.get('mrus', row), row))

            for row in mrus
        ])
        label = LabeledItemList(rows=mrus_labeled)

        # TODO how to explain better?
        # Skip rows from rows_without_mru if the GESComponent exists
        # in rows (we do not insert justification delay/non-use
        # if the GESComponent has reported data)
        # example: ges component D6C3, D6C4
        # .../fi/bal/d6/art9/@@view-report-data-2018

        ges_comps_with_data = set(x.GESComponent.id for x in rows)

        for row_extra in rows_without_mru:
            ges_comp = row_extra.GESComponent.id

            if ges_comp in ges_comps_with_data:
                continue

            rows.append(row_extra)

        # rows.extend(rows_without_mru)
        out[label] = rows

    if not regroup and rows_without_mru:
        rows = ItemLabel('No Marine unit ID reported',
                         'No Marine unit ID reported')
        label = LabeledItemList(rows=(rows, ))
        out[label] = rows_without_mru

    return out


@timeit
def consolidate_singlevalue_to_list(proxies, fieldname, order=None):
    """ Given a list of proxies where one of the fields needs to be a list, but
    is spread across different similar proxies, consolidate the single values
    to a list and return only one object for that list of similar objects
    """

    map_ = defaultdict(list)

    for o in proxies:
        map_[o.hash(fieldname)].append(o)

    res = []

    for set_ in map_.values():
        o = set_[0]
        values = [getattr(xo, fieldname) for xo in set_]

        if any(values):
            l = ItemList(rows=values)
            setattr(o, fieldname, l)

        res.append(o)

    # consolidate_singlevalue_to_list is used in regional descriptor too
    # where we do not order the results
    if order:
        res = list(sorted(res, key=attrgetter(*order)))

    return res


class ViewSavedAssessmentData(BrowserView):
    """ Temporary class for viewing saved assessment data
    """

    def get_saved_assessment_data(self):
        catalog = self.context.portal_catalog

        brains = catalog.searchResults(
            portal_type='wise.msfd.nationaldescriptorassessment',
            path={
                "query": "/Plone/marine/assessment-module"
                         "/national-descriptors-assessments"
            }
        )

        res = []

        for brain in brains:
            obj = brain.getObject()
            if not hasattr(obj, 'saved_assessment_data'):
                continue

            sad = obj.saved_assessment_data

            if not sad:
                continue

            if len(sad) == 1:
                continue

            # import pdb; pdb.set_trace()
            res.append((obj, obj.saved_assessment_data))

        return res

    def fix_assessment_data(self):
        from wise.msfd.compliance.content import AssessmentData

        for obj, data in self.get_saved_assessment_data():
            last = data.last().copy()

            new_data = AssessmentData()
            new_data._append(last)

            obj.saved_assessment_data = new_data

    def __call__(self):
        if 'fix' in self.request.form:
            self.fix_assessment_data()

            return 'Done'

        return self.index()