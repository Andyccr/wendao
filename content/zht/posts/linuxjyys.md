---
title: Linux解壓/壓縮的大集合
date: '2020-03-13T22:02:51+08:00'
slug: linuxjyys
original_url: https://andychen.net/linuxjyys.html
---

此文章將介紹 如何在Linux命令行下，壓縮，解壓，打包一個或多個文件

打包

*   .tar

假設有一個文件（夾）foo,要打包爲archive.tar

tar cf archive.tar foo

假設有多個文件（夾）foo和bar ,要打包爲archive.tar

tar cf archive.tar foo bar

壓縮

.tar.gz

假設有文件（夾）foo和bar,要壓縮archive.tar.gz

tar cfz archive.tar.gz foo bar

*   .tar.xz

假設有文件（夾）foo和bar,要壓縮爲archive.tar.xz1

tar cfz archive.tar.xz foo bar

*   .zip

假設有文件foo和bar,要壓縮爲archive.zip (！！注意，不適用於文件夾！！)

zip archive.zip foo bar

假設有文件夾foo和bar,要壓縮爲archive.zip

zip -r archive.zip foo bar

*   .7z

假設有文件（夾）foo和bar,要壓縮爲archive.7z

7z a archive.7z foo bar

解壓

*   .tar.\*

解壓/解包.tar.\*文件，假設爲archive.tar.gz

tar xf archive.tar.gz

*   .7z

解壓.7z文件，假設爲archive.7z

7z e archive.7z

*   .zip

解壓.zip文件，假設爲archive.zip

unzip archive.zip
