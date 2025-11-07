# S3 模块变量

variable "environment" {
  description = "部署环境"
  type        = string
}

variable "data_bucket_name" {
  description = "数据存储桶名称"
  type        = string
}

variable "models_bucket_name" {
  description = "模型存储桶名称"
  type        = string
}

variable "logs_bucket_name" {
  description = "日志存储桶名称"
  type        = string
}
