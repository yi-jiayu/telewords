resource "digitalocean_floating_ip" "telewords" {
  region = var.do_region
}

resource "aws_route53_record" "telewords" {
  zone_id = var.route53_zone_id
  name    = var.host
  type    = "A"
  ttl     = 300
  records = [digitalocean_floating_ip.telewords.ip_address]
}

resource "digitalocean_ssh_key" "telewords" {
  name       = "id_telewords"
  public_key = file(var.ssh_public_key_file)
}

resource "digitalocean_droplet" "telewords" {
  image      = "ubuntu-18-04-x64"
  name       = "telewords"
  region     = var.do_region
  size       = "s-1vcpu-1gb"
  monitoring = true
  ssh_keys   = [digitalocean_ssh_key.telewords.fingerprint]
  user_data = templatefile("cloud-init.yaml", {
    ssh_public_key = digitalocean_ssh_key.telewords.public_key,
    telewords_service_file = base64encode(templatefile("telewords.service", {
      bot_token    = var.bot_token,
      bot_username = var.bot_username,
    })),
    caddyfile              = base64encode(templatefile("Caddyfile", { host = var.host })),
    telewords_setup_script = filebase64("telewords_setup.sh"),
    caddy_setup_script     = filebase64("caddy_setup.sh"),
  })
}

resource "digitalocean_floating_ip_assignment" "telewords" {
  ip_address = digitalocean_floating_ip.telewords.ip_address
  droplet_id = digitalocean_droplet.telewords.id
}

resource "digitalocean_firewall" "telewords" {
  name = "telewords"

  droplet_ids = [digitalocean_droplet.telewords.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
