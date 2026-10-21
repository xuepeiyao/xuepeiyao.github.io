#!/usr/bin/env python3
"""Run in the user's Terminal. Upload an isolated branch and open a draft PR."""
import getpass, json, os, pathlib, subprocess, sys, time, urllib.request, urllib.parse, urllib.error, webbrowser
SOURCE=pathlib.Path(__file__).resolve().parent.parent
REPOSITORY='xuepeiyao/xuepeiyao.github.io'
def configure_network():
    """Configure only this process and its children; never change system settings."""
    # Some proxies terminate Go's HTTP/2 connections. Keep TLS verification enabled.
    debug=[item for item in os.environ.get('GODEBUG','').split(',') if item and not item.startswith('http2client=')]
    os.environ['GODEBUG']=','.join(debug+['http2client=0'])
    proxy=os.environ.get('AGNES_PROXY') or os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    if not proxy:
        config=pathlib.Path.home()/'Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml'
        if config.exists():
            import re
            match=re.search(r'^mixed-port:\s*(\d+)\s*$',config.read_text(),re.MULTILINE)
            if match and 1<=int(match.group(1))<=65535:
                proxy='http://127.0.0.1:'+match.group(1)
    if proxy:
        parsed=urllib.parse.urlparse(proxy)
        if parsed.scheme not in ('http','https') or not parsed.hostname:
            raise RuntimeError('代理地址无效；AGNES_PROXY 应为 http://主机:端口。')
        for name in ['HTTPS_PROXY','https_proxy','HTTP_PROXY','http_proxy']:os.environ[name]=proxy
        print('本次上传使用代理：'+str(parsed.hostname)+':'+str(parsed.port or 80)+'（不修改系统设置）',flush=True)
    return proxy

def verify_repository_token(token):
    url='https://api.github.com/repos/'+REPOSITORY
    for attempt in range(3):
        try:
            request=urllib.request.Request(url,headers={
                'User-Agent':'Agnes-Portfolio-Sync','Accept':'application/vnd.github+json',
                'Authorization':'Bearer '+token})
            with urllib.request.urlopen(request,timeout=30) as response:
                data=json.load(response)
            if data.get('full_name')!=REPOSITORY:
                raise RuntimeError('GitHub 返回的仓库与目标不一致，已停止。')
            if data.get('permissions',{}).get('push') is False:
                raise RuntimeError('GitHub 明确返回当前账号不能写入目标仓库，已停止。')
            return
        except urllib.error.HTTPError as error:
            try:message=json.loads(error.read(4096)).get('message','')
            except (ValueError,AttributeError):message=''
            message=str(message).replace(token,'[已隐藏]')
            if error.code==401:
                reason='令牌无效、已过期，或粘贴不完整。请检查现有令牌。'
            elif error.code==403:
                if error.headers.get('X-RateLimit-Remaining')=='0':
                    reason='GitHub API 请求额度已用尽，请稍后重试。'
                else:reason='GitHub 拒绝当前授权。请核对令牌对目标仓库的访问权限；如提示待审批，需要先完成审批。'
            elif error.code==404:
                reason='当前令牌看不到目标仓库。请核对 Resource owner 为 xuepeiyao，并已选择 xuepeiyao.github.io。'
            else:reason='GitHub 服务返回错误。'
            raise RuntimeError('仓库验证失败：HTTP '+str(error.code)+'。'+reason+(' GitHub：'+message if message else '')) from None
        except (OSError,urllib.error.URLError) as error:
            if attempt<2:
                print('仓库验证连接中断，正在重试 '+str(attempt+2)+'/3…',flush=True)
                time.sleep(2)
                continue
            detail=str(error).replace(token,'[已隐藏]')
            raise RuntimeError('仓库验证连接失败（未获得 GitHub HTTP 响应，不能认定为令牌权限错误）：'+detail) from None

def check_github_connection():
    print('检查 GitHub API 连接…',flush=True)
    last_error=None
    for attempt in range(3):
        try:
            request=urllib.request.Request('https://api.github.com/repos/'+REPOSITORY,headers={'User-Agent':'Agnes-Portfolio-Sync'})
            with urllib.request.urlopen(request,timeout=20) as response:
                if response.status!=200:raise RuntimeError('GitHub HTTP '+str(response.status))
            print('GitHub API 连接可用。',flush=True)
            return
        except (OSError,urllib.error.URLError,RuntimeError) as error:
            last_error=error
            if attempt<2:
                print('连接中断，正在重试 '+str(attempt+2)+'/3…',flush=True)
                time.sleep(2)
    raise RuntimeError('GitHub API 连接仍不可用。请先打开 Clash Verge，确认已连接可用节点，再双击桌面上传脚本。未尝试上传。错误：'+str(last_error))

def token_login(open_form=False,allow_retry=True):
    if not sys.stdin.isatty():
        raise RuntimeError('令牌只能在你本机的交互终端中隐藏输入，请双击桌面上传脚本。')
    url='https://github.com/settings/personal-access-tokens/new?'+urllib.parse.urlencode({
        'name':'Agnes portfolio upload','target_name':'xuepeiyao','expires_in':'7',
        'contents':'write','workflows':'write','pull_requests':'write'})
    print('\n使用 GitHub 官方细粒度令牌登录，不再请求设备验证码接口。',flush=True)
    print('1. 在打开的 GitHub 页面登录 xuepeiyao。',flush=True)
    print('2. Repository access 选择 Only select repositories，仅选 xuepeiyao.github.io。',flush=True)
    print('3. 确认 Contents、Workflows、Pull requests 为写入权限，点击 Generate token。',flush=True)
    print('4. 已有令牌可直接粘贴，无需重新生成；输入不会显示，也不会保存到文件。',flush=True)
    print('请勿把令牌发到聊天中。页面地址：'+url,flush=True)
    if open_form or '--new-token' in sys.argv:webbrowser.open(url)
    token=getpass.getpass('在此粘贴令牌（隐藏输入）：').strip()
    if not token or any(c.isspace() for c in token):
        raise RuntimeError('没有输入有效令牌，已停止。')
    # Pass credentials only in the child process environment, never in argv or files.
    for name in ['GH_DEBUG','GIT_TRACE','GIT_TRACE_CURL','GIT_CURL_VERBOSE']:os.environ.pop(name,None)
    previous=os.environ.get('GH_TOKEN')
    os.environ['GH_TOKEN']=token
    try:
        verify_repository_token(token)
    except BaseException as error:
        if previous is None:os.environ.pop('GH_TOKEN',None)
        else:os.environ['GH_TOKEN']=previous
        if isinstance(error,RuntimeError) and 'HTTP 401' in str(error) and allow_retry:
            print('GitHub 已拒绝该令牌。请在即将打开的官方页面创建新令牌，选择原仓库和原有三项写入权限。',flush=True)
            return token_login(open_form=True,allow_retry=False)
        raise
    print('仓库访问验证通过，开始上传开发分支；写入权限将在实际推送时核实。',flush=True)
def run(args,cwd=None,capture=False):
    return subprocess.run([str(x) for x in args],cwd=cwd,check=True,text=True,stdout=subprocess.PIPE if capture else None).stdout

def main():
    print('将上传 Agnes 新版到独立分支并创建草稿 PR。此操作不切换线上网站。',flush=True)
    run(['node','scripts/build.mjs'],SOURCE)
    run(['node','scripts/check.mjs'],SOURCE)
    configure_network()
    check_github_connection()
    from github_api import GitHubAPI, sync
    if os.environ.get('GH_TOKEN'):
        try:verify_repository_token(os.environ['GH_TOKEN'])
        except RuntimeError as error:
            if 'HTTP 401' not in str(error):raise
            os.environ.pop('GH_TOKEN',None)
            token_login(open_form=True)
    else:
        token_login()
    def replace_token():
        print('请生成一个新的7天有效期令牌，然后回到此终端粘贴。不要将令牌发到聊天中。',flush=True)
        token_login(open_form=True)
        return os.environ['GH_TOKEN']
    state=sync(SOURCE,GitHubAPI(os.environ['GH_TOKEN'],refresh_token=replace_token))
    webbrowser.open(state['pull_request'])

if __name__=='__main__':
    try:main()
    except (Exception,KeyboardInterrupt) as error:
        print('\n同步未完成：'+str(error)+'\n本地源码和原站没有被删除。',file=sys.stderr)
        sys.exit(1)
