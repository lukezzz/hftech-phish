tags_metadata = [
    {
        "name": "auth",
        "description": "用户认证相关。 普通用户登陆后返回cookie，api用户使用token",
        "externalDocs": {
            "description": "Notion文档",
            "url": "https://www.notion.so/app-aaa-0dc930056d2a44d3b713f4e445634116",
        },
    },
    {
        "name": "user_account_mgmt",
        "description": "系统和普通用户账号管理，权限管理.",
    },
]


openapi_auth_login = {
    "summary": "用户登陆和获取api token",
    "description": """
使用表单(form)进行登陆

## 权限

1. 任意

    """,
}

openapi_auth_logout = {
    "summary": "用户登出",
    "description": """
使用合法的cookie或token， 登出后jwt id将进入黑名单

## 权限

1. admin, api

    """,
}

openapi_auth_self = {
    "summary": "获取当前用户信息",
    "description": """
获取当前user相关信息

## 权限

1. admin, api

    """,
}

openapi_user_account_mgmt_role = {
    "summary": "获取系统角色列表",
    "description": """


## 权限

1. admin, api

    """,
}

openapi_user_account_mgmt_create = {
    "summary": "新建用户账号",
    "description": """


## 权限

1. admin

    """,
}

openapi_user_account_mgmt_search = {
    "summary": "获取/搜索用户并返回列表",
    "description": """

query: ElasticSearch syntax for search in SQLAlchemy

## 权限

1. admin, api

    """,
}


openapi_user_account_mgmt_get_by_user_id = {
    "summary": "通过id获取用户信息",
    "description": """


## 权限

1. admin, api

    """,
}

openapi_user_account_mgmt_delete_by_user_id = {
    "summary": "通过id删除用户信息",
    "description": """


## 权限

1. admin

    """,
}

openapi_user_account_mgmt_edit_by_user_id = {
    "summary": "编辑当前用户信息",
    "description": """


## 权限

1. admin, api

    """,
}

openapi_call_trigger = {
    "summary": "触发呼叫",
    "description": """
## 权限

1. admin, api

    """,
}

openapi_call_cdr = {
    "summary": "获取cdr(呼叫详细)列表",
    "description": """
## 权限

1. admin, api
        
    """,
}


openapi_sms_mock = {
    "summary": "短信测试模拟",
    "description": """

## 权限

1. admin, api

    """,
}

openapi_sms_trigger = {
    "summary": "发送短信",
    "description": """

## 权限

1. admin, api

    """,
}

openapi_config_upload_default_tts_file = {
    "summary": "上传默认tts文件",
    "description": """

## 权限

1. admin

## 上传内容
> 🚧 音频文件格式必须为 mp3或wav

    """,
}

openapi_config_add_ali_api = {
    "summary": "添加ali tts api配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_patch_ali_api = {
    "summary": "修改ali tts api配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_delete_ali_api = {
    "summary": "删除ali tts api配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_list_ali_api = {
    "summary": "返回ali tts api配置列表",
    "description": """

## 权限

1. admin

    """,
}


openapi_config_renew_ali_api_token = {
    "summary": "更新ali app token",
    "description": """

## 权限

1. admin

> 🚧 token有效期24小时，通过airlfow自动更新


    """,
}


openapi_config_add_baidu_api = {
    "summary": "添加baidu tts api配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_patch_baidu_api = {
    "summary": "修改baidu tts api配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_delete_baidu_api = {
    "summary": "删除baidu tts api配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_list_baidu_api = {
    "summary": "返回baidu tts api配置列表",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_add_cucm_config = {
    "summary": "添加cucm config配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_patch_cucm_config = {
    "summary": "修改cucm config配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_delete_cucm_config = {
    "summary": "删除cucm config配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_list_cucm_config = {
    "summary": "返回cucm config配置列表",
    "description": """

## 权限

1. admin

    """,
}


# call
openapi_config_add_call_config = {
    "summary": "添加call配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_patch_call_config = {
    "summary": "修改call配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_delete_call_config = {
    "summary": "删除call配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_list_call_config = {
    "summary": "返回call配置列表",
    "description": """

## 权限

1. admin

    """,
}


# sms
openapi_config_add_sms_config = {
    "summary": "添加sms配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_patch_sms_config = {
    "summary": "修改sms配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_delete_sms_config = {
    "summary": "删除sms配置",
    "description": """

## 权限

1. admin

    """,
}

openapi_config_list_sms_config = {
    "summary": "返回sms配置列表",
    "description": """

## 权限

1. admin

    """,
}
