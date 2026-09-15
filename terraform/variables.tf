variable "aws_account_id" {
  description = "The verified course AWS account. Prevents applying to another account."
  type        = string
  validation {
    condition     = can(regex("^[0-9]{12}$", var.aws_account_id))
    error_message = "Provide the 12-digit course AWS account ID."
  }
}

variable "public_subnet_id" {
  description = "A verified public subnet in the course VPC."
  type        = string
  validation {
    condition     = can(regex("^subnet-[a-f0-9]+$", var.public_subnet_id))
    error_message = "Provide a real subnet ID from the course VPC."
  }
}

variable "allowed_cidr" {
  description = "Student public IPv4 CIDR for SSH and the application; use /32 when possible."
  type        = string
  validation {
    condition = (
      can(cidrhost(var.allowed_cidr, 0)) &&
      !strcontains(var.allowed_cidr, ":") &&
      try(tonumber(split("/", var.allowed_cidr)[1]) >= 24, false)
    )
    error_message = "Use a valid, restricted IPv4 CIDR from /24 to /32, preferably your public IP/32."
  }
}

variable "ssh_public_key" {
  description = "Public SSH key generated outside Terraform. Never supply a private key."
  type        = string
  validation {
    condition     = can(regex("^ssh-(ed25519|rsa) [A-Za-z0-9+/=]+", trimspace(var.ssh_public_key)))
    error_message = "Supply an OpenSSH Ed25519 or RSA public key."
  }
}

variable "ssh_private_key_path" {
  description = "Local private-key path, used only in outputs. The file contents are never read."
  type        = string
  default     = "~/.ssh/devops-builder"
}

variable "instance_type" {
  description = "Builder instance size. Confirm availability and cost before applying."
  type        = string
  default     = "t3.medium"
}

variable "iam_instance_profile" {
  description = "Optional existing course IAM instance profile for the application."
  type        = string
  default     = null
}
