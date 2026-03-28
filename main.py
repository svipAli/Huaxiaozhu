import json
import asyncio
from Huaxiaozhu import HuaXiaoZhuCar

if __name__ == '__main__':
    phone = input("请输入手机号码:")
    hxz = HuaXiaoZhuCar(phone)
    city = input("请输入城市:")
    hxz.set_location(city)
    while True:
        sms_result = hxz.get_sms_code()
        if sms_result is None:
            input("发送短信验证码失败,按下回车退出....")
            exit(0)
        if "图形验证码" not in sms_result:
            break
        else:
            img = hxz.get_captcha()
            if img is None:
                input("获取图形验证码失败,按下回车退出....")
                exit(0)
            hxz.show_img_code(img)
            img_code = input("请输入图形验证码:")
            hxz.verify_captcha(img_code)
    code = input("请输入短信验证码:")
    result = hxz.sms_login(code)
    hxz.set_user_info(json.dumps(result))
    loop = asyncio.new_event_loop()
    loop.run_until_complete(hxz.run())
