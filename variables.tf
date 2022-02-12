variable "instance_name" {
  description = "Value of the Name tag for the EC2 instance"
  type        = string
  default     = "ExampleAppServerInstance"
}

variable "bucket_name" {
  description = "Value of the bucket name for storing state on s3"
  type        = string
  default     = "terraform_state_bucket"
}
