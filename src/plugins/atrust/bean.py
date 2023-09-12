from enum import Enum

from .tool import url_to_proxy


class Url(Enum):
    login = "https://at.njpi.edu.cn/portal/#!/login"
    center = "https://at.njpi.edu.cn/portal/service_center.html"
    qrCode = "https://open.work.weixin.qq.com/wwopen/sso/qrImg?key="  # 16位字符串
    xfbApi = "http://ykt.njpi.edu.cn:8988/web/Common/Tsm.html"
    onlineInfo = "https://at.njpi.edu.cn/passport/v1/user/onlineInfo?clientType=SDPBrowserClient&platform=Windows" \
                 "&lang=zh-CN"
    logout = "https://at.njpi.edu.cn/passport/v1/user/logout?clientType=SDPBrowserClient&platform=Windows&lang=zh-CN"

    @staticmethod
    def to_proxy(url: "Url"):
        return url_to_proxy(url.value)
