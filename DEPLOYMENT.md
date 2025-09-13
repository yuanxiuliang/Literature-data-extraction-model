# 部署指南

## 本地开发环境部署

### 1. 环境要求

- Python 3.9+
- Docker 20.0+
- Docker Compose 2.0+
- Git

### 2. 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/yuanxiuliang/Literature-data-extraction-model.git
cd Literature-data-extraction-model

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动MySQL数据库
docker-compose up -d mysql

# 5. 等待数据库启动（约30秒）
sleep 30

# 6. 运行数据库迁移
alembic upgrade head

# 7. 启动应用
python app/main.py
```

### 3. 访问应用

- **API文档**: http://localhost:8000/docs
- **API接口**: http://localhost:8000
- **健康检查**: http://localhost:8000/health

### 4. 数据库管理

```bash
# 连接MySQL数据库
docker exec -it crystal_growth_mysql mysql -u app_user -p crystal_growth

# 查看数据库状态
docker-compose ps

# 停止服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

## 生产环境部署

### 1. 云服务商选择

#### 阿里云
- **RDS MySQL**: 数据库服务
- **ECS**: 应用服务器
- **SLB**: 负载均衡
- **OSS**: 文件存储

#### 腾讯云
- **CDB MySQL**: 数据库服务
- **CVM**: 应用服务器
- **CLB**: 负载均衡
- **COS**: 文件存储

#### AWS
- **RDS MySQL**: 数据库服务
- **EC2**: 应用服务器
- **ALB**: 负载均衡
- **S3**: 文件存储

### 2. 部署步骤

#### 2.1 数据库部署
1. 创建云数据库MySQL实例
2. 配置安全组和访问权限
3. 创建数据库和用户
4. 导入初始数据

#### 2.2 应用部署
1. 创建应用服务器
2. 安装Docker和Docker Compose
3. 上传应用代码
4. 配置环境变量
5. 启动应用服务

#### 2.3 域名和SSL
1. 购买域名
2. 配置DNS解析
3. 申请SSL证书
4. 配置HTTPS

### 3. 环境变量配置

#### 开发环境 (.env.development)
```env
DATABASE_URL=mysql+pymysql://app_user:app_password@localhost:3306/crystal_growth
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True
LOG_LEVEL=DEBUG
```

#### 生产环境 (.env.production)
```env
DATABASE_URL=mysql+pymysql://username:password@your-db-host:3306/crystal_growth
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False
LOG_LEVEL=INFO
```

### 4. 监控和日志

#### 应用监控
- 使用云服务商的监控服务
- 配置告警规则
- 监控CPU、内存、磁盘使用率

#### 日志管理
- 配置日志收集
- 设置日志轮转
- 监控错误日志

### 5. 备份和恢复

#### 数据库备份
```bash
# 备份数据库
mysqldump -h your-db-host -u username -p crystal_growth > backup.sql

# 恢复数据库
mysql -h your-db-host -u username -p crystal_growth < backup.sql
```

#### 应用备份
- 定期备份应用代码
- 备份配置文件
- 备份上传的文件

### 6. 安全配置

#### 数据库安全
- 使用强密码
- 限制访问IP
- 启用SSL连接
- 定期更新密码

#### 应用安全
- 使用HTTPS
- 配置防火墙
- 定期更新依赖
- 监控异常访问

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查数据库状态
docker-compose ps mysql

# 查看数据库日志
docker-compose logs mysql

# 重启数据库
docker-compose restart mysql
```

#### 2. 应用启动失败
```bash
# 检查应用日志
docker-compose logs app

# 检查端口占用
netstat -tlnp | grep 8000

# 重启应用
docker-compose restart app
```

#### 3. 依赖安装失败
```bash
# 更新pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装
pip install -r requirements.txt --force-reinstall
```

### 性能优化

#### 数据库优化
- 配置合适的连接池大小
- 优化查询语句
- 添加必要的索引
- 定期分析表

#### 应用优化
- 使用缓存
- 优化图片处理
- 配置CDN
- 启用压缩

---

*如有问题，请查看项目文档或提交Issue*
