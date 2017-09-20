#!/usr/bin/python

import subprocess, re, json

def sub_items(lines):
    return

def dict_from_list(list, obj, items):
    new_dict = {obj: dict(items)}
    for i, l in enumerate(list[::-1]):
        new_dict = { l: new_dict }
    return new_dict

def parse_generic_config(profile):
    generic_profiles = ['analytics', 'apm', 'auth', 'cm', 'gtm', 'net', 'security', 'sys']
    modules = []
    keys = []
    lines = profile.split('\n')
    for line in lines:
        single_line = line.split(' ')
        if (single_line[0] in generic_profiles):
            obj_name = single_line[len(single_line) - 2]
            for word in single_line:
                if (word != obj_name) and (word != '{'):
                    modules.append(word)
        else:
            single_line = line.strip().split(' ')
            try:
                keys.append([single_line[0], single_line[1]])
            except IndexError:
                pass
    config_object = dict_from_list(modules, obj_name, keys)
    return config_object

def parse_ltm(profile):
    modules = []
    keys = []
    lines = profile.split('\n')
    for line in lines:
        single_line = line.split(' ')
        if (single_line[0] == 'ltm') and (single_line[1] == 'rule'):
            obj_name = single_line[len(single_line) - 2]
            for word in single_line:
                if (word != obj_name) and (word != '{'):
                    modules.append(word)
                print modules
            raise ValueError
        elif (single_line[0] == 'ltm'):
            obj_name = single_line[len(single_line) - 2]
            for word in single_line:
                if (word != obj_name) and (word != '{'):
                    modules.append(word)
        else:
            single_line = line.strip().split(' ')
            try:
                keys.append([single_line[0], single_line[1]])
            except IndexError:
                pass
    config_object = dict_from_list(modules, obj_name, keys)
    return config_object

def read_config_items(full_config):
    generic_profiles = ['analytics', 'apm', 'auth', 'cm', 'gtm', 'net', 'security', 'sys']
    config_items = []
    this_config = []

    # splits items up but iRules will choke on it since they usually have braces
    # at the beginning of the line which gets put exactly as is into the config
    split_items = re.compile('^\}', flags=re.MULTILINE).split(full_config)
    for item in split_items:
        lines = item.split('\n')
        for line in lines:
            words = line.split(' ')
            if (words[0] in generic_profiles):
                conf = parse_generic_config(item)
                config_items.append(conf)
            elif (words[0] == 'ltm'):
                try:
                    conf = parse_ltm(item)
                    config_items.append(conf)
                except:
                    pass
            else:
                pass
    final_config = {}
    for item in config_items:
        for k in item:
            try:
                 final_config[k]
            except KeyError:
                final_config[k] = item[k]
                #print final_config
            else:
                for l in item[k]:
                    try:
                        final_config[k][l]
                    except KeyError:
                        final_config[k][l] = item[k][l]
                    else:
                        for m in item[k][l]:
                            try:
                                final_config[k][l][m]
                            except KeyError:
                                final_config[k][l][m] = item[k][l][m]
                            else:
                                for n in item[k][l][m]:
                                    try:
                                        final_config[k][l][m]
                                    except KeyError:
                                        final_config[k][l][m][n] = item[k][l][m][n]

    return final_config

# output is string
output = subprocess.check_output(['./tmsh', '-a', '-e', '-q', '-r', '12.1.2', 'list', 'all-properties'])

split_config = read_config_items(output)

#print json.dumps(split_config, indent=4, separators=(',', ': '))
