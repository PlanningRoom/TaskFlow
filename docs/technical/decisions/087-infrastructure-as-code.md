# Decision 087: Infrastructure as Code

**Status:** Decided

**Category:** Ops & Observability

**Question:** How is AWS infrastructure provisioned and managed?

**Options considered:**
- AWS CloudFormation
- Terraform
- AWS CDK
- Pulumi
- Manual console configuration

**Decision:** AWS CloudFormation. All AWS resources are defined as CloudFormation templates in `infra/cloudformation/` and deployed via GitHub Actions (Decision 071).

Resources managed via CloudFormation:

| Stack | Resources |
|---|---|
| `network` | VPC, public subnet, internet gateway, route table, security group |
| `compute` | EC2 `t4g.small` instance, Elastic IP, IAM role + instance profile, user-data script installing Docker |
| `storage` | S3 bucket for backups (with lifecycle rule), S3 bucket for source maps |
| `container-registry` | ECR repositories (`taskflow/api`, `taskflow/web`) with lifecycle policies |
| `parameters` | SSM Parameter Store SecureString parameters (values set out-of-band) |
| `monitoring` | CloudWatch log groups, metric filters, alarms, SNS topic |
| `dns` | Route 53 hosted zone + A record → EC2 Elastic IP |
| `email` | SES verified domain identity, DKIM records |
| `iam` | OIDC provider for GitHub Actions, deploy role |

Deployment: `aws cloudformation deploy --template-file ... --stack-name ... --capabilities CAPABILITY_NAMED_IAM`.

**Rationale:** User constraint. CloudFormation is AWS-native — no third-party state backend to manage, no drift-detection race conditions with Terraform state files, integrates naturally with GitHub Actions' AWS tooling. Trade-off: more verbose than CDK/Terraform for the same resource graph; acceptable for a small, stable topology.
