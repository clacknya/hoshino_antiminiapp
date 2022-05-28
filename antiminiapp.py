#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict

import nonebot
import json
import yaml

from hoshino import Service
from hoshino.typing import CQEvent, MessageSegment
from hoshino.config import NICKNAME

from . import bilibili

sv = Service('反小程序', visible=True, enable_on_default=False)

appid_map = {
	'1109937557': bilibili.miniapp,
}

def com_tencent_miniapp(meta: Dict) -> Dict:
	return meta.get('detail_1', {})

def com_tencent_structmsg(meta: Dict) -> Dict:
	return meta.get('news', {})

app_map = {
	'com.tencent.miniapp_01': com_tencent_miniapp,
	'com.tencent.structmsg':  com_tencent_structmsg,
}

nickname = NICKNAME if isinstance(NICKNAME, str) else NICKNAME[0]

@sv.on_message('group')
async def antiminiapp(bot, ev: CQEvent):
	if ev.detail_type == 'guild':
		return
	for msg in ev.message:
		if msg.get('type') == 'json':
			data = json.loads(nonebot.message.unescape(msg['data'].get('data', '{}')))
			if data.get('app') in app_map:
				meta = app_map[data['app']](data.get('meta', {}))
				appid = str(meta.get('appid'))
				if appid in appid_map:
					msg = await appid_map[appid](meta)
					await bot.send_group_msg(group_id=ev.group_id, message=msg)
					return
			msg = yaml.dump(data, allow_unicode=True)
			node = MessageSegment.node_custom(
				user_id=ev.self_id,
				nickname=nickname,
				content=nonebot.message.escape(msg),
			)
			node['data']['name'] = nickname
			chain = [node]
			await bot.send_group_forward_msg(group_id=ev.group_id, messages=chain)
