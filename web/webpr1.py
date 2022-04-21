
import flask
import math
from flask import Flask, request

app = Flask(__name__, static_folder="web", static_url_path="", template_folder="templates")

@app.route('/', methods = ['GET'])
def root():
    a = request.args.get('A')
    b = request.args.get('B')
    p = request.args.get('P')
    q = request.args.get('Q')
    m = request.args.get('M')
    n = request.args.get('N')
    if a is None:
        a = 1
    else:
        a = int(a)
    if b is None:
        b = 1
    else:
        b = int(b)
    if p is None:
        p = 1
    else:
        p = int(p)
    if q is None:
        q = 1
    else:
        q = int(q)
    if m is None:
        m = 1
    else:
        m = int(m)
    if n is None:
        n = 1
    else:
        n = int(n)
    return flask.render_template(
        'index.html', a=a, b=b, p=p, q=q, m=m, n=n, GCD=gcd(a,b), EGCD=egcd(p,q), TEST=test(m), FI=fi(n)
    )

def gcd(a,b):
    while b != 0:
        a, b = b, a % b
    return a

def egcd(p, q):
    if q == 0:
        return p, 1, 0
    else:
        d, x, y = egcd(q, p % q)
        return d, y, x - y * (p // q)

def test(m):
    if (math.factorial(m-1) + 1) % m == 0 and m>1:
        return True
    else:
        return False

def fi(n):
    f = n;
    if n%2 == 0:
        while n%2 == 0:
            n = n // 2;
        f = f // 2;
    i = 3
    while i*i <= n:
        if n%i == 0:
            while n%i == 0:
                n = n // i;
            f = f // i;
            f = f * (i-1);
        i = i + 2;
    if n > 1:
        f = f // n;
        f = f * (n-1);
    return f;

if __name__ == '__main__':
   app.run(debug = True)