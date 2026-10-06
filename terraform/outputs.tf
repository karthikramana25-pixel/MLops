output "vpc_id" {
  description = "ID of the project VPC."
  value       = module.vpc.vpc_id
}

output "availability_zones" {
  description = "Availability zones used for the public and private subnet pairs."
  value       = module.vpc.availability_zones
}

output "public_subnet_ids" {
  description = "IDs of public subnets for internet-facing load balancers and ingress."
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of private subnets for future EKS nodes and workloads."
  value       = module.vpc.private_subnet_ids
}

output "nat_gateway_ids" {
  description = "ID of the single NAT Gateway serving private subnet egress, keyed by its availability zone."
  value       = module.vpc.nat_gateway_ids
}

output "ecr_repository_name" {
  description = "Name of the immutable ECR repository for the ML API image."
  value       = module.ecr.repository_name
}

output "ecr_repository_url" {
  description = "Registry URL for the ML API image."
  value       = module.ecr.repository_url
}

output "eks_cluster_role_arn" {
  description = "IAM role ARN for a future EKS control plane."
  value       = module.iam.cluster_role_arn
}

output "eks_node_role_arn" {
  description = "IAM role ARN for future EKS worker nodes."
  value       = module.iam.node_role_arn
}
