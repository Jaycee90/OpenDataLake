## STEP 8: Create an ECS Execution Role ##
# Before Fargate can pull Docker image from ECR and send logs to CloudWatch, it needs an IAM execution role.
# What this does:
# - Creates an IAM role that ECS Fargate can assume.
# - Grants the standard permissions to pull images from ECR and publish logs to CloudWatch.
# - Does not start a container or incur Fargate compute charges.
data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution" {
  name               = "OpenDataLakeECSExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = {
    Project     = "OpenDataLake"
    Environment = "dev"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS cluster can now use this role to pull Docker images from ECR and publish logs to CloudWatch.
# Now we can create the ECS task role for the ETL tasks to assume, which will have permissions to read from S3 and write to RDS.
# The distinction is important:
# - Execution role: Used by ECS infrastructure to pull images and send logs.
# - Task role: Used by your Python application to access AWS resources such as S3.
resource "aws_iam_role" "ecs_task" {
  name               = "OpenDataLakeECSTaskRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = {
    Project     = "OpenDataLake"
    Environment = "dev"
  }
}

# Grant the task role access to S3
# Python ETL needs to upload raw Ticketmaster JSON data to your S3 bucket.
# What this means:
#     The ECS task role will be allowed to list your OpenDataLake S3 bucket and read or upload objects within it.
#     It won't receive access to every S3 bucket in your AWS account.

resource "aws_iam_role_policy" "ecs_task_s3" {
  name = "OpenDataLakeECSTaskS3Policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListRawEventsBucket"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.raw_events.arn
      },
      {
        Sid    = "ReadWriteRawEvents"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.raw_events.arn}/*"
      }
    ]
  })
}

# What this does
# - aws_iam_role_policy: Creates an inline IAM policy on your existing ECS task role.
# - secretsmanager:GetSecretValue: Allows the running Python application to retrieve the database credentials.
# - Resource: Restricts access to your specific RDS secret.
resource "aws_iam_role_policy" "ecs_task_secrets" {
  name = "OpenDataLakeECSTaskSecretsPolicy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ReadRDSMasterSecret"
        Effect = "Allow"

        Action = [
          "secretsmanager:GetSecretValue"
        ]

        Resource = "arn:aws:secretsmanager:us-east-1:373058354498:secret:rds!db-984bcd2f-a3f7-4d3a-88b9-62b54233f9e4-TpezP3"
      }
    ]
  })
}

# Grant the ECS execution role access to the Ticketmaster secret allowing it to retrieve the Ticketmaster API key from AWS Secrets Manager.
# Remember, we have two ECS IAM roles:
# IAM role	Responsibility
# OpenDataLakeECSExecutionRole	Pulls the Docker image, sends logs to CloudWatch, and injects secrets
# OpenDataLakeECSTaskRole	Allows the Python application to access S3 and retrieve RDS credentials
# Because ECS injects the Ticketmaster API key before Python application starts, the permission belongs to the execution role.
resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "OpenDataLakeECSExecutionSecretsPolicy"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ReadTicketmasterAPIKey"
        Effect = "Allow"

        Action = [
          "secretsmanager:GetSecretValue"
        ]

        Resource = aws_secretsmanager_secret.ticketmaster_api_key.arn
      }
    ]
  })
}