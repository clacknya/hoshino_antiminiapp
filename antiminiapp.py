#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict

import nonebot
import json
import yaml

from hoshino import Service

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

@sv.on_notice('group_upload')
async def group_upload(session: nonebot.NoticeSession):
	self_info = await session.bot.get_login_info()
	chain = [
		nonebot.MessageSegment.node_custom(
			user_id=session.ctx.self_id,
			nickname=self_info['nickname'],
			content=f"{session.ctx.user_id} 上传了文件 {session.ctx.file.get('name')}",
		),
		nonebot.MessageSegment.node_custom(
			user_id=session.ctx.self_id,
			nickname=self_info['nickname'],
			content=session.ctx.file.get('url'),
		),
	]
	for node in chain:
		node['data']['name'] = self_info['nickname']
	await session.bot.send_group_forward_msg(group_id=session.ctx.group_id, messages=chain)

@sv.on_message('group')
async def antiminiapp(bot, ev: nonebot.message.CQEvent):
	if ev.detail_type == 'guild':
		return
	self_info = await bot.get_login_info()
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
					nonebot.MessageSegment.node_custom(
						user_id=ev.self_id,
						nickname=self_info['nickname'],
						content='解析结果',
					),
					nonebot.MessageSegment.node_custom(
						user_id=ev.self_id,
						nickname=self_info['nickname'],
						content=nonebot.message.escape(yaml.dump(data, allow_unicode=True)),
					),
				]
				for node in chain:
					node['data']['name'] = self_info['nickname']
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
