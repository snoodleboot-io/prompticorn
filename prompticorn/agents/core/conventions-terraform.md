<!-- path: prompticorn/prompts/agents/core/core-conventions-terraform.md -->
# Core Conventions Terraform

Language:             {{ language }} e.g., Terraform 1.6+
Provider:                        e.g., AWS, Azure, GCP
State:                     e.g., S3, Azure Blob, GCS

### Naming Conventions

Files:              snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase (for modules)
Functions:          snake_case
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Terraform-Specific Rules

### Infrastructure as Code
- Use Terraform for all infrastructure
- Use modules to organize code
- Never manually modify resources managed by Terraform

### State Management
- Use remote state (S3, Azure Blob, GCS)
- Enable state locking
- Never commit state files to version control

### Code Organization
- Use modules for reusable components
- Separate environments (dev, staging, prod)
- Use workspaces or directory structure

### Testing

#### Coverage Targets
Line:           {{ coverage_targets.get('line', '') }}          e.g., 80%
Branch:         {{ coverage_targets.get('branch', '') }}        e.g., 70%
Path:           {{ coverage_targets.get('path', '') }}           e.g., 60%

#### Test Types

##### Plan Review
- Always review terraform plan before apply
- Use `terraform plan` output to verify changes

##### Static Analysis
- Use terraform validate
- Use tflint for linting
- Use checkov for security scanning

##### Policy as Code
- Use Sentinel (Terraform Cloud/Enterprise)
- Use OPA/Conftest for open-source policy
- Test terraform plans against policies

##### Modules Testing
- Use terraform test (0.15+)
- Test modules in isolation
- Use examples for validation

#### Framework & Tools
Validation:        e.g., terraform validate
Linting:       {{ linter }}           e.g., tflint, checkov
Policy:                 e.g., Sentinel, Conftest, OPA

#### Scaffolding

```bash
# Validate and plan
terraform validate
terraform plan -out=tfplan

# Linting
tflint
checkov -d .

# Policy testing
conftest test tfplan -p policy.rego

# Module testing
terraform test

# Format
terraform fmt -recursive
```

##### CI Integration
```yaml
# GitHub Actions
- name: Terraform
  uses: hashicorp/terraform-github-actions@v1.0.0
  with:
    tf_actions_version: 1.6.0
```

##### Directory Structure
```
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── staging/
│   └── prod/
├── modules/
│   ├── vpc/
│   ├── ec2/
│   └── rds/
└── tests/
    └── modules/
```
