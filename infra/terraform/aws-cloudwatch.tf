## STEP 10: Configure CloudWatch logging ##
# This configuration creates a CloudWatch Logs group to collect output from your Python ETL application.
# These messages can appear in CloudWatch once we configure the ECS task definition to send container logs there.
resource "aws_cloudwatch_log_group" "ecs_etl" {
  name              = "/ecs/opendatalake-etl"
  retention_in_days = 7

  tags = {
    Project     = "OpenDataLake"
    Environment = "dev"
  }
}