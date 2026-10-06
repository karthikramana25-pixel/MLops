# Terraform foundation

This configuration defines a two-AZ network foundation, an ECR repository for the ML API image, and the IAM roles/policies intended for a later EKS deployment. It does not create EKS, a database, Kubernetes resources, monitoring, or Terraform backend resources.

## Authentication and configuration

Terraform uses the standard AWS credential chain (for example, an AWS CLI profile, IAM Identity Center/SSO, or environment-based temporary credentials). Do not put access keys or secret keys in `.tf`, `.tfvars`, or provider blocks. Copy `terraform.tfvars.example` to `terraform.tfvars` and edit region, names, CIDRs, and tags as needed. The `.gitignore` excludes local tfvars and state files.

## Backend design for a later phase

The current configuration uses Terraform's local backend. Before a team or CI workflow manages this state, bootstrap a dedicated S3 bucket separately. Enable bucket versioning, server-side encryption, S3 Block Public Access, and tightly scoped access. Then add an S3 backend block and initialize with an untracked partial backend file, for example:

```hcl
terraform {
  backend "s3" {}
}
```

Example `backend.hcl` contents (create locally after the bucket exists; do not commit account-specific backend configuration):

```hcl
bucket       = "<pre-created-state-bucket>"
key          = "mlops/dev/terraform.tfstate"
region       = "us-east-1"
encrypt      = true
use_lockfile = true
```

Then use Terraform 1.10 or newer and run `terraform init -backend-config=backend.hcl`. The current infrastructure configuration supports Terraform 1.6+, while the future S3 backend's native `use_lockfile` option requires Terraform 1.10+. S3 lockfiles provide state locking without a DynamoDB table. Backend settings and credentials are deliberately not embedded in this configuration, and no backend resources are created here.

## Validation

From this directory:

```shell
terraform fmt -recursive
terraform init
terraform validate
terraform plan
```

The plan command is read-only; never run `terraform apply` without an explicit reviewed change plan and approval.

## Resources in this foundation

- VPC with DNS support/hostnames, an internet gateway, two public subnets, and two private subnets across two AZs.
- Public route table to the internet gateway; each private subnet has its own route table, both routing egress through one NAT Gateway in the first configured AZ.
- One NAT Gateway Elastic IP allocation. This cost-optimized learning setup has a single-AZ egress dependency; use one NAT Gateway per AZ for production high availability.
- ECR repository with immutable tags, encryption at rest, scan-on-push, and lifecycle cleanup.
- EKS cluster and node IAM roles with AWS-managed policies needed as a starting point for a later EKS phase.

No standalone security groups are created: there are no instances, endpoints, or load balancers to attach them to yet. Define the EKS control-plane/node/workload security groups alongside the EKS resources, where their traffic rules can be scoped accurately.

## Cost considerations

The VPC, subnets, route tables, internet gateway, and IAM roles/policy attachments do not have direct hourly charges. The single NAT Gateway incurs hourly, data-processing, and transfer charges, and its public IPv4 address is billed separately. ECR storage is billed for image data retained; the lifecycle policy limits accumulation. Basic scan-on-push is enabled. The future S3 state bucket will incur storage/request charges and possibly KMS charges if configured for a customer-managed key. Actual rates vary by region and traffic; check the AWS Pricing Calculator before deployment.
