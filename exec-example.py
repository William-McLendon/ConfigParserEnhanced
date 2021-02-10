#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
test app for ConfigParserEnhanced (will be deleted later, probably).
"""
from __future__ import print_function  # python 2 -> 3 compatiblity

import os

from configparserenhanced import ConfigParserEnhanced



def find_config_ini(filename="config.ini", rootpath="." ):
    """
    Recursively searches for a particular file among the subdirectory structure.
    If we find it, then we return the full relative path to `pwd` to that file.

    The _first_ match will be returned.

    Args:
        filename (str): The _filename_ of the file we're searching for. Default: 'config.ini'
        rootpath (str): The _root_ path where we will begin our search from. Default: '.'

    Returns:
        String containing the path to the file if it was found. If a matching filename is not
        found then `None` is returned.

    """
    output = None
    for dirpath,dirnames,filename_list in os.walk(rootpath):
        if filename in filename_list:
            output = os.path.join(dirpath, filename)
            break
    if output is None:
        raise FileNotFoundError("Unable to find {} in {}".format(filename, os.getcwd()))  # pragma: no cover
    return output



def test_configparserEnhanced(filename="config.ini"):


    print("filename    : {}".format(filename))
    print("")

    parser = ConfigParserEnhanced(filename=filename)
    parser.debug_level = 1
    parser.exception_control_level = 4

    section = "SECTION-A+"
    section = "SECTION C+"
    #section = "OPERAND_TEST"


    #
    # Check if 'key 4' is a member of this section in the basic configdata_parsed
    # result ()
    #
    option = "key 4"
    print("Is option `{}` in `{}`?".format(option, section))

    if parser.configdata_parsed.has_option(section, option):
        value = parser.configdata_parsed.get(section, option)
        print("---> [{}][{}] == '{}'".format(section, option, value))
    else:
        print("---> NO")
    print("")

    section = "SECTION C+"
    print("Get {}".format(section))
    sec_c = parser.configdata_parsed[section]
    print(sec_c)
    print("")

    section = "SECTION-A"
    print("Get {}".format(section))
    sec_a = parser.configdata_parsed["SECTION-A"]
    print(sec_a)
    print("")

    print("Loop over items in parser.configdata_parsed")
    for section,options in parser.configdata_parsed.items():
        print("[{}]".format(section))
        max_keylen=0
        for key in options.keys():
            max_keylen=max(max_keylen, len(key))
        for option,value in options.items():
            print("{} : {}".format(option.ljust(max_keylen, ' '), value))
        print("")
    print("")

    # Print the loginfo from the last search
    parser._loginfo_print(pretty=True)

    return



def experimental(filename="config.ini"):

    #section = "SECTION C+"

    #print("\n")
    #print("Load file  : {}".format(filename))
    #print("section    : {}".format(section))

    #parser = ConfigParserEnhanced(filename=filename)
    #parser.debug_level = 1

    #data = parser.parse_configuration(section)

    #parser._loginfo_print(pretty=True)

    return



def main():
    """
    main app
    """
    fname_ini = "config_test_configparserenhanced.ini"
    fpath_ini = find_config_ini(filename=fname_ini)

    experimental(filename=fpath_ini)

    test_configparserEnhanced(filename=fpath_ini)


if __name__ == "__main__":
    main()
    print("Done.")

