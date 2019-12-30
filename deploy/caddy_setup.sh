#!/bin/sh -

set -e

# Download and extract Caddy
curl 'https://caddyserver.com/download/linux/amd64?license=personal&telemetry=off' >caddy.tar.gz
mkdir caddy
tar -xvzf caddy.tar.gz -C caddy

# First, put the caddy binary in the system wide binary directory and give it appropriate ownership and permissions:
cp caddy/caddy /usr/local/bin
chown root:root /usr/local/bin/caddy
chmod 755 /usr/local/bin/caddy

# Give the caddy binary the ability to bind to privileged ports (e.g. 80, 443) as a non-root user:
setcap 'cap_net_bind_service=+ep' /usr/local/bin/caddy

# Set up the user, group, and directories that will be needed:
# www-data already exists on Debian-based systems so skip creation
#groupadd -g 333 www-data
#useradd -g www-data --no-user-group --home-dir /var/www --no-create-home --shell /usr/sbin/nologin --system --uid 333 www-data

mkdir /etc/caddy
chown -R root:root /etc/caddy

mkdir /etc/ssl/caddy
chown -R root:www-data /etc/ssl/caddy
chmod 0770 /etc/ssl/caddy

# Place your caddy configuration file ("Caddyfile") in the proper directory and give it appropriate ownership and permissions:
cp Caddyfile /etc/caddy/Caddyfile
chown root:root /etc/caddy/Caddyfile
chmod 644 /etc/caddy/Caddyfile

# Install the systemd service unit configuration file, reload the systemd daemon, and start caddy:
curl 'https://raw.githubusercontent.com/caddyserver/caddy/4b68de84181938381f604064336b0342e389c551/dist/init/linux-systemd/caddy.service' >/etc/systemd/system/caddy.service
chown root:root /etc/systemd/system/caddy.service
chmod 644 /etc/systemd/system/caddy.service
systemctl daemon-reload
systemctl start caddy.service
