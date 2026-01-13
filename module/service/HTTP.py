#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP 服务端模块
基于 FastAPI 的纯 HTTP 服务端封装，提供 REST API 能力
通过回调函数机制让外部注入业务逻辑
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.responses import RedirectResponse
from fastapi.responses import FileResponse
import uvicorn

class HTTPServer:
    def __init__(self):
      # 创建FastAPI实例
      self.app = FastAPI()

    # ==================== 启动服务器 ====================
    def start(self):
      # 启动服务器
      uvicorn.run(self.app, host="127.0.0.1", port=8000)
