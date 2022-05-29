#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Text, Dict

async def webpage(meta: Dict) -> Text:
	return (
		f"{meta.get['title']}\n"
		f"{meta.get('jumpUrl')}"
	)
