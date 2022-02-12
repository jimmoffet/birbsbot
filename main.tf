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
            key    = "birbsbot_terraform_state"
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
    "version" : "2012-10-17",
    "statement" : [
        {
            "action" : [
                "s3:GetObject"
            ],
            "effect" : "Allow",
            "resource" : "arn:aws:s3:::terraformstatebirbsbot/*",
            "principal" : "*"
        }
        ]
    }
    EOF
    website {
       index_document = "index.html"
   }
}
