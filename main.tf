terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 1.1.0"
  backend "s3" {
            bucket = "terraformstatebirbsbot"
            key    = "terraform/state"
            region = "us-west-2"
        }
}

provider "aws" {
  profile = "default"
  region  = "us-west-2"
}

resource "aws_instance" "app_server" {
  ami           = "ami-08d70e59c07c61a3a"
  instance_type = "t2.micro"

  tags = {
    Name = var.instance_name
  }
}

resource "aws_s3_bucket" "s3Bucket" {
     bucket = var.bucket_name
     acl       = "public-read"

     policy  = <<EOF
    {
        "id" : "MakePublic",
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": "s3:ListBucket",
        "Resource": "arn:aws:s3:::mybucket"
        },
        {
        "Effect": "Allow",
        "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
        "Resource": "arn:aws:s3:::terraformstatebirbsbot/terraform/state"
        }
    ]
    }
    EOF
    website {
       index_document = "index.html"
   }
}

data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "terraformstatebirbsbot"
    key    = "network/terraform.tfstate"
    region = "us-west-2"
  }
}
