import hmac
from flask import Blueprint, request, abort

# Be extremely mindful of this. These are endpoints available without a password
whitelist_endpoints = ('siteapi.site', 'www', 'staticfiles.onionrhome', 'staticfiles.homedata', 
'staticfiles.board', 'staticfiles.profiles', 
'staticfiles.profilesindex', 
'staticfiles.boardContent', 'staticfiles.sharedContent', 
'staticfiles.mail', 'staticfiles.mailindex', 'staticfiles.friends', 'staticfiles.friendsindex',
'staticfiles.clandestine', 'staticfiles.clandestineIndex')

@app.before_request
def validateRequest():
    '''Validate request has set password and is the correct hostname'''
    # For the purpose of preventing DNS rebinding attacks
    if request.host != '%s:%s' % (self.host, self.bindPort):
        abort(403)
    if request.endpoint in whitelist_endpoints:
        return
    try:
        if not hmac.compare_digest(request.headers['token'], self.clientToken):
            if not hmac.compare_digest(request.form['token'], self.clientToken):
                abort(403)
    except KeyError:
        if not hmac.compare_digest(request.form['token'], self.clientToken):
            abort(403)

@app.after_request
def afterReq(resp):
    # Security headers
    resp = httpheaders.set_default_onionr_http_headers(resp)
    if request.endpoint == 'site':
        resp.headers['Content-Security-Policy'] = "default-src 'none'; style-src data: 'unsafe-inline'; img-src data:"
    else:
        resp.headers['Content-Security-Policy'] = "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self'; img-src 'self'; media-src 'none'; frame-src 'none'; font-src 'none'; connect-src 'self'"
    return resp