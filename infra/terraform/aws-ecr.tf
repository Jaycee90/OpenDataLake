##  STEP 4: Create an ECR Repository ##
# Private container registry for the OpenDataLake ETL.
resource "aws_ecr_repository" "opendatalake" {
  name                 = "opendatalake"
  image_tag_mutability = "MUTABLE" # Allows updating latest during development

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Project     = "OpenDataLake"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

# Display the repository URL after provisioning.
output "ecr_repository_url" {
  description = "ECR repository URL for the OpenDataLake Docker image"
  value       = aws_ecr_repository.opendatalake.repository_url
}