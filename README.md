# 需要的module
web3，blocknative-sdk，requests


# FollowMint

选一个狗王，跟着狗王，狗王mint啥软件自动帮你mint啥

已经自动排除非mint交易，非免费交易，已做模拟交易，模拟成功的才发送


编辑config.json里的参数：

RPC：ETH节点RPC

privateKey：私钥数组["私钥1", "私钥2"]，有几个号加几个

blocknativeKey：https://www.blocknative.com/  创建个账号，个人中心获取，每天1000次，完全够用，不需要设置，直接复制key即可

barkKey：IOS的bark软件推送key，用于推送mint成功或者失败信息（没有可以空着）

maxGasPrice：最大的GAS，超过不会跟

maxGasLimit：最大的GAS消耗，超过不会跟

follow：需要跟随的狗王地址，"follow": {"狗王地址":{"start": 开始跟单时间, "end": 结束跟单时间}}

blacklist：土狗名字黑名单，含有这些词的屏蔽

# 已打包的exe
https://github.com/Fooyao/FollowMint/releases

监控开始，又闪退的，是网络连不上blocknative，不行就用香港VPS跑，

直接提示错误的，应该是配置文件错误

# 推特
https://twitter.com/fooyao158

# Discord

https://discord.gg/mgrcUfPEF9



