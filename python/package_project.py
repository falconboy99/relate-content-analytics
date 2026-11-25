"""Package self-hostable dashboard and complete reproducible project."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables';OUT.mkdir(exist_ok=True)
exclude={'tmp','deliverables','__pycache__','.git','node_modules','.venv','coverage'}
def package(name,base,prefix=''):
 files=[p for p in base.rglob('*') if p.is_file() and not any(part in exclude for part in p.relative_to(base).parts) and p.name!='.DS_Store' and not p.name.startswith('.env')]
 with ZipFile(OUT/name,'w',ZIP_DEFLATED) as z:
  for p in sorted(files):z.write(p,prefix+str(p.relative_to(base)))
 with ZipFile(OUT/name) as z:
  assert z.testzip() is None
  assert prefix+'index.html' in z.namelist() if base.name=='dist' else prefix+'README.md' in z.namelist()
 return {'name':name,'files':len(files),'bytes':(OUT/name).stat().st_size,'sha256':hashlib.sha256((OUT/name).read_bytes()).hexdigest()}
results=[package('relate-dashboard-deploy.zip',ROOT/'dist'),package('relate-complete-project.zip',ROOT,'relate-analytics/')]
(OUT/'manifest.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
