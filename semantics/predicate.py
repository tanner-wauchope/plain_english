from plain_english.semantics import relations, entities


class Predicate:
    """
    Verb phrases represents bindings of arguments to a verb.
    These objects manage when a verb's procedure should be called.
    """
    def __init__(self, name, subject=None, complement=None, query=None):
        self.name = name
        self.subject = subject
        self.complement = complement
        self.query = query
        self.support_text = ''

    def __call__(self, complement=''):
        """
        :param complement: an ordered set or text containing supporting sentences
                           The complement can be an empty string for 1-sentence paragraphs.
        :return: If the complement is support text,
                 either execute the whole paragraph or define a new verb.
                 Otherwise, store the complement and return this predicate.
        """
        if isinstance(complement, str):
            self.resolve_arguments()
            self.support_text = complement
            self.resolve_predicate(complement)
        else:
            self.complement = complement
            return self

    def resolve_predicate(self, support_sentences):
        """
        A name error is thrown if the name is not formatted correctly.
        Run the topic sentence and support sentences if:
            the name references a behavior and the statement is definite.
        Run the topic sentences and add support sentences to a definition if:
            the name references a behavior and the statement is indefinite.
        Do not run anything and add the support sentences to a definition if:
            the verb name is quoted.
        A name error is thrown non-quoted verb name doesn't reference a behavior.
        """
        previously_defined = hasattr(self.subject.kind, self.name)
        definite = self.definite()
        if not self.name.endswith('_'):
            raise NameError(self.name)
        elif previously_defined and definite:
            behavior = getattr(self.subject.kind, self.name)
            behavior.run(self.subject, self.complement)
            lines = support_sentences.split('\n')
            executables = '()\n'.join(lines) + '()'
            exec(executables, self.subject.scope())
        elif previously_defined and not definite:
            behavior = getattr(self.subject.kind, self.name)
            behavior.run(self.subject, self.complement)
            behavior.definitions.append(self)
        elif self.name.startswith('_'):
            new_name = self.name[1:]
            behavior = relations.Relation(new_name, definitions=[self])
            setattr(self.subject.kind, new_name, behavior)
        else:
            raise NameError(self.name)

    def definite(self):
        definite_subject = self.subject and self.subject.definite()
        definite_complement = self.complement and self.complement.definite()
        return definite_subject and definite_complement

    def resolve_arguments(self):
        self.subject.members = self.subject.resolve()
        if self.complement:
            self.complement.members = self.complement.resolve()


class ExceededCardinalityError(Exception):
    pass


class OrderedSet:
    def __init__(self, determiner, name, plural=None, kind=None, members=None):
        self.determiner = determiner
        self.name = name
        self.kind = kind or entities.Entity
        self.members = members or []

    def plural(self):
        return self.name in self.scope()

    def scope(self):
        return self.determiner.scope

    def __eq__(self, other):
        return self.members == other.members

    def __getattr__(self, item):
        """
        :param item: the name of a verb or a name wrapped in '_'
        :return: a Verb Phrase with this noun phrase as its subject
        """
        return Predicate(item, subject=self)

    def __call__(self, complement, eager=False):
        """
        :param complement: a relative clause or
                           a string representing a primitive
        :param eager: whether to query if this group is indefinite
        :return: a group containing a new primitive or
                 a group whose members result from a query or
                 a group with an un-queried relative clause
        """
        if not isinstance(complement, Predicate):
            primitive = self.kind(complement, self.scope())
            self.members = [primitive.format(self.scope())]
            return self
        elif eager or self.members:
            return OrderedSet(
                self.determiner,
                self.name,
                kind=self.kind,
                members=self.resolve(complement.query(self, complement)),
            )
        else:
            self.relative_clause = complement
            return self

    def add(self, members):
        if len(self.members) + len(members) > 1 and not self.plural():
            raise ExceededCardinalityError((self, self.members))
        self.members.extend(members)

    def resolve(self, members=None):
        members = members or self.members
        if self.plural():
            return members
        else:
            return self.members[-1:]

    def copy(self):
        return OrderedSet(
            self.determiner,
            self.name,
            kind=self.kind,
            members=list(self.members),
        )

    def accepts(self, other):
        # TODO: should check if the parm satisfies any relative clause on self
        other_ancestors = ancestors(other.kind)
        return self.kind in other_ancestors

    def instantiate(self):
        complement = self.copy()
        instance = self.kind()
        self.members.append(instance)
        self.scope()['singular'][self.name].members.append(instance)
        self.is_(complement)

    def definite(self):
        return self.determiner.DEFINITE

    def full(self):
        return not self.plural() and self.members

def ancestors(kind):
    if not kind.__bases__:
        return [kind]
    return ancestors(kind.__bases__[0]) + [kind]