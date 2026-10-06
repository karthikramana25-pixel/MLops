locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = merge(var.additional_tags, {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  })
}

module "vpc" {
  source = "./modules/vpc"

  name                 = local.name_prefix
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  tags                 = local.common_tags
}

module "ecr" {
  source = "./modules/ecr"

  repository_name       = "${local.name_prefix}-ml-api"
  image_retention_count = var.ecr_image_retention_count
  tags                  = local.common_tags
}

module "iam" {
  source = "./modules/iam"

  name = local.name_prefix
  tags = local.common_tags
}
