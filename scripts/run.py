import shlex, os.path, sys, tempfile, subprocess, http.server, threading

sources = ' '.join(map(shlex.quote, map(os.path.abspath, sys.argv[1:])))

os.chdir(os.path.split(__file__)[0]+'/..')
js = os.popen('8cc/python/rop-ps4-8cc /dev/stdout librop/*.c printf/*.c ps4/*.c '+sources+' | python3 bad_hoist/rop/compiler.py /dev/stdin bad_hoist/dumps/gadgets.txt').read()

js = ('''\
try
{
%s\
}
catch(e)
{
var printf_ans = ''+e+'\\n'+e.stack;
}
'''%js).encode('utf-8')

HTML = b'''\
<html>
<body>
<script>function print(){}</script>
<script src="/exploit.js"></script>
<script src="/helpers.js"></script>
<script src="/malloc.js"></script>
<script src="/rop.js"></script>
<script src="/syscalls.js"></script>
<script src="/syscalls2.js"></script>
<script src="/c-code.js"></script>
<script>
var xxx = new XMLHttpRequest();
xxx.open("POST", "/", true);
xxx.onload = read_ptr_at.bind(window, 0);
xxx.send(printf_ans+'\\nmain() returned '+main_ret);
</script>
</body>
</html>
'''

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/': data = HTML
        elif self.path == '/c-code.js': data = js
        else:
            try: filename = {
                '/exploit.js': 'bad_hoist/exploit.js',
                '/helpers.js': 'bad_hoist/helpers.js',
                '/malloc.js': 'bad_hoist/malloc.js',
                '/rop.js': 'bad_hoist/rop/rop.js',
                '/syscalls.js': 'bad_hoist/dumps/syscalls.txt',
                '/syscalls2.js': 'build/syscall_names.txt',
            }[self.path]
            except KeyError:
                self.send_error(404)
                return
            data = open(filename, 'rb').read()
        self.send_response(200)
        self.send_header('Content-Type', 'application/javascript' if self.path.endswith('.js') else 'text/html')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)
    def do_POST(self):
        ll = int(self.headers.get('Content-Length'))
        data = self.rfile.read(ll)
        print(data.decode('utf-8'))
        self.send_error(200)
        threading.Thread(target=self.server.shutdown, daemon=True).start()

print('Navigate the PS4 web browser to port 8080 on this PC')
print('(or just press OK if you are already on error screen)')
http.server.HTTPServer(('', 8080), RequestHandler).serve_forever()
