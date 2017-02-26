#!/bin/bash

export PATH=/usr/local/bin:$PATH

kill -QUIT $(< /tmp/byrsite/byrsearch_site.pid)

echo "byrsearch_site stop success."