# Cloud Provider Tradeoffs (Minimal)

## Purpose
Choose a primary cloud by comparing the primitives and managed services you will
actually use, weighting your team's existing skills and data gravity far above
any feature-count comparison.

## Core Techniques

### 1. Compare on What You'll Actually Run
Every major provider has comparable compute, object storage, block storage, a
managed relational database, a queue, and a load balancer. That commodity layer
is effectively a tie. Differentiation lives one tier up, in the managed services
and the ecosystem around them.

| Need | AWS | GCP | Azure |
|---|---|---|---|
| Object storage | S3 | Cloud Storage | Blob Storage |
| VMs | EC2 | Compute Engine | Virtual Machines |
| Managed Kubernetes | EKS | GKE | AKS |
| Serverless functions | Lambda | Cloud Functions / Run | Functions |
| Managed relational | RDS / Aurora | Cloud SQL / AlloyDB | Azure SQL / Flexible Server |
| Data warehouse | Redshift | BigQuery | Synapse / Fabric |

### 2. Weight Existing Footprint and Team Skill
The strongest predictor of success is what your team already operates. A team
fluent in AWS IAM and CloudFormation pays a real re-learning tax to move to
another cloud, no matter which is "better" on paper. Enterprise agreements — an
existing Microsoft relationship, committed spend already on the table — often
settle this before any technical comparison starts.

### 3. Follow the Data Gravity
Whichever cloud holds your large datasets is where compute wants to live. Egress
is billed and cross-cloud data movement is slow and expensive, so a data lake in
one cloud quietly pulls all its consumers into the same cloud. See
cloud-cost-optimization for the egress specifics.

### 4. Score the Managed Services That Carry Your Architecture
Pick the two or three services your design leans on hardest — warehouse, managed
Kubernetes, serverless, ML platform — and compare those concretely. BigQuery's
serverless query model differs sharply from Redshift's provisioned-cluster model;
GKE is widely regarded as the most mature managed Kubernetes. Those specifics
decide it. Use technical-decision-making for the weighted-matrix method.

### 5. Treat Lock-In as a Cost, Not a Veto
Deep use of a proprietary managed service (DynamoDB, BigQuery, Cosmos DB) buys
velocity and repays it as switching cost later. That is usually a good trade.
multi-cloud-strategy covers the rarer cases where avoiding it is worth the price.

## Warning Signs
- Choosing on a feature-comparison spreadsheet nobody will ever open again
- Ignoring the team's existing operational skill and tooling
- Compute in one cloud and the data lake in another, paying egress both ways
- "Cloud-agnostic from day one" with no requirement that actually demands it
- Assuming price-list parity — the pricing models differ enough that only your
  workload's shape reveals the real cost
- Letting a single flashy service pick the whole platform for unrelated workloads
