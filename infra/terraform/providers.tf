# terraform — Defines Terraform's version and required plugins.
terraform {
  required_version = ">= 1.5.0"

  # required_providers — Tells Terraform to use the official HashiCorp AWS provider.
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# provider "aws" — Configures how Terraform communicates with AWS.
# region — Specifies where AWS resources will be deployed.
# profile — Uses the authenticated opendatalake CLI profile rather than the old AWS credentials.
provider "aws" {
  region  = "us-east-1"
  profile = "opendatalake"
}
