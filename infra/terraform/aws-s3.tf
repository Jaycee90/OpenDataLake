# resource defines an AWS resource Terraform will manage.
resource "aws_s3_bucket" "raw_events" {
  bucket_prefix = "opendatalake-raw-"

  tags = {
    Project     = "OpenDataLake"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

# aws_s3_bucket_public_access_block helps prevent accidental public access.
resource "aws_s3_bucket_public_access_block" "raw_events" {
  bucket = aws_s3_bucket.raw_events.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
