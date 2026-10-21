"""Upload a review branch through GitHub's API, retaining the original Git tree."""
import base64, datetime, hashlib, json, os, pathlib, time, urllib.request, urllib.error, urllib.parse
REPOSITORY='xuepeiyao/xuepeiyao.github.io'
DIRECTORIES=['.github','content','legacy','public','scripts','src','reports']
FILES=['package.json','.gitignore','README.md']

def save_json(path,data):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temporary.replace(path)

class GitHubAPI:
    def __init__(self,token,refresh_token=None):
        self.token=token;self.last_write=0
        self.refresh_token=refresh_token;self.auth_refreshes=0
    def request(self,method,path,data=None):
        if not path.startswith('/repos/'+REPOSITORY+'/') and path!='/repos/'+REPOSITORY:
            raise RuntimeError('不允许访问目标仓库以外的 API。')
        payload=json.dumps(data,ensure_ascii=True,separators=(',',':')).encode('utf-8') if data is not None else None
        for attempt in range(4):
            if method!='GET':
                delay=1.15-(time.monotonic()-self.last_write)
                if delay>0:time.sleep(delay)
                self.last_write=time.monotonic()
            request=urllib.request.Request('https://api.github.com'+path,method=method,
                data=payload,
                headers={'Authorization':'Bearer '+self.token,'User-Agent':'Agnes-Portfolio-Sync',
                         'Accept':'application/vnd.github+json','Content-Type':'application/json',
                         'X-GitHub-Api-Version':'2022-11-28','Connection':'close',
                         **({'Content-Length':str(len(payload))} if payload is not None else {})})
            try:
                with urllib.request.urlopen(request,timeout=90) as response:return json.load(response)
            except urllib.error.HTTPError as error:
                try:message=json.loads(error.read(4096)).get('message','')
                except (ValueError,AttributeError):message=''
                message=str(message).replace(self.token,'[已隐藏]')
                request_id=error.headers.get('X-GitHub-Request-Id','未提供')
                if error.code==401 and self.refresh_token is not None and self.auth_refreshes<1:
                    self.auth_refreshes+=1
                    print('GitHub 拒绝了当前令牌（HTTP 401）。上传已暂停，已完成文件保留。',flush=True)
                    replacement=self.refresh_token()
                    if not replacement:raise RuntimeError('未提供新令牌，已停止并保留上传进度。')
                    self.token=replacement
                    return self.request(method,path,data)
                if error.code==400 and 'malformed request' in message.lower() and attempt<3:
                    print('GitHub 返回临时 malformed request，重新建立连接重试 '+str(attempt+2)+'/4…',flush=True)
                    time.sleep(3*(attempt+1));continue
                retry=error.headers.get('Retry-After')
                if attempt<3 and (error.code in (429,500,502,503,504) or (error.code==403 and (retry or 'secondary rate limit' in message.lower()))):
                    pause=min(60,int(retry)) if retry and retry.isdigit() else 60
                    print('GitHub 暂时限流或繁忙，'+str(pause)+' 秒后继续；已上传文件会保留。',flush=True)
                    time.sleep(pause);continue
                reason={401:'令牌无效或已过期。',403:'授权被拒绝或请求受限，请核对 Contents / Workflows / Pull requests 写入权限。',404:'当前令牌无法访问该仓库或对象，请核对仓库选择。',422:'GitHub 拒绝当前提交数据。'}.get(error.code,'GitHub 请求失败。')
                raise RuntimeError('GitHub API HTTP '+str(error.code)+' ['+method+' '+path+']：'+reason+' '+message+' 请求编号：'+request_id) from None
            except (OSError,urllib.error.URLError) as error:
                if attempt<3:
                    print('API 连接中断，正在重试；已上传文件会保留。',flush=True);time.sleep(2+attempt*2);continue
                raise RuntimeError('GitHub API 连接中断 ['+method+' '+path+']：'+str(error).replace(self.token,'[已隐藏]')) from None

def source_files(source):
    paths=[]
    for name in DIRECTORIES:
        for path in (source/name).rglob('*'):
            relative=path.relative_to(source)
            if not path.is_file() or path.is_symlink() or '__pycache__' in relative.parts or path.name=='.DS_Store':continue
            if relative.as_posix()=='reports/remote-sync.json':continue
            paths.append(path)
    paths.extend(source/name for name in FILES)
    result=[]
    for path in sorted(paths):
        body=path.read_bytes();sha=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()
        result.append({'path':path.relative_to(source).as_posix(),'sha':sha,'size':len(body)})
    return result

def sync(source,api,cache_path=None):
    source=pathlib.Path(source)
    cache_path=pathlib.Path(cache_path or pathlib.Path.home()/'Library/Caches/agnes-github-sync/upload-blobs.json')
    state_path=source/'reports/remote-sync.json'
    entries=source_files(source)
    fingerprint=hashlib.sha256(json.dumps([item for item in entries if item['path']!='reports/checks.json'],sort_keys=True).encode()).hexdigest()
    try:cache=json.loads(cache_path.read_text())
    except (OSError,ValueError):cache={}
    if cache.get('repository')!=REPOSITORY:cache={'repository':REPOSITORY,'uploaded':[]}
    known=set(cache['uploaded']);prefix='/repos/'+REPOSITORY
    repo=api.request('GET',prefix);default=repo['default_branch']
    previous=None
    try:previous=json.loads(state_path.read_text())
    except (OSError,ValueError):pass
    reuse_branch=bool(previous and previous.get('commit') and previous.get('branch'))
    if reuse_branch:
        ref=api.request('GET',prefix+'/git/ref/heads/'+previous['branch'])
        if ref['object']['sha']!=previous['commit']:raise RuntimeError('远程开发分支已被修改，已停止以避免覆盖。')
    if reuse_branch and previous.get('fingerprint')==fingerprint:
        state=previous
        print('继续之前已上传的开发分支：'+state['branch'],flush=True)
    else:
        base_ref=previous['commit'] if reuse_branch else default
        head=api.request('GET',prefix+'/commits/'+urllib.parse.quote(base_ref,safe=''))
        oldtree=api.request('GET',prefix+'/git/trees/'+head['commit']['tree']['sha']+'?recursive=1')
        known.update(item['sha'] for item in oldtree['tree'] if item['type']=='blob')
        print('通过 GitHub API 上传 '+str(len(entries))+' 个文件（不再 clone，不使用 Git TLS）。',flush=True)
        print('首次上传约需 5～10 分钟；中断后再次运行可复用已上传文件。',flush=True)
        for index,item in enumerate(entries,1):
            if item['sha'] not in known:
                body=(source/item['path']).read_bytes()
                actual=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()
                if actual!=item['sha']:raise RuntimeError('上传过程中源文件发生改变，请重新运行。')
                try:
                    result=api.request('POST',prefix+'/git/blobs',{'content':base64.b64encode(body).decode(),'encoding':'base64'})
                except RuntimeError as error:
                    raise RuntimeError('上传文件失败：'+item['path']+'（'+str(len(body))+' 字节）。'+str(error)) from None
                if result['sha']!=item['sha']:raise RuntimeError('GitHub 文件哈希校验失败，已停止。')
                known.add(result['sha']);cache['uploaded']=sorted(known);save_json(cache_path,cache)
            if index%10==0 or index==len(entries):print('上传进度：'+str(index)+' / '+str(len(entries)),flush=True)
        tree=api.request('POST',prefix+'/git/trees',{'base_tree':head['commit']['tree']['sha'],
            'tree':[{'path':item['path'],'mode':'100644','type':'blob','sha':item['sha']} for item in entries]})
        commit=api.request('POST',prefix+'/git/commits',{'message':'Rebuild Agnes portfolio with migrated content and browser checks','tree':tree['sha'],'parents':[head['sha']]})
        branch=previous['branch'] if reuse_branch else 'rebuild/agnes-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        if reuse_branch:
            latest=api.request('GET',prefix+'/git/ref/heads/'+branch)
            if latest['object']['sha']!=previous['commit']:raise RuntimeError('开发分支已变化，已停止以避免覆盖他人修改。')
            api.request('PATCH',prefix+'/git/refs/heads/'+branch,{'sha':commit['sha'],'force':False})
            print('修复已同步到原开发分支，将重新运行 PR 检查。',flush=True)
        else:
            try:api.request('POST',prefix+'/git/refs',{'ref':'refs/heads/'+branch,'sha':commit['sha']})
            except RuntimeError as original:
                # A lost response may occur after GitHub has accepted the write.
                try:ref=api.request('GET',prefix+'/git/ref/heads/'+branch)
                except RuntimeError:raise original
                if ref['object']['sha']!=commit['sha']:raise RuntimeError('无法确认新分支状态，停止以避免覆盖。')
        state={'branch':branch,'commit':commit['sha'],'base':default,'fingerprint':fingerprint,
            'uploaded_at':datetime.datetime.now().astimezone().isoformat(),'production_changed':False,'status':'branch_uploaded'}
        save_json(state_path,state)
    query=urllib.parse.urlencode({'state':'all','head':REPOSITORY.split('/')[0]+':'+state['branch'],'base':state['base']})
    existing=api.request('GET',prefix+'/pulls?'+query)
    if existing:pr=existing[0]
    else:
        body='重建个人设计作品集：迁移32个旧项目、增加16组用户提供素材，更新个人简介并优化图片。\n\nPR工作流保留旧图、构建、检查路由，并执行 Chromium 浏览器断点与交互测试。\n\n当前为草稿，尚未确认正式发布；请勿自动合并。正式发布须先审核预览及测试结果。'
        try:pr=api.request('POST',prefix+'/pulls',{'title':'重建 Agnes 作品集并准备 GitHub Pages 部署','base':state['base'],'head':state['branch'],'body':body,'draft':True})
        except RuntimeError as original:
            try:existing=api.request('GET',prefix+'/pulls?'+query)
            except RuntimeError:raise original
            if not existing:raise original
            pr=existing[0]
    state.update({'pull_request':pr['html_url'],'status':'draft_pr_created'});save_json(state_path,state)
    print('\n上传成功：'+pr['html_url']+'\n请在 PR 的 Checks 查看远程构建和浏览器检查。线上网站未切换。',flush=True)
    return state
