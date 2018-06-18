import mwbase
import json

from ....datasources import Datasource
from ....dependencies import DependentSet
from .diff import Diff


class Revision(DependentSet):

    def __init__(self, name, revision_datasources):
        super().__init__(name)

        self.text = revision_datasources.text

        self.entity = Datasource(
            name + ".entity", _process_entity,
            depends_on=[self.text]
        )
        """
        A `~mwbase.Entity` for the Wikibase content
        """

        self.sitelinks = Datasource(
            name + ".sitelinks", _process_sitelinks, depends_on=[self.entity]
        )
        """
        A `dict` of wiki/sitelink pairs in the revision
        """

        self.labels = Datasource(
            name + ".labels", _process_labels, depends_on=[self.entity]
        )
        """
        A `dict` of lang/label pairs in the revision
        """

        self.aliases = Datasource(
            name + ".aliases", _process_aliases, depends_on=[self.entity]
        )
        """
        A `dict` of lang_code/aliases in the revision
        """

        self.descriptions = Datasource(
            name + ".descriptions", _process_descriptions,
            depends_on=[self.entity]
        )
        """
        A `dict` of lang_code/description pairs in the revision
        """

        self.properties = Datasource(
            name + ".properties", _process_properties, depends_on=[self.entity]
        )
        """
        A `dict` of properties with statement lists in the revision
        """

        self.claims = Datasource(
            name + ".claim", _process_claims, depends_on=[self.entity]
        )
        """
        A `set` of unique claims in the revision
        """

        self.references = Datasource(
            name + ".references", _process_references, depends_on=[self.entity]
        )
        """
        A `set` of unique references in the revision
        """

        self.qualifiers = Datasource(
            name + ".qualifiers", _process_qualifiers, depends_on=[self.entity]
        )
        """
        A `set` of unique qualifiers in the revision
        """

        self.badges = Datasource(
            name + ".badges", _process_badges, depends_on=[self.entity]
        )
        """
        A `set` of unique badges in the revision
        """

        if hasattr(revision_datasources, "parent") and \
           hasattr(revision_datasources.parent, "text"):
            self.parent = Revision(
                name + ".parent",
                revision_datasources.parent
            )

            if hasattr(revision_datasources, "diff"):
                self.diff = Diff(name + ".diff", self)


def _process_entity(text):
    if text is not None:
        return mwbase.Entity.from_json(text)
    else:
        return mwbase.Entity.from_json({})


def _process_labels(entity):
    return entity.labels


def _process_descriptions(entity):
    return entity.descriptions


def _process_aliases(entity):
    return entity.aliases


def _process_properties(entity):
    return entity.properties


def _process_sitelinks(entity):
    return entity.sitelinks

def _process_claims(entity):
    return set(
        (property, str(statement.claim.datavalue))
        for property in entity.properties
        for statement in entity.properties[property]
    )

def _process_references(entity):
    return set(
        (property, str(statement.claim.datavalue), len(statement.references))
        for property in entity.properties
        for statement in entity.properties[property]
    )

def _process_qualifiers(entity):
    return set(
    (property, claim, qualifier)
    for property in entity.claims
    for claim in entity.claims[property]
    for qualifier in entity.qualifiers
    )

def _process_badges(entity):
    return entity.badges
