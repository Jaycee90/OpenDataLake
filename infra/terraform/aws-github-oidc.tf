##  STEP 3: Configure GitHub OIDC for AWS ##
# This configuration creates three AWS resources:
# 1. An IAM OIDC identity provider for GitHub.
# 2. An IAM role that trusts only workflow runs from Jaycee90/OpenDataLake on main.
# 3. An IAM policy that grants the role permissions to authenticate and push images to your existing ECR repository.


# Establishes trust between AWS and GitHub Actions
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]
}

# Allows authorized GitHub workflows to assume an AWS role
resource "aws_iam_role" "github_actions_ecr" {
  name = "OpenDataLakeGitHubActionsECR"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
            "token.actions.githubusercontent.com:sub" = "repo:Jaycee90/OpenDataLake:ref:refs/heads/main"
          }
        }
      }
    ]
  })

  tags = {
    Project     = "OpenDataLake"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

# Grants permission to push Docker images to your ECR repository
resource "aws_iam_role_policy" "github_actions_ecr" {
  name = "OpenDataLakeECRPushPolicy"
  role = aws_iam_role.github_actions_ecr.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
          "ecr:BatchGetImage"
        ]
        Resource = aws_ecr_repository.opendatalake.arn
      }
    ]
  })
}
