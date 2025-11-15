# Hostinger DNS 配置指南

## 🌐 如何在 Hostinger 配置子域名

### 步骤 1：登录 Hostinger

1. 访问 https://www.hostinger.com
2. 登录你的账户
3. 进入 **hPanel** 或 **域名管理**

### 步骤 2：找到 DNS 管理

1. 在控制面板中找到你的域名 `omnidoc.info`
2. 点击 **DNS 管理** 或 **DNS Zone Editor**
3. 找到 **DNS Records** 或 **DNS 记录** 部分

### 步骤 3：添加 A 记录（用于 API 子域名）

你需要添加以下 DNS 记录：

#### 记录 1：主域名（如果还没有）

```
类型: A
名称: @ 或 omnidoc.info
值: [你的 Vercel IP 地址或 CNAME]
TTL: 3600 (或自动)
```

**注意**：如果你使用 Vercel，应该使用 **CNAME** 记录指向 Vercel，而不是 A 记录。Vercel 会提供具体的 CNAME 值。

#### 记录 2：API 子域名

```
类型: A
名称: api
值: [你的 Oracle Cloud 服务器 IP 地址]
TTL: 3600 (或自动)
```

**示例**：
- 如果你的 Oracle Cloud 服务器 IP 是 `123.45.67.89`
- 那么添加：
  - **类型**: A
  - **名称**: `api`
  - **值**: `123.45.67.89`
  - **TTL**: `3600`

#### 记录 3：WWW 子域名（可选）

```
类型: CNAME 或 A
名称: www
值: omnidoc.info (如果是 CNAME) 或 [Vercel IP]
TTL: 3600
```

### 步骤 4：在 Hostinger 中的具体操作

#### 方法 A：使用 hPanel（新界面）

1. 登录 hPanel
2. 点击 **域名** → **DNS / 域名服务器**
3. 选择 `omnidoc.info`
4. 点击 **管理 DNS 记录**
5. 点击 **添加记录**
6. 填写：
   - **类型**: 选择 `A`
   - **名称**: 输入 `api`
   - **值**: 输入你的 Oracle Cloud 服务器 IP
   - **TTL**: `3600` 或默认
7. 点击 **保存**

#### 方法 B：使用旧版控制面板

1. 登录控制面板
2. 找到 **域名** 部分
3. 点击 `omnidoc.info` 旁边的 **管理**
4. 找到 **DNS Zone Editor** 或 **DNS 管理**
5. 添加新记录：
   - **Type**: A
   - **Name**: api
   - **Points to**: [你的服务器 IP]
   - **TTL**: 3600
6. 点击 **添加记录**

### 步骤 5：验证 DNS 配置

等待几分钟让 DNS 传播（通常 5-30 分钟），然后验证：

```bash
# 检查主域名
nslookup omnidoc.info

# 检查 API 子域名
nslookup api.omnidoc.info

# 或者使用 dig
dig api.omnidoc.info
```

### 步骤 6：配置 SSL 证书

DNS 配置完成后，在 Oracle Cloud 服务器上运行：

```bash
sudo certbot --nginx -d api.omnidoc.info --non-interactive --agree-tos --email your-email@example.com --redirect
```

## 📋 完整的 DNS 记录列表

根据你的部署架构，需要以下 DNS 记录：

### 前端（Vercel）

**选项 1：使用 CNAME（推荐）**
```
类型: CNAME
名称: @ 或 omnidoc.info
值: [Vercel 提供的 CNAME，例如：cname.vercel-dns.com]
```

**选项 2：使用 A 记录**
```
类型: A
名称: @
值: [Vercel 提供的 IP 地址]
```

**WWW 子域名**
```
类型: CNAME
名称: www
值: omnidoc.info
```

### 后端（Oracle Cloud）

```
类型: A
名称: api
值: [你的 Oracle Cloud 服务器 IP 地址]
```

## 🔍 如何找到 Oracle Cloud 服务器 IP？

1. 登录 Oracle Cloud Console
2. 进入 **Compute** → **Instances**
3. 点击你的实例
4. 在 **Instance Details** 中找到 **Public IP Address**
5. 复制这个 IP 地址

## ⚠️ 常见问题

### Q: DNS 记录添加后多久生效？
**A**: 通常 5-30 分钟，最多可能需要 48 小时（但很少见）

### Q: 如何检查 DNS 是否生效？
**A**: 使用以下命令：
```bash
nslookup api.omnidoc.info
# 或
dig api.omnidoc.info +short
```

### Q: 如果使用 Vercel，主域名应该用 A 还是 CNAME？
**A**: Vercel 推荐使用 CNAME。在 Vercel 项目设置中会提供具体的 DNS 配置说明。

### Q: Hostinger 支持 CNAME 记录吗？
**A**: 是的，Hostinger 支持 CNAME 记录。但根域名（@）通常只能使用 A 记录，不能使用 CNAME。

### Q: 如果根域名必须用 A 记录，怎么办？
**A**: 
- 如果使用 Vercel，Vercel 会提供 A 记录的值
- 在 Vercel 项目设置 → Domains 中查看具体的 DNS 配置

## 📝 配置示例

假设：
- Oracle Cloud 服务器 IP: `150.230.45.123`
- Vercel CNAME: `cname.vercel-dns.com`

### Hostinger DNS 记录配置：

| 类型 | 名称 | 值 | TTL |
|------|------|-----|-----|
| A | @ | [Vercel IP] | 3600 |
| CNAME | www | omnidoc.info | 3600 |
| A | api | 150.230.45.123 | 3600 |

## 🔗 相关文档

- [Vercel DNS 配置](https://vercel.com/docs/concepts/projects/domains)
- [Oracle Cloud 获取公网 IP](https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/managingpublicIPs.htm)
- [Hostinger DNS 管理帮助](https://support.hostinger.com/en/articles/4421895-how-to-manage-dns-records)

## 💡 提示

1. **DNS 传播时间**：添加记录后，等待 5-30 分钟再测试
2. **使用工具验证**：使用 https://dnschecker.org 检查全球 DNS 传播状态
3. **备份记录**：在修改前，先截图保存现有的 DNS 记录
4. **测试连接**：DNS 生效后，测试 `ping api.omnidoc.info` 应该返回你的服务器 IP

