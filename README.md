Clog
====

Clog is an extremely simple IRC chat logger.

To run Clog, first create a configuration file named `clog.json` like
the following in the current directory:

```json
{
  "host": "irc.libera.chat",
  "port": 6697,
  "tls": true,
  "nick": "...",
  "password": "...",
  "channels": ["#foo", "#bar"],
  "directory": "/tmp/clog/",
  "max_files": 90
}
```

The occurrences of triple-dots (`...`) in the above example represent
placeholders that need to be replaced with actual credentials.

Then run the following command:

```sh
python3 clog.py
```

With the above example configuration, the channel logs are written to
files named in the format `/tmp/clog/clog-YYYY-MM-DD.txt` where
`YYYY-MM-DD` represents the current date.  All channel logs from all
channels are written to the same file.

Note that this is not a typical channel logger that formats the
messages beautifully.  This picks the JOIN, PART, QUIT, and PRIVMSG
payloads and logs almost the raw payloads with very minor
preprocessing.  The preprocessing step performs minor clean up on the
nick names.


License
-------

This is free and open source software.  You can use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of it,
under the terms of the MIT License.  See [LICENSE.md][L] for details.

This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND,
express or implied.  See [LICENSE.md][L] for details.

[L]: LICENSE.md
