r"""

TODO:: Include module imports in each doctest.
TODO:: Reword
Loader for CSV files (https://datatracker.ietf.org/doc/html/rfc4180)
which consist of a single header line containing the column (field)
names and rows with comma separated values.

In pandas the names of the columns are referred to as `column_names`,
whereas in a frictionless datapackage the column names are called `fields`.
The datapackage contains information about, i.e.,
the type of data, a title and a set of descriptors.

The CSV object has the following properties:

TODO:: Add examples for the following functions
    * a DataFrame
    * the column names
    * the header contents
    * the number of header lines

Loaders for non standard CSV files can be called:

TODO:: Add example

"""

# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2025 Albert Engstfeld
#        Copyright (C) 2022 Johannes Hermann
#        Copyright (C) 2022 Julian Rüth
#
#  unitpackage is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  unitpackage is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with unitpackage. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************


import logging

logger = logging.getLogger("loader")


class BaseLoader:
    r"""
    Loads a CSV, where the first line must contain the column (field) names
    and the following lines comma separated values.

    EXAMPLES::

        >>> from io import StringIO
        >>> file = StringIO(r'''a,b
        ... 0,0
        ... 1,1''')
        >>> csv = BaseLoader(file)
        >>> csv.df
           a  b
        0  0  0
        1  1  1

    A list of column names::

        >>> csv.column_header_names
        ['a', 'b']

    TODO: Link to device list in the documentation.
    More specific loaders can be selected.::

        >>> from io import StringIO
        >>> file = StringIO('''EC-Lab ASCII FILE
        ... Nb header lines : 6
        ...
        ... Device metadata : some metadata
        ...
        ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
        ... 2\t0\t0.1\t0\t0
        ... 2\t1\t1.4\t5\t1
        ... ''')
        >>> from unitpackage.loaders.baseloader import BaseLoader
        >>> csv = BaseLoader.create('eclab')(file)
        >>> csv.df
           mode  time/s  Ewe/V  <I>/mA  control/V
        0     2       0    0.1       0          0
        1     2       1    1.4       5          1

    """

    def __init__(
        self,
        file,
        header_lines=None,
        column_header_lines=None,
        decimal=None,
        delimiters=None,
    ):  # pylint: disable=dangerous-default-value
        self._file = file.read()
        self._header_lines = header_lines
        self._column_header_lines = column_header_lines
        self._decimal = decimal
        self.delimiters = delimiters or ["\t", ";", ","]

    @property
    def file(self):
        r"""
        A file like object of the loaded file.

        EXAMPLES::
            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> type(csv.file)
            <class '_io.StringIO'>

        """
        from io import StringIO

        return StringIO(self._file)

    @classmethod
    def _loaders(cls):
        r"""
        A dictionary of known loaders.
        """
        return {"eclab": __import__('unitpackage.loaders.eclabloader').loaders.eclabloader.ECLabLoader,
                "gamry": __import__('unitpackage.loaders.gamryloader').loaders.gamryloader.GamryLoader}

    @classmethod
    def known_loaders(cls):
        r"""
        A list of known loaders. Refer to the documentation for details
        on supported file types for the individual Loaders.

        EXAMPLES::

            >>> BaseLoader.known_loaders()
            ['eclab', 'gamry']

        """
        return list(cls._loaders().keys())

    @classmethod
    def create(cls, device=None):
        r"""
        Calls a specific `loader` based on a given device.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0.1\t0\t0
            ... 2\t1\t1.4\t5\t1
            ... ''')
            >>> csv = BaseLoader.create('eclab')(file)
            >>> csv.df
               mode  time/s  Ewe/V  <I>/mA  control/V
            0     2       0    0.1       0          0
            1     2       1    1.4       5          1

        An unknown device loader provides a list with supported Loaders::

            >>> BaseLoader.create('unknown_device') # doctest: +NORMALIZE_WHITESPACE
            Traceback (most recent call last):
            ...
            KeyError: "Device wth name 'unknown_device' is not in the list of supported Loaders (['eclab', 'gamry'])'."

        """
        if device in BaseLoader.known_loaders():

            return cls._loaders()[device]

        raise KeyError(f"Device wth name '{device}' is not in the list of supported Loaders ({cls.known_loaders()})'.")

    @property
    def header_lines(self):
        r"""
        The number of header lines in a CSV excluding the line with the column names.

        EXAMPLES:

        Files for the base loader do not have a header::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.header_lines
            0

        Implementation in a specific device loader::

            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0,1\t0\t0
            ... 2\t1\t1,4\t5\t1
            ... ''')
            >>> csv = BaseLoader.create('eclab')(file)
            >>> csv.header_lines
            5

        """
        return self._header_lines or 0

    @property
    def header(self):
        r"""
        The header of the CSV (excluding column names).

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> type(csv.header)
            <class '_io.StringIO'>

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.header.readlines()
            []

        """
        from io import StringIO

        return StringIO(
            "".join(line for line in self.file.readlines()[: self.header_lines])
        )

    @property
    def metadata(self):  # pylint: disable=abstract-method
        r"""A dict containing the metadata of the file found in its header.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.metadata
            Traceback (most recent call last):
            ...
            NotImplementedError

        """
        raise NotImplementedError

    @property
    def column_header_lines(self):
        r"""
        The number of lines containing the descriptive information of the data
        for each column.

        EXAMPLES:

        A file with a single column header line::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.column_header_lines
            1

        A file with a two column header lines::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... x,y
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file, column_header_lines=2)
            >>> csv.column_header_lines
            2

        """
        return self._column_header_lines or 1

    @property
    def column_headers(self):
        r"""
        The lines in the file containing the descriptive information of the data
        for each column.

        EXAMPLES:

        A file with a single column header line::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.column_headers.readlines()
            ['a,b\n']

        A file with two column header lines, which is sometimes, for example,
        used for storing units to the values::

            >>> from io import StringIO
            >>> file = StringIO(r'''T,v
            ... K,m/s
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file, column_header_lines=2)
            >>> csv.column_headers.readlines()
            ['T,v\n', 'K,m/s\n']

        """
        from io import StringIO

        return StringIO(
            "".join(
                line
                for line in self.file.readlines()[
                    self.header_lines : self.header_lines + self.column_header_lines
                ]
            )
        )

    @property
    def column_header_names(self):
        r"""
        A list of column header names constructed from the lines
        containing the column head names.

        EXAMPLES:

        A file with a single column header line::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.column_header_names
            ['a', 'b']

        For a file containing two or more column header lines,
        we create a single name for each column including the information
        from the following lines and separating those with a ``/``.::

            >>> from io import StringIO
            >>> file = StringIO(r'''T,v
            ... K,m/s
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file, column_header_lines=2)
            >>> csv.column_header_names
            ['T / K', 'v / m/s']

        """

        headers = [
            line.strip().split(self.delimiter)
            for line in self.column_headers.getvalue().splitlines()
        ]

        # If there's only one line, return it as is
        if len(headers) == 1:
            return headers[0]

        # If there are multiple lines, combine them column-wise
        return [" / ".join(items) for items in zip(*headers)]

    @property
    def data(self):
        r"""
        A file like object with the data of the CSV without header lines.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> type(csv.data)
            <class '_io.StringIO'>

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.data.readlines()
            ['0,0\n', '1,1']

        """
        from io import StringIO

        return StringIO(
            "".join(
                line
                for line in self.file.readlines()[
                    self.header_lines + self.column_header_lines :
                ]
            )
        )

    @property
    def df(self):
        r"""
        A pandas dataframe of the data in the CSV.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.df
               a  b
            0  0  0
            1  1  1

        """
        import pandas as pd

        return pd.read_csv(
            self.data,
            delimiter=self.delimiter,
            decimal=self.decimal,
            names=self.column_header_names,
        ).reset_index(drop=True)

    @property
    def delimiter(self):
        r"""
        The delimiter in the CSV, which is extracted from
        the first two lines of the CSV data.

        A CSV containing integers::

            >>> from io import StringIO
            >>> file = StringIO('''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.delimiter
            ','

        A CSV containing floats::

            >>> from io import StringIO
            >>> file = StringIO('''a,b
            ... 0.0,0.0
            ... 1.0,1.0''')
            >>> csv = BaseLoader(file)
            >>> csv.delimiter
            ','

        A TSV containing floats with a single header line::

            >>> from io import StringIO
            >>> file = StringIO('''a\tb
            ... 0\t0.0
            ... 1\t1.0''')
            >>> csv = BaseLoader(file)
            >>> csv.delimiter
            '\t'

        A TSV with three columns containing floats using `,` as decimal separator
        with a single header line::

            >>> from io import StringIO
            >>> file = StringIO('''a\tb\tc
            ... 0,0\t0,0\t0,0
            ... 1,1\t1,0\t0,0''')
            >>> csv = BaseLoader(file)
            >>> csv.delimiter
            '\t'

        A TSV with two columns containing floats using `,` as decimal separator
        with a single header line::

            >>> from io import StringIO
            >>> file = StringIO('''a\tb
            ... 0,0\t0,0
            ... 1,1\t1,0''')
            >>> csv = BaseLoader(file)
            >>> csv.delimiter
            '\t'

        A TSV containing integers and floats using `,` as decimal separator
        with a single header line::

            >>> from io import StringIO
            >>> file = StringIO('''a\tb
            ... 0\t0,0
            ... 1\t1,0
            ... ''')
            >>> csv = BaseLoader(file)
            >>> csv.delimiter
            '\t'

        A rather messy file:

            >>> from io import StringIO
            >>> file = StringIO(('''# I am messy data
            ... Random stuff
            ... maybe metadata : 3
            ... in different formats = abc123
            ... hopefully, some information
            ... on where the data block starts!
            ... t\tE\tj
            ... s\tV\tA/cm2
            ... 0\t0\t0
            ... 1\t1\t1
            ... 2\t2\t2
            ... '''))
            >>> csv = BaseLoader(file)
            >>> csv.delimiter
            '\t'

        """
        # TODO:: Validate that the number of delimiters in the data lines
        # matches those in the column header line.
        # This will otherwise likely lead to erroneous loading of pandas dataframes
        # and requires setting the column names specifically.
        if len(self.delimiters) == 1:
            return self.delimiters[0]

        if not len(self.delimiters) == 0:
            from io import StringIO

            import clevercsv

            for delimiter in self.delimiters:
                combined = StringIO(
                    self.column_headers.getvalue() + self.data.getvalue()
                )
                combined.seek(0)
                delimiter_ = (
                    clevercsv.detect.Detector()
                    .detect(combined.read(), delimiters=[delimiter])
                    .delimiter
                )
                if delimiter_:
                    return delimiter_

        return clevercsv.detect.Detector().detect(combined.read()).delimiter

    @property
    def decimal(self):
        r"""
        The decimal separator in the floats in the CSV data.

        EXAMPLES:

        A standard CVS containing floats with a single header line::

            >>> from io import StringIO
            >>> file = StringIO('''a,b
            ... 0.0,0.0
            ... 1.0,1.0''')
            >>> csv = BaseLoader(file)
            >>> csv.decimal
            '.'

        For CVS containing only integers we simply return None.::

            >>> from io import StringIO
            >>> file = StringIO('''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.decimal
            '.'

        A standard CVS containing integers with a single header line::

            >>> from io import StringIO
            >>> file = StringIO('''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = BaseLoader(file)
            >>> csv.decimal
            '.'

        A standard CVS containing integers and floats with a single header line::

            >>> from io import StringIO
            >>> file = StringIO('''a,b
            ... 0,0.0
            ... 1,1.0''')
            >>> csv = BaseLoader(file)
            >>> csv.decimal
            '.'

        A TSV containing floats with a single header line::

            >>> from io import StringIO
            >>> file = StringIO('''a\tb
            ... 0\t0.0
            ... 1\t1.0''')
            >>> csv = BaseLoader(file)
            >>> csv.decimal
            '.'

        A TSV containing integers and floats using `,` as decimal separator
        with a single header line::

            >>> from io import StringIO
            >>> file = StringIO('''a,b
            ... 0\t0,0
            ... 1\t1,0''')
            >>> csv = BaseLoader(file)
            >>> # csv.data.readlines()[1].strip().split(csv.delimiter)
            >>> csv.decimal
            ','

        Data rows containing both '.' and ','::

            >>> from io import StringIO
            >>> file = StringIO('''a\tb\ttext
            ... 0.0\t0.0\ta,b
            ... 1.0\t1.0\tc,d''')
            >>> csv = BaseLoader(file)
            >>> csv.decimal
            '.'

        Data rows containing both '.' and ',' in the values::

            >>> from io import StringIO
            >>> file = StringIO('''a\tb\ttext
            ... 0.1\t0,0\ta,b
            ... 1.1\t1,0\tc,d''')
            >>> csv = BaseLoader(file)
            >>> csv.decimal
            Traceback (most recent call last):
            ...
            ValueError: Decimal separator could not be determined. Found both ',' and '.' in numeric values in a single data line.

        Implementation in a specific device loader::

            >>> from io import StringIO
            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0,1\t0\t0
            ... 2\t1\t1,4\t5\t1
            ... ''')
            >>> csv = BaseLoader.create('eclab')(file)
            >>> csv.decimal
            ','

        """
        if self._decimal:
            return self._decimal

        data = self.data.readlines()[0].strip().split(self.delimiter)

        has_dot = any("." in item for item in data if self._validate_digit(item, "."))
        has_comma = any("," in item for item in data if self._validate_digit(item, ","))

        if has_dot and has_comma:
            raise ValueError(
                "Decimal separator could not be determined. Found both ',' and '.' in numeric values in a single data line."
            )

        if has_comma:
            return ","

        return "."

    @classmethod
    def _validate_digit(cls, item, character):
        """
        Validate if the string is numeric,
        upon removing a specified character.

        Examples::


            >>> BaseLoader._validate_digit('12,33', ',')
            True

            >>> BaseLoader._validate_digit('a,b', ',')
            False

            >>> BaseLoader._validate_digit('1.0', '.')
            True

            >>> BaseLoader._validate_digit('1.1E10', '.')
            True

            >>> BaseLoader._validate_digit('1,1E10', ',')
            True

        """
        try:
            without_character = item.replace(character, "")
            float(without_character)
            return True
        except ValueError:
            return False
