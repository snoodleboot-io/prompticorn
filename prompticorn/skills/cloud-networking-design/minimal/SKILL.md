# Cloud Networking Design (Minimal)

## Purpose
Lay out VPCs, subnets, routing, and private connectivity so traffic reaches only what it should — without paying a fortune to cross an availability-zone boundary.

## Core Techniques

### 1. Size the VPC CIDR Once, Generously
Pick a private range (RFC 1918) large enough to never renumber, and carve non-overlapping blocks per region and account.
```
VPC       10.20.0.0/16          # one region, ~65k addresses
 ├ public  10.20.0.0/20  (AZ-a)  10.20.16.0/20 (AZ-b)   # has route to IGW
 └ private 10.20.64.0/20 (AZ-a)  10.20.80.0/20 (AZ-b)   # no direct inbound
```
Overlapping CIDRs are the one mistake you cannot fix later without renumbering — peering and VPNs both refuse to route between overlapping ranges.

### 2. Split Public and Private by Route Table, Not by Name
A subnet is "public" only because its route table sends `0.0.0.0/0` to an internet gateway. Private subnets route egress through a NAT gateway; nothing outside can initiate a connection inward.
```
public  RT:  0.0.0.0/0 -> igw      # load balancers, bastions only
private RT:  0.0.0.0/0 -> nat      # app + data tiers live here
```
Put every stateful and application workload in private subnets. Expose them through a load balancer in the public tier.

### 3. Layer Security Groups Over NACLs
- **Security groups** — stateful, attached to instances/ENIs, allow-only. Your primary control. Reference other groups by id (`app-sg` allows `lb-sg`), not by IP.
- **NACLs** — stateless, subnet-wide, allow *and* deny. Use sparingly for coarse blocks; they force you to open ephemeral return ports manually.

### 4. Choose the Right Cross-Network Path
| Need | Use |
|---|---|
| Two VPCs talk, few relationships | VPC peering (non-transitive) |
| Many VPCs, hub topology | Transit gateway / Cloud Router |
| Consume one service privately | PrivateLink / Private Service Connect |
| Reach a managed service, no internet | VPC/Gateway endpoint |
Peering does not transit: A–B and B–C never gives A–C. Reach for a transit gateway before the peering mesh gets past a handful of VPCs.

### 5. Keep Managed-Service Traffic Off the Internet
Route object storage, secrets, and managed databases through private endpoints. This keeps data on the provider backbone, removes the NAT hop, and often avoids NAT/egress charges for that traffic entirely.

### 6. Design Around the Cross-AZ Cost Trap
Inter-AZ traffic is billed in most clouds, in both directions. A chatty service that lands its replicas across three AZs pays for every hop. Keep latency-sensitive, high-volume chatter zone-local (topology-aware routing), and spread across AZs for availability — accepting the cost deliberately, not by accident.

## Warning Signs
- Two VPCs (or a VPC and on-prem) with overlapping CIDR ranges
- Databases or app servers sitting in public subnets
- Security groups written with wide IP ranges instead of group references
- A NAT gateway on the hot path for traffic that could use a private endpoint
- A growing full mesh of peering connections instead of a transit hub
- Surprise egress/cross-AZ line items nobody can attribute
- `0.0.0.0/0` inbound on a security group for anything but a public load balancer
