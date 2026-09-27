terraform {
  required_version = ">= 1.11, < 2.0"
  backend "local" { path = "/state/terraform.tfstate" }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.64.0"
    }
  }
}

# Deliberately local-only: no real credentials or configurable cloud endpoint.
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "local-lab"
  secret_key                  = "local-lab"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints {
    ec2   = "http://moto:5000"
    elbv2 = "http://moto:5000"
    sts   = "http://moto:5000"
    iam   = "http://moto:5000"
  }
  default_tags {
    tags = { Project = "devops-final-exam", Environment = "local-emulation" }
  }
}
