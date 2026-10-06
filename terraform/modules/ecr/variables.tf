variable "repository_name" {
  description = "ECR repository name."
  type        = string
}

variable "image_retention_count" {
  description = "Maximum number of images retained in the repository."
  type        = number
}

variable "tags" {
  description = "Tags applied to the repository."
  type        = map(string)
}
