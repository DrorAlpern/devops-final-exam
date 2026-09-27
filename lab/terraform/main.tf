# These are API resources in Moto, not billable AWS resources or running VMs.
resource "aws_vpc" "lab" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "devops-lab" }
}

resource "aws_subnet" "public" {
  for_each                = { a = "10.42.1.0/24", b = "10.42.2.0/24" }
  vpc_id                  = aws_vpc.lab.id
  cidr_block              = each.value
  availability_zone       = "us-east-1${each.key}"
  map_public_ip_on_launch = true
  tags                    = { Name = "lab-public-${each.key}" }
}

resource "aws_internet_gateway" "lab" {
  vpc_id = aws_vpc.lab.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.lab.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.lab.id
  }
}

resource "aws_route_table_association" "public" {
  for_each       = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "builder" {
  name        = "local-builder"
  description = "Example restricted builder access in the emulator"
  vpc_id      = aws_vpc.lab.id
  dynamic "ingress" {
    for_each = [22, 5001]
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["203.0.113.10/32"]
    }
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Moto ships this fixed image record. It supplies metadata only; no OS boots.
data "aws_ami" "seed" {
  owners = ["amazon"]
  filter {
    name   = "image-id"
    values = ["ami-1e749f67"]
  }
}

resource "aws_ami_from_instance" "builder" {
  name               = "local-builder-image"
  description        = "API-only image record; no bootable machine image"
  source_instance_id = aws_instance.builder.id
}
resource "aws_network_interface" "builder" {
  subnet_id       = aws_subnet.public["a"].id
  security_groups = [aws_security_group.builder.id]
  tags            = { Name = "builder-network" }
}

resource "aws_instance" "builder" {
  ami           = data.aws_ami.seed.id
  instance_type = "t3.medium"
  primary_network_interface {
    network_interface_id = aws_network_interface.builder.id
  }
  metadata_options { http_tokens = "required" }
  tags = { Name = "builder" }
}
resource "aws_lb" "monitor" {
  name               = "local-monitor-alb"
  internal           = true
  load_balancer_type = "application"
  subnets            = [for subnet in aws_subnet.public : subnet.id]
  security_groups    = [aws_security_group.builder.id]
}

output "inventory" {
  value = {
    mode              = "local-emulation"
    instance_id       = aws_instance.builder.id
    vpc_id            = aws_vpc.lab.id
    image_id          = aws_ami_from_instance.builder.id
    load_balancer_arn = aws_lb.monitor.arn
  }
}
