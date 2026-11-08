// Cairn (hiCTF) : marche dans le graphe d'isogénies supersingulières, version C rapide.
// p = 2^256 - 2^32 - 977 (premier de secp256k1), GF(p^2) = GF(p)[i]/(i^2+1).
// Usage : ./cairn [nb_etapes]  -> affiche j_T (a, b) en hexadécimal.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <openssl/sha.h>

typedef unsigned __int128 u128;
typedef struct { uint64_t v[4]; } fp;          // élément de GF(p), 4 mots little-endian
typedef struct { fp a, b; } f2;                // a + b*i
typedef struct { int xe, ye; fp c; } term;     // terme c * X^xe * Y^ye de Phi_l
#include "data.h"

#define CC 0x1000003D1ULL                      // 2^256 mod p = 2^32 + 977

/* ---------- GF(p) ---------- */
static inline void fp_fix(fp *s) {             // s in [0,2^256) -> [0,p)
    // s >= p  <=>  s + CC déborde 2^256
    fp y; u128 t = (u128)s->v[0] + CC; y.v[0] = (uint64_t)t;
    for (int k = 1; k < 4; k++) { t = (u128)s->v[k] + (uint64_t)(t >> 64); y.v[k] = (uint64_t)t; }
    if (t >> 64) *s = y;
}
static inline void fp_add(fp *r, const fp *a, const fp *b) {
    u128 t = 0; fp s;
    for (int k = 0; k < 4; k++) { t = (u128)a->v[k] + b->v[k] + (uint64_t)(t >> 64); s.v[k] = (uint64_t)t; }
    if (t >> 64) {                             // débordement : +2^256 == +CC
        t = (u128)s.v[0] + CC; s.v[0] = (uint64_t)t;
        for (int k = 1; k < 4; k++) { t = (u128)s.v[k] + (uint64_t)(t >> 64); s.v[k] = (uint64_t)t; }
    } else fp_fix(&s);
    *r = s;
}
static inline void fp_sub(fp *r, const fp *a, const fp *b) {
    fp s; uint64_t br = 0;
    for (int k = 0; k < 4; k++) {
        u128 t = (u128)a->v[k] - b->v[k] - br; s.v[k] = (uint64_t)t; br = (uint64_t)(t >> 64) & 1;
    }
    if (br) {                                  // +p == -CC (mod 2^256)
        br = 0;
        for (int k = 0; k < 4; k++) {
            u128 t = (u128)s.v[k] - (k == 0 ? CC : 0) - br; s.v[k] = (uint64_t)t; br = (uint64_t)(t >> 64) & 1;
        }
    }
    *r = s;
}
static inline void fp_mul(fp *r, const fp *a, const fp *b) {
    uint64_t w[8] = {0};
    for (int i = 0; i < 4; i++) {
        uint64_t c = 0;
        for (int j = 0; j < 4; j++) {
            u128 t = (u128)a->v[i] * b->v[j] + w[i + j] + c; w[i + j] = (uint64_t)t; c = (uint64_t)(t >> 64);
        }
        w[i + 4] = c;
    }
    // w = lo + hi*2^256 == lo + hi*CC
    fp s; uint64_t c = 0;
    for (int k = 0; k < 4; k++) { u128 t = (u128)w[4 + k] * CC + w[k] + c; s.v[k] = (uint64_t)t; c = (uint64_t)(t >> 64); }
    u128 t = (u128)c * CC + s.v[0]; s.v[0] = (uint64_t)t;
    for (int k = 1; k < 4; k++) { t = (u128)s.v[k] + (uint64_t)(t >> 64); s.v[k] = (uint64_t)t; }
    if (t >> 64) {                              // rare : encore un 2^256
        t = (u128)s.v[0] + CC; s.v[0] = (uint64_t)t;
        for (int k = 1; k < 4; k++) { t = (u128)s.v[k] + (uint64_t)(t >> 64); s.v[k] = (uint64_t)t; }
    }
    fp_fix(&s);
    *r = s;
}
static inline int fp_zero(const fp *a) { return !(a->v[0] | a->v[1] | a->v[2] | a->v[3]); }
static int fp_cmp(const fp *a, const fp *b) {
    for (int k = 3; k >= 0; k--) if (a->v[k] != b->v[k]) return a->v[k] < b->v[k] ? -1 : 1;
    return 0;
}
static void fp_pow(fp *r, const fp *a, const fp *e) {
    fp x = {{1, 0, 0, 0}};
    for (int k = 255; k >= 0; k--) { fp_mul(&x, &x, &x); if ((e->v[k / 64] >> (k % 64)) & 1) fp_mul(&x, &x, a); }
    *r = x;
}
static void fp_inv(fp *r, const fp *a) { fp_pow(r, a, &PM2); }   // Fermat : a^(p-2)

/* ---------- GF(p^2) ---------- */
static const f2 F2ZERO = {{{0}}, {{0}}};
static const f2 F2ONE = {{{1, 0, 0, 0}}, {{0}}};
static inline void f2_add(f2 *r, const f2 *x, const f2 *y) { fp_add(&r->a, &x->a, &y->a); fp_add(&r->b, &x->b, &y->b); }
static inline void f2_sub(f2 *r, const f2 *x, const f2 *y) { fp_sub(&r->a, &x->a, &y->a); fp_sub(&r->b, &x->b, &y->b); }
static inline void f2_mul(f2 *r, const f2 *x, const f2 *y) {  // Karatsuba, i^2 = -1
    fp t0, t1, s0, s1, m;
    fp_mul(&t0, &x->a, &y->a); fp_mul(&t1, &x->b, &y->b);
    fp_add(&s0, &x->a, &x->b); fp_add(&s1, &y->a, &y->b); fp_mul(&m, &s0, &s1);
    fp_sub(&r->a, &t0, &t1);
    fp_sub(&m, &m, &t0); fp_sub(&r->b, &m, &t1);
}
static inline void f2_mulfp(f2 *r, const f2 *x, const fp *c) { fp_mul(&r->a, &x->a, c); fp_mul(&r->b, &x->b, c); }
static inline int f2_zero(const f2 *x) { return fp_zero(&x->a) && fp_zero(&x->b); }
static inline void f2_neg(f2 *r, const f2 *x) { fp z = {{0}}; fp_sub(&r->a, &z, &x->a); fp_sub(&r->b, &z, &x->b); }
static inline void f2_conj(f2 *r, const f2 *x) { fp z = {{0}}; r->a = x->a; fp_sub(&r->b, &z, &x->b); }
static void f2_inv(f2 *r, const f2 *x) {      // 1/(a+bi) = (a-bi)/(a^2+b^2)
    fp n, t; fp_mul(&n, &x->a, &x->a); fp_mul(&t, &x->b, &x->b); fp_add(&n, &n, &t); fp_inv(&n, &n);
    f2 c; f2_conj(&c, x); f2_mulfp(r, &c, &n);
}

/* ---------- polynômes : arithmétique modulo f unitaire de degré n ---------- */
#define MAXD 20
static void mulmod(f2 *r, const f2 *x, const f2 *y, const f2 *f, int n) {
    f2 t[2 * MAXD], u;
    for (int k = 0; k < 2 * n - 1; k++) t[k] = F2ZERO;
    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) { f2_mul(&u, &x[i], &y[j]); f2_add(&t[i + j], &t[i + j], &u); }
    for (int k = 2 * n - 2; k >= n; k--)       // Y^n == -(f0 + ... + f_{n-1} Y^{n-1})
        for (int j = 0; j < n; j++) { f2_mul(&u, &t[k], &f[j]); f2_sub(&t[k - n + j], &t[k - n + j], &u); }
    memcpy(r, t, n * sizeof(f2));
}
static void sqrmod(f2 *r, const f2 *x, const f2 *f, int n) {
    f2 t[2 * MAXD], u;
    for (int k = 0; k < 2 * n - 1; k++) t[k] = F2ZERO;
    for (int i = 0; i < n; i++) {
        f2_mul(&u, &x[i], &x[i]); f2_add(&t[2 * i], &t[2 * i], &u);
        for (int j = i + 1; j < n; j++) { f2_mul(&u, &x[i], &x[j]); f2_add(&u, &u, &u); f2_add(&t[i + j], &t[i + j], &u); }
    }
    for (int k = 2 * n - 2; k >= n; k--)
        for (int j = 0; j < n; j++) { f2_mul(&u, &t[k], &f[j]); f2_sub(&t[k - n + j], &t[k - n + j], &u); }
    memcpy(r, t, n * sizeof(f2));
}
static void mulY(f2 *r, const f2 *x, const f2 *f, int n) {   // r = Y*x mod f
    f2 c = x[n - 1], u, t[MAXD];
    t[0] = F2ZERO;
    for (int k = 1; k < n; k++) t[k] = x[k - 1];
    for (int j = 0; j < n; j++) { f2_mul(&u, &c, &f[j]); f2_sub(&t[j], &t[j], &u); }
    memcpy(r, t, n * sizeof(f2));
}

/* ---------- polynômes ordinaires (pgcd, division) ---------- */
static int trim(f2 *a, int d) { while (d >= 0 && f2_zero(&a[d])) d--; return d; }
// pgcd sans division (pseudo-restes ; sur un corps les coefficients ne grossissent pas)
static int pgcd(f2 *out, const f2 *a0, int da, const f2 *b0, int db) {
    f2 A[MAXD], B[MAXD], u, v;
    memcpy(A, a0, (da + 1) * sizeof(f2)); memcpy(B, b0, (db + 1) * sizeof(f2));
    da = trim(A, da); db = trim(B, db);
    while (db >= 0) {
        while (da >= db) {                     // A = lc(B)*A - lc(A)*Y^(da-db)*B
            f2 la = A[da], lb = B[db]; int s = da - db;
            for (int k = 0; k <= da; k++) {
                f2_mul(&u, &A[k], &lb);
                if (k >= s) { f2_mul(&v, &B[k - s], &la); f2_sub(&u, &u, &v); }
                A[k] = u;
            }
            da = trim(A, da - 1);
            if (da < 0) break;
        }
        f2 T[MAXD]; memcpy(T, A, sizeof T); memcpy(A, B, sizeof T); memcpy(B, T, sizeof T);
        int td = da; da = db; db = td;
    }
    f2 il; f2_inv(&il, &A[da]);                // rendre unitaire
    for (int k = 0; k <= da; k++) f2_mul(&out[k], &A[k], &il);
    return da;
}
static int divexact(f2 *q, const f2 *a, int da, const f2 *g, int dg) {  // g unitaire
    f2 R[MAXD], u; memcpy(R, a, (da + 1) * sizeof(f2));
    for (int k = da - dg; k >= 0; k--) {
        q[k] = R[k + dg];
        for (int j = 0; j <= dg; j++) { f2_mul(&u, &q[k], &g[j]); f2_sub(&R[k + j], &R[k + j], &u); }
    }
    return da - dg;
}

/* ---------- recherche de racines ---------- */
static f2 ROOTS[MAXD]; static int NR;
static uint64_t rng = 0x9E3779B97F4A7C15ULL;
static uint64_t rnd(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }

// Cantor-Zassenhaus générique (secours, petits degrés) : g unitaire de degré k, scindé
static void cz_split(const f2 *g, int k) {
    if (k == 1) { f2_neg(&ROOTS[NR++], &g[0]); return; }
    for (;;) {
        f2 B[MAXD], W[MAXD], U[MAXD], Q[MAXD];
        for (int t = 0; t < k; t++) B[t] = F2ZERO;
        B[0].a.v[0] = rnd() >> 1; B[0].b.v[0] = rnd() >> 1;         // delta aléatoire
        if (k > 1) B[1] = F2ONE; else { /* unreachable */ }
        // W = (Y+delta)^((p^2-1)/2) mod g
        int top = 511; while (!((EH[top / 64] >> (top % 64)) & 1)) top--;
        memcpy(W, B, k * sizeof(f2));
        for (int e = top - 1; e >= 0; e--) {
            sqrmod(W, W, g, k);
            if ((EH[e / 64] >> (e % 64)) & 1) mulmod(W, W, B, g, k);
        }
        f2_sub(&W[0], &W[0], &F2ONE);
        int du = pgcd(U, g, k, W, k - 1);
        if (du > 0 && du < k) {
            int dq = divexact(Q, g, k, U, du);
            cz_split(U, du); cz_split(Q, dq);
            return;
        }
    }
}

static fp INVK[MAXD];
// f unitaire de degré n, sans facteur carré, totalement scindé sur GF(p^2), 0 non racine
static void roots(const f2 *f, int n) {
    NR = 0;
    if (n == 1) { f2_neg(&ROOTS[NR++], &f[0]); return; }
    f2 D[MAXD], X[MAXD], A[MAXD], AP[MAXD][MAXD], FD[MAXD], H[MAXD], u;
    // 1) D = Y^((p-1)/42) mod f   (bases = Y : multiplier par Y est quasi gratuit)
    int top = 255; while (!((E1.v[top / 64] >> (top % 64)) & 1)) top--;
    for (int k = 0; k < n; k++) D[k] = F2ZERO; D[1] = F2ONE;
    for (int e = top - 1; e >= 0; e--) { sqrmod(D, D, f, n); if ((E1.v[e / 64] >> (e % 64)) & 1) mulY(D, D, f, n); }
    // 2) Y^p = Y * D^42  (car p = 42*E1 + 1)
    f2 D2[MAXD], D3[MAXD], D7[MAXD], D21[MAXD];
    sqrmod(D2, D, f, n); mulmod(D3, D2, D, f, n); sqrmod(X, D3, f, n); mulmod(D7, X, D, f, n);
    sqrmod(X, D7, f, n); mulmod(D21, X, D7, f, n); sqrmod(X, D21, f, n); mulY(A, X, f, n);
    // 3) Frobenius : D^p = sum conj(d_k) * (Y^p)^k
    for (int k = 0; k < n; k++) AP[0][k] = F2ZERO; AP[0][0] = F2ONE;
    for (int k = 1; k < n; k++) mulmod(AP[k], AP[k - 1], A, f, n);
    for (int k = 0; k < n; k++) FD[k] = F2ZERO;
    for (int k = 0; k < n; k++) { f2 c; f2_conj(&c, &D[k]);
        for (int t = 0; t < n; t++) { f2_mul(&u, &c, &AP[k][t]); f2_add(&FD[t], &FD[t], &u); } }
    // 4) H = D^(p+1) = Y^((p^2-1)/42) : H(r) est une racine 42-ième de l'unité
    mulmod(H, D, FD, f, n);
    // 5) polynôme G(Z) = prod (Z - H(r)) via traces + identités de Newton
    f2 ps[MAXD], s[MAXD], G[MAXD], HK[MAXD];
    ps[0] = F2ZERO; ps[0].a.v[0] = n;
    for (int k = 1; k < n; k++) {               // sommes de Newton des racines de f
        f2 acc = F2ZERO; f2_mulfp(&acc, &f[n - k], &(fp){{(uint64_t)k, 0, 0, 0}});
        for (int i = 1; i < k; i++) { f2_mul(&u, &f[n - i], &ps[k - i]); f2_add(&acc, &acc, &u); }
        f2_neg(&ps[k], &acc);
    }
    memcpy(HK, H, n * sizeof(f2));
    for (int k = 1; k <= n; k++) {              // s_k = Tr(H^k)
        f2 tr = F2ZERO;
        for (int j = 0; j < n; j++) { f2_mul(&u, &HK[j], &ps[j]); f2_add(&tr, &tr, &u); }
        s[k] = tr;
        if (k < n) mulmod(HK, HK, H, f, n);
    }
    G[n] = F2ONE;
    for (int k = 1; k <= n; k++) {
        f2 acc = s[k];
        for (int i = 1; i < k; i++) { f2_mul(&u, &G[n - i], &s[k - i]); f2_add(&acc, &acc, &u); }
        f2_mulfp(&acc, &acc, &INVK[k]); f2_neg(&G[n - k], &acc);
    }
    // 6) pour chaque zeta racine de G : pgcd(f, H - zeta) isole les racines de cette classe
    int dG = n;
    for (int z = 0; z < 42 && dG > 0; z++) {
        f2 zeta = {MU[z], {{0}}};
        int mult = 0;
        for (;;) {                               // multiplicité de zeta dans G
            f2 Q[MAXD], acc = G[dG];
            for (int k = dG - 1; k >= 0; k--) { Q[k] = acc; f2_mul(&u, &acc, &zeta); f2_add(&acc, &u, &G[k]); }
            if (!f2_zero(&acc)) break;
            mult++; dG--; memcpy(G, Q, (dG + 1) * sizeof(f2));
        }
        if (!mult) continue;
        f2 W[MAXD], U[MAXD];
        memcpy(W, H, n * sizeof(f2)); f2_sub(&W[0], &W[0], &zeta);
        int du = pgcd(U, f, n, W, n - 1);
        if (du != mult) { fprintf(stderr, "classe incohérente\n"); exit(1); }
        cz_split(U, du);                         // du==1 : racine directe
    }
    if (NR != n) { fprintf(stderr, "racines manquantes %d/%d\n", NR, n); exit(1); }
}

static int cmp_f2(const void *x, const void *y) {
    const f2 *p = x, *q = y; int c = fp_cmp(&p->a, &q->a); return c ? c : fp_cmp(&p->b, &q->b);
}

int main(int argc, char **argv) {
    long T = argc > 1 ? atol(argv[1]) : TSTEPS;
    for (int k = 1; k < MAXD; k++) { fp kk = {{(uint64_t)k, 0, 0, 0}}; fp_inv(&INVK[k], &kk); }
    const term *PHI[8] = {0}; int NPHI[8] = {0};
    PHI[2] = PHI2; NPHI[2] = NPHI2; PHI[3] = PHI3; NPHI[3] = NPHI3;
    PHI[5] = PHI5; NPHI[5] = NPHI5; PHI[7] = PHI7; NPHI[7] = NPHI7;
    const int L[4] = {2, 3, 5, 7};
    f2 j = {J0A, J0B};
    for (long i = 0; i < T; i++) {
        // 1) h = SHA256( ser(j) || BE8(i) || salt )
        uint8_t buf[104], h[32];
        memcpy(buf, j.a.v, 32); memcpy(buf + 32, j.b.v, 32);     // LE32(a)||LE32(b) (x86 = little-endian)
        for (int k = 0; k < 8; k++) buf[64 + k] = (uint8_t)((uint64_t)i >> (56 - 8 * k));
        memcpy(buf + 72, SALT, 32);
        SHA256(buf, 104, h);
        int l = L[h[0] % 4];
        // 2) f(Y) = Phi_l(j, Y)
        f2 pw[9], f[MAXD], fd[MAXD], g[MAXD], fs[MAXD], u;
        pw[0] = F2ONE; for (int k = 1; k <= l + 1; k++) f2_mul(&pw[k], &pw[k - 1], &j);
        for (int k = 0; k <= l + 1; k++) f[k] = F2ZERO;
        for (int t = 0; t < NPHI[l]; t++) { f2_mulfp(&u, &pw[PHI[l][t].xe], &PHI[l][t].c); f2_add(&f[PHI[l][t].ye], &f[PHI[l][t].ye], &u); }
        int n = l + 1;
        // 3) partie sans carré : f / pgcd(f, f')
        for (int k = 1; k <= n; k++) f2_mulfp(&fd[k - 1], &f[k], &(fp){{(uint64_t)k, 0, 0, 0}});
        int dg = pgcd(g, f, n, fd, n - 1);
        int ns = n;
        if (dg > 0) ns = divexact(fs, f, n, g, dg); else memcpy(fs, f, (n + 1) * sizeof(f2));
        // 4) racines distinctes, triées (a, b)
        roots(fs, ns);
        qsort(ROOTS, NR, sizeof(f2), cmp_f2);
        j = ROOTS[h[1] % NR];
        if ((i & 0xFFFF) == 0) { fprintf(stderr, "step %ld l=%d n=%d\n", i, l, NR); }
    }
    printf("%016lx%016lx%016lx%016lx %016lx%016lx%016lx%016lx\n",
           j.a.v[3], j.a.v[2], j.a.v[1], j.a.v[0], j.b.v[3], j.b.v[2], j.b.v[1], j.b.v[0]);
    return 0;
}
