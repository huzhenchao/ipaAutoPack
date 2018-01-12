# -*- coding: utf-8 -*-
import os
import sys
import time
import hashlib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

# ==========================需要配置分割线=========================================

# 项目配置
project_name = "xxxxxx"                     # 工程名
scheme = "xxxxxx"                           # scheme
project_type = "-workspace"                 # 工程类型 pod工程 -workspace 普通工程 -project
configuration = "Release"                   # 编译模式 Debug, Release
project_path = "xxxxxx"                     # 项目根目录
pack_robot_path = "xxxxxx"                  # 打包后ipa存储目录
exportOptionsPlist = "xxxxxx/ipaAutoPack"   # 项目中的ExportOptions_*.plist的绝对目录，需要配置该文件中的teamID

# mobileprovision uuid, 不能使用 xcode 自动生成的文件
mobileprovision_uuid_dev = "xxxxxx"
mobileprovision_uuid_dis = "xxxxxx"

# 证书名称
signing_certificate_dev = "iPhone Developer: xxxxxx (xxxxxx)"
signing_certificate_dis = "iPhone Distribution: xxxxxx (xxxxxx)"

# AppStore账户信息，如果不使用, 请不要修改此处
appstore_login_name = "xxxxxx"
appstore_login_pwd = "xxxxxx"

# fir配置 如果不使用, 请不要修改此处
fir_api_token = "xxxxxx"  # firm的api token
download_address = "https://fir.im/xxxxxxxxx"   # firm 下载地址

# 蒲公英配置 优先使用fir，如果使用蒲公英，fir的配置请保持默认即可
pgyer_uKey = 'xxxxxx'
pgyer_apiKey = "xxxxxx"
pgyer_appQRCodeURL = "http://www.pgyer.com/xxxxxxxxx"    # 下载地址
pgyer_installType = 2                                   # 1：公开，2：密码安装，3：邀请安装。
pgyer_password = "12345"

# 邮件配置
app_name = ""   # App名
from_name = ""
from_addr = ""
password = ""
smtp_server = "smtp.exmail.qq.com"
to_addr = ['xx@qq.com', 'xx@126.com']

# ==========================配置结束分割线=========================================

# 用户选项, 可配置默认值，配置后将不再提示手动输入
isXcodeAutoSign = "y"
env = ""
while isXcodeAutoSign not in ["y", "n"]:
    isXcodeAutoSign = raw_input("Xcode是否勾选自动签名（y/n）: ")
while env not in ["dev", "dis"]:
    env = raw_input("请输入导出的环境类型（dev、dis）: ")

identit_profile = ""
if isXcodeAutoSign == "n":
    mobileprovision_uuid = eval("mobileprovision_uuid_" + env)
    signing_certificate = eval("signing_certificate_" + env)
    if mobileprovision_uuid.find("xxxxxx") != -1 or signing_certificate.find("xxxxxx") != -1:
        print("\033[31m请配置该环境类型的说明文件uuid和证书名称！\033[0m")
        exit(0)
    identit_profile = "CODE_SIGN_IDENTITY=\"{0}\" PROVISIONING_PROFILE=\"{1}\"".format(mobileprovision_uuid, signing_certificate)

exportOptionsPlist = exportOptionsPlist + "/ExportOptions_" + env + ".plist"


# 清理项目
def clean_project():
    print("\033[32m开始自动打包！\033[0m")
    os.system('cd %s;xcodebuild clean' % project_path)


# archive项目
def build_project():
    print("\033[32m正在编译项目\033[0m")
    os.system('cd %s;mkdir build' % project_path)
    if project_type == "-workspace":
        project_suffix_name = "xcworkspace"
    else:
        project_suffix_name = "xcodeproj"
    os.system('cd %s;xcodebuild archive %s %s.%s -scheme %s -configuration %s -archivePath %s/build/%s %s || exit' % (project_path, project_type, project_name, project_suffix_name, scheme, configuration, project_path, project_name,  identit_profile))


# 导出ipa包到自动打包程序所在目录
def export_archive_ipa():
    print("\033[32m正在导出ipa\033[0m")
    global ipa_filename
    ipa_filename = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    ipa_filename = project_name + "_" + ipa_filename
    os.system('cd %s;xcodebuild -exportArchive -archivePath %s/build/%s.xcarchive -exportPath %s/%s -exportOptionsPlist %s %s || exit' % (pack_robot_path,  project_path,  project_name,  pack_robot_path,  ipa_filename,  exportOptionsPlist,  identit_profile))


# 删除build目录
def rm_project_build():
    os.system('rm -r %s/build' % project_path)


# 上传
def upload_app():
    local_path_filename = os.path.expanduser(pack_robot_path)  # 相对路径转换绝对路径
    if os.path.exists("%s/%s" % (local_path_filename, ipa_filename)):
        ipafilepath = "%s/%s/%s.ipa" % (local_path_filename, ipa_filename, project_name)
        if env == "dev":
            if fir_api_token.find("xxxxxx") == -1:
                print("\033[32m正在上传至Fir\033[0m")
                # 直接使用fir 有问题 这里使用了绝对地址 在终端通过 which fir 获得
                os.system("fir publish '%s' --token='%s'" % (ipafilepath,  fir_api_token))
            elif pgyer_uKey.find("xxxxxx") == -1:
                print("\033[32m正在上传至蒲公英\033[0m")
                os.system('curl -F "file=@%s" -F "uKey=%s" -F "_api_key=%s" -F "installType=%s" -F "password=%s" http://www.pgyer.com/apiv1/app/upload' % (ipafilepath,  pgyer_uKey, pgyer_apiKey, pgyer_installType, pgyer_password))
        elif env == "dis":
            if appstore_login_name.find("xxxxxx") == -1:
                altoolpath = "/Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/Frameworks/ITunesSoftwareService.framework/Versions/A/Support/altool"
                print("\033[32m准备上传至AppStore - 验证App\033[0m")
                os.system('%s --validate-app -f %s -u %s -p %s -t ios --output-format xml' % (altoolpath, ipafilepath, appstore_login_name, appstore_login_pwd))
                print("\033[32m开始上传至AppStore\033[0m")
                os.system('%s --upload-app -f %s -u %s -p %s -t ios --output-format xml' % (
                    altoolpath, ipafilepath, appstore_login_name, appstore_login_pwd))
    else:
        print("\033[31m没有找到ipa文件！\033[0m")
        exit(0)


# 地址格式化
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


# 发邮件
def send_mail():
    if from_addr != "":
        print("\033[32m正在发送邮件\033[0m")
        app_url = ""
        if fir_api_token.find("xxxxxx") == -1:
            app_url = download_address
        elif pgyer_uKey.find("xxxxxx") == -1:
            app_url = pgyer_appQRCodeURL
        msg = MIMEText(app_name + " iOS客户端已经打包完毕，请前往 " + app_url + " 下载测试！如有问题，请联系iOS相关人员或者直接将问题提至Teambition，我们会及时解决，谢谢!", 'plain', 'utf-8')
        msg['From'] = _format_addr('%s''<%s>' % (from_name, from_addr))
        msg['To'] = ", ".join(_format_addr('%s' % to_addr))
        msg['Subject'] = Header(app_name + "iOS客户端自动打包程序 打包于:" + time.strftime('%Y年%m月%d日%H:%M:%S', time.localtime(time.time())), 'utf-8').encode()
        server = smtplib.SMTP(smtp_server, 25)
        server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()


# 输出包信息
def ipa_info():
    print('\n')
    local_path_filename = os.path.expanduser(pack_robot_path)  # 相对路径转换绝对路径
    print("\033[34m自动打包成功，请查看目录： %s/%s/%s.ipa\033[0m" % (local_path_filename, ipa_filename, project_name))
    print('\n')


def main():
    # 清理并创建build目录
    clean_project()
    # 编译目录
    build_project()
    # 导出ipa到机器人所在目录
    export_archive_ipa()
    # 删除build目录
    rm_project_build()
    # 上传
    upload_app()
    # 发邮件
    send_mail()
    # 输出包信息
    ipa_info()


# 执行
main()
