#!/usr/bin/env python

import os
from functools import partial

from . import attrs

LANG_ROOT = os.path.join(os.getenv('ATTRS_ROOT'), 'lang')

put = partial(attrs.put, attrs_root=LANG_ROOT)
get = partial(attrs.get, attrs_root=LANG_ROOT)
walk= partial(attrs.walk, attrs_root=LANG_ROOT)
build = partial(attrs.build, attrs_root=LANG_ROOT)
close = partial(attrs.close, attrs_root=LANG_ROOT)
