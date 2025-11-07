output "db_instance_id" {
  description = "RDS实例ID"
  value       = aws_db_instance.postgres.id
}

output "db_instance_arn" {
  description = "RDS实例ARN"
  value       = aws_db_instance.postgres.arn
}

output "db_endpoint" {
  description = "数据库连接端点"
  value       = aws_db_instance.postgres.endpoint
}

output "db_host" {
  description = "数据库主机地址"
  value       = aws_db_instance.postgres.address
}

output "db_port" {
  description = "数据库端口"
  value       = aws_db_instance.postgres.port
}

output "db_name" {
  description = "数据库名称"
  value       = aws_db_instance.postgres.db_name
}

output "db_security_group_id" {
  description = "数据库安全组ID"
  value       = aws_security_group.rds.id
}

output "read_replica_endpoint" {
  description = "读副本端点"
  value       = var.create_read_replica ? aws_db_instance.read_replica[0].endpoint : null
}
