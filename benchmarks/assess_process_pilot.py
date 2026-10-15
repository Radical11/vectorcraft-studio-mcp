"""Post-build analysis only; missing evidence never becomes agreement."""
from pathlib import Path
import argparse,json,sys
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'src'))
from workflow import read,atomic,digest
from experiment import Ledger

def packet_artifacts(packets,index):
 base=Path(packets).resolve();paths={base/'index.json'}
 for entry in index:
  p=Path(entry['packet']).resolve()
  if not p.is_relative_to(base):raise ValueError('Evaluation input escapes neutral packet root')
  paths.add(p);packet=read(p)
  if packet.get('brief'):paths.add(Path(packet['brief']).resolve())
  for variant in packet['variants'].values():
   paths.update(Path(x).resolve() for x in variant['images'])
   if variant.get('structure'):paths.add(Path(variant['structure']).resolve())
 if any(not p.is_relative_to(base) for p in paths):raise ValueError('Evaluation input escapes neutral packet root')
 return sorted(paths,key=str)

def freeze_inputs(packets,private_map):
 base=Path(packets).resolve();dest=base/'input-manifest.json'
 if dest.exists():raise ValueError('Preserve existing evaluation input binding')
 index=read(base/'index.json')
 atomic(dest,{'private_mapping_sha256':digest(private_map),
  'artifacts':[{'path':str(p.relative_to(base)),'sha256':digest(p)} for p in packet_artifacts(base,index)],
  'purpose':'Freeze actual neutral input bytes before reviews; no image judgment or authentication of perception'})
 return dest

def verify_inputs(packets,private_map,index):
 base=Path(packets).resolve();dest=base/'input-manifest.json'
 if not dest.is_file():raise ValueError('Freeze comparison inputs before collecting preferences')
 manifest=read(dest)
 try:
  actual=[{'path':str(p.relative_to(base)),'sha256':digest(p)} for p in packet_artifacts(base,index)]
  if manifest['private_mapping_sha256']!=digest(private_map) or actual!=manifest['artifacts']:
   raise ValueError('Evaluation input bytes changed after binding')
 except (FileNotFoundError,KeyError) as error:raise ValueError('Bound evaluation input unavailable or malformed') from error
 return {'path':str(dest),'sha256':digest(dest)}

def votes_by_pair(owner,expected,study):
 if owner is None:return {}
 if owner.get('study')!=study:raise ValueError('Owner response study differs')
 votes={}
 for vote in owner.get('responses',[]):
  identifier=vote.get('pair')
  if identifier not in expected or identifier in votes:raise ValueError('Unknown or duplicate owner pair')
  if vote.get('winner') not in (None,'A','B','equal','cannot_assess'):raise ValueError('Invalid owner preference')
  votes[identifier]=vote
 return votes

def assess(folder,packets,owner_path,out):
 ledger=Ledger(r,folder)
 if any(t['status'] in ('pending','building') for t in ledger.data['trials']):raise ValueError('Finish every attempt before analysis')
 pairs=read(ledger.folder/'blind-map-private.json')
 index=read(Path(packets)/'index.json')
 if len(pairs)!=12 or len(index)!=12:raise ValueError('Preserve all twelve paired units')
 identifiers={item['id'] for item in index}
 if len(identifiers)!=12:raise ValueError('Duplicate packet identity')
 expected_units={(b['id'],repeat,baseline) for b in ledger.protocol['inputs'] for repeat in (1,2)
                 for baseline in ('designer-v1','layout-blockout-v1')}
 units={(m['brief'],m['repeat'],m['baseline']) for m in pairs}
 if units!=expected_units or len(units)!=12:raise ValueError('Paired units differ from design')
 owner=read(owner_path) if owner_path else None
 votes=votes_by_pair(owner,identifiers,ledger.protocol['name'])
 binding=verify_inputs(packets,ledger.folder/'blind-map-private.json',index)
 results=[];evidence=[{'path':str(path),'sha256':digest(path)} for path in
                     (ledger.folder/'blind-map-private.json',Path(packets)/'index.json')]
 evidence.append(binding)
 if owner_path:evidence.append({'path':str(owner_path),'sha256':digest(owner_path)})
 for number,(mapping,entry) in enumerate(zip(pairs,index),1):
  packet_path=Path(entry['packet']);packet=read(packet_path);identifier=entry['id']
  evidence.append({'path':str(packet_path),'sha256':digest(packet_path)})
  if identifier!=f'pair-{number:02d}' or packet['id']!=identifier:raise ValueError('Frozen pair order differs')
  conditions={label:ledger.trial(mapping[label])['condition'] for label in ('A','B')}
  if set(conditions.values())!={'designer-process-v1',mapping['baseline']}:
   raise ValueError('Mapped conditions differ from pair')
  for label in ('A','B'):
   trial=ledger.trial(mapping[label])
   if trial['brief']!=mapping['brief'] or trial['repeat']!=mapping['repeat']:
    raise ValueError('Mapped trial differs from brief/repeat')
  full=next(label for label in ('A','B') if conditions[label]=='designer-process-v1')
  judgments={};issues=[];gain=True;clear=True
  for label in ('A','B'):
   if not packet['variants'][label]['images']:
    issues.append(f'{label} artwork unavailable');gain=False;clear=False
  expected_paths=set(packet['required_image_paths'])
  if expected_paths!={p for variant in packet['variants'].values() for p in variant['images']}:
   raise ValueError('Packet image requirements differ from available artwork')
  for role in ('communication','craft'):
   path=packet_path.parent/f'{role}-review.json'
   if not path.is_file():issues.append(f'{role} review missing');gain=False;clear=False;continue
   review=read(path);judgments[role]=review;evidence.append({'path':str(path),'sha256':digest(path)})
   if review.get('pair')!=identifier or review.get('role')!=role:raise ValueError('Review identity differs from packet')
   if review.get('winner') not in ('A','B','equal','cannot_assess'):raise ValueError('Invalid specialist preference')
   if not isinstance(review.get('visible_reason'),str) or not review['visible_reason'].strip():
    issues.append(f'{role} actual image observations missing');gain=False;clear=False
   inspected={p for action in review.get('image_actions',[]) for p in action.get('paths',[])}
   if not expected_paths.issubset(inspected):issues.append(f'{role} reported image coverage incomplete');gain=False;clear=False
   gain=gain and review['winner']==full
   regression=review.get('consequential_regression',{})
   if not isinstance(regression.get('evidence'),str) or not regression['evidence'].strip():
    issues.append(f'{role} regression evidence missing');clear=False
   if type(regression.get('present')) is not bool or regression.get('variant') not in ('A','B','neither','cannot_assess'):
    issues.append(f'{role} regression assessment missing');clear=False
   elif regression['variant']=='cannot_assess':clear=False;issues.append(f'{role} cannot assess regression')
   elif (regression['present'] and regression['variant']=='neither') or (not regression['present'] and regression['variant']!='neither'):
    clear=False;issues.append(f'{role} regression assessment inconsistent')
   elif regression['present'] and regression['variant']==full:clear=False;issues.append(f'{role} reports full-process regression')
   if review['winner']=='cannot_assess':clear=False
  vote=votes.get(identifier,{})
  if vote.get('answered') is False or vote.get('winner') not in ('A','B','equal'):
   issues.append('Owner choice missing or cannot assess');gain=False;clear=False
  else:gain=gain and vote['winner']==full
  if vote.get('regression') not in ('A','B','neither'):
   issues.append('Owner regression assessment missing or cannot assess');clear=False
  elif vote['regression']==full:issues.append('Owner reports full-process regression');clear=False
  results.append({'pair':identifier,'brief':mapping['brief'],'repeat':mapping['repeat'],
   'baseline':mapping['baseline'],'full_process_position':full,'all_three_prefer_full':gain,
   'no_consequential_full_regression_established':clear,'limitations':issues,
   'specialist_preferences':{k:v['winner'] for k,v in judgments.items()},'owner_preference':vote.get('winner')})
 default=[x for x in results if x['baseline']=='designer-v1']
 genres={next(b['genre'] for b in ledger.protocol['inputs'] if b['id']==x['brief']) for x in default if x['all_three_prefer_full']}
 count=sum(x['all_three_prefer_full'] for x in default)
 gate=count>=4 and len(genres)>=2 and all(x['no_consequential_full_regression_established'] for x in default)
 document={'study':ledger.protocol['name'],'gate':'promising' if gate else 'not_established',
 'agreement_pairs_over_default':count,'expected_default_pairs':6,'genres_with_agreement':sorted(genres),
 'independent_brief_units':3,'pairs':results,'input_evidence':evidence,
 'limitations':['Operational failures and missing responses remain in the denominator.',
 'Reported image coverage is host-attested and does not authenticate perception.',
 'This release gate is not population significance or professional-quality validation.',
 'Default promotion remains outside scope.']}
 atomic(out,document);return document

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--experiment',required=True);p.add_argument('--packets',required=True)
 p.add_argument('--owner');p.add_argument('--out',required=True);a=p.parse_args()
 result=assess(a.experiment,a.packets,a.owner,a.out)
 print(json.dumps({k:result[k] for k in ('gate','agreement_pairs_over_default','expected_default_pairs','genres_with_agreement')}))
