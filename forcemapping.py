import bisect
import json
import logging
import os.path
from collections import OrderedDict


# TODO 'KeysView' object does not support indexing
class ForceMapping(object):
    def __init__(self):
        self._map = dict(
            [(0, 0), (50, 5826), (60, 6783), (70, 7209), (80, 8177), (90, 8816), (100, 9498), (130, 11469)])
        self._reverse = self.reverse(self._map)

    def configure(self, key, value):
        if key in self._map:
            self._map[key] = value
        else:
            raise Exception('No such key ' + key)
        self._reverse = self.reverse(self._map)

    def get(self, key):
        try:
            return self._map[key]
        except KeyError as e:
            logging.exception('Map value missing')
            return 0

    def write(self):
        with open("mapping.json", "w") as file:
            # TODO catch write issues
            json.dump(self._map, file)

    def read(self):
        if os.path.isfile("mapping.json"):
            with open("mapping.json", "r") as file:
                # TODO catch read problem
                self._map = json.load(file)
            for key in self._map:
                self._map[int(key)] = self._map.pop(key)
            self._reverse = self.reverse(self._map)

    @staticmethod
    def reverse(omap):
        return OrderedDict(sorted([(t[1], t[0]) for t in omap.items()], key=lambda t: t[0]))

    def map(self, value):
        if value in self._reverse:
            return self._reverse[value]
        length = len(self._reverse)
        pos = bisect.bisect_left(list(self._reverse.keys()), value)
        if length == pos:
            pos = length - 1

        elif 0 == pos:
            pos = 1
        key1 = list(self._reverse.keys())[pos - 1]
        key2 = list(self._reverse.keys())[pos]
        value1 = self._reverse[key1]
        value2 = self._reverse[key2]
        pitch = float(value2 - value1) / float(key2 - key1)
        retval = pitch * (value - key1) + value1
        return int(retval)
