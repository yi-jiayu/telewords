#!/bin/sh -

set -e

pip3 install pipenv

git clone 'https://github.com/yi-jiayu/telewords.git' /home/telewords/telewords

(cd /home/telewords/telewords && PIPENV_VENV_IN_PROJECT=1 pipenv install --python "$(command -v python3)")

chown -R telewords:telewords /home/telewords/telewords

/home/telewords/telewords/.venv/bin/python -m nltk.downloader -d /usr/local/share/nltk_data wordnet

cp telewords.service /etc/systemd/system/
systemctl daemon-reload
systemctl start telewords.service
