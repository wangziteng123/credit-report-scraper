## 依赖
运行该爬虫需要 Python 3, 以及 Scrapy 框架。

### Python 3
Python 3 可以在 Python 的[官网](https://www.python.org/downloads/)下载，也可以用各平台的包管理器安装。安装好 Python 3 之后，在 credit_downloader 目录下面运行：
```
python3 -m venv .
```
来创建一个 virtual environment。然后可以用

```
source bin/activate
```
来启动这个 vitual environment。如果 `which python` 的结果是 `bin` 下面的 python 那么 vitual environment 已经启动了。

### 第三方库

在 vitual environment 下面，运行
```
pip install -r requirements.txt
```

来安装第三方库。

## 运行爬虫

不同的数据源，有一个对应的爬虫（这些爬虫都存储在 `credit_downloader/spiders/` 下面，以数据源命名）。如果要爬取某个数据源，运行：
```
scrapy crawl <source> -o <output_file>
```
其中 `source` 为数据源名称，`output_file` 为记录爬取信息的文件路径，必须是一个 JSON 文件。
例如，要运行大公资信的爬虫，可以运行 `scrapy crawl dagongrating -o dagongrating-20170719.json`。

## 爬虫产生的数据
上面提到的 `output_file` 里面是一个 JSON 对象的数组，包含了每条单独数据的信息。每个对象的结构如下：
```
{
    "id_": 一条数据的 identifier，可以跟 6estates 数据库的 idstr 相对应
    "name": 数据的名称
    "source": 数据源
    "category": 数据的分类
    "rating": 评级
    "pub_time": 数据发布时间
    "fet_time": 数据爬取时间
    "files": [{
        "url": 下载文件的 URL
        "path": 下载文件的本地路径
        "checksum": 下载文件的 MD5 校验值
    }],
    "status": 下载状态，可以为 success、download_failed、missing（文件在网站上没有下载链接）
}
```

爬虫对应每一条数据都会下载文件，下载的路径在 `downloads/` 下面，按照数据源和数据文件的类型来归类。

## 爬取失败
有一些原因会导致下载文件失败，比如网络状况不佳、连接被中断、下载超时等等。在爬虫运行完之后可以运行 `credit_downloader/retry.py` 来重新下载文件。运行：
```
python3 credit_downloader/retry.py <json_file>
```
其中 `json_file` 是爬虫的 output_file。如之前的大公资信爬虫，可以在 Scrapy 运行结束之后用 `python3 credit_downloader/retry.py dagongrating-20170719.json` 来重新下载。

## 文件大小和速度
由于文档文件的占用空间会比较大，一个数据源下最终下载的文档一共可能会有几G到小几十G。为了不给服务器施加过大压力，爬虫设置了自动减速。根据网络状况，一个数据源一次下载可能需要几个小时甚至十几个小时时间。

## 设置
- 默认的 JSON dump 会转义 Unicode，需要在 settings.py 里设置 `FEED_EXPORT_ENCODING = 'utf-8'`
- 每次下载和访问之间会有一定的间隔时间，在 settings.py 里可以寻找 `throttle`，`delay` 来调整