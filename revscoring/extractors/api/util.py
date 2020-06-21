from ...datasources import Datasource

REV_PROPS = {'ids', 'user', 'timestamp', 'userid', 'comment', 'size',
             'contentmodel'}
USER_PROPS = {'groups', 'editcount', 'gender', 'registration'}


def identity(v):
    return v


class key(Datasource):

    def __init__(self, keys, dict_datasource, name=None, if_missing=None,
                 apply=None):
        self.keys = keys
        self.if_missing = if_missing
        self.apply = apply or identity
        if name is None:
            name = "{0}[{1}]".format(dict_datasource.name, repr(keys))

        super().__init__(name, self.process, depends_on=[dict_datasource])

    def process(self, d):
        if d is None:
            # Special case for when no doc could be found and that is OK
            return None

        try:
            value = _lookup_keys(self.keys, d)
        except KeyError:
            if self.if_missing is not None:
                Exc, args = self.if_missing[0], self.if_missing[1:]
                raise Exc(*args)
            else:
                return None

        return self.apply(value)


class key_exists(Datasource):

    def __init__(self, key, dict_datasource, name=None):
        self.key = key
        if name is None:
            name = "{1} in {0}".format(dict_datasource.name, repr(key))

        super().__init__(name, self.process, depends_on=[dict_datasource])

    def process(self, d):
        return self.key in d


def _lookup_keys(keys, d):
    if isinstance(keys, str) or not hasattr(keys, "__iter__"):
        keys = [keys]
    try:
        for key in keys:
            d = d[key]
    except KeyError:
        if ('.').join(keys) == 'slots.main.*':
            d = d['*']
            return d
        raise KeyError(keys)
    return d
