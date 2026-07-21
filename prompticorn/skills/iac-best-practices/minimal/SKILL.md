# IaC Best Practices (Minimal)

## Purpose
Write infrastructure code that a second engineer can change safely on a Friday — versioned, reviewed, and with a plan you read before you apply.

## Core Techniques

### 1. Remote State With Locking — Set This Up First
```hcl
terraform {
  backend "s3" {
    bucket         = "acme-tfstate-prod"
    key            = "network/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-locks"   # the lock; without it, concurrent applies corrupt state
    encrypt        = true
  }
}
```
Local state means exactly one person can ever apply, and CI cannot. Worse, two simultaneous applies against an unlocked backend interleave writes and produce a state file that describes neither reality — the recovery is hand-editing JSON against a live account. Do this on day one, before the first resource.

State also contains secrets in plaintext (RDS passwords, generated keys). Encrypt the bucket, enable versioning, and restrict read access as tightly as production credentials.

### 2. Run `terraform plan` in CI on Every Pull Request
This is the actual safety mechanism, not the code review.
```bash
terraform init -backend=false
terraform validate
terraform plan -lock-timeout=5m -out=tfplan
terraform show -no-color tfplan > plan.txt   # post as a PR comment
```
The reviewer approves a diff of real resources — "3 to add, 0 to change, 1 to destroy" — not an intention. Apply from the saved plan file so what merges is what runs. A `destroy` line on a stateful resource should require a second approval; `terraform plan` output is the only place that becomes visible before it happens.

### 3. Never Modify Infrastructure by Hand
A console change is invisible to the next `plan` author until it shows as an unexplained diff, and the next apply silently reverts it. Grant humans read-only in production and route change through the pipeline. See `infrastructure-drift-detection` for catching what slips through.

### 4. Compose Modules — But Not Too Early
| Situation | Do |
|---|---|
| One caller | Plain resources in the root module |
| Two callers, diverging | Still copy — abstraction is guesswork |
| Three callers, stable shape | Extract a module |

A module written for one use site encodes one team's assumptions as an interface. The tell is a module whose variables are a passthrough of every resource argument — that is a worse copy-paste. Pin module sources by version, never a branch:
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"   # a moving ref makes plans non-reproducible
}
```

### 5. Separate State by Blast Radius
One state file for the whole estate means a typo in a tag can queue a database replacement. Split by lifecycle — network, data, apps — and per environment. Read across boundaries with data sources rather than merging states.

### 6. Pin Provider Versions
```hcl
terraform {
  required_version = "~> 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }
}
```
Commit `.terraform.lock.hcl`. Without it, two engineers get different provider builds and different plans from identical code.

## Warning Signs

- State stored locally, or in a bucket with no lock table and no versioning
- Applies run from laptops instead of CI
- Anyone has write access to the production console
- Module sources pointed at `main` instead of a version tag
- A single state file spanning every environment
- `.terraform.lock.hcl` gitignored
- Plans nobody reads because they are 400 lines of noise
- Secrets committed as literals in `.tf` files rather than referenced from a secret store
