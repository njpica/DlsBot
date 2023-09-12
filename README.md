# DlsBot
提供校内服务

> 23/9/11号学校把我vpn ban了，懒得搞了
> 
> 手动去敏 + 删除一堆没有的插件
> 
> 各个插件时间跨度有点长，风格都不一样~

# 功能

- xfb
- - 实现查电费 充电费 电费表 ...
- atrust
- - 通过学校VPN做代理

# 部署
> 数据库用的是postgresql
> 
> 到 db/__init__.py 修改下 link_db
> 
> 当这个是个插件库吧，想要开发的话自己新建个bot
> 
> 这个写的太乱了，不想重构了
```bash
poetry install
poetry run python bot.py
```
> 其实部署环境是全局pip...，poetry环境上传前才补的...
