from random import randint
from gmpy2 import powmod, invert, mpz
from math import ceil, floor, sqrt, gcd
from sympy.ntheory import factorint

# really lazily refactored

def expmod(b, e, m):
    '''wrapper for gmpy2 powmod - don't want to have to convert from mpz every time'''
    return int(powmod(b,e,m))

def euler(n, p):
    '''eulers criterion - an integer n (< prime p) is a quadratic residue mod p if and only if n^{(p-1)/2} = 1 mod p'''
    x = expmod(n, (p-1)//2, p)
    return -1 if x > 1 else x

def ascii_encode(msg):
    '''returns string of ascii characters representing string msg''' 
    return ''.join([str(ord(msg[i])).rjust(3,'0') for i in range(len(msg))])


class ECC():
    '''helper class for elliptic curve cryptography \\
    uses as reference frame the curve y^2 = x^3 + ax + b over F_p'''
    def __init__(self, p, a, b, N = None, kf = 1000, bound=3):
        self.p = p
        self.a = a
        self.b = b
        self.kf = kf
        self.bound = bound

        if N is None: # allow precomputing of this since it takes a while
            self.N = self.bsgs(p,a,b)
        else:
            self.N = N

    def tonellishanks(self, n):
        '''given a quadratic residue n mod p, returns an r such that r^2 is congruent to n mod p'''
        p = self.p
        S = 1
        Q = (p-1)//(2**S)
        while (Q % 2 == 0):
            S += 1
            Q //= 2
        while True:
            z = randint(2,p)
            while (euler(z,p) != -1): #find nonresidue (half of the values are nonresidues - shouldnt be hard)
                z = randint(2,p)
            M = S
            c = expmod(z, Q, p)
            t = expmod(n, Q, p)
            if t == p - 1:
                return False # bad n value (why does this occasionally happen?)
            R = expmod(n, (Q+1)//2, p) # note Q odd, so Q+1/2 even
            while True:
                if t == 0: return 0
                if t == 1: return R
                else: 
                    i = 1
                    while expmod(t, 2**i, p) != 1:
                        if i > M:
                            return False
                        i += 1
                    b = expmod(c, 2**(M-i-1), p)
                    M = i 
                    c = b**2 % p
                    t = t*c % p 
                    R = R*b % p


    def randpoint(self):
        '''finds a pair (r,y) by picking a random integer r such that \\
            y^2 = r^3 + a*r + b \\
            is a residue mod p and performs tonelli shanks algo\\
            to find a suitable y'''
        p = self.p
        a = self.a
        b = self.b
        while True:
            r = randint(2,p)
            while (euler(((expmod(r,3,p) + a*r + b) % p), p) != 1):
                r = randint(2,p)
            y = self.tonellishanks(p, ((expmod(r,3,p) + a*r + b) % p))
            if y is False:
                continue
            return (r,y)
        

    def lcm(a,b):
        return a*b//gcd(a,b)


    def pt_add(self, P, Q):
        '''implementation of the elliptic curve group law\\
            returns the sum P + Q'''
        a = self.a
        p = self.p
        if (P == (0,0)):
            return Q
        if (Q == (0,0)):
            return P
        if (P[0] == Q[0]): 
            if ((P[1] == 0 and Q[1] == 0) or (P[1] + Q[1]) % p == 0): # either P = Q, or Py = -Qy - in either case, sum is 0
                return (0,0)
            #elif (P[1] + Q[1]) % p == 0:
            #    return (P[0], p-Q[0])
            else:
                s = ((3*P[0]*P[0] + a) * invert(mpz(2*P[1]), mpz(p))) % p
        else:
            s = ((Q[1] - P[1]) * invert(mpz(Q[0] - P[0]), mpz(p))) % p
        x = (s*s - P[0] - Q[0]) % p
        return ((int(x), int((-(P[1] + s * (x - P[0]))) % p)))

    def pt_scal(self, P, n):
        a = self.a
        p = self.p
        '''more efficient way to perform successive iterations of P + P + ... + P = nP'''
        if n == 0: return (0,0)
        elif n == 1: 
            return P
        elif n % 2 == 1: 
            return self.pt_add(P, self.pt_scal(P, n-1))
        else: 
            return self.pt_scal(self.pt_add(P, P), n/2)

    def bsgs(self):
        '''baby-steps giant-steps algorithm implementation \\ 
        computes cardinality of the elliptic curve y^2 = x^3 + a*x + b over the field F_p with p elements'''
        p = self.p
        a = self.a
        b = self.b
        m = ceil(p**(1/4))
        steps = 0
        while True:
            steps += 1
            P = self.randpoint()
            print('starting calculation with point', P)
            Pl = [(0,0),]
            for j in range(1,m+1):
                Pl.append(self.pt_add(Pl[j-1], P))
            # print('generated list')
            Q = self.pt_scal(P, p+1)
            # print('Q = {}'.format(Q))
            tmP = self.pt_scal(P, 2*m)
            #print('2mP = {}'.format(tmP))
            k = 0
            Qk = Q
            M = 0
            reset = False
            # print('calculating M')
            while M == 0:
                if k > 100000: #reset - unlucky
                    reset = True
                    break
                l1 = [point[0] for point in Pl]
                l2 = [p - point[0] for point in Pl]
                j = -1
                try:
                    j = l1.index(Qk[0])
                except:
                    pass
                try:
                    j = l2.index(Qk[0])
                except:
                    pass
                if j != -1:
                    M = p + 1 + 2*m*k - j
                    if self.pt_scal(P,M) == (0,0): # can just check both pretty efficiently (if its the lower one, it certainly cant be the higher one unless p = 3 or something ridiculous)
                        break
                    else:
                        M += 2*j
                        break
                k += 1
                Qk = self.pt_add(Qk, tmP)
            if reset:
                continue
            print('M calculated', M)
            factors = list(factorint(M).keys())
            i = 0
            while (i < len(factors)):
                if self.pt_scal(P, M//factors[i]) == (0,0):
                    M = M//factors[i]
                else:
                    i += 1
            print('M reduced', M)
            count = 0
            N = 0
            print('testing interval ({}, {})'.format(floor(p + 1 - 2*sqrt(p)), ceil(p+1+2*sqrt(p))+1))
            for i in range(floor(p + 1 - 2*sqrt(p)), ceil(p+1+2*sqrt(p))+1): # cardinality of the ec must be in this interval - can narrow it down to one of them using lagrange
                if i % M == 0:
                    count += 1
                    N = i
            if count == 1:
                print('steps required:', steps)
                return N

    def msg_bound(self):
        '''koblitz encoding with prime p allows encoding of msg blocks < p/kf - 1 - return the number of digits allowed'''
        return len(str(self.p//self.kf-1))-1

    def block_to_point(self, block):
        p = self.p
        a = self.a
        b = self.b
        kf = self.kf
        '''encodes block of characters into points on elliptic curve using koblitz method \\
            note this can fail with probability roughly 2^{-kf} for each msg block, as roughly half of values are residues mod p'''
        for r in range(kf*block, kf*(block+1)): # find suitable point 
            x = (expmod(r, 3, p) + a*r + b) % p
            ys = expmod(x, ((p+1)//2), p) 
            if euler(x,p) == 1 and euler(ys,p) == 1: # check that x and x^(p+1)/2 is a quadratic residue
                y = self.tonellishanks(ys) # use tonelli shanks again to find y
                if y is False:
                    continue
                return (r,y)
            
    def ascii_blocks(self, msg):
        '''splits string into (integer) blocks of at most bound digits'''
        bound = self.bound
        blocks = []
        while len(msg) >= bound: # break up msgs into chunks smaller than bound
            blocks.append(int(msg[:bound]))
            msg = msg[bound:]

        if len(msg) > 0: # there may be up to (bound-1) characters left - add those
            blocks.append(int(msg))
        return blocks

    def encode(self, msg):
        return [self.block_to_point(block) for block in self.ascii_blocks(ascii_encode(msg))]
    


    def generate_key_pair(self): # TODO do i need to allow custom keys in class dec?
        N = self.N
        pu = randint(N//20, N)
        while gcd(pu,N) != 1:
            pu = randint(N//20, N)
        pr = int(invert(mpz(pu), mpz(N)))
        return (pu, pr)

    def encrypt(self, points, key):
        return [self.pt_scal(point, key) for point in points]

    def decode(self, points):
        kf = self.kf
        bound = self.bound
        ascii = ''.join([str(point[0] // kf).rjust(bound, '0') for point in points[:-1]] + [str(points[-1][0] // kf)])
        out = ''
        ind = 0
        while ind+2 <= len(ascii):
            out += chr(int(ascii[ind:ind+3]))
            ind += 3
        return out
