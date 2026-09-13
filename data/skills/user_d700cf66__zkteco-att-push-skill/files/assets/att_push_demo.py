#!/usr/bin/env python3
"""
考勤 PUSH V5.8 通讯协议 —— 服务端参考实现

参考文档：zkteco-att-push-skill/references/att-push-v58-reference.md
协议版本：V5.8 | PUSH V2.4.2

本文件提供完整的 PUSH 服务端框架，可直接运行，包含：
  - 初始化信息交互（/iclock/cdata?options=all）
  - 数据上传处理（ATTLOG / ATTPHOTO / OPERLOG / BIODATA / ERRORLOG）
  - 命令获取与队列（/iclock/getrequest）
  - 命令回复（/iclock/devicecmd）
  - 心跳（/iclock/ping）
  - 密钥交换（/iclock/exchange）

依赖：Python 3.8+（仅标准库）

使用方式：
  python att_push_demo.py              # 启动服务端（默认端口 8088）
  python att_push_demo.py --port 9090  # 指定端口
"""

import http.server
import json
import time
import urllib.parse
import uuid
import hashlib
import base64
import re
import os
import sys
from collections import defaultdict, deque
from datetime import datetime


# ============================================================
# 配置
# ============================================================
DEFAULT_PORT = 8088
SERVER_VERSION = "V5.8"
PUSH_PROTO_VERSION = "2.4.2"
SERVER_NAME = "AttPushDemo"
ERROR_DELAY = 30  # 秒
REQUEST_DELAY = 10  # 秒
TRANS_TIMES = "00:00;14:00"
TRANS_INTERVAL = 1
TIMEZONE = 8  # 东8区
REALTIME = 1


# ============================================================
# 设备会话管理（内存）
# ============================================================
class AttDeviceSession:
    """考勤设备会话"""

    def __init__(self, sn):
        self.sn = sn
        self.registry_code = self._generate_code(10)
        self.session_id = self._generate_code(32)
        self.public_key = None  # 设备公钥
        self.server_public_key = None  # 服务器公钥
        self.last_seen = time.time()
        self.info = {}  # 设备上报的 INFO 信息
        self.config = {}  # 推送的配置参数
        self.cmd_queue = deque()  # 待下发的命令队列
        self.stamps = {
            "ATTLOG": "None",
            "OPERLOG": "None",
            "ATTPHOTO": "None",
            "BIODATA": "None",
            "IDCARD": "None",
            "ERRORLOG": "None",
        }
        # 配置参数（初始化时返回）
        self.params = {
            "ErrorDelay": str(ERROR_DELAY),
            "Delay": str(REQUEST_DELAY),
            "TransTimes": TRANS_TIMES,
            "TransInterval": str(TRANS_INTERVAL),
            "TimeZone": str(TIMEZONE),
            "Realtime": str(REALTIME),
            "Encrypt": "None",
        }

    @staticmethod
    def _generate_code(length):
        """生成随机码"""
        return uuid.uuid4().hex[:length].upper()

    def add_command(self, cmd):
        """添加待下发命令到队列"""
        cmd_id = str(uuid.uuid4())[:8]
        self.cmd_queue.append((cmd_id, cmd))
        return cmd_id

    def get_pending_commands(self):
        """获取并清空待下发的命令"""
        if not self.cmd_queue:
            return None
        lines = []
        while self.cmd_queue:
            cmd_id, cmd = self.cmd_queue.popleft()
            lines.append(f"C:{cmd_id}:{cmd}")
        return "\n".join(lines) + "\n"

    def update_stamp(self, table, value):
        """更新时间戳"""
        if table in self.stamps:
            self.stamps[table] = str(value)

    def update_info(self, info_values):
        """更新 INFO 信息"""
        keys = [
            "firmware_ver", "user_count", "fingerprint_count", "attlog_count",
            "ip_address", "fp_algo_ver", "face_algo_ver", "face_required_img",
            "face_count", "support_flags", "card_count", "userpic_count", "attphoto_count"
        ]
        for i, val in enumerate(info_values):
            if i < len(keys):
                self.info[keys[i]] = val


# ============================================================
# PUSH 服务端
# ============================================================
class AttPushHandler(http.server.BaseHTTPRequestHandler):
    """考勤 PUSH HTTP 请求处理"""

    # 设备会话存储（类级别，所有请求共享）
    sessions = {}

    # 日志格式时间
    server_version = f"AttPushDemo/{SERVER_VERSION}"

    def log_message(self, format, *args):
        """自定义日志格式（兼容框架调用）"""
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if args:
            msg = format % args if "%" in format else " ".join(str(a) for a in args)
        else:
            msg = format
        sys.stderr.write(f"[{ts}] {msg}\n")

    def _parse_query(self):
        """解析 URL 查询参数"""
        parsed = urllib.parse.urlparse(self.path)
        return parsed.path, dict(urllib.parse.parse_qsl(parsed.query))

    def _read_body(self):
        """读取请求体"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            return self.rfile.read(content_length).decode("utf-8", errors="replace")
        return ""

    def _send_response(self, body, content_type="text/plain", status=200, headers=None):
        """发送 HTTP 响应"""
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type};charset=UTF-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Date", self.date_time_string())
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _get_or_create_session(self, sn):
        """获取或创建设备会话"""
        if sn not in self.sessions:
            self.sessions[sn] = AttDeviceSession(sn)
        return self.sessions[sn]

    # ---- HTTP 方法路由 ----

    def do_GET(self):
        path, params = self._parse_query()
        sn = params.get("SN", "")

        if path == "/iclock/cdata":
            self._handle_cdata_get(sn, params)
        elif path == "/iclock/ping":
            self._handle_ping(sn, params)
        elif path == "/iclock/getrequest":
            self._handle_getrequest(sn, params)
        else:
            self._send_response("OK")

    def do_POST(self):
        path, params = self._parse_query()
        sn = params.get("SN", "")
        body = self._read_body()

        if path == "/iclock/cdata":
            self._handle_cdata_post(sn, params, body)
        elif path == "/iclock/exchange":
            self._handle_exchange(sn, params, body)
        elif path == "/iclock/devicecmd":
            self._handle_devicecmd(sn, params, body)
        else:
            self._send_response("OK")

    # ---- 具体处理逻辑 ----

    def _handle_cdata_get(self, sn, params):
        """
        初始化信息交互（3. 初始化信息交互）
        GET /iclock/cdata?SN=xxx&options=all&pushver=xxx&language=xxx&DeviceType=xxx
        """
        session = self._get_or_create_session(sn)
        session.last_seen = time.time()

        pushver = params.get("pushver", "2.2.14")
        language = params.get("language", "83")
        device_type = params.get("DeviceType", "att")

        # 构建配置响应
        lines = [f"GET OPTION FROM: {sn}"]
        for stamp_type, stamp_val in session.stamps.items():
            lines.append(f"{stamp_type}Stamp={stamp_val}")
        lines.append(f"ErrorDelay={ERROR_DELAY}")
        lines.append(f"Delay={REQUEST_DELAY}")
        lines.append(f"TransTimes={TRANS_TIMES}")
        lines.append(f"TransInterval={TRANS_INTERVAL}")
        lines.append(f"TransFlag=TransData AttLog\tOpLog\tAttPhoto\tEnrollUser\tUserPic")
        lines.append(f"TimeZone={TIMEZONE}")
        lines.append(f"Realtime={REALTIME}")
        lines.append(f"Encrypt=None")
        lines.append(f"ServerVer={SERVER_VERSION}")
        lines.append(f"PushProtVer={PUSH_PROTO_VERSION}")
        lines.append(f"PushOptionsFlag=1")
        lines.append(f"PushOptions=FingerFunOn,FaceFunOn,UserPicURLFunOn")

        body = "\n".join(lines)
        self._send_response(body)

        # 更新会话信息
        session.params["pushver"] = pushver
        session.params["language"] = language
        session.params["DeviceType"] = device_type

        self.log_message(f"[INIT] SN={sn} pushver={pushver} lang={language} type={device_type}")

    def _handle_cdata_post(self, sn, params, body):
        """
        数据上传处理（9. 上传数据）
        支持多表：ATTLOG / ATTPHOTO / OPERLOG / BIODATA / ERRORLOG / options
        """
        session = self._get_or_create_session(sn)
        session.last_seen = time.time()
        table = params.get("table", "")

        if table == "options":
            # 6. 推送配置信息
            self._handle_push_options(sn, params, body)
            return

        if table == "ATTLOG":
            # 9.1 上传考勤记录 + 9.6 上传身份证考勤记录
            count = self._parse_attlog(body)
            session.update_stamp("ATTLOG", params.get("Stamp", str(int(time.time()))))
            self._send_response(f"OK:{count}")
            self.log_message(f"[UPLOAD] SN={sn} ATTLOG: {count} records")

        elif table == "ATTPHOTO":
            # 9.2 上传考勤照片 + 9.7 上传身份证考勤照片
            filename = self._parse_attphoto(body)
            session.update_stamp("ATTPHOTO", params.get("Stamp", str(int(time.time()))))
            self._send_response("OK")
            self.log_message(f"[UPLOAD] SN={sn} ATTPHOTO: {filename}")

        elif table == "OPERLOG":
            # 9.3 操作记录 / 9.4 用户信息 / 9.8 指纹模板 / 9.9 面部模板 /
            # 9.10 指静脉模板 / 9.12 用户照片 / 9.14 比对照片
            count = self._parse_operlog(body)
            session.update_stamp("OPERLOG", params.get("Stamp", str(int(time.time()))))
            self._send_response(f"OK:{count}")
            self.log_message(f"[UPLOAD] SN={sn} OPERLOG: {count} records")

        elif table == "IDCARD":
            # 9.5 上传身份证信息
            count = self._parse_idcard(body)
            self._send_response(f"OK:{count}")

        elif table == "BIODATA":
            # 9.11 上传一体化模板
            count = self._parse_biodata(body)
            session.update_stamp("BIODATA", params.get("Stamp", str(int(time.time()))))
            self._send_response(f"OK:{count}")
            self.log_message(f"[UPLOAD] SN={sn} BIODATA: {count} records")

        elif table == "ERRORLOG":
            # 9.15 上传异常日志
            count = self._parse_errorlog(body)
            self._send_response("OK")
            self.log_message(f"[UPLOAD] SN={sn} ERRORLOG")

        else:
            self._send_response("OK:0")

    def _handle_push_options(self, sn, params, body):
        """处理推送配置（6. 推送配置信息）"""
        session = self._get_or_create_session(sn)
        if body:
            for pair in body.split(","):
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    session.config[key.strip()] = value.strip()
        self._send_response("OK")
        self.log_message(f"[CONFIG] SN={sn} options={body[:100]}")

    def _handle_ping(self, sn, params):
        """心跳（8. 心跳）"""
        if sn in self.sessions:
            self.sessions[sn].last_seen = time.time()
        self._send_response("OK")
        self.log_message(f"[HEARTBEAT] SN={sn}")

    def _handle_getrequest(self, sn, params):
        """
        获取命令（10. 获取命令）+ 上传更新信息（7. 上传更新信息）

        当 URL 中包含 INFO 参数时，同时上传设备状态信息
        当有命令待下发时，返回命令；否则返回 OK
        """
        if not sn:
            self._send_response("OK")
            return

        session = self._get_or_create_session(sn)
        session.last_seen = time.time()

        # 7. 上传更新信息
        info = params.get("INFO", "")
        if info:
            info_values = info.split(",")
            session.update_info(info_values)

        # 10. 获取命令
        commands = session.get_pending_commands()
        if commands:
            self._send_response(commands)
        else:
            # 无命令时，返回 OK
            self._send_response("OK")

    def _handle_devicecmd(self, sn, params, body):
        """命令回复（11. 命令回复）"""
        if body:
            self.log_message(f"[DEVICECMD] SN={sn}: {body.strip()}")
        self._send_response("OK")

    def _handle_exchange(self, sn, params, body):
        """
        密钥交换（4. 交换公钥 / 5. 交换因子）
        POST /iclock/exchange?SN=xxx&type=publickey|factors
        """
        session = self._get_or_create_session(sn)
        exchange_type = params.get("type", "")

        if exchange_type == "publickey":
            # 4. 交换公钥
            if "PublicKey=" in body:
                session.public_key = body.split("PublicKey=", 1)[1].strip()
            # 返回服务器公钥
            server_pk = f"ServerPublicKey_{sn}_{uuid.uuid4().hex[:16]}"
            session.server_public_key = server_pk
            self._send_response(f"PublicKey={server_pk}",
                                headers={"Set-Cookie": f"token={uuid.uuid4().hex}; Path=/; HttpOnly"})

        elif exchange_type == "factors":
            # 5. 交换因子
            if "Factors=" in body:
                session.params["device_factor"] = body.split("Factors=", 1)[1].strip()
            server_factor = f"ServerFactor_{uuid.uuid4().hex[:16]}"
            session.params["server_factor"] = server_factor
            self._send_response(f"Factors={server_factor}",
                                headers={"Set-Cookie": f"token={uuid.uuid4().hex}; Path=/; HttpOnly"})

        else:
            self._send_response("OK")

    # ============================================================
    # 数据解析（仅示例，实际应持久化存储）
    # ============================================================

    def _parse_attlog(self, body):
        """
        解析考勤记录（9.1 上传考勤记录）
        格式：${Pin}\t${Time}\t${Status}\t${Verify}\t${Workcode}\t...\tMaskFlag\tTemperature\tConvTemperature\tTimeOffset
        """
        records = body.strip().split("\n")
        count = 0
        for line in records:
            line = line.strip()
            if not line:
                continue
            fields = line.split("\t")
            if len(fields) >= 4:
                pin = fields[0]
                time_val = fields[1]
                status = fields[2]
                verify = fields[3]
                count += 1
                # 实际应保存到数据库
                # print(f"  Pin={pin}, Time={time_val}, Status={status}, Verify={verify}")
        return count

    def _parse_attphoto(self, body):
        """解析考勤照片（9.2 上传考勤照片）"""
        # PIN=文件名\nSN=序列号\nsize=大小\nCMD=uploadphoto\0二进制数据
        filename = "unknown"
        for line in body.split("\n"):
            if line.startswith("PIN="):
                filename = line[4:].strip()
                break
        return filename

    def _parse_operlog(self, body):
        """
        解析操作/用户/模板记录（9.3-9.4, 9.8-9.10, 9.12, 9.14）
        包含：OPLOG / USER / FP / FACE / FVEIN / USERPIC / BIOPHOTO
        """
        records = body.strip().split("\n")
        count = 0
        i = 0
        while i < len(records):
            line = records[i].strip()
            if not line:
                i += 1
                continue

            # OPLOG 记录：OPLOG ${OpType}\t${Operator}\t${OpTime}...
            if line.startswith("OPLOG"):
                count += 1
                i += 1
                continue

            # USER 记录：USER PIN=xxx\tName=xxx\t...
            if line.startswith("USER"):
                count += 1
                i += 1
                continue

            # FP 记录：FP PIN=xxx\tFID=xxx\t...
            if line.startswith("FP"):
                count += 1
                i += 1
                continue

            # FACE 记录：FACE PIN=xxx\t...
            if line.startswith("FACE"):
                count += 1
                i += 1
                continue

            # FVEIN 记录：FVEIN Pin=xxx\t...
            if line.startswith("FVEIN"):
                count += 1
                i += 1
                continue

            # USERPIC 记录：USERPIC PIN=xxx\t...
            if line.startswith("USERPIC"):
                count += 1
                i += 1
                continue

            # BIOPHOTO 记录：BIOPHOTO PIN=xxx\t...
            if line.startswith("BIOPHOTO"):
                count += 1
                i += 1
                continue

            i += 1

        return count

    def _parse_idcard(self, body):
        """解析身份证信息（9.5 上传身份证信息）"""
        records = body.strip().split("\n")
        count = 0
        for line in records:
            if line.startswith("IDCARD"):
                count += 1
        return count

    def _parse_biodata(self, body):
        """解析一体化模板（9.11 上传一体化模板）"""
        records = body.strip().split("\n")
        count = 0
        for line in records:
            if line.startswith("BIODATA"):
                count += 1
        return count

    def _parse_errorlog(self, body):
        """解析异常日志（9.15 上传异常日志）"""
        count = 0
        if "ERRORLOG" in body:
            count = 1
        return count


class AttPushServer:
    """考勤 PUSH 服务端启动器"""

    def __init__(self, port=DEFAULT_PORT):
        self.port = port
        self.server = None

    def start(self):
        """启动 HTTP 服务端"""
        server_addr = ("0.0.0.0", self.port)

        class Handler(AttPushHandler):
            pass

        self.server = http.server.HTTPServer(server_addr, Handler)
        print(f"考勤 PUSH 服务端已启动:")
        print(f"  地址     : http://0.0.0.0:{self.port}")
        print(f"  协议版本 : V5.8 / PUSH V2.4.2")
        print(f"  初始化   : GET  /iclock/cdata?SN={{SN}}&options=all")
        print(f"  上传数据 : POST /iclock/cdata?SN={{SN}}&table=ATTLOG")
        print(f"  获取命令 : GET  /iclock/getrequest?SN={{SN}}")
        print(f"  命令回复 : POST /iclock/devicecmd?SN={{SN}}")
        print(f"  心跳     : GET  /iclock/ping?SN={{SN}}")
        print(f"  密钥交换 : POST /iclock/exchange?SN={{SN}}&type=publickey")
        print(f"按 Ctrl+C 停止")
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n服务端已停止")
            self.server.server_close()


# ============================================================
# 命令构建工具（辅助函数）
# ============================================================

def build_update_userinfo_cmd(pin, name, card="", pri="0", grp="1",
                               tz="0000000000000000", verify="-1",
                               vice_card="", start_time="", end_time="",
                               expires=""):
    """
    构建下发用户信息命令（10.1.1 用户信息）
    C:CmdID:DATA UPDATE USERINFO PIN=xxx\tName=xxx\t...
    """
    parts = [f"PIN={pin}"]
    if name:
        parts.append(f"Name={name}")
    if card:
        parts.append(f"Card={card}")
    parts.append(f"Pri={pri}")
    parts.append(f"Grp={grp}")
    parts.append(f"TZ={tz}")
    parts.append(f"Verify={verify}")
    if vice_card:
        parts.append(f"ViceCard={vice_card}")
    if start_time:
        parts.append(f"StartDatetime={start_time}")
    if end_time:
        parts.append(f"EndDatetime={end_time}")
    if expires:
        parts.append(f"Expires={expires}")

    return f"DATA UPDATE USERINFO {'\t'.join(parts)}"


def build_update_fingertmp_cmd(pin, fid, tmp_base64, valid="1"):
    """
    构建下发指纹模板命令（10.1.3 指纹模板）
    C:CmdID:DATA UPDATE FINGERTMP PIN=xxx\tFID=xxx\t...
    """
    size = len(tmp_base64)
    return (f"DATA UPDATE FINGERTMP PIN={pin}\tFID={fid}\t"
            f"Size={size}\tValid={valid}\tTMP={tmp_base64}")


def build_update_face_cmd(pin, fid, tmp_base64, valid="1"):
    """
    构建下发面部模板命令（10.1.4 面部模板）
    """
    size = len(tmp_base64)
    return (f"DATA UPDATE FACE PIN={pin}\tFID={fid}\t"
            f"Valid={valid}\tSize={size}\tTMP={tmp_base64}")


def build_update_biodata_cmd(pin, type_val, major_ver, minor_ver,
                              tmp_base64, no="0", index="0",
                              valid="1", duress="0", fmt="0"):
    """
    构建下发一体化模板命令（10.1.6 一体化模板）
    type_val: 0=通用, 1=指纹, 2=面部, 6=掌纹, 7=指静脉,
              8=掌静脉, 9=可见光人脸, 10=可见光手掌
    """
    size = len(tmp_base64)
    return (f"DATA UPDATE BIODATA Pin={pin}\tNo={no}\tIndex={index}\t"
            f"Valid={valid}\tDuress={duress}\tType={type_val}\t"
            f"MajorVer={major_ver}\tMinorVer={minor_ver}\tFormat={fmt}\t"
            f"Tmp={tmp_base64}")


def build_delete_user_cmd(pin):
    """构建删除用户命令（10.2.1 用户信息）"""
    return f"DATA DELETE USERINFO PIN={pin}"


def build_delete_fingertmp_cmd(pin, fid=None):
    """构建删除指纹模板命令（10.2.2 指纹模板）"""
    if fid is not None:
        return f"DATA DELETE FINGERTMP PIN={pin}\tFID={fid}"
    return f"DATA DELETE FINGERTMP PIN={pin}"


def build_query_attlog_cmd(start_time, end_time):
    """构建查询考勤记录命令（10.3.1 考勤记录）"""
    return f"DATA QUERY ATTLOG StartTime={start_time}\tEndTime={end_time}"


def build_query_user_cmd(pin):
    """构建查询用户信息命令（10.3.3 用户信息）"""
    return f"DATA QUERY USERINFO PIN={pin}"


def build_reboot_cmd():
    """构建重启设备命令（10.9.1 重新启动客户端）"""
    return "REBOOT"


def build_upgrade_cmd(checksum, url, size, upgrade_type=None):
    """
    构建在线升级命令（10.10.2 在线升级）
    三种方式：
      - 方式一：build_upgrade_cmd(cs, url, size)
      - 方式二：build_upgrade_cmd(cs, url, size, 'direct')
      - 方式三：build_upgrade_cmd(cs, url, size, 'subcontracting')
    """
    if upgrade_type == "direct":
        return f"UPGRADE type=1,checksum={checksum},size={size},url={url}"
    elif upgrade_type == "subcontracting":
        return f"UPGRADE checksum={checksum},size={size},url={url},supportsubcontracting=1"
    else:
        return f"UPGRADE checksum={checksum},url={url},size={size}"


def build_enroll_fp_cmd(pin, fid=0, retry=3, overwrite=0):
    """构建远程登记指纹命令（10.8.1 登记用户指纹）"""
    return f"ENROLL_FP PIN={pin}\tFID={fid}\tRETRY={retry}\tOVERWRITE={overwrite}"


# ============================================================
# 用法示例
# ============================================================
def demo_commands():
    """展示常用命令的构建方式"""
    print("=" * 60)
    print("命令构建示例：")
    print("=" * 60)

    # 下发用户信息
    cmd1 = build_update_userinfo_cmd(
        pin="12345",
        name="张三",
        card="133440",
        pri="0",
        grp="1",
        tz="0001000000000000",
        verify="-1"
    )
    print(f"\n[下发用户信息] C:cmd1:{cmd1}")

    # 下发指纹模板
    cmd2 = build_update_fingertmp_cmd(
        pin="12345",
        fid=0,
        tmp_base64="SghTUzIxAAADS00ECAUHCc7QAAAnSnkBAAAA..."
    )
    print(f"\n[下发指纹模板] C:cmd2:{cmd2}")

    # 查询考勤记录
    cmd3 = build_query_attlog_cmd(
        "2026-07-01 00:00:00",
        "2026-07-25 23:59:59"
    )
    print(f"\n[查询考勤记录] C:cmd3:{cmd3}")

    print("\n" + "=" * 60)
    print("将上述命令添加到设备命令队列即可下发：")
    print("  session.add_command(build_update_userinfo_cmd(...))")
    print("=" * 60)


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="考勤 PUSH V5.8 服务端")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"监听端口（默认 {DEFAULT_PORT}）")
    parser.add_argument("--demo", action="store_true", help="仅展示命令示例，不启动服务端")
    args = parser.parse_args()

    if args.demo:
        demo_commands()
    else:
        server = AttPushServer(port=args.port)
        server.start()
