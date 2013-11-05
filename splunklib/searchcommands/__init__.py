# coding=utf-8
# Copyright 2011-2012 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

""" Splunk search command library

    #Design Notes

    1. Command lines are constrained to this grammar (expressed informally):

       command-line = `*<command>* [*<option>***=**<value>**]… [*<field>*]…`
       command = `\w+`
       option = `\w+`
       value = `([^\s"]+|"(?:[^"]+|""|\\")*")`
       field = `"?[.-\w]"?`

       Note that this grammar does not indicate that *<field>* values may be
       comma-separated. This is because Splunk strips commas from the command
       line. You never see them.

    2. Commands support dynamic probing for settings.
       Splunk probes for settings when `supports_getinfo=true`.

    3. Commands do not support static probing for settings.
       This class expects that commands are statically configured as follows:

       ```
       [*<command>*]
       filename = *<command>*.py
       supports_getinfo = true
       ```

       No other static configuration is required or expected and may interfere
       with command execution.

    4. Commands do not support parsed arguments on the command line.
       Splunk parses arguments when `supports_rawargs=false`. This class sets
       `supports_rawargs=true` unconditionally.

       **Rationale:*
       Splunk parses arguments by stripping quotes, nothing more. This
       may be useful in some cases, but doesn't work well with our chosen
       grammar.

    5. Commands consume input headers.
       An input header is provided by Splunk when `enableheader=true`. This
       class sets this value unconditionally.

    6. Commands produce an output messages header.
       Splunk expects a command to produce an output messages header when
       `outputheader=true`. This class sets this value unconditionally.

    7. Commands support multi-value fields.
       Multi-value fields are provided and consumed by Splunk when
       `supports_multivalue=true`. This class sets this value unconditionally.

    8. Commands represent all fields on the output stream as multi-value
       fields.
       Splunk represents multi-value fields with a pair of fields:

       + `<field-name>`
         Contains the text from which the multi-value field was derived.

       + `__mv_<field-name>`
         Contains an encoded list. Values in the list are wrapped in dollar
         signs ('$') and separated by semi-colons (';). Dollar signs ('$')
         within a value are represented by a pair of dollar signs ('$$').
         Empty lists are represented by the empty string. Single-value lists
         are represented by the single value.

       On input this class processes and hides all **__mv_** fields. On output
       this class produces backing **__mv_** fields for all fields, thereby
       enabling a command to reduce its memory footprint by using streaming
       I/O. This is done at the cost of one extra byte of data per field per
       record on the output stream and extra processing time by the next
       processor in the pipeline.

    9. A ReportingCommand must implement both its map (a.k.a, streaming preop)
       and reduce (a.k.a., reporting) operations. Map/reduce command lines are
       distinguished as exemplified below:

       **Command:**
       ```
       ...| sum total=total_date_hour date_hour
       ```

       **Reduce command line:**
       ```
       sum __GETINFO__ total=total_date_hour date_hour
       sum __EXECUTE__ total=total_date_hour date_hour
       ```

       **Map command line:**
       ```
       sum __GETINFO__ __map__ total=total_date_hour date_hour
       sum __EXECUTE__ __map__ total=total_date_hour date_hour
       ```

       The `__map__`` argument is introduced by the `ReportingCommand._execute`
       method. ReportingCommand authors cannot influence the contents of the
       command line in this release.

    #References

    1. [Commands.conf.spec](http://docs.splunk.com/Documentation/Splunk/5.0.5/Admin/Commandsconf)
    2. [Search command style guide](http://docs.splunk.com/Documentation/Splunk/6.0/Search/Searchcommandstyleguide)

    #Implementation notes

    1. `# BFR` comments denote issues that should either be resolved before
       formal review or turned into TODO comments.

    2. `# TODO` comments denote issues that should be eliminated or reported as
       issues to be addressed in a later draft following formal review.

 """

from __future__ import absolute_import

from . import logging
from . decorators import *
from . validators import *

from . generating_command import GeneratingCommand
from . reporting_command import ReportingCommand
from . streaming_command import StreamingCommand
