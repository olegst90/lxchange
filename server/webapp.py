import re

class WebApp:
    def __init__(self):
        self.urlmap = []
        self.subappmap = {}
    
    def route(self,path):
        def route_decorator(handler):
            path_reg = re.sub(r'<([a-zA-Z0-9]+)>',r'([a-zA-Z0-9]+)', path) + "$"
            self.urlmap.append({"regex": path_reg, "handler" : handler})
            return handler
        return route_decorator
    
    def wsgi_subapp(self, path):
        def wsgi_subapp_decorator(wsgi_app):
            self.subappmap.update({path : wsgi_app})
            return wsgi_app
        return wsgi_subapp_decorator
    
    def __call__(self, env, start_response):
        print self.urlmap
        print self.subappmap
        path = env['PATH_INFO']
        
        # first try to match path against routes of this app
        for route in self.urlmap:
            print "Trying to match {} against {}".format(route["regex"],path)
            m = re.match(route["regex"], path)
            if m is not None:
                print m.groups()
                start_response('200 OK', [('Content-Type', 'text/html')])
                route["handler"].__globals__["reg"] = route["regex"]
                return route["handler"](*m.groups())
        
        # then check subapps 
        if path in self.subappmap:
            print "Handling {} in {}".format(path,self.subappmap[path])
            try:
                res =  self.subappmap[path](env, start_response)
            except:
                print "error occurred"
            print "Handled" + str(res)
            return res
        
        # finally, return Not Found error if nothing has matched so far
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return path + " can't be resolved"