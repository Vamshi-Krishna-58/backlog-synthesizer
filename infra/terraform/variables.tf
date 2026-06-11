# ── Azure credentials ─────────────────────────────────────────────────────────
variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "tenant_id" {
  description = "Azure Tenant ID"
  type        = string
}

variable "client_id" {
  description = "Service Principal Application (client) ID"
  type        = string
}

variable "client_secret" {
  description = "Service Principal client secret"
  type        = string
  sensitive   = true
}

# ── Infrastructure ────────────────────────────────────────────────────────────
variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-meridian-motors"
}

variable "acr_name" {
  description = "Azure Container Registry name (globally unique, alphanumeric)"
  type        = string
  default     = "meridianmotorsacr"
}

variable "acr_sku" {
  description = "ACR SKU: Basic | Standard | Premium"
  type        = string
  default     = "Basic"
}

variable "container_app_env_name" {
  description = "Container Apps environment name"
  type        = string
  default     = "cae-meridian-motors"
}

variable "app_name_staging" {
  description = "Staging Container App name"
  type        = string
  default     = "backlog-synthesizer-staging"
}

variable "app_name_prod" {
  description = "Production Container App name"
  type        = string
  default     = "backlog-synthesizer-prod"
}

variable "spn_object_id" {
  description = "Object ID of the GitHub Actions SPN (for ACR role assignment)"
  type        = string
  default     = "e4610223-aa9d-4533-aeaa-1fc9bc38be62"
}

# ── App configuration ─────────────────────────────────────────────────────────
variable "client_name" {
  description = "Fictional client name shown in the UI"
  type        = string
  default     = "Meridian Motors"
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
}

variable "google_api_key" {
  description = "Google Gemini API key (optional)"
  type        = string
  sensitive   = true
  default     = ""
}

# ── Jira ──────────────────────────────────────────────────────────────────────
variable "jira_base_url" {
  description = "Jira base URL"
  type        = string
  default     = "https://vamshi58.atlassian.net"
}

variable "jira_email" {
  description = "Jira account email"
  type        = string
  default     = "vamshi58@gmail.com"
}

variable "jira_api_token" {
  description = "Jira API token"
  type        = string
  sensitive   = true
}

variable "jira_project_key" {
  description = "Jira project key"
  type        = string
  default     = "MM"
}

# ── Entra ID SSO ──────────────────────────────────────────────────────────────
variable "entra_tenant_id" {
  description = "Entra ID tenant ID for SSO app"
  type        = string
  default     = "5812d1e2-7392-48c9-9265-ba6c08c62346"
}

variable "entra_tenant_domain" {
  description = "Entra ID tenant domain"
  type        = string
  default     = "vkrishna1404gmail.onmicrosoft.com"
}

variable "entra_client_id" {
  description = "Entra ID app registration client ID"
  type        = string
  default     = "786b0f93-b38d-41c7-8ebd-30a405b7385d"
}

variable "entra_client_secret" {
  description = "Entra ID app registration client secret"
  type        = string
  sensitive   = true
}

# ── Scaling ───────────────────────────────────────────────────────────────────
variable "staging_min_replicas" {
  description = "Minimum replicas for staging (0 = scale to zero)"
  type        = number
  default     = 0
}

variable "staging_max_replicas" {
  description = "Maximum replicas for staging"
  type        = number
  default     = 1
}

variable "prod_min_replicas" {
  description = "Minimum replicas for production"
  type        = number
  default     = 1
}

variable "prod_max_replicas" {
  description = "Maximum replicas for production"
  type        = number
  default     = 3
}

variable "cpu_requests" {
  description = "CPU cores per replica"
  type        = string
  default     = "1.0"
}

variable "memory_requests" {
  description = "Memory per replica"
  type        = string
  default     = "2Gi"
}
