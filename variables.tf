variable "region" {
  description = "Region for the EC2 instance"
  default     = "us-west-2"
  type        = string
}

variable "instance_type" {
  description = "Instance type for the EC2 instance"
  default     = "t2.micro"
  type        = string
}

variable "instance_name" {
  description = "Value of the Name tag for the EC2 instance"
  type        = string
  default     = "birbsbot"
}

variable "bucket_name" {
  description = "Value of the bucket name for storing state on s3"
  type        = string
  default     = "terraform-birbsbot-state"
}

variable "lock_table_name" {
  description = "Value of the dynamo table name for maintaining lock state source of truth"
  type        = string
  default     = "tf-up-and-run-locks"
}
