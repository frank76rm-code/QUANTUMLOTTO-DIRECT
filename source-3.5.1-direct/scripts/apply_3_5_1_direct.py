#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, shutil, sys
from pathlib import Path

root=Path(sys.argv[1]).resolve()
source_root=Path(__file__).resolve().parent.parent
q=root/'quantum_lotto'; ui=q/'ui.py'; spec=root/'buildozer.spec'; config=q/'config.py'; init=q/'__init__.py'; preflight=root/'scripts/preflight.py'; manifest=root/'manifest/app_manifest.json'
runtime=source_root/'runtime/direct_entitlement.py'
for p in (ui,spec,config,init,preflight,manifest,runtime):
    if not p.exists(): raise SystemExit(f'Missing required file: {p}')
def once(s,a,b,label):
    if s.count(a)!=1: raise SystemExit(f'{label}: expected one anchor, found {s.count(a)}')
    return s.replace(a,b,1)

s=spec.read_text(); s=once(s,'version = 3.4.2','version = 3.5.1','version'); s=once(s,'android.numeric_version = 30402','android.numeric_version = 30501','versionCode'); spec.write_text(s)
s=config.read_text(); s=once(s,'VERSION = "3.4.2"','VERSION = "3.5.1"','config version'); s=once(s,'VERSION_CODE = 30402','VERSION_CODE = 30501','config code'); config.write_text(s)
s=init.read_text(); s=once(s,'__version__ = "3.4.2"','__version__ = "3.5.1"','package version'); init.write_text(s)
s=preflight.read_text(); s=once(s,"    'version = 3.4.2',","    'version = 3.5.1',",'preflight version'); s=once(s,"    'android.numeric_version = 30402',","    'android.numeric_version = 30501',",'preflight code'); s=once(s,"!=('3.4.2',30402):","!=('3.5.1',30501):",'manifest identity'); preflight.write_text(s)
m=json.loads(manifest.read_text()); m['version_name']='3.5.1'; m['version_code']=30501; m['ui_release']='3.5.1 DIRECT: licenza offline Ed25519 separata dal motore stabile 3.4.2; nessuna modifica matematica o agli archivi'; manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
shutil.copy2(runtime,q/'direct_entitlement.py')

s=ui.read_text()
s=once(s,"        def __init__(self,service,**kw):\n            super().__init__(orientation='vertical',**kw); self.service=service\n            with self.canvas.before:\n","        def __init__(self,service,**kw):\n            super().__init__(orientation='vertical',**kw); self.service=service\n            # QUANTUM LOTTO 3.5.1 DIRECT ACCESS\n            from pathlib import Path as _DirectPath\n            from .direct_entitlement import EntitlementManager\n            self._direct_entitlement=EntitlementManager(_DirectPath(self.service.db_path).parent)\n            with self.canvas.before:\n",'root entitlement')
s=once(s,"        def navigate(self,name):\n            if name not in self.sm.screen_names: return False\n            try:\n                self.sm.current=name; return True\n            except Exception as exc:\n","        def navigate(self,name):\n            if name not in self.sm.screen_names: return False\n            try:\n                from .direct_entitlement import is_android_runtime, restricted_screen\n                if is_android_runtime() and restricted_screen(name) and not self._direct_entitlement.has_full_access():\n                    self.message('VERSIONE COMPLETA','Questa funzione è disponibile nella versione completa.\\n\\nCodice dispositivo:\\n'+self._direct_entitlement.device_id+'\\n\\nConserva questo codice per l’attivazione.')\n                    return False\n            except Exception as exc:\n                detail=self.record_runtime_error('DIRECT-ACCESS',exc); self.message('Accesso non verificato',detail+'\\n\\nLa schermata corrente resta aperta.'); return False\n            try:\n                self.sm.current=name; return True\n            except Exception as exc:\n",'navigation gate')
s=once(s,"        def _import_callback(self,path):\n            if not path: return\n            clear_layout(self.report); self.report.add_widget(WrappedLabel(text='Validazione e importazione in corso…',color=GOLD))\n            self.controller.run_service_task('ql-archive-import',lambda service:service.import_file(path),self._finish_import)\n","        def _import_callback(self,path):\n            if not path: return\n            try:\n                access=self.controller._direct_entitlement.try_import_file(path)\n            except Exception as exc:\n                access=None; self.controller.record_runtime_error('DIRECT-IMPORT',exc)\n            if access is not None and access.recognized:\n                clear_layout(self.report)\n                if access.valid:\n                    self.report.add_widget(WrappedLabel(text='[b]IMPORTAZIONE COMPLETATA[/b]\\nArchivio verificato correttamente.',markup=True,color=GREEN)); self.refresh(False)\n                else: self.report.add_widget(WrappedLabel(text='Errore importazione: file non valido.',color=DANGER))\n                return\n            clear_layout(self.report); self.report.add_widget(WrappedLabel(text='Validazione e importazione in corso…',color=GOLD))\n            self.controller.run_service_task('ql-archive-import',lambda service:service.import_file(path),self._finish_import)\n",'license import')
s=once(s,"        def export_pdf(self,*_):\n            if not self._last_report or not self._last_mode:\n","        def export_pdf(self,*_):\n            try:\n                from .direct_entitlement import is_android_runtime\n                if is_android_runtime() and not self.controller._direct_entitlement.has_full_access():\n                    self.controller.message('VERSIONE COMPLETA','L’esportazione PDF è disponibile nella versione completa.\\n\\nCodice dispositivo:\\n'+self.controller._direct_entitlement.device_id); return\n            except Exception as exc:\n                self.controller.record_runtime_error('DIRECT-PDF',exc); return\n            if not self._last_report or not self._last_mode:\n",'PDF gate')
ui.write_text(s)

# Refresh the exact source checksum manifest after the deliberately limited DIRECT changes.
checksum=root/'manifest/SOURCE_FILES.sha256'; lines=[]
for p in sorted(root.rglob('*')):
    if not p.is_file(): continue
    rel=p.relative_to(root).as_posix()
    if rel=='manifest/SOURCE_FILES.sha256' or '__pycache__/' in rel or rel.endswith('.pyc'): continue
    lines.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}')
checksum.write_text('\n'.join(lines)+'\n')
print('DIRECT_3_5_1_PATCH_OK')
print('VERSION=3.5.1 VERSION_CODE=30501 PACKAGE=com.frankpetra.quantumlotto LICENSE=ED25519')
