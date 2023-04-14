def call_message_format(message:str):
    if ":" in message and "LASTVALUE" in message:
        return  "【星巴克统一告警平台】"+("".join(message.split(":")[1:])).split("LASTVALUE")[0]
    return "【星巴克统一告警平台】"+message