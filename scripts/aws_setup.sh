#!/usr/bin/env bash
# =============================================================================
# Backlog Synthesizer — One-time AWS resource provisioning
#
# Run this ONCE to create all AWS infrastructure. After this, GitHub Actions
# handles all deployments automatically on push to main.
#
# Prerequisites:
#   - AWS CLI v2 installed and configured:  aws configure
#   - Sufficient IAM permissions (see below)
#   - python3 available (for JSON processing)
#
# Required IAM permissions on the caller:
#   ec2:*, ecs:*, ecr:*, elasticloadbalancing:*, iam:*, logs:*,
#   elasticfilesystem:*, secretsmanager:*, sts:GetCallerIdentity
#
# Usage:
#   chmod +x scripts/aws_setup.sh
#   ./scripts/aws_setup.sh
#
# What it creates:
#   - ECR repository (image registry)
#   - ECS cluster (Fargate — serverless container runtime)
#   - Application Load Balancer with two listeners:
#       port 80   → production service
#       port 8080 → staging service
#   - EFS file system with two access points (prod + staging)
#   - Secrets Manager secrets for API keys
#   - IAM roles for ECS task execution and the application
#   - ECS task definitions + services (staging + prod, min=0 replicas)
#   - CloudWatch log groups
#   - IAM user + access key for GitHub Actions
#   - Prints all GitHub secrets you need to set
# =============================================================================

set -euo pipefail

# ── Configuration — edit these before running ─────────────────────────────────
REGION="us-east-1"
CLUSTER_NAME="backlog-synthesizer"
ECR_REPO_NAME="backlog-synthesizer"
ALB_NAME="backlog-synthesizer"
EFS_NAME="backlog-synthesizer"
SECRETS_PREFIX="/backlog-synthesizer"
GITHUB_REPO="your-org/backlog-synthesizer"   # ← update to your GitHub repo

# ECS service / task definition names
SERVICE_PROD="backlog-synthesizer"
SERVICE_STAGING="backlog-synthesizer-staging"
TASK_FAMILY_PROD="backlog-synthesizer"
TASK_FAMILY_STAGING="backlog-synthesizer-staging"

# Container config
CONTAINER_PORT=8502
CONTAINER_NAME="backlog-synthesizer"

# ── Colours ───────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --region "$REGION")
info "Using AWS account: $ACCOUNT_ID  region: $REGION"

# ── 1. ECR repository ─────────────────────────────────────────────────────────
info "Creating ECR repository: $ECR_REPO_NAME"
aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$REGION" \
  --output none 2>/dev/null || \
aws ecr create-repository \
  --repository-name "$ECR_REPO_NAME" \
  --image-scanning-configuration scanOnPush=true \
  --region "$REGION" \
  --output none

# Enable lifecycle policy to auto-expire untagged images after 14 days
aws ecr put-lifecycle-policy \
  --repository-name "$ECR_REPO_NAME" \
  --region "$REGION" \
  --lifecycle-policy-text '{
    "rules": [{
      "rulePriority": 1,
      "description": "Expire untagged images after 14 days",
      "selection": {"tagStatus": "untagged", "countType": "sinceImagePushed", "countUnit": "days", "countNumber": 14},
      "action": {"type": "expire"}
    }]
  }' \
  --output none

ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
ECR_IMAGE="${ECR_REGISTRY}/${ECR_REPO_NAME}"
ok "ECR repository: $ECR_IMAGE"

# ── 2. ECS cluster ────────────────────────────────────────────────────────────
info "Creating ECS cluster: $CLUSTER_NAME"
aws ecs create-cluster \
  --cluster-name "$CLUSTER_NAME" \
  --capacity-providers FARGATE FARGATE_SPOT \
  --region "$REGION" \
  --output none 2>/dev/null || true
ok "ECS cluster: $CLUSTER_NAME"

# ── 3. CloudWatch log groups ──────────────────────────────────────────────────
info "Creating CloudWatch log groups"
for LG in "/ecs/${SERVICE_PROD}" "/ecs/${SERVICE_STAGING}"; do
  aws logs create-log-group --log-group-name "$LG" --region "$REGION" \
    --output none 2>/dev/null || true
  aws logs put-retention-policy \
    --log-group-name "$LG" --retention-in-days 30 \
    --region "$REGION" --output none
done
ok "Log groups ready (30-day retention)"

# ── 4. Networking — look up default VPC and subnets ───────────────────────────
info "Discovering default VPC and subnets"
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=isDefault,Values=true" \
  --query "Vpcs[0].VpcId" --output text --region "$REGION")

if [ "$VPC_ID" = "None" ] || [ -z "$VPC_ID" ]; then
  echo "ERROR: No default VPC found in $REGION. Create one with: aws ec2 create-default-vpc --region $REGION" >&2
  exit 1
fi
ok "VPC: $VPC_ID"

# Collect all subnets in the default VPC
SUBNETS=$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query "Subnets[*].SubnetId" \
  --output text --region "$REGION")
SUBNET_LIST=$(echo "$SUBNETS" | tr '\t' ',')
SUBNET_ARR=($(echo "$SUBNETS"))  # bash array for ECS/EFS use
ok "Subnets: ${SUBNET_LIST}"

# ── 5. Security groups ────────────────────────────────────────────────────────
info "Creating security groups"

# ALB: inbound 80 (prod) + 8080 (staging) from internet; outbound all
ALB_SG_ID=$(aws ec2 create-security-group \
  --group-name "sg-${ALB_NAME}-alb" \
  --description "ALB for Backlog Synthesizer (prod:80, staging:8080)" \
  --vpc-id "$VPC_ID" \
  --region "$REGION" \
  --query GroupId --output text 2>/dev/null) || \
ALB_SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=sg-${ALB_NAME}-alb" "Name=vpc-id,Values=$VPC_ID" \
  --query "SecurityGroups[0].GroupId" --output text --region "$REGION")

for PORT in 80 8080; do
  aws ec2 authorize-security-group-ingress \
    --group-id "$ALB_SG_ID" --protocol tcp --port "$PORT" --cidr 0.0.0.0/0 \
    --region "$REGION" --output none 2>/dev/null || true
done
ok "ALB security group: $ALB_SG_ID"

# ECS tasks: inbound ${CONTAINER_PORT} from ALB SG only; outbound all (ECR, Secrets, EFS)
ECS_SG_ID=$(aws ec2 create-security-group \
  --group-name "sg-${CLUSTER_NAME}-ecs" \
  --description "ECS tasks for Backlog Synthesizer" \
  --vpc-id "$VPC_ID" \
  --region "$REGION" \
  --query GroupId --output text 2>/dev/null) || \
ECS_SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=sg-${CLUSTER_NAME}-ecs" "Name=vpc-id,Values=$VPC_ID" \
  --query "SecurityGroups[0].GroupId" --output text --region "$REGION")

aws ec2 authorize-security-group-ingress \
  --group-id "$ECS_SG_ID" \
  --protocol tcp --port "$CONTAINER_PORT" \
  --source-group "$ALB_SG_ID" \
  --region "$REGION" --output none 2>/dev/null || true
ok "ECS security group: $ECS_SG_ID"

# EFS: inbound NFS (2049) from ECS SG only
EFS_SG_ID=$(aws ec2 create-security-group \
  --group-name "sg-${EFS_NAME}-efs" \
  --description "EFS mount targets for Backlog Synthesizer" \
  --vpc-id "$VPC_ID" \
  --region "$REGION" \
  --query GroupId --output text 2>/dev/null) || \
EFS_SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=sg-${EFS_NAME}-efs" "Name=vpc-id,Values=$VPC_ID" \
  --query "SecurityGroups[0].GroupId" --output text --region "$REGION")

aws ec2 authorize-security-group-ingress \
  --group-id "$EFS_SG_ID" \
  --protocol tcp --port 2049 \
  --source-group "$ECS_SG_ID" \
  --region "$REGION" --output none 2>/dev/null || true
ok "EFS security group: $EFS_SG_ID"

# ── 6. IAM roles ──────────────────────────────────────────────────────────────
info "Creating IAM roles"

# Execution role: used by the ECS agent to pull images + push logs + fetch secrets
EXEC_ROLE_NAME="role-${CLUSTER_NAME}-execution"
aws iam create-role \
  --role-name "$EXEC_ROLE_NAME" \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]
  }' \
  --output none 2>/dev/null || true
aws iam attach-role-policy \
  --role-name "$EXEC_ROLE_NAME" \
  --policy-arn "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" \
  --output none 2>/dev/null || true

# Allow the execution role to read secrets by prefix
EXEC_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${EXEC_ROLE_NAME}"
aws iam put-role-policy \
  --role-name "$EXEC_ROLE_NAME" \
  --policy-name "SecretsManagerRead" \
  --policy-document "{
    \"Version\":\"2012-10-17\",
    \"Statement\":[{
      \"Effect\":\"Allow\",
      \"Action\":[\"secretsmanager:GetSecretValue\"],
      \"Resource\":\"arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:${SECRETS_PREFIX}/*\"
    }]
  }" \
  --output none
ok "Execution role: $EXEC_ROLE_ARN"

# Task role: used by the application container (EFS read/write access)
TASK_ROLE_NAME="role-${CLUSTER_NAME}-task"
aws iam create-role \
  --role-name "$TASK_ROLE_NAME" \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]
  }' \
  --output none 2>/dev/null || true
aws iam attach-role-policy \
  --role-name "$TASK_ROLE_NAME" \
  --policy-arn "arn:aws:iam::aws:policy/AmazonElasticFileSystemClientReadWriteAccess" \
  --output none 2>/dev/null || true
TASK_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${TASK_ROLE_NAME}"
ok "Task role: $TASK_ROLE_ARN"

# ── 7. Secrets Manager ────────────────────────────────────────────────────────
warn "Enter your API keys for Secrets Manager storage."
warn "These are injected as environment variables into the container at runtime."
echo ""

read -rsp "ANTHROPIC_API_KEY (required): " ANTHROPIC_KEY; echo
read -rsp "GOOGLE_API_KEY (optional, press Enter to skip): " GOOGLE_KEY; echo
read -rsp "JIRA_API_TOKEN (optional, press Enter to skip): " JIRA_TOKEN; echo

_put_secret() {
  local name="$1" value="$2"
  [ -z "$value" ] && return 0
  aws secretsmanager describe-secret --secret-id "$name" --region "$REGION" \
    --output none 2>/dev/null && \
  aws secretsmanager put-secret-value --secret-id "$name" --secret-string "$value" \
    --region "$REGION" --output none || \
  aws secretsmanager create-secret --name "$name" \
    --description "Backlog Synthesizer API key" \
    --secret-string "$value" \
    --region "$REGION" --output none
}

_put_secret "${SECRETS_PREFIX}/ANTHROPIC_API_KEY" "$ANTHROPIC_KEY"
_put_secret "${SECRETS_PREFIX}/GOOGLE_API_KEY"    "$GOOGLE_KEY"
_put_secret "${SECRETS_PREFIX}/JIRA_API_TOKEN"    "$JIRA_TOKEN"
ok "Secrets stored in Secrets Manager under $SECRETS_PREFIX/"

ANTHROPIC_SECRET_ARN="arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:${SECRETS_PREFIX}/ANTHROPIC_API_KEY"

# ── 8. EFS file system ────────────────────────────────────────────────────────
info "Creating EFS file system: $EFS_NAME"
EFS_ID=$(aws efs describe-file-systems \
  --query "FileSystems[?Name=='${EFS_NAME}'].FileSystemId" \
  --output text --region "$REGION")

if [ -z "$EFS_ID" ] || [ "$EFS_ID" = "None" ]; then
  EFS_ID=$(aws efs create-file-system \
    --performance-mode generalPurpose \
    --throughput-mode bursting \
    --encrypted \
    --tags "Key=Name,Value=${EFS_NAME}" \
    --region "$REGION" \
    --query FileSystemId --output text)
fi

# Wait for EFS to become available
for _i in $(seq 1 12); do
  EFS_STATE=$(aws efs describe-file-systems --file-system-id "$EFS_ID" \
    --query "FileSystems[0].LifeCycleState" --output text --region "$REGION")
  [ "$EFS_STATE" = "available" ] && break
  echo "  EFS state: $EFS_STATE — waiting…"; sleep 5
done
ok "EFS: $EFS_ID"

# Create mount targets in each subnet (idempotent — skip if already exists)
for SUBNET in "${SUBNET_ARR[@]}"; do
  AZ=$(aws ec2 describe-subnets --subnet-ids "$SUBNET" \
    --query "Subnets[0].AvailabilityZone" --output text --region "$REGION")
  EXISTS=$(aws efs describe-mount-targets --file-system-id "$EFS_ID" \
    --query "MountTargets[?SubnetId=='$SUBNET'].MountTargetId" \
    --output text --region "$REGION")
  if [ -z "$EXISTS" ] || [ "$EXISTS" = "None" ]; then
    aws efs create-mount-target \
      --file-system-id "$EFS_ID" \
      --subnet-id "$SUBNET" \
      --security-groups "$EFS_SG_ID" \
      --region "$REGION" --output none
    echo "  Mount target created in $AZ"
  fi
done

# Separate access points for prod and staging so their data never collides
_make_ap() {
  local label="$1" path="$2"
  EXISTING=$(aws efs describe-access-points \
    --file-system-id "$EFS_ID" \
    --query "AccessPoints[?Tags[?Key=='Name' && Value=='${EFS_NAME}-${label}']].AccessPointId" \
    --output text --region "$REGION")
  if [ -z "$EXISTING" ] || [ "$EXISTING" = "None" ]; then
    aws efs create-access-point \
      --file-system-id "$EFS_ID" \
      --posix-user "Uid=1000,Gid=1000" \
      --root-directory "Path=${path},CreationInfo={OwnerUid=1000,OwnerGid=1000,Permissions=755}" \
      --tags "Key=Name,Value=${EFS_NAME}-${label}" \
      --region "$REGION" \
      --query AccessPointId --output text
  else
    echo "$EXISTING"
  fi
}

EFS_AP_PROD=$(    _make_ap "prod"    "/prod")
EFS_AP_STAGING=$( _make_ap "staging" "/staging")
ok "EFS access points — prod: $EFS_AP_PROD  staging: $EFS_AP_STAGING"

# ── 9. Application Load Balancer ──────────────────────────────────────────────
info "Creating Application Load Balancer: $ALB_NAME"
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --names "$ALB_NAME" \
  --query "LoadBalancers[0].LoadBalancerArn" \
  --output text --region "$REGION" 2>/dev/null) || ALB_ARN=""

if [ -z "$ALB_ARN" ] || [ "$ALB_ARN" = "None" ]; then
  ALB_ARN=$(aws elbv2 create-load-balancer \
    --name "$ALB_NAME" \
    --subnets "${SUBNET_ARR[@]}" \
    --security-groups "$ALB_SG_ID" \
    --scheme internet-facing \
    --type application \
    --region "$REGION" \
    --query "LoadBalancers[0].LoadBalancerArn" --output text)
fi

ALB_DNS=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns "$ALB_ARN" \
  --query "LoadBalancers[0].DNSName" \
  --output text --region "$REGION")
ok "ALB: http://$ALB_DNS"

# Target groups — health-check on Streamlit's built-in health endpoint
_make_tg() {
  local name="$1"
  EXISTING=$(aws elbv2 describe-target-groups \
    --names "$name" \
    --query "TargetGroups[0].TargetGroupArn" \
    --output text --region "$REGION" 2>/dev/null) || EXISTING=""
  if [ -z "$EXISTING" ] || [ "$EXISTING" = "None" ]; then
    aws elbv2 create-target-group \
      --name "$name" \
      --protocol HTTP \
      --port "$CONTAINER_PORT" \
      --vpc-id "$VPC_ID" \
      --target-type ip \
      --health-check-path "/_stcore/health" \
      --health-check-interval-seconds 30 \
      --health-check-timeout-seconds 10 \
      --healthy-threshold-count 2 \
      --unhealthy-threshold-count 3 \
      --region "$REGION" \
      --query "TargetGroups[0].TargetGroupArn" --output text
  else
    echo "$EXISTING"
  fi
}

TG_ARN_PROD=$(    _make_tg "${ALB_NAME}-prod")
TG_ARN_STAGING=$( _make_tg "${ALB_NAME}-staging")
ok "Target groups — prod: $TG_ARN_PROD"
ok "               staging: $TG_ARN_STAGING"

# ALB listeners
_make_listener() {
  local port="$1" tg_arn="$2"
  EXISTING=$(aws elbv2 describe-listeners \
    --load-balancer-arn "$ALB_ARN" \
    --query "Listeners[?Port==\`${port}\`].ListenerArn" \
    --output text --region "$REGION" 2>/dev/null) || EXISTING=""
  if [ -z "$EXISTING" ] || [ "$EXISTING" = "None" ]; then
    aws elbv2 create-listener \
      --load-balancer-arn "$ALB_ARN" \
      --protocol HTTP \
      --port "$port" \
      --default-actions "Type=forward,TargetGroupArn=${tg_arn}" \
      --region "$REGION" --output none
  fi
}
_make_listener 80   "$TG_ARN_PROD"
_make_listener 8080 "$TG_ARN_STAGING"
ok "Listeners — port 80 → prod, port 8080 → staging"

# ── 10. ECS task definitions ──────────────────────────────────────────────────
info "Registering ECS task definitions"

_register_task_def() {
  local family="$1"
  local logs_dir="$2"
  local outputs_dir="$3"
  local efs_ap_id="$4"

  python3 - <<PYEOF
import json, subprocess, sys

td = {
  "family": "${family}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "${EXEC_ROLE_ARN}",
  "taskRoleArn": "${TASK_ROLE_ARN}",
  "containerDefinitions": [{
    "name": "${CONTAINER_NAME}",
    "image": "${ECR_IMAGE}:latest",
    "essential": True,
    "portMappings": [{"containerPort": ${CONTAINER_PORT}, "protocol": "tcp"}],
    "environment": [
      {"name": "AUTH_DISABLED",          "value": "0"},
      {"name": "OTEL_ENABLED",           "value": "0"},
      {"name": "LOGS_DIR",               "value": "${logs_dir}"},
      {"name": "OUTPUTS_DIR",            "value": "${outputs_dir}"},
      {"name": "SHUTDOWN_FLAG_PATH",     "value": "/tmp/.shutdown_requested"},
      {"name": "SHUTDOWN_GRACE_SECONDS", "value": "75"},
    ],
    "secrets": [
      {"name": "ANTHROPIC_API_KEY",
       "valueFrom": "${ANTHROPIC_SECRET_ARN}"}
    ],
    "mountPoints": [{
      "sourceVolume": "backlog-data",
      "containerPath": "/app/backlog-data",
      "readOnly": False
    }],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group":         "/ecs/${family}",
        "awslogs-region":        "${REGION}",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }],
  "volumes": [{
    "name": "backlog-data",
    "efsVolumeConfiguration": {
      "fileSystemId": "${EFS_ID}",
      "transitEncryption": "ENABLED",
      "authorizationConfig": {
        "accessPointId": "${efs_ap_id}",
        "iam": "ENABLED"
      }
    }
  }]
}

result = subprocess.run(
  ["aws", "ecs", "register-task-definition",
   "--cli-input-json", json.dumps(td),
   "--region", "${REGION}",
   "--query", "taskDefinition.taskDefinitionArn",
   "--output", "text"],
  capture_output=True, text=True, check=True
)
print(result.stdout.strip())
PYEOF
}

TD_ARN_PROD=$(    _register_task_def "$TASK_FAMILY_PROD"    "/app/backlog-data/logs"         "/app/backlog-data/outputs"         "$EFS_AP_PROD")
TD_ARN_STAGING=$( _register_task_def "$TASK_FAMILY_STAGING" "/app/backlog-data/staging/logs" "/app/backlog-data/staging/outputs" "$EFS_AP_STAGING")
ok "Task definitions registered"
ok "  prod:    $TD_ARN_PROD"
ok "  staging: $TD_ARN_STAGING"

# ── 11. ECS services (staging + prod) ─────────────────────────────────────────
info "Creating ECS services"

# Subnets as a JSON list for --network-configuration
SUBNET_JSON=$(python3 -c "import json,sys; subs=sys.argv[1:]; print(json.dumps(subs))" "${SUBNET_ARR[@]}")

_make_service() {
  local service_name="$1"
  local td_arn="$2"
  local tg_arn="$3"
  local min_count="$4"

  EXISTING=$(aws ecs describe-services \
    --cluster "$CLUSTER_NAME" \
    --services "$service_name" \
    --query "services[?status=='ACTIVE'].serviceArn" \
    --output text --region "$REGION" 2>/dev/null) || EXISTING=""

  if [ -z "$EXISTING" ] || [ "$EXISTING" = "None" ]; then
    aws ecs create-service \
      --cluster "$CLUSTER_NAME" \
      --service-name "$service_name" \
      --task-definition "$td_arn" \
      --desired-count "$min_count" \
      --launch-type FARGATE \
      --network-configuration \
        "awsvpcConfiguration={subnets=${SUBNET_JSON},securityGroups=[\"${ECS_SG_ID}\"],assignPublicIp=ENABLED}" \
      --load-balancers \
        "targetGroupArn=${tg_arn},containerName=${CONTAINER_NAME},containerPort=${CONTAINER_PORT}" \
      --health-check-grace-period-seconds 120 \
      --region "$REGION" \
      --output none
    echo "  Created service: $service_name"
  else
    echo "  Service already exists: $service_name"
  fi
}

# Staging: min=0 (scales to zero when idle, no cost when unused)
# Prod:    min=1 (always one task ready)
_make_service "$SERVICE_STAGING" "$TD_ARN_STAGING" "$TG_ARN_STAGING" 0
_make_service "$SERVICE_PROD"    "$TD_ARN_PROD"    "$TG_ARN_PROD"    1
ok "ECS services created"

# ── 12. IAM user for GitHub Actions ───────────────────────────────────────────
info "Creating IAM user for GitHub Actions: ghactions-${CLUSTER_NAME}"
GH_USER="ghactions-${CLUSTER_NAME}"

aws iam create-user --user-name "$GH_USER" --output none 2>/dev/null || true

# Policy: ECR push + ECS deploy on this cluster
aws iam put-user-policy \
  --user-name "$GH_USER" \
  --policy-name "BacklogSynthesizerDeploy" \
  --policy-document "{
    \"Version\":\"2012-10-17\",
    \"Statement\":[
      {
        \"Sid\":\"ECRAuth\",
        \"Effect\":\"Allow\",
        \"Action\":[\"ecr:GetAuthorizationToken\"],
        \"Resource\":\"*\"
      },
      {
        \"Sid\":\"ECRPush\",
        \"Effect\":\"Allow\",
        \"Action\":[
          \"ecr:BatchCheckLayerAvailability\",\"ecr:GetDownloadUrlForLayer\",
          \"ecr:BatchGetImage\",\"ecr:InitiateLayerUpload\",\"ecr:UploadLayerPart\",
          \"ecr:CompleteLayerUpload\",\"ecr:PutImage\"
        ],
        \"Resource\":\"arn:aws:ecr:${REGION}:${ACCOUNT_ID}:repository/${ECR_REPO_NAME}\"
      },
      {
        \"Sid\":\"ECSReadTaskDef\",
        \"Effect\":\"Allow\",
        \"Action\":[\"ecs:DescribeTaskDefinition\"],
        \"Resource\":\"*\"
      },
      {
        \"Sid\":\"ECSRegisterTaskDef\",
        \"Effect\":\"Allow\",
        \"Action\":[\"ecs:RegisterTaskDefinition\"],
        \"Resource\":\"*\"
      },
      {
        \"Sid\":\"ECSUpdateService\",
        \"Effect\":\"Allow\",
        \"Action\":[\"ecs:UpdateService\",\"ecs:DescribeServices\"],
        \"Resource\":[
          \"arn:aws:ecs:${REGION}:${ACCOUNT_ID}:service/${CLUSTER_NAME}/${SERVICE_PROD}\",
          \"arn:aws:ecs:${REGION}:${ACCOUNT_ID}:service/${CLUSTER_NAME}/${SERVICE_STAGING}\"
        ]
      },
      {
        \"Sid\":\"ELBDescribe\",
        \"Effect\":\"Allow\",
        \"Action\":[\"elasticloadbalancing:DescribeLoadBalancers\"],
        \"Resource\":\"*\"
      },
      {
        \"Sid\":\"IAMPassRole\",
        \"Effect\":\"Allow\",
        \"Action\":\"iam:PassRole\",
        \"Resource\":[\"${EXEC_ROLE_ARN}\",\"${TASK_ROLE_ARN}\"]
      }
    ]
  }" \
  --output none

# Create access key (shown once — save it immediately)
ACCESS_KEY_JSON=$(aws iam create-access-key --user-name "$GH_USER" --output json)
GH_ACCESS_KEY_ID=$(     echo "$ACCESS_KEY_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['AccessKey']['AccessKeyId'])")
GH_SECRET_ACCESS_KEY=$( echo "$ACCESS_KEY_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['AccessKey']['SecretAccessKey'])")
ok "GitHub Actions IAM user created: $GH_USER"

# ── 13. Print GitHub Secrets ───────────────────────────────────────────────────
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complete! Add these secrets to your GitHub repo:    ${NC}"
echo -e "${GREEN}  $GITHUB_REPO → Settings → Secrets → Actions             ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Secret name               Value${NC}"
echo "──────────────────────────────────────────────────────────────"
echo "AWS_ACCESS_KEY_ID         ${GH_ACCESS_KEY_ID}"
echo "AWS_SECRET_ACCESS_KEY     ${GH_SECRET_ACCESS_KEY}"
echo "AWS_REGION                ${REGION}"
echo "AWS_ECR_REGISTRY          ${ECR_REGISTRY}"
echo "AWS_ECS_CLUSTER           ${CLUSTER_NAME}"
echo "AWS_ALB_NAME              ${ALB_NAME}"
echo "──────────────────────────────────────────────────────────────"
echo ""
echo -e "${YELLOW}Also create these GitHub Environments (repo Settings → Environments):${NC}"
echo "  aws-staging    — no protection rules"
echo "  aws-production — add Required Reviewers for the manual approval gate"
echo ""
echo -e "${GREEN}App URLs:${NC}"
echo "  Production:  http://$ALB_DNS          (port 80)"
echo "  Staging:     http://$ALB_DNS:8080     (port 8080)"
echo ""
echo -e "${GREEN}Next step: push a commit to main to trigger your first real deployment.${NC}"
echo ""
