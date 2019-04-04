/*
Copyright (C) 2007, 2008  Alina Friedrichsen <x-alina@gmx.net>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
*/

/*
The md5_crypt() function was ported to JavaScript from FreeBSD's libcrypt
and contains this license:
"THE BEER-WARE LICENSE" (Revision 42): 
<phk@login.dknet.dk> wrote this file.  As long as you retain this notice you 
can do whatever you want with this stuff. If we meet some day, and you think 
this stuff is worth it, you can buy me a beer in return.   Poul-Henning Kamp 
*/

function md5_to64(value, n) {
    if(typeof VarType != "undefined") {
	value = VarType.toUInt(value);
	n = VarType.toUInt(n);
    }
    
    var itoa64 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    
    var str = "";
    while(--n >= 0) {
	str += itoa64.charAt(value & 0x3f);
	value = value >> 6;
    }
    
    return str;
}

function md5_crypt(key, salt) {
    
    if (salt == null) {
        salt = '';
    }
    if(typeof VarType != "undefined") {
	key = VarType.toStr(key);
	salt = VarType.toStr(salt);
    }
    
    var old_b64pad = b64pad;
    b64pad = "";
    var old_chrsz = chrsz;
    chrsz = 8;

    var magic = "$1$";
    
    if(salt.substr(0, magic.length) == magic) {
	salt = salt.substr(magic.length);
    }

    var i = salt.indexOf("$");
    if(i < 0 || i > 8) i = 8;
    salt = salt.substr(0, i);
    
    var str = key + magic + salt;
    var hash = str_md5(key + salt + key);

    for(var i = key.length; i > 0; i -= 16) {
	if(i >= 16) {
	    str += hash;
	}
	else {
	    str += hash.substr(0, i);
	}
    }
    
    for(var i = key.length; i != 0; i = i >> 1) {
	if((i & 1) != 0) {
	    str += String.fromCharCode(0x00);
	}
	else {
	    str += key.charAt(0);
	}
    }
    
    var passwd = magic + salt + "$";
    
    hash = str_md5(str);
    for(i = 0; i < 1000; i++) {
	str = "";
	if((i & 1) != 0) str += key;
	else str += hash;
        
	if(i % 3 != 0) str += salt;
	if(i % 7 != 0) str += key;
        
	if((i & 1) != 0) str += hash;
	else str += key;
        
	hash = str_md5(str);
    }
    
    hash += hash.charAt(5);
    var value;
    for(var i = 0; i < 5; i++) {
	value = ((hash.charCodeAt(i) << 16) | (hash.charCodeAt(i + 6) << 8) | hash.charCodeAt(i + 12));
	passwd += md5_to64(value, 4);
    }
    value = hash.charCodeAt(11);
    passwd += md5_to64(value, 2);
    
    b64pad = old_b64pad;
    chrsz = old_chrsz;
    
    return passwd;
}
