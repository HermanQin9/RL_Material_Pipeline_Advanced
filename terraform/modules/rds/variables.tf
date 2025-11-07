variable "project_name" {
  description = "项目名称"
  type        = string
}

variable "environment" {
  description = "环境名称 (dev/staging/prod)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR块"
  type        = string
}

variable "subnet_ids" {
  description = "数据库子网ID列表"
  type        = list(string)
}

variable "postgres_version" {
  description = "PostgreSQL版本"
  type        = string
  default     = "15.4"
}

variable "instance_class" {
  description = "RDS实例类型"
  type        = string
  default     = "db.t3.medium"
}

variable "allocated_storage" {
  description = "初始存储空间 (GB)"
  type        = number
  default     = 100
}

variable "max_allocated_storage" {
  description = "最大存储空间 (GB)"
  type        = number
  default     = 500
}

variable "database_name" {
  description = "数据库名称"
  type        = string
  default     = "matformppo"
}

variable "master_username" {
  description = "主用户名"
  type        = string
  default     = "admin"
}

variable "master_password" {
  description = "主密码"
  type        = string
  sensitive   = true
}

variable "backup_retention_period" {
  description = "备份保留天数"
  type        = number
  default     = 7
}

variable "multi_az" {
  description = "是否启用多可用区部署"
  type        = bool
  default     = false
}

variable "performance_insights_enabled" {
  description = "是否启用性能洞察"
  type        = bool
  default     = true
}

variable "monitoring_interval" {
  description = "增强监控间隔 (秒，0表示禁用)"
  type        = number
  default     = 60
}

variable "create_read_replica" {
  description = "是否创建读副本"
  type        = bool
  default     = false
}

variable "replica_instance_class" {
  description = "读副本实例类型"
  type        = string
  default     = "db.t3.medium"
}
