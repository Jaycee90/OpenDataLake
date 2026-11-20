## STEP 11: Create an ECS Task Definition ##
# Now that we have an ECS cluster, an IAM execution role, and an IAM task role, we can create an ECS task definition for our ETL container.
# What this does:
# - Defines the container image to use (from ECR. This tells ECS which Docker image to run and how to configure the container).
# - Defines the CPU and memory requirements for the container.
# - Defines the environment variables to pass to the container.

resource "aws_ecs_task_definition" "etl" {
  family                   = "opendatalake-etl"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu    = "512"
  memory = "4096"

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.ecs_task.arn
  container_definitions = jsonencode([
    {
      name      = "opendatalake-etl"
      image     = "${aws_ecr_repository.opendatalake.repository_url}:latest"
      essential = true

      environment = [
        {
          name  = "ENABLE_S3"
          value = "true"
        },
        {
          name  = "S3_BUCKET_NAME"
          value = "opendatalake-raw-8f2445ce62ec6513bb05805ece"
        },
        {
          name  = "DB_HOST"
          value = "opendatalake-postgres.cy5c22m0ewgn.us-east-1.rds.amazonaws.com"
        },
        {
          name  = "DB_NAME"
          value = "postgres"
        },
        {
          name  = "DB_SECRET_ARN"
          value = "arn:aws:secretsmanager:us-east-1:373058354498:secret:rds!db-984bcd2f-a3f7-4d3a-88b9-62b54233f9e4-TpezP3"
        }
      ]

      # Inject the Ticketmaster API key securely from AWS Secrets Manager.
      # ECS retrieves this secret using the execution role.
      secrets = [
        {
          name      = "TICKETMASTER_API_KEY"
          valueFrom = aws_secretsmanager_secret.ticketmaster_api_key.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_etl.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "etl"
        }
      }
    }
  ])
}