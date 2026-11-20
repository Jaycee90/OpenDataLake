## STEP 5: Create an RDS Subnet Group and Security Group ##
# This configuration creates two AWS resources:
# 1. An RDS subnet group that defines which subnets the RDS instance can use.
# 2. A security group that allows inbound traffic to the RDS instance on port 5432 (PostgreSQL).
# what is subnet group? A subnet group is a collection of subnets that you can designate for your RDS DB instances in a VPC.
# When you create a DB instance in a VPC, you must specify a DB subnet group.
# The DB subnet group defines which subnets and IP ranges the DB instance can use.
resource "aws_db_subnet_group" "opendatalake" {
  name = "opendatalake-db-subnets"

  subnet_ids = [
    "subnet-0603fe9566d5b77a3",
    "subnet-0aae20ea736599651"
  ]

  tags = {
    Name    = "opendatalake-db-subnets"
    Project = "OpenDataLake"
  }
}

resource "aws_security_group" "rds" {
  name        = "opendatalake-rds-sg"
  description = "PostgreSQL access for OpenDataLake"
  vpc_id      = "vpc-033bee7eade244eb6"

  tags = {
    Name    = "opendatalake-rds-sg"
    Project = "OpenDataLake"
  }
}
