variable "do_token" {
  type = string
}

variable "do_region" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "route53_zone_id" {
  type = string
}

variable "host" {
  type = string
}

variable "bot_token" {
  type = string
}

variable "bot_username" {
  type = string
}

variable "ssh_public_key_file" {
  type        = string
  default     = "id_telewords.pub"
  description = "A path to an SSH public key file to use"
}
