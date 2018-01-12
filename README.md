# ipaAutoPack
ipa自动打包（可选择开发环境和生产环境） + 上传（fir、蒲公英、appStore） + 发邮件

引用 https://github.com/huangxuan518/HXPackRobot.git 基础上做的修改

# 使用说明

1、请先配置pack.py中带有xxxxxx的部分，上传和邮件可选择配置
2、配置项目中ExportOptions_*.plist，修改teamID为Apple开发者中心用户的teamID
3、修改PackRobot.app中的执行文件路径，需用mac先打开自动操作app，选择文件->打开后编辑文件中的路径即可
4、如配置不清楚的可以参考 https://github.com/huangxuan518/HXPackRobot.git 中的说明，后续会补充

# 程序运行条件：

Python 和 fir-cli(上传fir.im时需要)

# 程序支持上传平台：

fir.im / pgyer.com(蒲公英) / AppStore

# 错误说明

## 1、选择生产环境时：
ERROR ITMS-90161: "Invalid Provisioning Profile. The provisioning profile included in the bundle com.henoo.app [Payload/henoo.app] is invalid. [Missing code-signing certificate]. A Distribution Provisioning profile should be used when submitting apps to the App Store. For more information, visit the iOS Developer Portal."

解决方法：
打开目录~/Library/MobileDevice/Provisioning Profiles 清空所有证书后重新下载，如果还不能解决，Xcode->Product->Archive手动导出后再重试


## 2、上传至appStore时：
altool[] *** Error: Exception while launching iTunesTransporter: 
Transporter not found at path: /usr/local/itms/bin/iTMSTransporter. 
You should reinstall the application.

解决方法：
建立个软链接可解决（类似于Windows的快捷方式）
ln -s /Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/itms /usr/local/itms

# 扩展

Python下载：https://www.python.org/downloads/

fir-cli 安装使用:https://github.com/FIRHQ/fir-cli/blob/master/README.md
