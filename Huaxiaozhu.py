import asyncio
import datetime
import json
import random
import string
import time
from urllib.parse import quote_plus
import aiohttp
import requests
from typing import Optional
from PIL import Image
import re
import base64
from io import BytesIO
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from area import area_info


def rsa_encrypt(str_data: str) -> str:
    public_key_str = """MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3yWkNvyIYZMLLm4BJdt7DaD/3
    kxPXkjuvPcsd8aVeoRb4RIFEUZhXCbppEuhGAAgJoaZtMaFEn9pSByQ8V7AaOIZT
    qDlSus8R1yXOMsotYG7bTgLbaPMB1wGgrn95woNZzZP9tYZ84oBi8Nm5pofEhZ/W
    ImT1HOLVP5EtGG6lbwIDAQAB"""
    try:
        # 步骤1: 原始输入
        # 步骤2: trim()处理
        public_key_str = public_key_str.strip()
        # 步骤3: Base64解码前清理
        public_key_clean = re.sub(r'\s+', '', public_key_str)
        # 步骤4: Base64解码
        public_key_bytes = base64.b64decode(public_key_clean)
        # 步骤5: 加载公钥
        public_key = RSA.import_key(public_key_bytes)
        # 步骤6: 加密
        cipher = PKCS1_v1_5.new(public_key)
        plaintext_bytes = str_data.encode('utf-8')
        encrypted_bytes = cipher.encrypt(plaintext_bytes)
        # 步骤7: Base64编码
        result = base64.b64encode(encrypted_bytes).decode('utf-8')
        # 步骤8: 移除换行符
        final_result = re.sub(r'[\r\n]+', '', result)
        return final_result

    except Exception as e:

        return ""


class HuaXiaoZhuCar:
    def __init__(self, phone: str, proxy: str = ""):
        # 手机号码
        self.phone = phone
        # 随机生成Android版本号
        self.android_os = str(random.randint(8, 15))
        # 随机生成设备名称
        self.phone_model = self.get_random_phone_device()
        # 获取短信验证码URL
        self.get_sms_code_url = "https://epassport.hongyibo.com.cn/passport/login/v5/codeMT"
        # 获取图形验证码URL
        self.get_captcha_url = "https://epassport.hongyibo.com.cn/passport/login/v5/getCaptcha"
        # 验证图形验证码URL
        self.verify_captcha_url = "https://epassport.hongyibo.com.cn/passport/login/v5/verifyCaptcha"
        # 短信验证码登录URL
        self.sms_code_login_url = "https://epassport.hongyibo.com.cn/passport/login/v5/signInByCode"
        # 活动页面URL
        self.activity_url = "https://prod.huaxz.cn/imk-kf-index/index"
        # 获取活动信息URL
        self.activity_config_url = "https://api.didi.cn/webx/chapter/cover/config"
        # 公共请求头
        self.headers = {
            "didi-header-hint-content": '{"app_timeout_ms":20000,"Cityid":26,"lang":"zh-CN","locale":"zh-CN","utc_offset":"480"}',
            "TripCountry": "CN",
            "didi-header-omgid": self.generate_string(22),
            "didi-header-ssuuid": f"{self.generate_string(32).lower()}",
            "Productid": "430",
            "secdd-challenge": "1,com.huaxiaozhu.rider|1.0.29||||0||",
            "secdd-authentication": f"{self.generate_string(107).lower()}1000001000000",
            "Host": "epassport.hongyibo.com.cn",
            "Connection": "keep-alive",
            "wsgsig": "",
            "didi-header-rid": f"{self.generate_string(32).lower()}",
            "CityId": "26",
            "User-Agent": f"Mozilla/5.0 (Linux; Android {self.android_os}; {self.phone_model} Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0 OffMode/0",
            "didi-httpdns": "1"
        }
        # 随机生成SUUID
        self.suuid = self.generate_string(32).upper()
        # 随机生成DDFP
        self.ddfp = self.generate_string(32).lower()
        # 固定值
        self.xoid = "N-Wae-GvTDWzd8Jj-AAxww"
        # 全局代理
        if proxy != "":
            self.proxies = {
                "http": "http://" + proxy,
                "https": "http://" + proxy
            }
        else:
            self.proxies = {}
        # 地址信息
        self.location = {}
        # 用户信息
        self.user_info = {}
        # 基本信息
        self.base_info = {}
        # 当前活动
        self.current_activity = {}
        # 抢券结果
        self.final_result = {}

    def get_random_phone_device(self):
        """随机生成设备名称"""
        phone_model_list = [
            "Xiaomi 13 Pro",
            "Redmi K60 Ultra",
            "OPPO Find X6 Pro",
            "OPPO Reno10 Pro+",
            "vivo X90 Pro",
            "vivo iQOO 11",
            "HUAWEI Mate 50 Pro",
            "HUAWEI P60 Art",
            "HONOR Magic5 Pro",
            "HONOR 90 GT",
            "Apple iPhone 15 Pro Max",
            "Apple iPhone 14",
            "Samsung Galaxy S23 Ultra",
            "Samsung Galaxy Z Flip5",
            "OnePlus 11",
            "OnePlus Ace 2 Pro",
            "realme GT Neo5",
            "realme 11 Pro+",
            "Motorola Edge 40 Pro",
            "Lenovo Legion Y70"
        ]
        return random.choice(phone_model_list)

    def generate_string(self, length):
        """生成随机字大小写字母和数字组合的字符串"""
        letters = string.ascii_letters
        digits = string.digits
        result = ''.join(random.choice(letters + digits) for i in range(length))
        return result

    def init_headers(self):
        """初始化请求头"""
        headers = self.headers.copy()
        headers['Content-Type'] = "application/x-www-form-urlencoded"
        return headers

    def set_location(self, city_name: Optional[str]):
        if city_name is None or area_info.get(city_name) is None:
            return False
        location = area_info[city_name].copy()
        random_seed = random.uniform(0.000000123, 0.000000999)
        location['lat'] = location['lat'] + random_seed
        location['lng'] = location['lng'] + random_seed
        self.location = location
        return True

    def get_encrypted_phone(self) -> str:
        """获取加密后的手机号"""
        return rsa_encrypt(self.phone)

    def set_user_info(self, data: Optional[str]):
        """设置用户信息"""
        if data is None:
            return False
        self.user_info = json.loads(data)
        return True

    def get_sms_code(self):
        """获取短信验证码"""
        data = "q=" + quote_plus(json.dumps({
            "api_version": "1.0.2",
            "app_version": "1.12.14",
            "appid": 130000,
            "canonical_country_code": "CN",
            "cell_encrypted": self.get_encrypted_phone(),
            "channel": "123730",
            "city_id": self.location['cityid'],
            "country_calling_code": "+86",
            "country_id": 156,
            "ddfp": self.ddfp,
            "lang": "zh-CN",
            "lat": self.location['lat'],
            "lng": self.location['lng'],
            "extra_info": {
                "entrance_channel": "123730",
                "oaid": "",
                "huawei_channel": ""
            },
            "map_type": "soso",
            "model": self.phone_model,
            "network_type": "5G",
            "os": self.android_os,
            "role": 1,
            "scene": 1,
            "suuid": self.suuid,
            "utcoffset": -1
        }, separators=(',', ':')))
        try:
            response = requests.post(self.get_sms_code_url, headers=self.init_headers(), data=data)
            if response.status_code == 200:
                return response.text
            else:
                return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None

    def get_captcha(self):
        """获取图形验证码"""
        data = "q=" + quote_plus(json.dumps({
            "api_version": "1.0.2",
            "app_version": "1.12.14",
            "appid": 130000,
            "canonical_country_code": "CN",
            "cell_encrypted": self.get_encrypted_phone(),
            "channel": "123730",
            "city_id": 26,
            "country_calling_code": "+86",
            "country_id": 156,
            "ddfp": self.ddfp,
            "lang": "zh-CN",
            "lat": self.location['lat'],
            "lng": self.location['lng'],
            "extra_info": {
                "entrance_channel": "123730",
                "oaid": "",
                "huawei_channel": ""
            },
            "map_type": "soso",
            "model": self.phone_model,
            "network_type": "5G",
            "os": self.android_os,
            "role": 1,
            "scene": 1,
            "suuid": self.suuid,
            "utcoffset": -1
        }, separators=(',', ':')))
        try:
            response = requests.post(self.get_captcha_url, headers=self.init_headers(), data=data)
            if response.status_code == 200:
                return "data:image/png;base64," + response.json()['captcha']
            else:
                return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None

    def verify_captcha(self, captcha_code: str):
        data = "q=" + quote_plus(json.dumps({
            "captcha_code": captcha_code,
            "api_version": "1.0.2",
            "app_version": "1.12.14",
            "appid": 130000,
            "canonical_country_code": "CN",
            "cell_encrypted": self.get_encrypted_phone(),
            "channel": "123730",
            "city_id": self.location['cityid'],
            "country_calling_code": "+86",
            "country_id": 156,
            "ddfp": self.ddfp,
            "lang": "zh-CN",
            "lat": self.location['lat'],
            "lng": self.location['lng'],
            "extra_info": {
                "entrance_channel": "123730",
                "oaid": "",
                "huawei_channel": ""
            },
            "map_type": "soso",
            "model": self.phone_model,
            "network_type": "5G",
            "os": self.android_os,
            "role": 1,
            "scene": 1,
            "suuid": self.suuid,
            "utcoffset": -1
        }, separators=(',', ':')))
        try:
            response = requests.post(self.verify_captcha_url, headers=self.init_headers(), data=data)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None

    def sms_login(self, code: str):
        """短信验证码登录"""
        data = "q=" + quote_plus(json.dumps({
            "code": code,
            "code_type": 0,
            "api_version": "1.0.2",
            "app_version": "1.12.14",
            "appid": 130000,
            "canonical_country_code": "CN",
            "cell_encrypted": self.get_encrypted_phone(),
            "channel": "123730",
            "city_id": self.location["cityid"],
            "country_calling_code": "+86",
            "country_id": 156,
            "ddfp": self.ddfp,
            "lang": "zh-CN",
            "lat": self.location['lat'],
            "lng": self.location['lng'],
            "extra_info": {
                "entrance_channel": "123730",
                "oaid": "",
                "huawei_channel": ""
            },
            "map_type": "soso",
            "model": self.phone_model,
            "network_type": "5G",
            "os": self.android_os,
            "role": 1,
            "scene": 1,
            "suuid": self.suuid,
            "utcoffset": -1
        }, separators=(',', ':')))
        try:
            response = requests.post(self.sms_code_login_url, headers=self.init_headers(), data=data)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None

    def urlencoded_to_dict(self, url: str):
        url = url.split("?")[1]
        params_list = url.split("&")
        params_dict = {}
        for param in params_list:
            key, value = param.split("=")
            params_dict[key] = value
        return params_dict

    async def get_activity_html(self):
        """获取活动总页面"""
        url = "https://x.huaxz.cn/x/gpXkPmK"
        timestamp = str(int(time.time() * 1000))
        params = {
            "access_key_id": 27,
            "appid": "130000",
            "appversion": "1.12.14",
            "channel": "123733",
            "city_id": self.location["cityid"],
            "cityid": self.location["cityid"],
            "datatype": "1",
            "ddfp": self.ddfp,
            "lang": "zh-CN",
            "os": self.android_os,
            "platform": "1",
            "time": timestamp,
            "vcode": "1201121402",
            "xoid": self.xoid,
            "location_country": "CN",
            "location_cityid": self.location["cityid"],
            "brand": "xiaomi",
            "utc_offset": "480",
            "TripCountry": "CN",
            "maptype": "soso",
            "origin_id": "1",
            "terminal_id": "15",
            "model": "MI 9 SE"
        }
        headers = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "productid": "430",
            "cityid": str(self.location["cityid"]),
            "tripcountry": "CN",
            "X-Requested-With": "com.huaxiaozhu.rider",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=params, headers=headers, allow_redirects=False) as resp:
                url = resp.headers.get("location")
                return self.urlencoded_to_dict(url), url

    async def analysis_product_init(self, params: dict):
        url = "https://api.huaxz.cn/webx/v3/productInit?wsgsig="
        headers = {
            "User-Agent": f"Mozilla/5.0 (Linux; Android {str(self.android_os)}; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "com.huaxiaozhu.rider",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "X-Cluster-Id": "1000",
            "X-Prod-Key": "imk-kf-index",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://prod.huaxz.cn",
            "Referer": "https://prod.huaxz.cn/"
        }
        data = {
            "xbiz": "",
            "prod_key": params.get("prod_key", ""),
            "xpsid": params.get("xpsid", ""),
            "dchn": params.get("dchn", ""),
            "xoid": self.xoid,
            "xenv": params.get("xenv", ""),
            "xspm_from": params.get("xspm_from", ""),
            "xpsid_root": params.get("xpsid_root", ""),
            "xpsid_from": params.get("xpsid_from", ""),
            "xpsid_share": "",
            "x_act_key": params.get("x_act_key", ""),
            "root_xpsid": params.get("root_xpsid", ""),
            "f_xpsid": params.get("f_xpsid", ""),
            "token": self.user_info["ticket"],
            "args": {
                "runtime_args": {
                    "custom_channel": params.get("custom_channel", ""),
                    "os": "",
                    "appversion": "",
                    "model": params.get("model", ""),
                    "ddfp": params.get("ddfp", ""),
                    "openid": "",
                    "access_key_id": int(params.get("access_key_id", 12)),
                    "business_id": 256,
                    "platform_type": 0,
                    "token": self.user_info["ticket"],
                    "city_id": self.location["cityid"],
                    "lat": str(self.location["lat"]),
                    "lng": str(self.location["lng"]),
                    "env": json.dumps({
                        "dchn": params.get("dchn", ""),
                        "newTicket": self.user_info["ticket"],
                        "latitude": str(self.location["lat"]),
                        "longitude": str(self.location["lng"]),
                        "cityId": str(self.location["cityid"]),
                        "userAgent": f"Mozilla/5.0 (Linux; Android {str(self.android_os)}; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0",
                        "appVersion": "1.12.14",
                        "wifi": "2",
                        "model": "MI 9 SE",
                        "ddfp": self.ddfp,
                        "fromChannel": "5",
                        "newAppid": "130000",
                        "isHitButton": False,
                        "isOpenWeb": True,
                        "timeCost": 298,
                        "lat": str(self.location["lat"]),
                        "lng": str(self.location["lng"]),
                    }),
                    "custom_params": {},
                    "xenv": params.get("xenv", ""),
                    "share_id": "",
                    "channel_id": params.get("channel_id", ""),
                }
            },
            "need_page_config": True,
            "need_share_config": True,
            "need_project_content": True,
            "need_widget_list": True,
            "passport_type": "kf",
            "std_args": {
                "prod_key": params.get("prod_key", ""),
                "xak": params.get("x_act_key", ""),
                "dchn": params.get("dchn", ""),
                "xenv": params.get("xenv", ""),
                "token": self.user_info["ticket"],
                "lat": self.location["lat"],
                "lng": self.location["lng"],
                "uid": self.user_info["uid"],
                "xoid": self.xoid,
                "xpsid": params.get("xpsid", ""),
                "xpsid_root": params.get("xpsid_root", ""),
                "city_id": str(self.location["cityid"]),
                "trip_city_id": str(self.location["cityid"]),
                "app_lang": "zh-CN",
                "passport_type": "kf"
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, data=json.dumps(data)) as resp:
                result = await resp.json()
                return result['data']

    async def cover_config(self, params: dict, activity: dict, activity_dict: dict):
        xak = ""
        for key, value in activity_dict['xaks'].items():
            xak = key
        xid = activity_dict['xaks'][xak]['xid']
        root_xid = activity_dict['conf']['strategy_data']['aps_info']['xid']
        root_xak = params.get('x_act_key')
        url = "https://api.didi.cn/webx/chapter/cover/config"
        headers = {
            "User-Agent": f"Mozilla/5.0 (Linux; Android {self.android_os}; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "com.huaxiaozhu.rider",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "X-Prod-Session-Id": params.get("xpsid", ""),
            "X-Prod-Key": "imk-kf-index",
            "X-Act-Key": params.get("x_act_key", ""),
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://prod.huaxz.cn",
            "Referer": "https://prod.huaxz.cn/"
        }
        data = {
            "args": {
                "dchn": "g83ZZzX",
                "pass_through": f"xenv=kfpassenger&sku_id={str(activity['sku_id'])}&activity_id={str(activity['activity_id'])}&xak={xak}&xid={str(xid)}&root_xak={str(root_xak)}&root_xid={str(root_xid)}&dchn=gpXkPmK&xpsid={params.get("xpsid", "")}",
                "xenv": "kfpassenger"
            },
            "dchn": "g83ZZzX",
            "f_xpsid": params.get("xpsid", ""),
            "prod_key": "imk-kf-index",
            "root_xpsid": params.get("xpsid", ""),
            "std_args": {
                "app_lang": "zh-CN",
                "city_id": "4",
                "dchn": "gpXkPmK",
                "lat": str(self.location["lat"]),
                "lng": str(self.location["lng"]),
                "passport_type": "kf",
                "prod_key": "imk-kf-index",
                "token": self.user_info["ticket"],
                "trip_city_id": str(self.location["cityid"]),
                "uid": str(self.user_info["uid"]),
                "xak": params.get("x_act_key", ""),
                "xenv": "kfpassenger",
                "xoid": "J3zKQxV1T46mAfQGh2n4lw",
                "xpsid": params.get("xpsid", ""),
                "xpsid_root": params.get("xpsid", "")
            },
            "support_bridge": True,
            "uid": "",
            "xbiz": "",
            "xenv": "kfpassenger",
            "xoid": "J3zKQxV1T46mAfQGh2n4lw",
            "xpsid": params.get("xpsid", ""),
            "xpsid_from": "",
            "xpsid_root": params.get("xpsid_root", ""),
            "xpsid_share": "",
            "xspm_from": ""
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, data=json.dumps(data)) as response:
                    if response.status == 200:
                        data = await response.json()
                        data = data["data"]
                        data.update({
                            "xak": xak,
                            "xid": xid,
                            "root_xak": root_xak,
                            "root_xid": root_xid,
                        })
                        return data
                    else:
                        return None
        except:
            return None

    async def analysis_activity(self, url):
        headers = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "productid": "430",
            "cityid": str(self.location["cityid"]),
            "tripcountry": "CN",
            "X-Requested-With": "com.huaxiaozhu.rider",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as resp:
                html = await resp.text()
                return json.loads(html.split('"details":')[2].split('},"shareConf":')[0])[0], \
                    html.split('"xid":')[1].split(',')[0], html.split('"xak":"')[1].split('"')[0]

    def set_current_activity(self, activity_dict: dict):
        for item in activity_dict['session_list']:
            session_start_time = item["session_start_time"]
            if datetime.datetime.strptime(session_start_time, "%Y-%m-%d %H:%M:%S") > datetime.datetime.now():
                self.current_activity = item
                return item
        return None

    async def get_activity_detail(self, params: dict, activity: dict):
        url = "https://dop.hongyibo.com.cn/kcard/api/package/detail"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "com.huaxiaozhu.rider",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "X-Cluster-Id": "1000",
            "X-Prod-Key": "imk-kf-index",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://page.hongyibo.com.cn",
            "Referer": "https://page.hongyibo.com.cn"
        }

        params = {
            "xbiz": "",
            "prod_key": "kf-economical-package-detail",
            "xpsid": params.get("xpsid", ""),
            "dchn": "g83ZZzX",
            "xoid": self.xoid,
            "xenv": params.get("xenv", ""),
            "xspm_from": params.get("xspm_from", ""),
            "xpsid_root": params.get("xpsid_root", ""),
            "xpsid_from": params.get("xpsid_root", ""),
            "xpsid_share": params.get("xpsid_share", ""),
            "nginx_cors": "false",
            "token": self.user_info['ticket'],
            "city_id": self.location["cityid"],
            "lng": self.location["lng"],
            "lat": self.location["lat"],
            "sku_id": activity["sku_id"],
            "client_type": "1",
            "app_version": "1.12.14",
            "open_id": "",
            "activity_id": activity["activity_id"],
            "wsgsig": ""
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=params, headers=headers) as resp:
                result = await resp.json()
                return result['data']

    async def submit(self, params: dict, detail: dict, activity_dict: dict, root_xak, root_xid):
        url = 'https://dop.hongyibo.com.cn/kcard/api/passenger/order/submit?nginx_cors=false&wsgsig=&token={}'.format(
            self.user_info['ticket'])
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "com.huaxiaozhu.rider",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "X-Cluster-Id": "1000",
            "X-Prod-Key": "imk-kf-index",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://page.hongyibo.com.cn",
            "Referer": "https://page.hongyibo.com.cn"
        }
        data = {
            "app_id": 0,
            "channel": "ztyx_ms",
            "city_id": self.location["cityid"],
            "client_type": 1,
            "dchn": "g83ZZzX",
            "env": json.dumps({'dchn': 'g83ZZzX',
                               'newTicket': self.user_info['ticket'],
                               'latitude': str(self.location['lat']), 'longitude': str(self.location['lng']),
                               'cityId': str(self.location['cityid']),
                               'userAgent': f'Mozilla/5.0 (Linux; Android {str(self.android_os)}; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0',
                               'appVersion': '1.12.14', 'wifi': '2', 'model': 'MI 9 SE',
                               'ddfp': self.ddfp, 'fromChannel': '5', 'newAppid': '130000',
                               'isHitButton': False, 'isOpenWeb': True, 'timeCost': 17239}),
            "extra": json.dumps(
                {'xak': activity_dict['xak'], 'xid': int(activity_dict['xid']), 'root_xak': root_xak,
                 'root_xid': int(root_xid)}),
            "good_list": [
                {
                    "activity_id": detail['activity_id'],
                    "coupon_id": "",
                    "issue_num": 1,
                    "order_type": 1,
                    "price": detail['price'],
                    "sku_id": detail['sku_id']
                }
            ],
            "lat": self.location["lat"],
            "lng": self.location["lng"],
            "new_env": {
                "appVersion": "1.12.14",
                "cityId": "4",
                "dchn": "g83ZZzX",
                "ddfp": self.ddfp,
                "fromChannel": "5",
                "isHitButton": False,
                "isOpenWeb": True,
                "latitude": str(self.location["lat"]),
                "longitude": str(self.location["lng"]),
                "model": "MI 9 SE",
                "newAppid": "130000",
                "newTicket": self.user_info['ticket'],
                "timeCost": 17239,
                "userAgent": f"Mozilla/5.0 (Linux; Android {str(self.android_os)}; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0",
                "wifi": "2"
            },
            "nginx_cors": False,
            "open_id": "",
            "prod_key": "kf-economical-package-detail",
            "token": self.user_info['ticket'],
            "total_fee": 90,
            "xbiz": "",
            "xenv": params.get("xenv", ""),
            "xoid": self.xoid,
            "xpsid": params.get("xpsid", ""),
            "xpsid_from": params.get("xpsid_root", ""),
            "xpsid_root": params.get("xpsid_root", ""),
            "xpsid_share": "",
            "xspm_from": ""
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=data) as resp:
                print(await resp.json())

    async def submit_new(self, cover_config: dict, activity: dict):
        url = 'https://dop.hongyibo.com.cn/kcard/api/passenger/order/submit?nginx_cors=false&wsgsig=&token={}'.format(
            self.user_info['ticket'])
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "com.huaxiaozhu.rider",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://page.hongyibo.com.cn",
            "Referer": "https://page.hongyibo.com.cn"
        }
        data = {
            "app_id": 0,
            "channel": "ztyx_ms",
            "city_id": self.location["cityid"],
            "client_type": 1,
            "dchn": "g83ZZzX",
            "env": json.dumps({'dchn': 'g83ZZzX',
                               'newTicket': self.user_info['ticket'],
                               'latitude': str(self.location['lat']), 'longitude': str(self.location['lng']),
                               'cityId': str(self.location['cityid']),
                               'userAgent': f'Mozilla/5.0 (Linux; Android {str(self.android_os)}; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0',
                               'appVersion': '1.12.14', 'wifi': '2', 'model': 'MI 9 SE',
                               'ddfp': self.ddfp, 'fromChannel': '5', 'newAppid': '130000',
                               'isHitButton': False, 'isOpenWeb': True, 'timeCost': random.randint(200, 10000)},
                              separators=(',', ':')),
            "extra": json.dumps(
                {'xak': cover_config['xak'], 'xid': cover_config['xid'], 'root_xak': cover_config['root_xak'],
                 'root_xid': cover_config['root_xid']}, separators=(',', ':')),
            "good_list": [
                {
                    "activity_id": activity['activity_id'],
                    "coupon_id": "",
                    "issue_num": 1,
                    "order_type": 1,
                    "price": activity['price'],
                    "sku_id": activity['sku_id']
                }
            ],
            "lat": self.location["lat"],
            "lng": self.location["lng"],
            "new_env": {
                "appVersion": "1.12.14",
                "cityId": "4",
                "dchn": "g83ZZzX",
                "ddfp": self.ddfp,
                "fromChannel": "5",
                "isHitButton": False,
                "isOpenWeb": True,
                "latitude": str(self.location["lat"]),
                "longitude": str(self.location["lng"]),
                "model": "MI 9 SE",
                "newAppid": "130000",
                "newTicket": self.user_info['ticket'],
                "timeCost": random.randint(200, 10000),
                "userAgent": f"Mozilla/5.0 (Linux; Android {str(self.android_os)}; MI 9 SE Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 kflower.passenger/1.12.14 FusionKit/2.0.0  OffMode/0",
                "wifi": "2"
            },
            "nginx_cors": False,
            "open_id": "",
            "prod_key": "kf-economical-package-detail",
            "token": self.user_info['ticket'],
            "total_fee": 90,
            "xbiz": "",
            "xenv": "kfpassenger",
            "xoid": self.xoid,
            "xpsid": cover_config.get("xpsid", ""),
            "xpsid_from": cover_config.get("xpsid_root", ""),
            "xpsid_root": cover_config.get("xpsid_root", ""),
            "xpsid_share": "",
            "xspm_from": ""
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, json=data) as resp:
                    data = await resp.text()
                    print(data)
                    if "order_id" in data:
                        self.write_order(data)
                        return True
                    else:
                        return False
        except Exception as e:
            print(str(e))
            return False

    async def get_current_activity(self):
        try:
            params, url = await self.get_activity_html()
            activity_dict = await self.analysis_product_init(params)
            activity_ = activity_dict['xaks'][list(activity_dict['xaks'].keys())[-1]]['strategy_data']['details'][0]
            activity = self.set_current_activity(activity_)
            detail = await self.get_activity_detail(params, activity)
            return {
                "detail": detail,
                "activity": activity,
                "activity_dict": activity_dict,
                "params": params
            }
        except:
            return None

    async def get_activity_info(self):
        params, url = await self.get_activity_html()
        activity_dict = await self.analysis_product_init(params)
        activity_ = activity_dict['xaks'][list(activity_dict['xaks'].keys())[-1]]['strategy_data']['details'][0]
        # activity_dict, root_xak, root_xid = await self.analysis_activity(url)
        activity = self.set_current_activity(activity_)
        print(activity)
        # print(activity)
        detail = await self.get_activity_detail(params, activity)
        # print(detail)
        input("按下开始")
        index = 0
        while True:
            await self.submit_new(activity_dict, activity)
            time.sleep(0.2)
            index += 1
            if index >= 100:
                jx = input("是否继续?")
                if jx == "0":
                    break
                else:
                    index = 0

    def write_order(self, order_info: str):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("order_info.txt", "a+", encoding="utf-8") as f:
            f.write(f"{current_time} : {order_info}\n\n")

    def show_img_code(self, base64_str: str):
        if base64_str.startswith('data:image'):
            base64_str = base64_str.split(',', 1)[1]
        image_data = base64.b64decode(base64_str)
        image = Image.open(BytesIO(image_data))

        # 显示（会弹出一个窗口）
        image.show()

    async def run(self):
        res = await self.get_current_activity()
        cover_config = await self.cover_config(
            params=res['params'],
            activity=res['activity'],
            activity_dict=res['activity_dict']
        )
        session_start_time = datetime.datetime.strptime(res['activity']['session_start_time'],
                                                        '%Y-%m-%d %H:%M:%S') - datetime.timedelta(seconds=1)
        response = ""
        print("等待活动开始自动抢券....")
        while True:
            if datetime.datetime.now() >= session_start_time:
                break
            else:
                time.sleep(0.3)
        for i in range(400):
            response = await self.submit_new(
                cover_config=cover_config,
                activity=res['activity'],
            )
            if response:
                break
            await asyncio.sleep(0.1)
        if response:
            print("恭喜你,抢到打券", response)
        else:
            print("很遗憾,未抢到券!")
        while True:
            end = input("按0回车结束:")
            if end == "0":
                break
