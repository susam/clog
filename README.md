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
  "file_prefix": "/tmp/clog",
  "max_files": 90
}
```

Then run the following command:

```sh
python3 clog.py
```

With the above example configuration, the channel logs are written to
files named in the format `/tmp/clog-YYYY-MM-DD.txt` where
`YYYY-MM-DD` represents the current date.  All channel logs from all
channels are written to the same file.


License
-------

This is free and open source software.  You can use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of it,
under the terms of the MIT License.  See [LICENSE.md][L] for details.

This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND,
express or implied.  See [LICENSE.md][L] for details.

[L]: LICENSE.md
