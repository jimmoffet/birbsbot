terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 1.1.0"
  # to destroy the s3 backend resource using terraform destroy
  # we need to migrate back to storing state locally with these steps
  # 1. comment out backend statement
  # 2. terraform init -migrate-state
  # 3. terraform destroy
  backend "s3" {
    bucket         = "terraform-birbsbot-state"
    key            = "state/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "tf-up-and-run-locks"
    encrypt        = true
  }
}

provider "aws" {
  profile = "default"
  region  = var.region
}

resource "aws_ecr_repository" "birbsbot_ecr_repo" {
  name = "birbsbot-ecr-repo" # Naming my repository
}

# resource "aws_instance" "app_server" {
#   ami           = "ami-08d70e59c07c61a3a"
#   instance_type = var.instance_type

#   tags = {
#     Name = var.instance_name
#   }
# }

#1 -this will create a S3 bucket in AWS
resource "aws_s3_bucket" "terraform_state_s3" {
  # make sure you give unique bucket name
  bucket        = var.bucket_name
  force_destroy = true
  # Enable versioning to see full revision history of our state files
  versioning {
    enabled = true
  }

  # Enable server-side encryption by default
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# 2 - this Creates Dynamo Table
resource "aws_dynamodb_table" "terraform_locks" {
  # make sure you give table bucket name
  # can we use for multiple projects?
  name         = var.lock_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}


