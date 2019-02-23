import re
import os
import tkinter as tk
from tkinter import filedialog


FIREWALL_RULES_CSV = 'firewall_rules.csv'


def parseblock(block, rules):
    re_default = re.findall('default-action (.+)\n',block)
    re_name = re.findall('name (.+) {', block)
    re_rules = re.findall(' rule (.+) {', block)
    re_actions = re.findall(' action (.+)\n', block)
    re_descriptions = re.findall(' description (.+)\n', block)
    # do: description offset. This is used because there is not always a description of the ruleset.
    # In case there isn't, the do = 0!
    do = re_descriptions.__len__() - re_rules.__len__()

    # write the default rule
    out_rule = re_name[0]+'-default-'+re_default[0][0].upper()
    rules[out_rule] = out_rule+','+out_rule
    # build the rule list
    for i in range(0, re_rules.__len__()):
        out_rule = re_name[0]+'-'+re_rules[i]+'-'+re_actions[i][0].upper()
        out_description = re_name[0]+'-'+re_descriptions[i+do].replace('"', '')
        rules[out_rule] = out_rule + ',' + out_description


def read_config_boot(file_path, rules):
    # read file into buffer
    block = ''
    blockmatching = False
    i = 0

    try:
        f = open(file_path)
    except FileNotFoundError:
        print('Could not open file!')
        exit()
    for line in f:
        i += 1
        if blockmatching:
            if line == '}\n':
                parseblock(block, rules)
                block = ''
                blockmatching = False   # there is no new block yet ...
            else:
                block += line

        match = re.findall(' name (.+) {', line)
        if match.__len__() > 0:
            if blockmatching:
                # this is the end of the block
                parseblock(block, rules)
            # this is a firewall rule name - start storing the text block for parsing
            block = line
            blockmatching = True
    f.close()
    return True


def getfilename():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path


def readrules(directory, rules):
    # read existing rules, to be updated in the next step
    # this allows old rules (no longer relevant in the current configuration) to still be
    # available for matching in Splunk)
    try:
        f = open(directory + '/' + FIREWALL_RULES_CSV)
    except FileNotFoundError:
        # there are no existing rules yet - nothing to do here
        elements = ''
    else:
        first = True
        for line in f:
            if not first:
                elements = line.split(',')
                rules[elements[0]] = line.strip()
            first = False


def writerules(directory, rules):
    # now write all the rules to a CSV file
    outfile = open(directory + '/' + FIREWALL_RULES_CSV, 'w')
    outfile.write('Rule,Description\n')
    for key in rules:
        outfile.write((rules[key]+'\n'))
    outfile.close()


def main():
    rules = dict()
    file_path = getfilename()
    if file_path == '':
        exit()

    directory = os.path.dirname(file_path)

    # read existing rules, so the current items can be added
    # (to ensure old events still have recognised firewall rule descriptions)
    readrules(directory, rules)

    # now read current edgerouter config to update existing rules
    if read_config_boot(file_path, rules,):
        writerules(directory, rules)


if __name__ == "__main__":
    main()