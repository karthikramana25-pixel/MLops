variable "name" {
  description = "Name prefix for VPC resources."
  type        = string
}

variable "vpc_cidr" {
  description = "IPv4 CIDR block for the VPC."
  type        = string
}

variable "availability_zones" {
  description = "Exactly two AZ names, or empty to select the first two available AZs."
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets, ordered to match availability_zones."
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets, ordered to match availability_zones."
  type        = list(string)
}

variable "tags" {
  description = "Tags applied to VPC resources."
  type        = map(string)
}
