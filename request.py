import json
from time import sleep

import requests
import urllib3
from loguru import logger

from util import getConfig, md5_string


class Request:
    _host = None
    _header = None

    _retry_max = None
    _enable_store = None
    _num = None
    _timeout = None

    _req_store = None

    def __init__(self, host, header):
        self._host = host
        self._header = header
        try:
            self._header['Connection']
        except KeyError:
            self._header['Connection'] = 'close'
        self._req_store = {}
        config = getConfig()
        self._retry_max = config["network_retry"]
        self._enable_store = config["enable_store_request"]
        self._num = 0
        self._timeout = 5
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _get(self, url, params=None, data=None, header=None):
        """
        get请求

        :param url:         请求路径，默认使用初始化时的host，如果http开头则不会使用初始化时的host
        :param params:      请求参数
        :param header:      请求头，默认使用初始化时设置的请求头
        :return:
        """
        try:
            if url.index("http") == 0:
                _url = url
            else:
                raise ValueError
        except ValueError:
            _url = "{0}{1}".format(self._host, url)
        _header = self._header if header is None else header
        _header_md5 = None
        _params_md5 = None
        _data_md5 = None

        if self._enable_store:
            _header_md5 = md5_string(_header)
            _params_md5 = md5_string(params)
            _data_md5 = md5_string(data)
            try:
                if self._req_store['GET'][_url][_header_md5][_data_md5][_params_md5]:
                    return self._req_store['GET'][_url][_header_md5][_data_md5][_params_md5]
            except KeyError:
                pass
        # logger.debug("Start Get {}".format(_url))
        res = requests.get(url=_url, params=params, data=data,
                           headers=_header, verify=False, timeout=self._timeout)
        # logger.debug("End Get {0}\tres={1}".format(_url, res))
        self._num += 1
        if self._enable_store:
            dic_key = ["GET", _url, _header_md5, _data_md5, _params_md5]
            temp = self._req_store
            for dk in dic_key:
                try:
                    temp[dk]
                except KeyError:
                    temp[dk] = {}
                temp = temp[dk]
            self._req_store['GET'][_url][_header_md5][_data_md5][_params_md5] = res
        return res

    def _post(self, url, data=None, params=None, header=None):
        """
        post请求

        :param url:         请求路径，默认使用初始化时的host，如果http开头则不会使用初始化时的host
        :param data:        请求数据
        :param header:      请求头，默认使用初始化时设置的请求头
        :return:
        """
        try:
            if url.index("http") == 0:
                _url = url
            else:
                raise ValueError
        except ValueError:
            _url = "{0}{1}".format(self._host, url)
        _header = self._header if header is None else header
        _header_md5 = None
        _data_md5 = None
        _params_md5 = None

        if self._enable_store:
            _header_md5 = md5_string(_header)
            _data_md5 = md5_string(data)
            _params_md5 = md5_string(params)

            try:
                if self._req_store['POST'][_url][_header_md5][_data_md5][_params_md5]:
                    return self._req_store['POST'][_url][_header_md5][_data_md5][_params_md5]
            except KeyError:
                pass
        # logger.debug("Start Post {}".format(_url))
        res = requests.post(url=_url, data=data, params=params,
                            headers=_header, verify=False, timeout=self._timeout)
        # logger.debug("End Post {0}\tres={1}".format(_url, res))
        self._num += 1
        if self._enable_store:
            dic_key = ["POST", _url, _header_md5, _data_md5, _params_md5]
            temp = self._req_store
            for dk in dic_key:
                try:
                    temp[dk]
                except KeyError:
                    temp[dk] = {}
                temp = temp[dk]
            self._req_store['POST'][_url][_header_md5][_data_md5][_params_md5] = res
        return res

    def get(self, url, params=None, data=None, header=None):
        return self.request(method="GET", url=url, params=params, data=data, header=header)

    def post(self, url, data=None, params=None, header=None):
        return self.request(method="POST", url=url, data=data, params=params, header=header)

    def request(self, method, **kwargs):
        """
        请求

        :param method:  请求方法
        :param kwargs:
        :return:
        """
        retry = 0
        try:
            res = None
            if method == "GET":
                res = self._get(**kwargs)
            elif method == "POST":
                res = self._post(**kwargs)
            if res is not None:
                res.close()
                return json.loads(res.text)
        except (requests.exceptions.ConnectionError, requests.exceptions.SSLError) as e:
            sleep(1)
            retry += 1
            if retry < self._retry_max:
                # 重试
                logger.warning(e)
                logger.warning("请求失败，正在重试... retry={}".format(retry))
                if method == "GET":
                    return self._get(**kwargs)
                if method == "POST":
                    return self._post(**kwargs)
            else:
                # 重试次数超过设置值
                logger.error(e)
                logger.info(kwargs)
                return {"errno": -1}
        except json.decoder.JSONDecodeError as e:
            logger.error(e)
            logger.info(**kwargs)
            return {"errno", -1}

    def get_num(self):
        return self._num
