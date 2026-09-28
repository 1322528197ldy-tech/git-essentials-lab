"""Observable outcome checks. These never claim to prove which commands a person used."""
from pathlib import Path
import re
import subprocess

def check_exercise(repo: Path, spec: dict, state: dict, launcher: Path) -> dict:
    repo=Path(repo).resolve(); rules=spec.get('checks',{}); items=[]
    def git(*args, input=None, okay=False):
        r=subprocess.run(['git','-C',str(repo),*args],input=input,text=True,capture_output=True,timeout=30)
        if r.returncode and not okay: raise RuntimeError(r.stderr.strip() or 'Git inspection failed')
        return r
    def add(name, result, detail=''):
        items.append(dict(name=name,passed=bool(result),detail=detail))
    def trusted(ref):
        r=subprocess.run(['git','-C',str(launcher),'rev-parse','--verify',ref+'^{commit}'],text=True,capture_output=True,timeout=30)
        if r.returncode: raise RuntimeError('Trusted launcher is missing seed '+ref)
        return r.stdout.strip()
    def ancestor(ref): return git('merge-base','--is-ancestor',trusted(ref),'HEAD',okay=True).returncode==0
    def count(ref): return int(git('rev-list','--count',trusted(ref)+'..HEAD').stdout.strip())
    def read(path):
        if spec.get('graded'):
            result=git('show','HEAD:'+path,okay=True)
            return result.stdout if result.returncode==0 else ''
        p=repo/path
        if p.is_symlink() or not p.resolve().is_relative_to(repo): return ''
        return p.read_text(encoding='utf-8') if p.is_file() else ''
    def patch_id(diff):
        out=git('patch-id','--stable',input=diff).stdout.split()
        return out[0] if out else ''
    try:
        start=spec['start']
        if spec.get('graded'):
            dirty=git('status','--porcelain','--untracked-files=all').stdout.strip()
            add('All answer changes are committed',not dirty,dirty)
        if rules.get('ancestor_start'): add('Original starting history is preserved',ancestor(start),start)
        if 'interrupted_work' in rules:
            interrupted=rules['interrupted_work']; start_oid=trusted(start)
            for path in interrupted['urgent_paths']:
                changed=git('diff','--quiet',start_oid,'HEAD','--',path,okay=True).returncode==1
                committed=(git('diff','--quiet','HEAD','--',path,okay=True).returncode==0
                           and git('diff','--quiet','--cached','HEAD','--',path,okay=True).returncode==0)
                add('Urgent fix is committed: '+path,changed and committed,
                    'The urgent file must differ from the starting commit and match HEAD.')
            protected=interrupted['resume_tracked']+interrupted['resume_untracked']
            mixed=[]
            for oid in git('rev-list',start_oid+'..HEAD').stdout.split():
                touched=git('diff-tree','--root','-m','--no-commit-id','--name-only','-r',oid,'--',*protected).stdout.strip()
                if touched: mixed.append(oid[:12])
            add('Unfinished receipt and note stay out of the urgent history',not mixed,
                'Commits containing unfinished work: '+', '.join(mixed) if mixed else '')
            for path in interrupted['resume_tracked']:
                original=git('diff','--quiet',start_oid,'HEAD','--',path,okay=True).returncode==0
                resumed=git('diff','--quiet','HEAD','--',path,okay=True).returncode==1
                add('Resumed tracked work remains uncommitted: '+path,original and resumed,
                    'HEAD retains the original receipt; the resumed change belongs in the working tree.')
            for path in interrupted['resume_untracked']:
                absent=git('cat-file','-e','HEAD:'+path,okay=True).returncode!=0
                untracked=path in git('ls-files','--others','--exclude-standard','--',path).stdout.splitlines()
                add('Resumed note remains untracked: '+path,absent and untracked,
                    'The note must be outside both the commit and the index.')
        for ref in rules.get('ancestors',[]): add('Required history is included: '+ref,ancestor(ref))
        for ref in rules.get('not_ancestors',[]): add('Experimental branch tip is not merged: '+ref,not ancestor(ref))
        for path, needles in rules.get('contains',{}).items():
            text=read(path)
            for needle in needles: add('Required content: '+path,needle in text,needle)
        for path in rules.get('absent',[]):
            exists=git('cat-file','-e','HEAD:'+path,okay=True).returncode==0 if spec.get('graded') else (repo/path).exists()
            add('Excluded experimental file: '+path,not exists)
        if 'commits_since_start' in rules:
            n=count(start);add('Commit count after the starting point',n==rules['commits_since_start'],str(n))
        if 'commits_since_ref' in rules:
            c=rules['commits_since_ref'];n=count(c['ref']);add('Commit count after the new base',n==c['count'],str(n))
        if 'minimum_merges' in rules:
            n=int(git('rev-list','--count','--min-parents=2',trusted(start)+'..HEAD').stdout)
            add('Required merge structure',n>=rules['minimum_merges'],str(n)+' merge commits')
        if 'no_merges_since' in rules:
            n=int(git('rev-list','--count','--min-parents=2',trusted(rules['no_merges_since'])+'..HEAD').stdout)
            add('Rebased segment is linear',n==0,str(n)+' merge commits')
        if 'tip_message' in rules:
            message=git('log','-1','--format=%s').stdout.strip()
            add('Final commit message',message==rules['tip_message'],message)
        if rules.get('one_path_per_commit'):
            commits=git('rev-list',trusted(start)+'..HEAD').stdout.split()
            sizes=[len(git('diff-tree','--no-commit-id','--name-only','-r',c).stdout.splitlines()) for c in commits]
            add('Receipt code and documentation are separate commits',len(sizes)==2 and all(n==1 for n in sizes),str(sizes))
        for bad in rules.get('reverts',[]):
            oid=trusted(bad)
            expected=patch_id(git('diff',oid,oid+'^').stdout)
            candidates=git('rev-list','--no-merges',trusted(start)+'..HEAD').stdout.split()
            matches=[c for c in candidates if patch_id(git('show','--format=','--no-ext-diff',c).stdout)==expected]
            add('A separate inverse change undoes the bad policy',bool(expected and matches),bad)
        if 'no_wip_since' in rules:
            messages=git('log','--format=%s',trusted(rules['no_wip_since'])+'..HEAD').stdout.splitlines()
            bad=[m for m in messages if re.search(r'\bwip\b',m,re.I)]
            add('No unfinished WIP commits in the submitted segment',not bad,', '.join(bad))
        if 'path_commit_count' in rules:
            c=rules['path_commit_count'];n=int(git('rev-list','--count','--no-merges',trusted(c['since'])+'..HEAD','--',c['path']).stdout)
            add('Release checklist is one logical commit',n==c['count'],str(n))
        if 'recovery_branch' in rules:
            ref=rules['recovery_branch'];r=git('rev-parse','--verify',ref,okay=True)
            text=git('show',ref+':src/library/LoanReceipt.java',okay=True).stdout if r.returncode==0 else ''
            add('Recovery branch retains the lost receipt',r.returncode==0 and '"Borrowed: "' in text,ref+' (practice only)')
            if state.get('last_commit'):
                add('Recovery points to the original lost commit',r.stdout.strip()==state['last_commit'])
        if rules.get('lease_remote'):
            # Inspect only this workspace's local simulation, without fetching
            # objects or moving the student's remote-tracking references.
            bare=repo/'.git/lab-remotes/practice.git'
            configured=git('remote','get-url','--all','practice',okay=True)
            urls=configured.stdout.splitlines() if configured.returncode==0 else []
            expected=bare.resolve()
            original=(len(urls)==1 and not bare.is_symlink() and bare.is_dir()
                      and (repo/urls[0]).resolve()==expected)
            def remote_git(*args):
                return subprocess.run(['git','-C',str(expected),*args],text=True,
                                      capture_output=True,timeout=30)
            if original:
                is_bare=remote_git('rev-parse','--is-bare-repository')
                original=is_bare.returncode==0 and is_bare.stdout.strip()=='true'
            add('Practice remote is the original local simulation',original,
                '' if original else 'The practice remote is missing, unavailable, or changed; start a new Exercise 11 workspace.')
            remote=remote_git('rev-parse','--verify','refs/heads/practice^{commit}') if original else None
            tip=remote.stdout.strip() if remote is not None and remote.returncode==0 else ''
            head=git('rev-parse','HEAD').stdout.strip()
            old=state.get('known_initial_remote_tip','')
            add('Local HEAD matches the practice remote tip and differs from the initial tip',
                bool(tip and tip==head and head!=old),
                'Current tips only; not proof of a rewritten push or lease use.' if tip else
                'The original local simulation must have a readable refs/heads/practice tip.')
            if not state.get('remote_advanced'):
                add('Receipt commit message is complete',git('log','-1','--format=%s').stdout.strip()=='feat: improve loan receipt')
            if state.get('remote_advanced'):
                peer=state.get('advanced_remote_tip','')
                included=bool(peer) and git('merge-base','--is-ancestor',peer,'HEAD',okay=True).returncode==0
                add('Local HEAD includes the simulated teammate commit',included,
                    'Local inclusion is separate from preservation on the practice remote.')
                add('Local working tree retains the teammate note',
                    'Keep the teammate update.' in read('docs/teammate-note.md'))
                retained=False
                if not original:
                    remote_detail='Cannot verify preservation: the original local simulation is missing, unavailable, or changed.'
                elif not tip:
                    remote_detail='Cannot verify preservation: refs/heads/practice is missing or is not a readable commit.'
                elif not peer:
                    remote_detail='Cannot verify preservation: no simulated teammate commit ID was recorded.'
                elif remote_git('cat-file','-e',peer+'^{commit}').returncode!=0:
                    remote_detail='Cannot verify preservation: the recorded teammate commit is unavailable in the local simulation.'
                elif remote_git('merge-base','--is-ancestor',peer,tip).returncode!=0:
                    remote_detail='The practice tip no longer includes the recorded simulated teammate commit.'
                else:
                    remote_note=remote_git('show',tip+':docs/teammate-note.md')
                    retained=remote_note.returncode==0 and 'Keep the teammate update.' in remote_note.stdout
                    remote_detail=('Checked directly in the original local remote; fetching is not required.' if retained else
                                   'The practice tip does not contain the required committed teammate note.')
                add('The practice remote retains the simulated teammate commit and note',
                    retained,remote_detail)
        # An unfinished merge/rebase cannot count as a finished answer.
        unresolved=git('ls-files','--unmerged').stdout
        add('No unresolved index conflicts',not unresolved)
        add('No tracked conflict markers',not any(re.search(r'^(<<<<<<< |=======\s*$|>>>>>>> )',read(p),re.M)
              for p in git('ls-files','src','docs').stdout.splitlines()))
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as exc:
        add('Check could complete',False,str(exc))
    return dict(passed=all(c['passed'] for c in items),graded=spec.get('graded',False),checks=items,
                note='Checks verify observable results, not authorship or command-use history.')
