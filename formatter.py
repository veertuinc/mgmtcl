from collections import defaultdict, OrderedDict
from numbers import Number

from tabulate import tabulate


class Formatter(object):

    def format_list_of_dicts(self, list_of_dicts):
        if isinstance(list_of_dicts, list) and len(list_of_dicts) > 0:
            headers = dict(zip(list_of_dicts[0].keys(), list_of_dicts[0].keys()))
            list_keys = self._has_list(list_of_dicts)
            if list_keys:
                return self.format_list_of_dicts_with_lists(list_of_dicts, list_keys)
            return tabulate(list_of_dicts, headers=headers, tablefmt='grid')

    def format_list_of_dicts_with_lists(self, list_of_dicts, list_keys):
        output = ''
        clean_list_of_dicts = []
        dict_of_sub_lists = defaultdict(list)
        for idx, d in enumerate(list_of_dicts):
            for key in list_keys:
                list_value = d.pop(key)
                new_list = []
                for value in list_value:
                    new_dict = OrderedDict()
                    new_dict['parent_index'] = idx
                    new_dict.update(value)
                    new_list.append(new_dict)
                dict_of_sub_lists[key] += new_list
            clean_list_of_dicts.append(d)
        output += self.format_list_of_dicts(clean_list_of_dicts)
        for k, v in dict_of_sub_lists.iteritems():
            if v:
                output += "\n\n" + k + "\n\n"
                output += self.format_list_of_dicts(v)

        return output

    def _has_list(self, dict_collection):
        list_keys = []
        for k, val in dict_collection[0].iteritems():
            if isinstance(val, list):
                list_keys.append(k)
        return list_keys

    def format_dict(self, dict_to_output):
        output = ''
        data = []
        additionals = {}
        for k, v in dict_to_output.iteritems():
            if isinstance(v, (basestring, Number)):
                data.append((k, v))
            elif isinstance(v, (dict, OrderedDict)):
                additionals[k] = v
            elif isinstance(v, list):
                if len(v) > 0 and isinstance(v[0], (dict, OrderedDict)):
                    additionals[k] = self.format_list_of_dicts(v)
                else:
                    data.append((k, ', '.join(v)))
        output += tabulate(data, tablefmt='grid')
        output += '\n\n'
        for k, v in additionals.iteritems():
            output += k + "\n\n"
            if isinstance(v, dict):
                output += self.format_dict(v)
            else:
                output += v
            output += '\n\n'
        return output
