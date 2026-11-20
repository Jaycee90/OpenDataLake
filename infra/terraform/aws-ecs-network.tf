## STEP 9: Create an ECS Security Group ##
# What this does: Creates a dedicated ECS security group and allows outbound connections.
# It does not allow unsolicited inbound traffic.

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "ecs_tasks" {
  name        = "opendatalake-ecs-tasks-sg"
  description = "Security group for OpenDataLake ECS Fargate tasks"
  vpc_id      = data.aws_vpc.default.id

  tags = {
    Name        = "opendatalake-ecs-tasks-sg"
    Project     = "OpenDataLake"
    Environment = "dev"
  }
}

resource "aws_vpc_security_group_egress_rule" "ecs_outbound" {
  security_group_id = aws_security_group.ecs_tasks.id

  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"

  description = "Allow ECS tasks to access required AWS services and APIs"
}

resource "aws_vpc_security_group_ingress_rule" "rds_from_ecs" {
  security_group_id = "sg-0ce81ef522853952c"

  referenced_security_group_id = aws_security_group.ecs_tasks.id

  ip_protocol = "tcp"
  from_port   = 5432
  to_port     = 5432

  description = "Allow PostgreSQL connections from OpenDataLake ECS tasks"
}