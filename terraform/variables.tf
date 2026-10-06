variable "aws_region" {
  description = "AWS region where the foundation will be created."
  type        = string
  default     = "us-east-1"

  validation {
    condition     = length(trimspace(var.aws_region)) > 0
    error_message = "aws_region must not be empty."
  }
}

variable "project_name" {
  description = "Short lowercase name used to name and tag project resources."
  type        = string
  default     = "mlops"

  validation {
    condition     = length(var.project_name) <= 30 && can(regex("^[a-z0-9][a-z0-9-]*$", var.project_name))
    error_message = "project_name must be at most 30 characters and contain lowercase letters, digits, or hyphens."
  }
}

variable "environment" {
  description = "Deployment environment name, such as dev, staging, or prod."
  type        = string
  default     = "dev"

  validation {
    condition     = length(var.environment) <= 10 && can(regex("^[a-z0-9][a-z0-9-]*$", var.environment))
    error_message = "environment must be at most 10 characters and contain lowercase letters, digits, or hyphens."
  }
}

variable "vpc_cidr" {
  description = "IPv4 CIDR block for the VPC."
  type        = string
  default     = "10.20.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid IPv4 CIDR block."
  }
}

variable "availability_zones" {
  description = "Exactly two AZ names, or an empty list to select the first two available AZs in the configured region."
  type        = list(string)
  default     = []

  validation {
    condition     = length(var.availability_zones) == 0 || length(var.availability_zones) == 2
    error_message = "availability_zones must be empty or contain exactly two availability zones."
  }
}

variable "public_subnet_cidrs" {
  description = "IPv4 CIDR blocks for the two public subnets, in availability-zone order."
  type        = list(string)
  default     = ["10.20.0.0/20", "10.20.16.0/20"]

  validation {
    condition     = length(var.public_subnet_cidrs) == 2 && alltrue([for cidr in var.public_subnet_cidrs : can(cidrhost(cidr, 0))])
    error_message = "public_subnet_cidrs must contain exactly two valid IPv4 CIDR blocks."
  }
}

variable "private_subnet_cidrs" {
  description = "IPv4 CIDR blocks for the two private subnets, in availability-zone order."
  type        = list(string)
  default     = ["10.20.128.0/20", "10.20.144.0/20"]

  validation {
    condition     = length(var.private_subnet_cidrs) == 2 && alltrue([for cidr in var.private_subnet_cidrs : can(cidrhost(cidr, 0))])
    error_message = "private_subnet_cidrs must contain exactly two valid IPv4 CIDR blocks."
  }
}

variable "ecr_image_retention_count" {
  description = "Maximum number of images retained in the ECR repository."
  type        = number
  default     = 30

  validation {
    condition     = var.ecr_image_retention_count >= 1 && floor(var.ecr_image_retention_count) == var.ecr_image_retention_count
    error_message = "ecr_image_retention_count must be a positive whole number."
  }
}

variable "additional_tags" {
  description = "Additional tags merged with the standard Project, Environment, and ManagedBy tags."
  type        = map(string)
  default     = {}
}
