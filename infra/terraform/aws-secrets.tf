## STEP 12: Create a Secrets Manager Secret ##
# This configuration creates a secret in AWS Secrets Manager to securely store sensitive information, such as API keys or database credentials.
# Add the Ticketmaster secret to Terraform

# What this does
# - Creates a Secrets Manager resource to hold your Ticketmaster API key.
# - Gives it a descriptive name.
# - Tags it as part of your OpenDataLake project.
# - Does not store your actual API key in Terraform code or state.
# We'll add the secret value separately and configure ECS to inject it securely into the TICKETMASTER_API_KEY environment variable.
resource "aws_secretsmanager_secret" "ticketmaster_api_key" {
  name        = "opendatalake/ticketmaster/api-key"
  description = "Ticketmaster API key for the OpenDataLake ETL pipeline"

  tags = {
    Project = "OpenDataLake"
  }
}