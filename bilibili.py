#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Text, Dict

import aiohttp
import re

from hoshino.typing import MessageSegment

filter_id = re.compile(r'\bbilibili\.com\/video\/(?:av(?P<aid>[0-9]+)|(?P<bvid>bv[0-9a-zA-Z]+))', flags=re.I)

def get_id_from_url(url: Text) -> Dict:
	return {k: v for k, v in filter_id.search(url).groupdict().items() if v}

async def miniapp(meta: Dict) -> Text:
	url = meta.get('qqdocurl')
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.head(url) as resp:
			headers = resp.headers
	params = get_id_from_url(headers['Location'])
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.get('https://api.bilibili.com/x/web-interface/view', params=params) as resp:
			ret = await resp.json()
	data = ret['data']
	return (
		f"{MessageSegment.image(data['pic'])}\n"
		f"av{data['aid']}\n"
		f"{data['title']}\n"
		f"UP:{data['owner']['name']}\n"
		f"{data['stat']['view']:,}播放 {data['stat']['danmaku']:,}弹幕\n"
		f"https://www.bilibili.com/video/{data['bvid']}"
	)
