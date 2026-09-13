/* crypto-sha256.js —— 纯 JS SHA-256 实现（零依赖，兼容 file:// 直开）
 * 用途：白名单登录（手机号哈希比对）+ 用户数据隔离前缀（hash8）
 *
 * ⚠️ 经典陷阱：JS 位移量按 mod 32 取模
 * ──────────────────────────────────────────────
 * 64 位消息长度编码时，用 >>>(j*8) 当 j≥4 时位移量回绕：
 *   l >>> 32  ≡  l >>> 0   (32 mod 32 = 0)
 *   l >>> 40  ≡  l >>> 8   (40 mod 32 = 8)
 * 这导致高 32 位污染 w[14]，使非空串哈希错误。
 * ——但空串长度=0，移位结果全为 0，恰好"自愈"，
 *   所以只测空串=正确很容易被蒙蔽。
 *
 * 修复：高低 32 位分别编码（Math.floor(l / 0x100000000) 和 l>>>0）。
 */

(function (global) {
  'use strict';
  var QuizApp = global.QuizApp || {};
  var Crypto = {};

  function rrot(x, n) {
    return (x >>> n) | (x << (32 - n));
  }

  Crypto.sha256 = function (asciiMsg) {
    // UTF-8 encoding of ASCII-safe message
    var utf8 = unescape(encodeURIComponent(String(asciiMsg || '')));
    var K = [
      0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
      0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
      0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
      0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
      0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
      0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
      0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
      0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
      0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
      0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
      0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
      0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
      0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
      0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
      0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
      0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ];
    var H = [
      0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ];

    var bytes = [];
    for (var i = 0; i < utf8.length; i++) {
      bytes.push(utf8.charCodeAt(i) & 0xff);
    }

    // Padding: append 0x80, then zeros, then 64-bit length
    var bitLen = bytes.length * 8;
    bytes.push(0x80);
    while ((bytes.length % 64) !== 56) {
      bytes.push(0);
    }

    // ── 关键：64 位长度用高低 32 位分别「大端序」编码（避开 JS >>> mod-32 陷阱）──
    // SHA-256 长度字段为 8 字节大端序：先高 32 位(lenHi)占字节 8..11，后低 32 位(bitLen)占字节 12..15。
    // ⚠️ 顺序与大端都不能错：错序/小端都会污染 w[14]/w[15] 导致非空串哈希错误，且空串(长度0)恰好被蒙蔽，只测空串极易漏检。
    var lenHi = Math.floor(bitLen / 0x100000000);
    var lenLo = bitLen >>> 0; // 低 32 位（>>>0 把关到 32 位无符号，避开 mod-32）
    // 高 32 位 → 字节 8..11（大端）
    for (var j = 3; j >= 0; j--) bytes.push((lenHi >>> (j * 8)) & 0xff);
    // 低 32 位 → 字节 12..15（大端）
    for (var j = 3; j >= 0; j--) bytes.push((lenLo >>> (j * 8)) & 0xff);

    var w = new Array(64);
    for (var chunk = 0; chunk < bytes.length; chunk += 64) {
      for (var t = 0; t < 16; t++) {
        w[t] = (bytes[chunk + t * 4] << 24) |
               (bytes[chunk + t * 4 + 1] << 16) |
               (bytes[chunk + t * 4 + 2] << 8) |
               (bytes[chunk + t * 4 + 3]);
      }
      for (t = 16; t < 64; t++) {
        var s0 = rrot(w[t - 15], 7) ^ rrot(w[t - 15], 18) ^ (w[t - 15] >>> 3);
        var s1 = rrot(w[t - 2], 17) ^ rrot(w[t - 2], 19) ^ (w[t - 2] >>> 10);
        w[t] = (w[t - 16] + s0 + w[t - 7] + s1) | 0;
      }

      var a = H[0], b = H[1], c = H[2], d = H[3];
      var e = H[4], f = H[5], g = H[6], hh = H[7];
      for (t = 0; t < 64; t++) {
        var S1 = rrot(e, 6) ^ rrot(e, 11) ^ rrot(e, 25);
        var ch = (e & f) ^ (~e & g);
        var temp1 = (hh + S1 + ch + K[t] + w[t]) | 0;
        var S0 = rrot(a, 2) ^ rrot(a, 13) ^ rrot(a, 22);
        var maj = (a & b) ^ (a & c) ^ (b & c);
        var temp2 = (S0 + maj) | 0;
        hh = g;
        g = f;
        f = e;
        e = (d + temp1) | 0;
        d = c;
        c = b;
        b = a;
        a = (temp1 + temp2) | 0;
      }

      H[0] = (H[0] + a) | 0;
      H[1] = (H[1] + b) | 0;
      H[2] = (H[2] + c) | 0;
      H[3] = (H[3] + d) | 0;
      H[4] = (H[4] + e) | 0;
      H[5] = (H[5] + f) | 0;
      H[6] = (H[6] + g) | 0;
      H[7] = (H[7] + hh) | 0;
    }

    var hex = '';
    for (var k = 0; k < 8; k++) {
      hex += ('00000000' + (H[k] >>> 0).toString(16)).slice(-8);
    }
    return hex;
  };

  // 取 SHA-256 前 8 位十六进制作为用户隔离 key（Storage 前缀用）
  Crypto.hashPrefix = function (msg) {
    return Crypto.sha256(msg).slice(0, 8);
  };

  QuizApp.Crypto = Crypto;
  global.QuizApp = QuizApp;
})(typeof window !== 'undefined' ? window : globalThis);
