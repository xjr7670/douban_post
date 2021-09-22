# douban_post
抓取指定ID在豆瓣指定小组内的发言。
由于豆瓣ID不是唯一的，所以可能会重复


本程序使用了第三方库
	requests
	BeautifulSoup

可以使用pip来安装：
	pip install requests bs4
	
## 只在一个组内查找

```bash
python single_group.py
```

### 查找用户在其加入的所有组的发言

```bash
python douban_post.py
```
