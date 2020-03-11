from __future__ import division, print_function, unicode_literals

from contextlib import contextmanager
import os
import shutil
import re
from base64 import b64encode
from tempfile import mkdtemp, NamedTemporaryFile


@contextmanager
def ignore_missing_file(filename=None):
    try:
        yield
    except OSError as e:
        if e.errno != 2 or filename and e.filename != filename:
            raise


@contextmanager
def in_dir(dirpath):
    # WARNING not thread-safe
    prev = os.path.abspath(os.getcwd())
    os.chdir(dirpath)
    try:
        yield
    finally:
        os.chdir(prev)


@contextmanager
def TempDir(**kw):
    """mkdtemp wrapper that automatically deletes the directory
    """
    d = mkdtemp(**kw)
    try:
        yield d
    finally:
        with ignore_missing_file(d):
            shutil.rmtree(d)


@contextmanager
def TempFile(**kw):
    """NamedTemporaryFile wrapper that doesn't fail if you (re)move the file
    """
    f = NamedTemporaryFile(**kw)
    try:
        yield f
    finally:
        with ignore_missing_file():
            f.__exit__(None, None, None)


def extract_basic_auth(url):
    """Parse URL for basic auth data and return as http header and cleaned url
    """

    header = {}

    m = re.match(r'(?P<protocol>http[s]?:\/\/)(?P<credentials>[^:]+:[^@]+@)?(?P<remaining>[^:]+)', url)

    if m is not None:
        if m.groupdict()["credentials"] is not None:
            url = m.groupdict()["protocol"] + m.groupdict()["remaining"]
            cred_bytes = bytes(m.groupdict()["credentials"][:-1], "utf-8")
            cred = b64encode(cred_bytes).decode("ascii")
            header = { 'Authorization' : 'Basic {}'.format(cred) }

    return url, header

def force_link(source, link_name):
    # WARNING not atomic
    with ignore_missing_file():
        os.remove(link_name)
    os.link(source, link_name)
