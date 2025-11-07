# S3 模块 - 数据湖存储
# S3 Module for Data Lake Storage

# 数据存储桶
resource "aws_s3_bucket" "data" {
  bucket = var.data_bucket_name
  
  tags = {
    Name        = "${var.data_bucket_name}"
    Environment = var.environment
    Purpose     = "材料数据存储"
  }
}

# 模型存储桶
resource "aws_s3_bucket" "models" {
  bucket = var.models_bucket_name
  
  tags = {
    Name        = "${var.models_bucket_name}"
    Environment = var.environment
    Purpose     = "训练模型存储"
  }
}

# 日志存储桶
resource "aws_s3_bucket" "logs" {
  bucket = var.logs_bucket_name
  
  tags = {
    Name        = "${var.logs_bucket_name}"
    Environment = var.environment
    Purpose     = "应用日志存储"
  }
}

# 数据桶版本控制
resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# 模型桶版本控制
resource "aws_s3_bucket_versioning" "models" {
  bucket = aws_s3_bucket.models.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# 数据桶加密
resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 模型桶加密
resource "aws_s3_bucket_server_side_encryption_configuration" "models" {
  bucket = aws_s3_bucket.models.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 日志桶加密
resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 数据桶生命周期规则
resource "aws_s3_bucket_lifecycle_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  
  rule {
    id     = "archive-old-data"
    status = "Enabled"
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    expiration {
      days = 365
    }
  }
}

# 模型桶生命周期规则
resource "aws_s3_bucket_lifecycle_configuration" "models" {
  bucket = aws_s3_bucket.models.id
  
  rule {
    id     = "archive-old-models"
    status = "Enabled"
    
    transition {
      days          = 30
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}

# 日志桶生命周期规则
resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  rule {
    id     = "delete-old-logs"
    status = "Enabled"
    
    expiration {
      days = 90
    }
  }
}

# 阻止公共访问
resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "models" {
  bucket = aws_s3_bucket.models.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Outputs
output "data_bucket_name" {
  description = "数据存储桶名称"
  value       = aws_s3_bucket.data.id
}

output "data_bucket_arn" {
  description = "数据存储桶 ARN"
  value       = aws_s3_bucket.data.arn
}

output "models_bucket_name" {
  description = "模型存储桶名称"
  value       = aws_s3_bucket.models.id
}

output "models_bucket_arn" {
  description = "模型存储桶 ARN"
  value       = aws_s3_bucket.models.arn
}

output "logs_bucket_name" {
  description = "日志存储桶名称"
  value       = aws_s3_bucket.logs.id
}

output "logs_bucket_arn" {
  description = "日志存储桶 ARN"
  value       = aws_s3_bucket.logs.arn
}
