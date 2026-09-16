# All runs use a mock provider and plan only. No AWS credentials are needed.
mock_provider "aws" {
  override_during = plan

  mock_data "aws_vpc" {
    defaults = { id = "vpc-044604d0bfb707142" }
  }
  mock_data "aws_subnet" {
    defaults = { vpc_id = "vpc-044604d0bfb707142" }
  }
  mock_data "aws_ami" {
    defaults = { id = "ami-0123456789abcdef0" }
  }
}

variables {
  aws_account_id       = "123456789012"
  public_subnet_id     = "subnet-0123456789abcdef0"
  allowed_cidr         = "203.0.113.10/32"
  ssh_public_key       = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBWVqJuLQrAiGIioWyhg97TrMfIrSQadOjphTdPGbxAM test-only"
  ssh_private_key_path = "/nonexistent/test-only/devops-builder"
}

run "restricted_builder" {
  command = plan

  assert {
    condition = (
      aws_security_group.builder.vpc_id == "vpc-044604d0bfb707142" &&
      aws_instance.builder.subnet_id == var.public_subnet_id &&
      aws_instance.builder.associate_public_ip_address
    )
    error_message = "The builder must use the selected course subnet and request a public IP."
  }
  assert {
    condition = (
      length(aws_vpc_security_group_ingress_rule.student) == 2 &&
      aws_vpc_security_group_ingress_rule.student["ssh"].from_port == 22 &&
      aws_vpc_security_group_ingress_rule.student["application"].from_port == 5001 &&
      alltrue([for rule in aws_vpc_security_group_ingress_rule.student :
        rule.cidr_ipv4 == "203.0.113.10/32" && rule.ip_protocol == "tcp" &&
        rule.from_port == rule.to_port
      ])
    )
    error_message = "Only SSH and application TCP ports should be open to the student CIDR."
  }
  assert {
    condition = (
      aws_instance.builder.root_block_device[0].encrypted &&
      aws_instance.builder.metadata_options[0].http_tokens == "required" &&
      aws_instance.builder.metadata_options[0].http_put_response_hop_limit == 2
    )
    error_message = "Keep disk encryption and IMDSv2, with container access to instance metadata."
  }
  assert {
    condition = (
      aws_vpc_security_group_egress_rule.outbound.ip_protocol == "-1" &&
      aws_vpc_security_group_egress_rule.outbound.cidr_ipv4 == "0.0.0.0/0"
    )
    error_message = "The builder needs outbound access for packages and AWS APIs."
  }
  assert {
    condition     = output.ssh_private_key_path == "/nonexistent/test-only/devops-builder"
    error_message = "The private key path must remain an output, without reading the key file."
  }
}

run "accept_restricted_network" {
  command = plan
  variables { allowed_cidr = "203.0.113.0/24" }
  assert {
    condition = alltrue([for rule in aws_vpc_security_group_ingress_rule.student :
      rule.cidr_ipv4 == "203.0.113.0/24"
    ])
    error_message = "A permitted /24 network must be applied to both incoming rules."
  }
}

run "reject_world_access" {
  command = plan
  variables { allowed_cidr = "0.0.0.0/0" }
  expect_failures = [var.allowed_cidr]
}

run "reject_broad_network" {
  command = plan
  variables { allowed_cidr = "203.0.112.0/23" }
  expect_failures = [var.allowed_cidr]
}

run "reject_ipv6" {
  command = plan
  variables { allowed_cidr = "2001:db8::/32" }
  expect_failures = [var.allowed_cidr]
}

run "reject_malformed_cidr" {
  command = plan
  variables { allowed_cidr = "not-a-cidr" }
  expect_failures = [var.allowed_cidr]
}

run "reject_invalid_account" {
  command = plan
  variables { aws_account_id = "invalid" }
  expect_failures = [var.aws_account_id]
}

run "reject_invalid_subnet" {
  command = plan
  variables { public_subnet_id = "not-a-subnet" }
  expect_failures = [var.public_subnet_id]
}

run "reject_private_key_input" {
  command = plan
  variables { ssh_public_key = "-----BEGIN OPENSSH PRIVATE KEY-----" }
  expect_failures = [var.ssh_public_key]
}

run "reject_other_vpc" {
  command = plan
  override_data {
    target = data.aws_subnet.public
    values = { vpc_id = "vpc-0123456789abcdef0" }
  }
  expect_failures = [data.aws_subnet.public]
}
