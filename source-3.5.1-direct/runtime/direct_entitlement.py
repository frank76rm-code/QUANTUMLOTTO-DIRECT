from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

PACKAGE_ID = "com.frankpetra.quantumlotto"
LICENSE_PREFIX = "QLD2"
PUBLIC_KEY_HEX = "1C69F083A1A40A73F759F02DC3BD8516AF70D500BE201AF062C16A1949EF8048"
PUBLIC_KEY = bytes.fromhex(PUBLIC_KEY_HEX)
PERSISTED_LICENSE_NAME = ".ql_direct_entitlement"
INSTALL_ID_NAME = ".ql_install_id"

FULL_ONLY_SCREENS = frozenset({"UNIVERSALE","MULTIVERSO","BUTTERFLY","EVENTI","IEC","PRONOSTICI","SIMULAZIONE","BACKTEST","MAI_ESTRATTE"})

_Q=2**255-19
_L=2**252+27742317777372353535851937790883648493
_D=(-121665*pow(121666,_Q-2,_Q))%_Q
_I=pow(2,(_Q-1)//4,_Q)
def _inv(x): return pow(x,_Q-2,_Q)
def _xrecover(y):
    xx=(y*y-1)*_inv(_D*y*y+1)%_Q; x=pow(xx,(_Q+3)//8,_Q)
    if (x*x-xx)%_Q!=0: x=x*_I%_Q
    if x&1: x=_Q-x
    return x
_BY=4*_inv(5)%_Q; _BX=_xrecover(_BY); _B=(_BX,_BY,1,_BX*_BY%_Q)
def _add(p,q):
    x1,y1,z1,t1=p; x2,y2,z2,t2=q
    a=(y1-x1)*(y2-x2)%_Q; b=(y1+x1)*(y2+x2)%_Q; c=2*_D*t1*t2%_Q; d=2*z1*z2%_Q
    e=(b-a)%_Q; f=(d-c)%_Q; g=(d+c)%_Q; h=(b+a)%_Q
    return e*f%_Q,g*h%_Q,f*g%_Q,e*h%_Q
def _mul(p,e):
    q=(0,1,1,0)
    while e:
        if e&1: q=_add(q,p)
        p=_add(p,p); e>>=1
    return q
def _decode(s):
    if len(s)!=32: raise ValueError("point length")
    y=int.from_bytes(s,"little")&((1<<255)-1)
    if y>=_Q: raise ValueError("non-canonical point")
    x=_xrecover(y)
    if (x&1)!=(s[31]>>7): x=_Q-x
    p=(x,y,1,x*y%_Q)
    if _mul(p,_L)[:2]!=(0,1): raise ValueError("point subgroup")
    return p
def _encode(p):
    x,y,z,_=p; zi=_inv(z); x=x*zi%_Q; y=y*zi%_Q; out=bytearray(y.to_bytes(32,"little")); out[31]|=(x&1)<<7; return bytes(out)
def _verify(message,signature):
    if len(signature)!=64: return False
    try:
        renc=signature[:32]; s=int.from_bytes(signature[32:],"little")
        if s>=_L: return False
        a=_decode(PUBLIC_KEY); r=_decode(renc); h=int.from_bytes(hashlib.sha512(renc+PUBLIC_KEY+message).digest(),"little")%_L
        return secrets.compare_digest(_encode(_mul(_B,s)),_encode(_add(r,_mul(a,h))))
    except Exception: return False

def _b64u(v):
    r=v.encode("ascii"); return base64.urlsafe_b64decode(r+b"="*((4-len(r)%4)%4))
def _canonical(p): return json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
def _utc(v):
    if not v: return None
    d=datetime.fromisoformat(str(v).strip().replace("Z","+00:00")); return (d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d).astimezone(timezone.utc)
def _android_id():
    try:
        from jnius import autoclass
        A=autoclass("org.kivy.android.PythonActivity"); S=autoclass("android.provider.Settings$Secure"); a=A.mActivity
        v=S.getString(a.getContentResolver(),S.ANDROID_ID) if a else None; return str(v) if v else None
    except Exception: return None
def is_android_runtime():
    try: import android; return True
    except Exception: return False
def installation_id(storage_dir):
    storage=Path(storage_dir); storage.mkdir(parents=True,exist_ok=True); raw=_android_id(); marker=storage/INSTALL_ID_NAME
    if not raw:
        try: raw=marker.read_text(encoding="utf-8").strip()
        except Exception: raw=""
        if not raw:
            raw=uuid.uuid4().hex+secrets.token_hex(16); tmp=marker.with_suffix(".tmp"); tmp.write_text(raw,encoding="utf-8"); os.replace(tmp,marker)
    d=hashlib.sha256((PACKAGE_ID+"|"+raw).encode()).hexdigest().upper(); return "QLD-"+"-".join(d[i:i+4] for i in range(0,24,4))

@dataclass(frozen=True)
class LicenseStatus:
    recognized: bool; valid: bool; full_access: bool; role: str="FREE"; reason: str=""; license_id: str=""
class EntitlementManager:
    def __init__(self,storage_dir): self.storage_dir=Path(storage_dir); self.storage_dir.mkdir(parents=True,exist_ok=True); self.license_path=self.storage_dir/PERSISTED_LICENSE_NAME
    @property
    def device_id(self): return installation_id(self.storage_dir)
    def _validate_token(self,token,allow_unbound_developer=True):
        parts=token.strip().split(".")
        if len(parts)!=3 or parts[0]!=LICENSE_PREFIX: return LicenseStatus(False,False,False,reason="NOT_LICENSE")
        try: pb=_b64u(parts[1]); sig=_b64u(parts[2]); p=json.loads(pb.decode("utf-8"))
        except Exception: return LicenseStatus(True,False,False,reason="MALFORMED")
        if not isinstance(p,dict) or _canonical(p)!=pb: return LicenseStatus(True,False,False,reason="NON_CANONICAL")
        if not _verify(pb,sig): return LicenseStatus(True,False,False,reason="BAD_SIGNATURE")
        if p.get("schema")!=LICENSE_PREFIX or p.get("package")!=PACKAGE_ID: return LicenseStatus(True,False,False,reason="WRONG_APP")
        role=str(p.get("role") or "").upper()
        if role not in {"FULL","PERPETUAL","DEVELOPER","TESTER","PROMO"}: return LicenseStatus(True,False,False,reason="ROLE")
        device=str(p.get("device") or "")
        if device=="*":
            if not (allow_unbound_developer and role=="DEVELOPER"): return LicenseStatus(True,False,False,role=role,reason="UNBOUND_NOT_ALLOWED")
        elif device!=self.device_id: return LicenseStatus(True,False,False,role=role,reason="DEVICE_MISMATCH")
        try: nb=_utc(p.get("not_before")); ex=_utc(p.get("expires_at"))
        except Exception: return LicenseStatus(True,False,False,role=role,reason="BAD_TIME")
        now=datetime.now(timezone.utc)
        if nb and now<nb: return LicenseStatus(True,False,False,role=role,reason="NOT_YET_VALID")
        if ex and now>=ex: return LicenseStatus(True,False,False,role=role,reason="EXPIRED")
        if p.get("features") not in (["*"],"*"): return LicenseStatus(True,False,False,role=role,reason="FEATURE_SCOPE")
        return LicenseStatus(True,True,True,role=role,reason="OK",license_id=str(p.get("license_id") or ""))
    def status(self):
        try: t=self.license_path.read_text(encoding="utf-8")
        except Exception: return LicenseStatus(False,False,False,reason="NO_LICENSE")
        return self._validate_token(t)
    def has_full_access(self): return self.status().full_access
    def try_import_file(self,path):
        p=Path(path)
        try:
            if p.stat().st_size>16384: return LicenseStatus(False,False,False,reason="NOT_LICENSE")
            t=p.read_text(encoding="utf-8").strip()
        except Exception: return LicenseStatus(False,False,False,reason="NOT_LICENSE")
        if not t.startswith(LICENSE_PREFIX+"."): return LicenseStatus(False,False,False,reason="NOT_LICENSE")
        s=self._validate_token(t)
        if s.valid:
            tmp=self.license_path.with_suffix(".tmp"); tmp.write_text(t+"\n",encoding="utf-8"); os.replace(tmp,self.license_path)
        return s
def restricted_screen(name): return str(name or "").upper() in FULL_ONLY_SCREENS
