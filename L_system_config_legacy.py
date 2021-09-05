from yaml import safe_load
import re
from random import gauss, triangular
from time import time_ns, time
from collections import OrderedDict

Directory = 'Patterns'
str_rules, rules = {}, {}
CHAR_SEPARATOR = ord('♂')
SIGMA_KOEF = 0.5


def get_turtles(path) -> list[list[int, int, int, int, str]]:
    global rules
    global str_rules
    with open(Directory + '\\' + path, 'r') as turt_f:
        tmp = safe_load(turt_f)
        turtles = tmp['Turtles']
        str_rules = {}
        for value in tmp['Rules'].values():
            if isinstance(value, str):
                str_rules[value] = parse_rule(value)
            else:
                for i in value:
                    str_rules[i] = parse_rule(i)
        add_rules(rules, tmp['Rules'])
        return turtles


key_re_list = []


def add_rules(source: dict, new_rules):
    for key, value in new_rules.items():
        key_re = None  # шаблон регулярного выражения для выделения ключа
        if '(' in key and ')' in key:  # ключ с параметрами
            key_re = key.replace("(", r"\(")
            key_re = key_re.replace(")", r"\)")
            key_re = key_re.replace("+", r"\+")
            key_re = key_re.replace("-", r"\-")
            key_re = re.sub(r"([a-z]+)([, ]*)", lambda m: r"([-+]?\b\d+(?:\.\d+)?\b)" + m.group(2), key_re)
            key_re_list.append(key_re)
        source[key] = (value, key_re)


def format_strings(*params, rule: str):
    transformed_str = rule
    keys_tuples = str_rules[rule][0].copy()
    ranges_tuples = str_rules[rule][1]
    for i in ranges_tuples:
        sigma = (abs(float(i[0])) + abs(float(i[1]))) / 2 * SIGMA_KOEF
        random_value = triangular(float(i[0]), float(i[1]), gauss((float(i[0]) + float(i[1])) / 2, sigma))
        transformed_str = transformed_str.replace("{" + i[0] + ".." + i[1] + "}", str(random_value), 1)
    for i in params:
        if not keys_tuples:
            break
        transformed_str = transformed_str.replace(keys_tuples.pop(), str(i))
    t = time()
    t_ns = time_ns()
    keys_tuples = re.finditer(r"[( ](-?\d+[.]?\d*[-+/*][^( ]+)[),]", transformed_str)
    for i in keys_tuples:
        no_double_operation = i.group(1)
        double_operations = re.finditer(r"[-+/*](-\d+[.]?\d*)", i.group(1))
        for j in double_operations:
            no_double_operation = no_double_operation.replace(j.group(1), f"({j.group(1)})", 1)
        transformed_str = transformed_str.replace(i.group(1), str(eval(no_double_operation)))
    transformed_str = transformed_str.replace('(', chr(CHAR_SEPARATOR))
    transformed_str = transformed_str.replace(')', chr(CHAR_SEPARATOR + 1)).lower()
    return transformed_str


def parse_rule(rule: str):
    params = reversed(re.findall(r'[a-z]', rule))
    params = list(OrderedDict.fromkeys(params))
    ranges = re.findall(r'{(-?\d+[.]?\d*)[.]{2}(-?\d+[.]?\d*)}', rule)
    ranges = tuple((i[0], i[1]) for i in ranges)
    return [params, ranges]
