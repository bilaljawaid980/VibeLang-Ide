terraform {
  required_version = ">= 1.0.0"
}

resource "local_file" "devops" {
  filename = "devops.txt"
  content  = "Terraform Configured Successfully"
}
