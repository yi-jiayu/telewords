provider "digitalocean" {
  token = var.do_token
}

provider "aws" {
  region = var.aws_region
}

provider "telegram" {
  bot_token = var.bot_token
}
