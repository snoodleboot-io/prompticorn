# Core Conventions HCL

Language: HCL (Terraform, Packer)
Framework: Terraform 1.x+
Style: 2-space indentation, lowercase identifiers

## Resource Naming

Resources: snake_case
- data.aws_ami.ubuntu
- resource.aws_instance.web_server

Variables: snake_case
- var.instance_count
- var.environment

Outputs: snake_case
- output.instance_ip

Local values: snake_case
- local.common_tags

## Structure

```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 4.0" }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "environment" {
  type        = string
  description = "Environment name"
  default     = "dev"
}

# Locals
locals {
  common_tags = {
    Environment = var.environment
    Managed     = "Terraform"
  }
}

# Resources
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"
  
  tags = merge(
    local.common_tags,
    { Name = "web-server" }
  )
}

# Outputs
output "instance_id" {
  value       = aws_instance.web.id
  description = "Instance ID"
}
```

## Best Practices
- Use variables for configuration
- Use locals for computed values
- Always tag resources
- Use data sources instead of hardcoding
- Validate inputs with custom validations
- Use remote state with locking

## Error Handling
- Use -target sparingly (only debugging)
- Always use terraform plan before apply
- Use workspaces for multiple environments
- Version provider constraints strictly
