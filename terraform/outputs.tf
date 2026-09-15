output "instance_id" {
  description = "EC2 builder instance ID."
  value       = aws_instance.builder.id
}

output "public_ip" {
  description = "Public IPv4 address of the builder."
  value       = aws_instance.builder.public_ip
}

output "security_group_id" {
  description = "Security group restricting incoming SSH and application traffic."
  value       = aws_security_group.builder.id
}

output "ssh_private_key_path" {
  description = "Local path only; Terraform never reads or generates the private key."
  value       = pathexpand(var.ssh_private_key_path)
}

output "ssh_key_name" {
  description = "Name of the public key registered with EC2."
  value       = aws_key_pair.builder.key_name
}

output "application_url" {
  description = "Application URL after Docker deployment."
  value       = "http://${aws_instance.builder.public_ip}:5001/"
}
