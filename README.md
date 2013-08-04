# uWSGI-helper

uWSGI-helper - A simple wrapper around the uWSGI process


## Synopsis

```
uwsgi.py   --path | [ --test ] | [ --stop ] | [ --start ] | [ --reload ]  |
           --name | [ --kill ] | [ --info ] | [ --state ] | [ --version ] |
```


## Dependencies

```
pip install pyyaml
```


## Example


*/usr/local/etc/uwsgi/uwsgi.yaml*

```yaml
default: &options
    path    : /usr/local/bin/uwsgi

example.com:
    path    : /usr/local/bin/uwsgi
    pid     : /var/run/uwsgi/example.com.uwsgi.pid
    config  : /home/www/example.com/uwsgi.yaml
```


*/home/www/example.com/uwsgi.yaml*

```yaml
uwsgi:
    # User identifier of uWSGI processes
    uid           : www

    # Group identifier of uWSGI processes
    gid           : www

    wsgi-file     : /home/www/example.com/wsgi.py

    # Bind to UNIX socket at /run/uwsgi/<confnamespace>/<confname>/socket
    socket: 127.0.0.1:9000

    # Set mode of created UNIX socket
    chmod-socket = 664

    # Write master's pid in file /run/uwsgi/<confnamespace>/<confname>/pid
    pidfile       : /var/run/uwsgi/example.com.uwsgi.pid

    # Write logs into file
    daemonize     : /var/log/uwsgi/example.com.uwsgi.log

    python-path   : /usr/bin
    chdir         : /home/www/example.com/

    # Enable master process manager
    master        : 1

    # Place timestamps into log
    log-date      : true

    show-config   : true

    # Automatically kill workers on master's death
    no-orphans    : true

    # Spawn 2 uWSGI worker processes
    workers       : 2
    processes     : 10

```


*/etc/init.d/uwsgi.py*

```sh

sudo ln -s /home/www/example.com/uwsgi.py /etc/init.d/uwsgi.py

alias uwsgi="sudo python /etc/init.d/uwsgi.py \
	--path='/usr/local/etc/uwsgi/uwsgi.yaml' \
	--name='example.com'"

uwsgi --test

```
























##

* uWSGI-helper library is licensed under the MIT (MIT_LICENSE.txt) license

* Copyright (c) 2012 [Alexander Guinness] (https://github.com/monolithed)