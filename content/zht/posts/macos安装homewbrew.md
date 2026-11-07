---
title: MacOS安裝HomewBrew
date: '2024-10-28T09:53:40+08:00'
slug: macos安装homewbrew
original_url: https://andychen.net/macos安装homewbrew.html
---

官方命令：

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

鏡像源：

```
/bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"
```

下載後(終端操作)：

```
sudo vim ~/.bash\_profile
```

```
export PATH="/opt/homebrew/bin:$PATH"
```

在:wq保存退出後

```
source ~/.bash\_profile
```
