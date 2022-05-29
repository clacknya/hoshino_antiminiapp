#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict

import nonebot
import json
import yaml

from hoshino import Service
from hoshino.typing import CQEvent, MessageSegment
from hoshino.config import NICKNAME

from . import common
from . import bilibili

sv = Service('反小程序', visible=True, enable_on_default=False)

appid_map = {
	'1014558937': common.webpage,
	'1103188687': common.webpage,
	'1109937557': bilibili.miniapp,
}

# def com_tencent_miniapp(meta: Dict) -> Dict:
	# return meta.get('detail_1', {})

# def com_tencent_structmsg(meta: Dict) -> Dict:
	# return meta.get('news', {})

# app_map = {
	# 'com.tencent.miniapp_01': com_tencent_miniapp,
	# 'com.tencent.structmsg':  com_tencent_structmsg,
# }

url_map = {
	bilibili.parse_urls: bilibili.get_info,
}

nickname = NICKNAME if isinstance(NICKNAME, str) else NICKNAME[0]

@sv.on_message('group')
async def antiminiapp(bot, ev: CQEvent):
	if ev.detail_type == 'guild':
		return
	for msg in ev.message:
		if msg.get('type') == 'json':
			data = json.loads(nonebot.message.unescape(msg['data'].get('data', '{}')))
			failed = False
			for meta in data.get('meta', {}).values():
				appid = str(meta.get('appid'))
				if appid in appid_map:
					await bot.send_group_msg(
						group_id=ev.group_id,
						message=await appid_map[appid](meta),
					)
				else:
					failed = True
			if failed:
				chain = [
					MessageSegment.node_custom(
						user_id=ev.self_id,
						nickname=nickname,
						content='解析结果',
					),
					MessageSegment.node_custom(
						user_id=ev.self_id,
						nickname=nickname,
						content=nonebot.message.escape(yaml.dump(data, allow_unicode=True)),
					),
				]
				for node in chain:
					node['data']['name'] = nickname
				await bot.send_group_forward_msg(group_id=ev.group_id, messages=chain)
		elif msg.get('type') == 'text':
			text = nonebot.message.unescape(msg['data'].get('text', ''))
			for parse in url_map:
				urls = parse(text)
				for url in urls:
					await bot.send_group_msg(
						group_id=ev.group_id,
						message=await url_map[parse](url),
					)
				if urls:
					break
