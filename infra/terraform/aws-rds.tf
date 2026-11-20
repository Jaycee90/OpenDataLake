## STEP 6: Create an RDS PostgreSQL Instance ##
# This configuration creates an AWS RDS PostgreSQL instance for the OpenDataLake project.
# which will be used as the data warehouse for storing and analyzing raw event data.
# PostgreSQL data warehouse
resource "aws_db_instance" "opendatalake" {
  identifier = "opendatalake-postgres"

  engine         = "postgres"
  engine_version = "16.15"
  instance_class = "db.t4g.micro"

  allocated_storage = 20
  storage_type      = "gp3"
  storage_encrypted = true
  kms_key_id        = "arn:aws:kms:us-east-1:373058354498:key/bab51aa3-87f5-4b7a-b270-89b66bb20c90"

  db_name  = "opendatalake"
  username = "opendatalake_admin"

  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.opendatalake.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = false
  multi_az            = false

  backup_retention_period = 0
  deletion_protection     = false
  skip_final_snapshot     = true

  auto_minor_version_upgrade = false

  tags = {
    Name        = "opendatalake-postgres"
    Project     = "OpenDataLake"
    Environment = "dev"
  }
}
