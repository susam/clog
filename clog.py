#!/usr/bin/env python3


"""Channel Logger."""


import datetime
import glob
import json
import logging
import os
import select
import socket
import ssl
import time

_NAME = 'clog'
_log = logging.getLogger(_NAME)


class _ctx:
    retry_delay = 1
    last_upkeep_time = 0


def main():
    """Run client."""
    log_fmt = ('%(asctime)s %(levelname)s %(filename)s:%(lineno)d '
               '%(funcName)s() %(message)s')
    logging.basicConfig(format=log_fmt, level=logging.INFO)

    # Read configuration.
    with open(f'{_NAME}.json', encoding='utf-8') as stream:
        config = json.load(stream)

    while True:
        try:
            _run(config['host'], config['port'], config['tls'],
                 config['nick'], config['password'], config['channels'],
                 config['file_prefix'], config['max_files'])
        except Exception:
            _log.exception('Client encountered error')
            _log.info('Reconnecting in %d s', _ctx.retry_delay)
            time.sleep(_ctx.retry_delay)
            _ctx.retry_delay = min(_ctx.retry_delay * 2, 3600)


def _run(host, port, tls, nick, password, channels, file_prefix, max_files):
    _log.info('Connecting ...')
    sock = socket.create_connection((host, port))
    if tls:
        tls_context = ssl.create_default_context()
        sock = tls_context.wrap_socket(sock, server_hostname=host)

    _log.info('Authenticating ...')
    _send(sock, f'PASS {password}')
    _send(sock, f'NICK {nick}')
    _send(sock, f'USER {nick} {nick} {host} :{nick}')

    _log.info('Joining channels ...')
    for channel in channels:
        _send(sock, f'JOIN {channel}')

    _log.info('Receiving messages ...')
    for line in _recv(sock):
        if line is not None:
            sender, command, middle, trailing = _parse_line(line)
            if command == 'PING':
                _send(sock, f'PONG :{trailing}')
            elif command in ['JOIN', 'PART', 'QUIT', 'PRIVMSG']:
                _log.info(
                    '>> sender: %s; command: %s; middle: %s; trailing: %s',
                    sender, command, middle, trailing)
                text = f'{sender} {command} {middle} :{trailing}\n'
                _fwrite(file_prefix, text)
            _ctx.retry_delay = 1
        if time.time() - _ctx.last_upkeep_time >= 3600:
            _upkeep(file_prefix, max_files)
            _ctx.last_upkeep_time = int(time.time())


def _fwrite(file_prefix, text):
    """Write content to file and close the file."""
    date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    filename = f'{file_prefix}-{date}.txt'
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)
    with open(filename, 'a', encoding='utf-8') as stream:
        stream.write(text)


def _upkeep(file_prefix, max_files):
    filenames = sorted(glob.glob(file_prefix + '*'))
    total_files = len(filenames)
    surplus_files = total_files - max_files
    _log.info('Upkeep: max_files: %d; total_files: %d; surplus_files: %d',
              max_files, total_files, surplus_files)
    if surplus_files > 0:
        filenames = filenames[0:surplus_files]
        for filename in filenames:
            os.remove(filename)
            _log.info('Removed file %s', filename)


# Protocol functions
def _recv(sock):
    buffer = ''
    while True:
        # Check if any data has been received.
        rlist, _, _ = select.select([sock], [], [], 1)
        if len(rlist) == 0:
            yield None
            continue

        # If data has been received, validate data length.
        data = sock.recv(1024)
        if len(data) == 0:
            message = 'Received zero-length payload from server'
            _log.error(message)
            raise ValueError(message)

        # If there is nonempty data, yield lines from it.
        buffer += data.decode(errors='replace')
        lines = buffer.split('\r\n')
        lines, buffer = lines[:-1], lines[-1]
        for line in lines:
            _log.info('recv: %s', line)
            yield line


def _send_message(sock, recipient, message):
    size = 400
    for line in message.splitlines():
        chunks = [line[i:i + size] for i in range(0, len(line), size)]
        for chunk in chunks:
            _send(sock, f'PRIVMSG {recipient} :{chunk}')


def _send(sock, message):
    sock.sendall(message.encode() + b'\r\n')
    _log.info('sent: %s', message)


def _parse_line(line):
    # RFC 1459 - 2.3.1
    # <message>  ::= [':' <prefix> <SPACE> ] <command> <params> <crlf>
    # <prefix>   ::= <servername> | <nick> [ '!' <user> ] [ '@' <host> ]
    # <command>  ::= <letter> { <letter> } | <number> <number> <number>
    # <SPACE>    ::= ' ' { ' ' }
    # <params>   ::= <SPACE> [ ':' <trailing> | <middle> <params> ]
    #
    # Example: :alice!Alice@user/alice PRIVMSG #hello :hello
    # Example: PING :foo.example.com
    if line[0] == ':':
        prefix, rest = line[1:].split(maxsplit=1)
    else:
        prefix, rest = None, line

    sender, command, middle, trailing = None, None, None, None

    if prefix:
        sender = prefix.split('!')[0]

    rest = rest.split(None, 1)
    command = rest[0].upper()

    if len(rest) == 2:
        params = rest[1]
        params = params.split(':', 1)
        middle = params[0].strip()
        if len(params) == 2:
            trailing = params[1].strip()

    return sender, command, middle, trailing


if __name__ == '__main__':
    main()
