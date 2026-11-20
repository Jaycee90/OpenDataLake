## STEP 7: Create an ECS Cluster ##
# Create an ECS cluster where our Docker ETL tasks will eventually run using Fargate.
resource "aws_ecs_cluster" "opendatalake" {
  name = "opendatalake-cluster"

  tags = {
    Name        = "opendatalake-cluster"
    Project     = "OpenDataLake"
    Environment = "dev"
  }
}