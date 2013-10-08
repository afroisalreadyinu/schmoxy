
class BiDict(object):
    def __init__(self):
        self.one = dict()
        self.two = dict()

    def __getitem__(self, key):
        try:
            return self.one[key]
        except KeyError:
            return self.two[key]

    def __setitem__(self, key, value):
        self.one[key] = value
        self.two[value] = key
