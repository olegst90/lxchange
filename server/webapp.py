import re
# TODO: for Python3 it must be urlib.parse
import urlparse
import cgi

class WebCallContext:
    def __init__(self):
        self.req_post_params = {}
        self.req_get_params = {}
        self.req_headers = {}
        self.req_files = {}
        self.req_json = {}
        
        self.rsp_code = "200 OK"
        self.rsp_headers = {}

class WebApp:
    def __init__(self):
        self.urlmap = []
        self.subappmap = []
        
    def build_path_regex(self,path):
        # 1. replace <url_var> placeholders with regex capture groups
        # TODO: make capture groups named after original url var names
        path_reg = re.sub(r'<([a-zA-Z0-9]+)>',r'([a-zA-Z0-9]+)', path)
        
        # 2. replace '*'(0 or more of any chars) wildcards with respective regex
        path_reg = re.sub(r'\*',r'[a-zA-Z0-9/-]*', path_reg)
        
        # 3. replace '?' (any char) wildcards with respective regex
        path_reg = re.sub(r'\?',r'[a-zA-Z0-9/-]', path_reg)
        
        return path_reg + "$"
    
    def route(self,path,methods=[]):
        def route_decorator(handler):
            path_reg = self.build_path_regex(path)
            self.urlmap.append({"regex": path_reg, "handler" : handler, "methods": methods})
            return handler
        return route_decorator
    
    def wsgi_subapp(self, path):
        def wsgi_subapp_decorator(wsgi_app):
            path_reg = self.build_path_regex(path)
            self.subappmap.append({"regex": path_reg, "handler" : wsgi_app})
            return wsgi_app
        return wsgi_subapp_decorator
    
    def __call__(self, env, start_response):
        #print self.urlmap
        #print self.subappmap
        path = env['PATH_INFO']
        
        # first try to match path against routes of this app
        for route in self.urlmap:
            print "Trying to match {} against {}".format(route["regex"],path)
            m = re.match(route["regex"], path)
            if m is not None:
                methods = route["methods"]
                if len(methods) == 0 or env['REQUEST_METHOD'] in methods:
                    ctx = WebCallContext()
                    ctx.req_headers = dict(env['headers_raw'])
                    
                    ctx.rsp_code = '200 OK'
                    ctx.rsp_headers = {'Content-Type' : 'text/html'}
                    
                    if "QUERY_STRING" in env:
                        ctx.req_get_params = urlparse.parse_qs(env['QUERY_STRING'])
                        
                    if env['REQUEST_METHOD'] == 'POST':
                        if ctx.req_headers['Content-Type'].split(";")[0] == "multipart/form-data" \
                                                  or ctx.req_headers['Content-Type'] == "application/x-www-form-urlencoded":
                            form_data = cgi.FieldStorage(fp=env["wsgi.input"], environ=env)
                            for field in form_data:
                                if form_data[field].filename is None:
                                    ctx.req_post_params.update({field: form_data.getvalue(field)})
                                else:
                                    ctx.req_files.update({field:form_data.getvalue(field)})
                        elif ctx.req_headers['Content-Type'] == "application/json":
                            ctx.req_json = json.loads(env["wsgi.input"].read())
                    
                    res = route["handler"](ctx,*m.groups())
                    start_response(ctx.rsp_code, ctx.rsp_headers.items())
                    return res
                else:
                    start_response('405 Method Not Allowed', [('Content-Type', 'text/plain')])
                    return env['REQUEST_METHOD'] + " is not allowed on " + path
        
        # then check subapps 
        for route in self.subappmap:
            m = re.match(route["regex"], path)
            if m is not None:
                return route["handler"](env, start_response)
        
        # finally, return Not Found error if nothing has matched so far
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return path + " can't be resolved"