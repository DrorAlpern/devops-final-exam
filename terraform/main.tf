locals {
  course_vpc_id = "vpc-044604d0bfb707142"
}

data "aws_vpc" "course" {
  id = local.course_vpc_id
}

data "aws_subnet" "public" {
  id = var.public_subnet_id

  lifecycle {
    postcondition {
      condition     = self.vpc_id == data.aws_vpc.course.id
      error_message = "The selected subnet must belong to the VPC required by the course."
    }
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

resource "aws_key_pair" "builder" {
  key_name_prefix = "dror-alpern-builder-"
  public_key      = trimspace(var.ssh_public_key)
}

resource "aws_security_group" "builder" {
  name_prefix = "dror-alpern-builder-"
  description = "Restricted access to the DevOps course builder"
  vpc_id      = data.aws_vpc.course.id
}

resource "aws_vpc_security_group_ingress_rule" "student" {
  for_each = {
    ssh         = 22
    application = 5001
  }

  security_group_id = aws_security_group.builder.id
  description       = "Student access: ${each.key}"
  ip_protocol       = "tcp"
  from_port         = each.value
  to_port           = each.value
  cidr_ipv4         = var.allowed_cidr
}

resource "aws_vpc_security_group_egress_rule" "outbound" {
  security_group_id = aws_security_group.builder.id
  description       = "Outbound package downloads and AWS API access"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_instance" "builder" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnet.public.id
  associate_public_ip_address = true
  key_name                    = aws_key_pair.builder.key_name
  vpc_security_group_ids      = [aws_security_group.builder.id]
  iam_instance_profile        = var.iam_instance_profile

  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  root_block_device {
    encrypted             = true
    volume_type           = "gp3"
    volume_size           = 30
    delete_on_termination = true
  }

  tags = {
    Name = "builder"
  }
}
