import hashlib
import os
import re

from urllib.parse import urlparse
from .sample import Sample
from .validation import sanitize_identifier, ValidationError

really_printable = '0123456789abcdefghijklmnopqrstuvwxyz' \
                   'ABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()' \
                   '*+,-./:;<=>?@[\\]^_`{|}~ \t'

url_regex = r"(https?://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]{2,})+(?:[/?][a-zA-Z-0-9?/:&+\-=.]+)?)"


class ResultsStore(object):
    """
    Storage for incoming analysis results from emulators
    """
    def __init__(self, workdir):
        self.workdir = workdir
        self.snippets = {}
        self.urls = {}
        self.url_origins = {}
        self.strings = set()
        self.logfiles = {}

    def _get_keypath(self, key, create=True):
        if key:
            key_path = os.path.join(self.workdir, key)
            if create:
                os.makedirs(key_path, exist_ok=True)
            else:
                if not os.path.isdir(key_path):
                    return None
        else:
            key_path = self.workdir
        return key_path

    def _store_as_symlink(self, key, identifier, target_path):
        target_path = os.path.abspath(target_path)
        key_path = self._get_keypath(key)
        element_path = os.path.join(key_path, identifier)
        symlink_path = os.path.abspath(key_path)
        rel_path = os.path.relpath(target_path, symlink_path)
        os.symlink(rel_path, element_path)
        return element_path

    def _store_as_file(self, key, identifier, content):
        key_path = self._get_keypath(key)
        element_path = os.path.join(key_path, identifier)
        with open(element_path, "wb") as f:
            f.write(content)
        return element_path

    def load_element(self, key, identifier, default=b""):
        # Validate identifier to prevent path traversal
        try:
            sanitize_identifier(identifier)
        except ValidationError:
            return default

        key_path = self._get_keypath(key)
        if key_path is None:
            return default
        element_path = os.path.join(key_path, identifier)

        # Ensure the resulting path is still within workdir
        try:
            abs_path = os.path.abspath(element_path)
            abs_workdir = os.path.abspath(self.workdir)
            if not abs_path.startswith(abs_workdir + os.sep) and abs_path != abs_workdir:
                return default
        except Exception:
            return default

        try:
            with open(element_path, "rb") as f:
                return f.read()
        except IOError:
            return default

    def _load_key(self, key):
        key_path = self._get_keypath(key)
        if key_path is None:
            return

        # Validate key_path is within workdir
        try:
            abs_key_path = os.path.abspath(key_path)
            abs_workdir = os.path.abspath(self.workdir)
            if not abs_key_path.startswith(abs_workdir + os.sep) and abs_key_path != abs_workdir:
                return
        except Exception:
            return

        for identifier in os.listdir(key_path):
            yield identifier

    def add_url(self, url, origin):
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        if not netloc:
            return
        # Is unique?
        if url in self.url_origins:
            self.url_origins[url].add(origin)
            return
        self.url_origins[url] = {origin}
        if netloc not in self.urls:
            self.urls[netloc] = []
        self.urls[netloc].append(url)

    def _look_for_url(self, data, found_in):
        for matches in re.findall(url_regex, data):
            self.add_url(matches[0], found_in)

    def add_string(self, string):
        if 3 < len(string) < 128 and all(map(lambda c: c in really_printable, string)):
            self.strings.add(string)
        if len(string) >= 128:
            self.add_snippet(string)
        self._look_for_url(string, "string")

    def add_snippet(self, snippet):
        if isinstance(snippet, (list, tuple)):
            snip_id, emulation_path = snippet
        else:
            if isinstance(snippet, str):
                snippet = snippet.encode("utf8")
            snip_id = hashlib.sha256(snippet).hexdigest()
            emulation_path = None

        if snip_id in self.snippets:
            return

        if emulation_path is None:
            snippet_path = self._store_as_file("snippets", snip_id, snippet)
        else:
            snippet_path = self._store_as_symlink("snippets", snip_id, emulation_path)
            snippet = self.load_element("snippets", snip_id)
        self.snippets[snip_id] = {
            "path": snippet_path,
            "size": len(snippet),
            "sha256": snip_id
        }
        snip_sample = Sample(snippet)
        self._look_for_url(snip_sample.stringified_code, ("snippet", snip_id))

    def add_logfile(self, emulator, key, path):
        if emulator.name not in self.logfiles:
            self.logfiles[emulator.name] = {}
        if key in self.logfiles[emulator.name]:
            return
        logfile_path = self._store_as_symlink("logfiles",
                                              "{}-{}".format(emulator.name, key),
                                              path)
        self.logfiles[emulator.name][key] = logfile_path

    def load(self, params):
        self.strings = set(params.get("strings", []))
        self.snippets = params.get("snippets", {})
        self.urls = params.get("urls", {})
        self.url_origins = params.get("url_origins", {})
        self.logfiles = params.get("logfiles", {})

    def store(self):
        return {
            "strings": list(self.strings),
            "snippets": self.snippets,
            "urls": self.urls,
            "url_origins": {k: list(v) for k, v in self.url_origins.items()},
            "logfiles": self.logfiles
        }
