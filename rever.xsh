# ********************************************************************
#  This file is part of unitpackage.
#
#        Copyright (C) 2022-2024 Albert Engstfeld
#        Copyright (C) 2022      Johannes Hermann
#        Copyright (C) 2022      Julian Rüth
#        Copyright (C) 2022      Nicolas Hörmann
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ********************************************************************

import re

# Check that we are on the main branch
branch=$(git branch --show-current)
if branch.strip() != "main":
  raise Exception("You must be on the main branch to release.")
# and that it is up to date with origin/main
git fetch https://github.com/echemdb/unitpackage.git
git reset FETCH_HEAD
git diff --exit-code
git diff --cached --exit-code

$PROJECT = 'unitpackage'

$ACTIVITIES = [
    'version_bump',
    'changelog',
    'tag',
    'push_tag',
    'pypi',
    'ghrelease',
]

$VERSION_BUMP_PATTERNS = [
    ('pyproject.toml', r'version =', 'version = "$VERSION"'),
    ('doc/conf.py', r"release = ", r"release = '$VERSION'"),
    ('doc/index.md', re.escape(r"[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/echemdb/unitpackage/"), r"[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/echemdb/unitpackage/$VERSION?labpath=tree%2Fdoc%2Findex.md)"),
    ('README.md', re.escape(r"[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/echemdb/unitpackage/"), r"[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/echemdb/unitpackage/$VERSION?labpath=tree%2Fdoc%2Findex.md)"),
    ('binder/environment.yml', r"  - unitpackage==", r"  - unitpackage==$VERSION"),
]

$CHANGELOG_FILENAME = 'ChangeLog'
$CHANGELOG_TEMPLATE = 'TEMPLATE.rst'
$CHANGELOG_NEWS = 'doc/news'
$PUSH_TAG_REMOTE = 'git@github.com:echemdb/unitpackage.git'

$PYPI_BUILD_COMMANDS = ['sdist', 'bdist_wheel']

$GITHUB_ORG = 'echemdb'
$GITHUB_REPO = 'unitpackage'

$CHANGELOG_CATEGORIES = ('Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Performance')
