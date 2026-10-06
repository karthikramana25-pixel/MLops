output "vpc_id" {
  description = "VPC identifier."
  value       = aws_vpc.this.id
}

output "availability_zones" {
  description = "Availability zones used by this VPC."
  value       = local.availability_zones
}

output "public_subnet_ids" {
  description = "Public subnet IDs keyed by availability zone."
  value       = { for az, subnet in aws_subnet.public : az => subnet.id }
}

output "private_subnet_ids" {
  description = "Private subnet IDs keyed by availability zone."
  value       = { for az, subnet in aws_subnet.private : az => subnet.id }
}

output "nat_gateway_ids" {
  description = "The single cost-optimized NAT Gateway ID keyed by its availability zone."
  value       = { (local.nat_gateway_az) = aws_nat_gateway.this.id }
}
