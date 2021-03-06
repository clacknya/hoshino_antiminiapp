#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Text, List, Dict

import aiohttp
import re
import datetime

from hoshino.typing import MessageSegment

pattern_id = re.compile(r'\bbilibili\.com\/video\/(?:av(?P<aid>[0-9]+)|(?P<bvid>bv[0-9a-zA-Z]+))', flags=re.I)
pattern_url = re.compile(r'\bbilibili\.com\/(?:video\/)?(?:av[0-9]+|bv[0-9a-zA-Z]+)|\bb23\.tv\/[a-zA-Z0-9]+', flags=re.I)

tz = datetime.timezone(datetime.timedelta(hours=+8))

async def get_info(url: Text) -> Text:
	async with aiohttp.ClientSession(raise_for_status=False) as session:
		async with session.head(url, allow_redirects=True) as resp:
			url = str(resp.url)
		params = {k: v for k, v in pattern_id.search(url).groupdict().items() if v}
		async with session.get('https://api.bilibili.com/x/web-interface/view', params=params) as resp:
			ret = await resp.json()
	if ret['code'] == 0:
		data = ret['data']
		return (
			f"{MessageSegment.image(data['pic'])}\n"
			f"av{data['aid']}\n"
			f"{data['title']}\n"
			f"UP:{data['owner']['name']}\n"
			f"日期:{datetime.datetime.fromtimestamp(data['pubdate'], tz).strftime('%Y-%m-%d %H:%M:%S')}\n"
			f"{data['stat']['view']:,}播放 {data['stat']['danmaku']:,}弹幕\n"
			f"https://www.bilibili.com/video/{data['bvid']}"
		)
	elif ret['code'] == -404:
		return (
			f"{MessageSegment.image('https://s1.hdslb.com/bfs/static/jinkela/video/asserts/no_video.png')}"
			f"啊叻？视频不见了？"
		)
	elif ret['code'] == -400:
		return (
			f"{MessageSegment.image('https://static.hdslb.com/error/very_sorry.png')}"
		)
	else:
		return f"code {ret['code']}: {ret['message']}"

def parse_urls(text: Text) -> List[Text]:
	return list(map(lambda x: 'https://' + x, set(pattern_url.findall(text))))

async def miniapp(meta: Dict, key: Text) -> Text:
	return await get_info(meta.get(key))
