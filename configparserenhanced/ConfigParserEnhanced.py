#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Todo:
    Fill in file-level docstring
    Clean up docstrings
"""
from __future__ import print_function

import configparser
import os
from pathlib import Path
import re
import sys

try:
    # @final decorator, requires Python 3.8.x
    from typing import final                                                      # pragma: no cover
except ImportError:                                                               # pragma: no cover
    pass                                                                          # pragma: no cover


from .Debuggable import Debuggable
from .ExceptionControl import ExceptionControl



# ===========================================================
#   H E L P E R   F U N C T I O N S   A N D   C L A S S E S
# ===========================================================



# ===============================
#   M A I N   C L A S S
# ===============================


class ConfigParserEnhanced(Debuggable, ExceptionControl):
    """
    Provides an enhanced version of the `configparser` module which enables some
    extended processing of the information provided in a `.ini` file.

    Args:
        filename (str): The filename of the .ini file to load.
        section  (str): The section in the .ini file to process
                        for an action list. Default: None

    Attributes:
        config  (object): The data from the .ini file as loaded by configparser.
            This will return a `configparser.ConfigParser` object.
        section (str): The section from the .ini file that is loaded.
        actions (dict): The actions that would be processed when apply() is called.

    .. configparser reference:
        https://docs.python.org/3/library/configparser.html

    Todo:
    1.  We might not want to rely on the `data` object for the parser to just be
        a free-form dictionary. It might be best to make this a class object that
        the parser can populate. Something like:

        class ConfigParserEnhancedData(Debuggable, ExceptionControl):

            def __init__(self):
                pass

            @property
            def section_data(self):
                - Provides the `use` equivalent of what happens when ConfigParser
                  loads multiple files that have the same section names. That is,
                  the union of all `key:value` pairs where the `last visited key`
                  is the entry when there are conflicts.
                - Returns:  { 'section name': {'key': 'value'}, ..., {'key': 'value'} }
                - Lazy evaluated - if a section name is requested that we have, we return it
                                   if a section name is requested we don't have, compute it.

            def handler_data(self):
                - Returns the data that the parser + handlers returns with special processing.

    2.  Create a `generic_handler` handler - which does somethign with entries that don't
        have a handler defined (i.e., what do we do with key-value pairs that have no 'rule')


    """
    def __init__(self, filename):
        self.inifilepath = filename


    # -----------------------
    #   P R O P E R T I E S
    # -----------------------


    @property
    def inifilepath(self) -> list:
        if not hasattr(self, '_inifilepath'):
            raise ValueError("ERROR: The filename has not been specified yet.")
        else:
            return self._inifilepath


    @inifilepath.setter
    def inifilepath(self, value) -> list:
        """
        inifilepath can be set to one of these things:
        1. a `str` contining a path to a .ini file.
        2. a `pathlib.Path` object pointing to a .ini file.
        3. a `list` of one or more of (1) or (2).

        entries in the list will be converted to pathlib.Path objects.
        """
        if not isinstance(value, (str,Path,list)):
            raise TypeError("ERROR: .ini filename must be a `str`, a `Path` or a `list` of either.")

        # if we have already loaded a .ini file, we should reset the data
        # structure. Delete any lazy-created properties, etc.
        if hasattr(self, '_inifilepath'):
            if hasattr(self, '_configdata'):
                delattr(self, '_configdata')
            if hasattr(self, '_loginfo'):
                delattr(self, '_loginfo')

        # Internally we represent the inifile as a `list of Path` objects.
        # Do the necessary conversions to make that so.
        if not isinstance(value, list):
            value = [ value ]

        self._inifilepath = []

        for entry in value:
            try:
                self._inifilepath.append( Path(entry) )
            except TypeError as ex:
                self.debug_message(0, "ERROR: invalid entry in `inifilepath` list.")
                raise ex

        return self._inifilepath


    @property
    def configdata(self) -> configparser.ConfigParser:
        """
        This property provides a link to the raw results from using the configparser
        class to parse a .ini file.

        This property is lazy-evaluated and will be processed the first time it is
        accessed.

        Returns:
            configparser.ConfigParser object containing the contents of the configuration
            file that is loaded from a .ini file.

        Raises:
            ValueError if the length of `self.inifilepath` is zero.
            IOError if any of the files in `self.inifilepath` don't
                exist or are not files.

        .. configparser reference:
            https://docs.python.org/3/library/configparser.html
        """
        if not hasattr(self, '_configdata'):
            self._configdata = configparser.ConfigParser(allow_no_value=True)

            # prevent ConfigParser from lowercasing the keys
            self._configdata.optionxform = str

            # configparser.ConfigParser.read() will not fail if it doesn't read the
            # .ini file(s) in the list, it'll just happily continue on and return
            # whatever it does get... or an empty configuration if no files were found.
            # We want to fail if we provide a bad file name so we need to check here.
            if len(self.inifilepath) == 0:
                raise ValueError("ERROR: No .ini filename(s) were provided.")

            for inifilepath_i in self.inifilepath:

                # Sanity type check here -- we'd throw on the .exists() and .is_file()
                # methods below if the entry isn't a Path object, but the erorr might
                # be cryptic. This will throw a more explicit error.
                # This should never happen if the users set things up through the
                # property interface.
                if isinstance(inifilepath_i, Path) is not True:
                    raise TypeError("INTERNAL ERROR: .ini file paths should be Path objects!")

                if (inifilepath_i.exists() and inifilepath_i.is_file()) is not True:
                    msg = "\n" + \
                          "+" + "="*78 + "+\n" + \
                          "|   ERROR: Unable to load configuration .ini file\n" + \
                          "|   - Requested file: `{}`\n".format(inifilepath_i) + \
                          "|   - CWD: `{}`\n".format(os.getcwd()) + \
                          "+" + "="*78 + "+\n"
                    raise IOError(msg)

            self._configdata.read(self.inifilepath, encoding='utf-8')

        return self._configdata


    @property
    def configdata_parsed(self):
        if not hasattr(self, '_configdata_parsed'):
            self._configdata_parsed = self.ConfigParserEnhancedDataSection(owner=self)
        return self._configdata_parsed


    # --------------------
    #   P A R S E R
    # --------------------


    def parser_data_init(self):
        """
        Initializer for the data object that gets sent to parser initially.

        Returns:
            dict containing the 'base' configuration that is empty and ready for
            for the parser handlers to populate.
        """
        output = {}
        return output


    @property
    def regex_op_splitter(self) -> str:
        """
        This parameter stores the regex used to match operation lines in the parser.

        We provide this as a property in case a subclass needs to override it.

        Warning: There be dragons here!
        This is only something you should do if you _really_ understand the
        core parser engine. If this is changed significantly, you will likely also
        need to override the following methods too:
        - `get_op1_from_regex_match()`
        - `get_op2_from_regex_match()`
        - `regex_op_matcher()`
        """
        if not hasattr(self, '_regex_op_splitter'):
            # regex op splitter to extract op1 and op2, this is pretty complicated so here's the
            # deets:
            # - The goal is to capture op1 and op2 into groups from a regex match.
            # - op1 will always be captured by group1. We only allow this to be letters,
            #   numbers, dashes, or underscores.
            #   - No spaces are ever allowed for op1 because this will get mapped to a handler method
            #     name of the form `_handler_{op1}()`
            # - op2 is captured by group 2 or 3
            #   - group2 if op2 is single-quoted (i.e., 'op 2' or 'op2' or 'op-2')
            #   - group3 if op2 is not quoted.
            # - op2 is just a string that gets passed down to the handler function so we will
            #   let this include spaces, but if you do include spaces it _must_ be single quoted
            #   otherwise we treat everything after the space as 'extra' stuff.
            #   - This 'extra' stuff is discarded by ConfigParserEnhanced so that it can be used
            #     to differentiate multiple commands in a section from one another that might otherwise
            #     map to the same key. Note, in a normal `configparser` `.ini` file each section is
            #     a list of key:value pairs. The keys must be unique but that can be problematic
            #     if we're implementing a simple parsed language on top of it.
            #     For example, if we're setting envvars and wanted multiple entries for PATH:
            #         envvar-prepend PATH: /something/to/prepend/to/path
            #         envvar-prepend PATH: /another/path/to/prepend
            #     Here, the keys would be invalid for configparser because they're identical.
            #     By allowing 'extra' entries after op2 we can allow a user to make each one unique.
            #     So our example above could be changed to:
            #         envvar-prepend PATH A: /something/to/prepend/to/path
            #         envvar-prepend PATH B: /another/path/to/prepend
            #     In both cases, op1 = 'envvar-prepend' and op2 = 'PATH' but the addition of the
            #     'A' and 'B' will differentiate these keys from the configparser's perspective.
            #  - Note: This comment information should find its way into the docs sometime.
            # regex_string = r"^([\w\d\-_]+)( '([\w\d\-_ ]+)'| ([\w\d\-_]+)(?: .*)*)?"   # (old and busted)
            regex_string = r"^([\w\d\-_]+) ?('([\w\d\-_ ]+)'|([\w\d\-_]+)(?: .*)*)?"
            #                  ^^^^^^^^^^    ^^^^^^^^^^^^^    ^^^^^^^^^^
            #                      \              \                \-- op3 : group 3
            #                       \              \--- op2 : group 2
            #                        \--- op1 : group 1
            self._regex_op_splitter = re.compile(regex_string)

        return self._regex_op_splitter


    def regex_op_matcher(self, text):
        """
        Executes the regex match operation against `regex_op_splitter`.
        This method adds the ability to add in extra checks for sanity
        that can be inserted into the parser. If the results of the match
        fails the extra scrutiny, then return None.

        Args:
            text (str): The string in which we're searching.

        Returns:
            Regex match if one exists and we pass any sanity checks that are
            added to this method.
        """
        m = self.regex_op_splitter.match(text)

        # Sanity checks: Change match to None if we fail
        if m != None:
            if m.groups()[0] != text.split()[0]:
                m = None
        return m


    def get_op1_from_regex_match(self, regex_match) -> str:
        """
        Extracts op1 from the regular expression match groups.

        Args:
            regex_match (object): A `re.match()` object.

        Returns:
            String containing the op1 parameter, formatted properly for use
            as part of a handler name.

        Note:
            op1 must be a string that could be used in a method name since this gets
            used by the parser to call a function of the pattern `_handler_{op1}`
        """
        output = str(regex_match.groups()[0])
        output = output.strip()
        output = output.replace('-','_')
        return output


    def get_op2_from_regex_match(self, regex_match) -> str:
        """
        Extracts op2 from the regular expression match groups.

        Args:
            regex_match (object): A `re.match()` object.

        Returns:
            String containing the op2 parameter or None if one doesn't exist.
        """
        output = None

        # op2 matches group 2 or 3 depending on whether or not there were quotes.
        # (there are 4 groups)
        if regex_match.groups()[2]:
            output = str(regex_match.groups()[2]).strip()
        elif regex_match.groups()[3]:
            output = str(regex_match.groups()[3]).strip()

        return output



    def parse_configuration(self, section) -> dict:
        """
        Top level parser entry point.

        Args:
            section (str): The section name that will be parsed and retrieved.

        Returns:
            dictionary containing the results of the section parsing. The contents
            of this depends on the handlers available to the current class.
        """
        if not isinstance(section, str):
            raise TypeError("`section` must be a string type.")

        if section == "":
            raise ValueError("`section` cannot be empty.")

        # clear out loginfo from any previous run(s)
        if hasattr(self, '_loginfo'):
            delattr(self, '_loginfo')

        data = self._parse_configuration_r(section)
        return data


    def _parse_configuration_r(self, section_name, data=None, processed_sections=None, section_name_root=None) -> dict:
        """
        Recursive driver of the parser.
        """
        current_section = None

        if section_name == None:
            raise TypeError("ERROR: a section name must not be None.")

        self.debug_message(1, "Enter section: `{}`".format(section_name))                      # Console Logging
        self._loginfo_add({'type': 'section-entry', 'name': section_name})                          # Logging

        if section_name_root is None:
            section_name_root = section_name
            self.configdata_parsed.sections_checked.add(section_name)

        try:
            current_section = self.configdata[section_name]
        except KeyError:
            message = "ERROR: No section named `{}` was found in the configuration file.".format(section_name)
            raise KeyError(message)

        # Verify that we actually got a section returned. If not, raise a KeyError.
        # (wcm) This might not be reachable given the KeyError check.
        #       It's probably not a bad idea to hang onto it for now, but maybe mark with
        #       a #pragma no cover?
        if current_section is None:
            raise Exception("ERROR: Unable to load section `{}` for unknown reason.".format(section_name))

        if data is None:
            data = self.parser_data_init()
            assert isinstance(data, dict)

        if processed_sections == None:
            processed_sections = {}
        processed_sections[section_name] = True

        for sec_k,sec_v in current_section.items():
            sec_k = str(sec_k).strip()
            sec_v = str(sec_v).strip()
            sec_v = sec_v.strip('"')
            # Todo: check configparser's configuration regarding settings, rules, etc.
            #       for expansion rules and quotation handling.

            self.debug_message(2, "- Entry: `{}` : `{}`".format(sec_k,sec_v))                       # Console
            self._loginfo_add({'type': 'section-key-value', 'key': sec_k, 'value': sec_v})          # Logging

            # process the key via Regex to extract op1 and op2
            regex_op_splitter_m = self.regex_op_matcher(sec_k)

            # Skip entry if we didn't get a match
            if regex_op_splitter_m is None:
                continue

            self.debug_message(5, "regex-groups {}".format(regex_op_splitter_m.groups()))
            op1 = self.get_op1_from_regex_match(regex_op_splitter_m)
            op2 = self.get_op2_from_regex_match(regex_op_splitter_m)

            self._loginfo_add({"type": 'section-operands', 'op1': op1, 'op2': op2})                 # Logging
            self.debug_message(2, "- op1: {}".format(op1))                                          # Console
            self.debug_message(2, "- op2: {}".format(op2))                                          # Console

            # Call the op handler if one exists for this op.
            handler_name = "_handler_{}".format(op1)
            ophandler_f = getattr(self, handler_name, None)
            if ophandler_f is not None:
                rval = ophandler_f(section_name_root,
                                   section_name,
                                   op1, op2,
                                   data,
                                   processed_sections,
                                   entry=(sec_k,sec_v))
                if rval != 0:
                    self.exception_control_event("WARNING", RuntimeError,
                                                 "Handler `{}` returned {} but we expected 0".format(handler_name, rval))
            else:
                # Call the generic handler to update the 'generic' view
                # of the (all key:value pairs that don't map to any other handlers)
                rval = self._handler_generic(section_name_root,
                                             section_name,
                                             op1, op2,
                                             data,
                                             processed_sections,
                                             entry=(sec_k,sec_v))



        # Remove the section from the `processed_sections` field when we exit.
        del processed_sections[section_name]

        self._loginfo_add({'type': 'section-exit', 'name': section_name})                           # Logging
        self.debug_message(1, "Exit section: `{}`".format(section_name))                       # Console

        return data


    # --------------------
    #   H A N D L E R S
    # --------------------

    def _handler_generic(self, section_root, section_name, op1, op2, data, processed_sections=None, entry=None) -> int:
        """
        """
        self._loginfo_add({'type': 'handler-entry', 'name': '_handler_generic'})

        self.configdata_parsed.set(section_root, entry[0], entry[1])

        self._loginfo_add({'type': 'handler-exit',  'name': '_handler_generic'})


    def _handler_use(self, section_root, section_name, op1, op2, data, processed_sections=None, entry=None) -> int:
        """
        This is a handler that will get executed when we detect a `use` operation in
        our parser.

        Args:
            section_name (str): The section name of the current _section_ we're processing.
            op1 (str): The first operation parameter
                       (i.e., `use` if the full key is `use section_name`)
            op2 (str): The second operation parameter
                       (i.e., `section_name` if the full key is `use section_name`)

        Returns:
            integer value: 0 if successful, 1 if there was a problem.

        Raises:
            Nothing

        Todo:
            Once we can use Python 3.8 in our environments, we can use the @final decorator
            to mark this as something that should not be overridden. We also have to
            import it: `from typing import final`
            See: https://stackoverflow.com/questions/321024/making-functions-non-override-able
        """
        self._loginfo_add({'type': 'handler-entry', 'name': '_handler_use'})                        # Logging
        self.debug_message(1, "Enter handler: _handler_{}".format(op1))                                        # Console

        if op2 not in processed_sections.keys():
            self._parse_configuration_r(op2, data, processed_sections, section_root)
        else:
            self._loginfo_add({'type': 'cycle-detected', 'sec-src': section_name, 'sec-dst': op1})  # Logging
            message  = "Detected a cycle in `use` dependencies in .ini file.\n"
            message += "- cannot load [{}] from [{}].".format(op1, section_name)
            self.exception_control_event("WARNING", ValueError, message)

        self._loginfo_add({'type': 'handler-exit', 'name': '_handler_use'})                         # Logging
        self.debug_message(1, "Exit handler: _handler_{}".format(op1))                                        # Console
        return 0


    # --------------------
    #   H E L P E R S
    # --------------------


    def _loginfo_add(self, entry) -> None:
        """
        If in debug mode, we can use this to log operations.
        Appends to _loginfo

        Args:
            entry (dict): A dictionary containing log information that we're appending.
                          At minimum it should have: `type: typestring`.

        Returns:
            Nothing


        Todo:
            Once we can use Python 3.8 in our environments, we can use the @final decorator
            to mark this as something that should not be overridden. We also have to
            import it: `from typing import final`
            See: https://stackoverflow.com/questions/321024/making-functions-non-override-able
        """
        if not hasattr(self, '_loginfo'):
            self._loginfo = []

        if self.debug_level > 0:
            if not isinstance(entry, dict):
                raise TypeError("entry should be a dictionary type.")
            if 'type' not in entry.keys():
                raise ValueError("entry must have a `type: typestr` entry`")
            self._loginfo.append(entry)
        else:
            pass
        return


    def _loginfo_print(self, pretty=True) -> None:
        """
        This is a helper to pretty-print the loginfo object

        Todo:
            Once we can use Python 3.8 in our environments, we can use the @final decorator
            to mark this as something that should not be overridden. We also have to
            import it: `from typing import final`
            See: https://stackoverflow.com/questions/321024/making-functions-non-override-able
        """
        if pretty:
            self.debug_message(1, "Loginfo:")
            for entry in self._loginfo:
                self.debug_message(1, "Entry Type: `{}`".format(entry['type']))
                self.debug_message(1, "--------------" + "-"*len(entry['type']))
                max_key_len = max(map(len, entry))
                for k,v in entry.items():
                    key_len_diff = max_key_len - len(k)
                    self.debug_message(1, "--- `{}`{}: `{}`".format(k,' '*(key_len_diff),v))
                self.debug_message(1, "")
        else:
            print(self._loginfo)

        return


    # ===========================================================
    #  I N N E R   C L A S S E S
    # ===========================================================


    class ConfigParserEnhancedDataSection(Debuggable, ExceptionControl):
        """
        """
        def __init__(self, owner=None):
            self.owner = owner
            self.set_owner_options()

        @property
        def owner(self):
            if not hasattr(self, '_owner'):
                self._owner = None
            return self._owner

        @owner.setter
        def owner(self, value):
            if not isinstance(value, (ConfigParserEnhanced)):
                raise TypeError("Owner class must be a ConfigParserEnhanced or derivitive.")
            self._owner = value
            return self._owner

        @property
        def data(self) -> dict:
            """
            """
            if not hasattr(self, '_data'):
                self._data = {}
            return self._data

        @data.setter
        def data(self, value) -> dict:
            """
            """
            if not isinstance(value, dict):
                raise TypeError("data must be a `dict` type.")
            self._data = value
            return self._data

        @property
        def sections_checked(self):
            """
            Implements a set that contains section names that
            have already been parsed via lazy evaluation.
            """
            if not hasattr(self, '_sections_checked'):
                self._sections_checked = set()
            return self._sections_checked

        def set_owner_options(self):
            """
            Get options from the owner class, if we have an owner class.
            """
            if self.owner != None:
                self.exception_control_level = self.owner.exception_control_level
                self.debug_level = self.owner.debug_level

        def items(self, section=None):
            section_list = self.data.keys()
            if self.owner != None:
                section_list = self.owner.configdata.keys()

            output = None
            if section is None:
                for seci in section_list:
                    self.parse_owner_section(seci)
                output = self.data.items()
            else:
                output = self.options(section).items()
            return output

        def keys(self):
            return self.data.keys()

        def __iter__(self):
            for k in self.keys():
                yield k

        def __getitem__(self, key):
            if not self.has_section(key):
                raise KeyError(key)
            return self.data[key]

        def __len__(self):
            return len(self.data)

        def sections(self):
            return self.data.keys()

        def has_section(self, section):
            if self.owner != None and section not in self.sections_checked:
                try:
                    self.parse_owner_section(section)
                except KeyError:
                    pass
            return section in self.data.keys()

        def options(self, section):
            if not self.has_section(section):
                raise KeyError("Section {} does not exist.".format(section))
            return self.data[section]

        def has_option(self, section, option):
            """
            """
            if self.owner != None and section not in self.sections_checked:
                self.parse_owner_section(section)
            return option in self.data[section].keys()

        def get(self, section, option):
            """
            Get a section/option pair if it exists. If we have not
            parsed the section yet, we should run the parser to
            fully get the key data.
            """
            if self.owner != None and section not in self.sections_checked:
                self.parse_owner_section(section)

            if self.has_section(section):
                if self.has_option(section, option):
                    return self.data[section][option]
                else:
                    raise KeyError("Missing section:option -> '{}': '{}'".format(section,option))

            # This is not reachable with a bad section name
            # because the call to parse_owner_section(section) will
            # raise a KeyError if the section name is bad, and
            # the owner setter doesn't allow a NoneType to be assigned.
            # But if someone assigned None to self._owner directly
            # which Python won't prevent, we could get here... so
            # this check helps prevent one from doing bad things.
            raise KeyError("Missing section {}.".format(section))

        def add_section(self, section):
            """
            Directly add a new section, if it does not exist.
            """
            if not self.has_section(section):
                self.data[section] = {}

        def set(self, section, option, value):
            """
            Directly set an option. If the section is missing we create an empty one.
            """
            if not self.has_section(section):
                self.add_section(section)
            if option not in self.data[section].keys():
                self.data[section][option] = value
            return self.data[section][option]

        def parse_owner_section(self, section):
            """
            Parse the section from the owner class
            """
            if self.owner != None:
                self.set_owner_options()
                self.sections_checked.add(section)
                self.owner.parse_configuration(section)
