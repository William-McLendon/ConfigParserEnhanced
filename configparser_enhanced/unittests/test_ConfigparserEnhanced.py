#!/usr/bin/env python
# -*- coding: utf-8; mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
"""
from __future__ import print_function
import sys
sys.dont_write_bytecode = True

import os
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pprint import pprint

import unittest
from unittest import TestCase

# Coverage will always miss one of these depending on the system
# and what is available.
try:                                               # pragma: no cover
    import unittest.mock as mock                   # pragma: no cover
except:                                            # pragma: no cover
    import mock                                    # pragma: no cover

from mock import Mock
from mock import MagicMock
from mock import patch

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import configparser

from configparser_enhanced import ConfigparserEnhanced



#===============================================================================
#
# General Utility Functions
#
#===============================================================================

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




#===============================================================================
#
# Mock Helpers
#
#===============================================================================

def mock_function_noreturn(*args):
    """
    Mock a function that does not return a value (i.e., returns NoneType)
    """
    print("\nmock> f({}) ==> NoneType".format(args))


def  mock_function_pass(*args):
    """
    Mock a function that 'passes', i.e., returns a 0.
    """
    print("\nmock> f({}) ==> 0".format(args))
    return 0


def mock_function_fail(*args):
    """
    Mock a function that 'fails', i.e., returns a 1.
    """
    print("\nmock> f({}) ==> 1".format(args))
    return 1



#===============================================================================
#
# Tests
#
#===============================================================================

class SetEnvironmentTest(TestCase):
    """
    Main test driver for the SetEnvironment class
    """
    def setUp(self):
        print("")
        self.maxDiff = None
        self._filename = find_config_ini(filename="config_test_configparserenhanced.ini")


    def test_ConfigparserEnhanced_load_configdata(self):
        """
        Tests the basic loading of a configuration .ini file using the lazy-evaluated
        `config` function.
        """
        section = None

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigparserEnhanced(self._filename, section)

        self.assertIsInstance(parser, ConfigparserEnhanced)


    def test_ConfigparserEnhanced_property_config(self):
        """
        Test the ConfigparserEnhanced property `config`
        """
        section = None

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigparserEnhanced(self._filename, section)

        configdata = parser.config

        self.assertIsInstance(configdata, configparser.ConfigParser)

        assert configdata.has_section("SECTION-A")
        assert configdata.has_section("SECTION-B")
        assert configdata.has_section("SECTION C")

        assert configdata.has_section("SECTION-A+")
        assert configdata.has_section("SECTION-B+")
        assert configdata.has_section("SECTION C+")


    def test_ConfigparserEnhanced_property_section_missing(self):
        """
        Test accessing the `section` property of ConfigparserEnhanced.
        """
        section = None

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigparserEnhanced(self._filename)

        self.assertEqual(parser.section, None)


    def test_ConfigparserEnhanced_property_section_provided(self):
        """
        Test accessing the `section` property of ConfigparserEnhanced.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file: {}".format(self._filename))
        print("Section  : {}".format(section))

        parser = ConfigparserEnhanced(filename=self._filename, section=section)

        self.assertEqual(parser.section, section)


    def test_ConfigparserEnhanced_property_section_setter(self):
        """
        Test the setter property for sections.
        """
        section = "SECTION-A"

        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser = ConfigparserEnhanced(filename=self._filename, section=section)
        self.assertEqual(parser.section, section)

        section = "SECTION C"
        print("new section: {}".format(section))
        parser.section = section
        self.assertEqual(parser.section, section)


    def test_ConfigparserEnhanced_property_section_setter_typeerror(self):
        """
        Test the setter property when it gets a non-string type in assignment.
        It should raise a TypeError.
        """
        section = 100

        print("\n")
        print("Load file  : {}".format(self._filename))
        print("section    : {}".format(section))

        parser = ConfigparserEnhanced(filename=self._filename)

        print("new section: {}".format(section))
        with self.assertRaises(TypeError):
            parser.section = section








# EOF
