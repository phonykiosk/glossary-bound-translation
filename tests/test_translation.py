import hashlib
import json
from pathlib import Path
import re
import pytest

ROOT=Path(__file__).parents[1]
CONTRACT=str(ROOT/'glossary_bound_translation.py')
SOURCES=json.loads((ROOT/'fixtures/sources.json').read_text())
BODIES=[(ROOT/'fixtures'/s['file']).read_text(encoding='utf-8') for s in SOURCES]
SOURCE='Typing an end-of-file character (:kbd:`Control-D` on Unix, :kbd:`Control-Z` on\nWindows) at the primary prompt causes the interpreter to exit with a zero exit\nstatus.  If that doesn\'t work, you can exit the interpreter by typing the\nfollowing command: ``quit()``.'
TARGET='在主提示符中，输入文件结束符 (Unix 里是 :kbd:`Control-D`，Windows 里是 :kbd:`Control-Z`)，就会退出解释器，退出状态码为 0。 如果不能退出，还可以输入这个命令: ``quit()``。'

def deploy(vm,deploy):
    vm.warp('2026-10-21T00:00:00Z')
    return deploy(CONTRACT,sdk_version='v0.2.12')

def spec(target=TARGET):
    return {'source':{'url':SOURCES[0]['url'],'sha256':SOURCES[0]['sha256']},'target':{'url':SOURCES[1]['url'],'sha256':SOURCES[1]['sha256']},'source_language':'en','target_language':'zh-CN','clauses':[{'id':'exit','source_quote':SOURCE,'target_quote':target,'tokens':['Control-D','Control-Z','quit()'],'glossary':[{'source':'interpreter','target':'解释器'}]}]}

def serve(vm,source=BODIES[0],target=BODIES[1]):
    for s,body in zip(SOURCES,[source,target]): vm.mock_web(re.escape(s['url']),{'status':200,'body':body})

def model(vm,decision='MATCH',sq='causes the interpreter to exit with a zero exit',tq='就会退出解释器，退出状态码为 0'):
    vm.mock_llm('GLOSSARY_BOUND_TRANSLATION_V1',json.dumps({'decision':decision,'source_quote':sq,'target_quote':tq},ensure_ascii=False))

def register(vm,c,s=None):
    c.register('python',json.dumps(s or spec(),ensure_ascii=False));serve(vm);model(vm)

def assessed(vm,c):
    register(vm,c);c.assess_clause('python','exit')

def test_real_po_translation_semantics_and_sealed_receipt(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy);assessed(direct_vm,c)
    assert c.get_bundle('python')['clauses'][0]['status']=='MATCH'
    assert direct_vm.run_validator() is True
    c.seal('python');receipt=c.get_receipt('python')
    assert receipt['valid'] is True
    assert receipt['scope_sha256']==c.get_bundle('python')['scope_sha256']
    assert receipt['sealed_at']==1792540800
    assert direct_vm.run_validator() is True

def test_validator_rederives_semantics_and_grounding(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy);assessed(direct_vm,c)
    direct_vm.clear_mocks();serve(direct_vm);model(direct_vm,'UNCERTAIN')
    assert direct_vm.run_validator() is False
    model(direct_vm)
    packet=c.get_bundle('python')['clauses'][0]['assessment']
    packet['target_quote']='Fabricated target quotation never translated'
    assert direct_vm.run_validator(leader_result=packet) is False

def test_validator_refetches_actual_bytes(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy);assessed(direct_vm,c)
    direct_vm.clear_mocks();serve(direct_vm,target='changed bytes');model(direct_vm)
    assert direct_vm.run_validator() is False

def test_msgid_english_cannot_be_used_as_target(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy);s=spec(SOURCE)
    s['clauses'][0]['glossary']=[]
    register(direct_vm,c,s)
    with direct_vm.expect_revert('selected clause'): c.assess_clause('python','exit')
    assert c.get_bundle('python')['clauses'][0]['status']=='PENDING'

@pytest.mark.parametrize('decision',['MISMATCH','UNCERTAIN'])
def test_nonmatch_is_terminal_and_never_seals(direct_vm,direct_deploy,decision):
    c=deploy(direct_vm,direct_deploy);register(direct_vm,c)
    direct_vm.clear_mocks();serve(direct_vm);model(direct_vm,decision)
    c.assess_clause('python','exit')
    assert c.get_bundle('python')['clauses'][0]['status']==decision
    with direct_vm.expect_revert('already assessed'): c.assess_clause('python','exit')
    with direct_vm.expect_revert('all clauses'): c.seal('python')
    with direct_vm.expect_revert('scope already locked'): c.register('reroll',json.dumps(spec(),ensure_ascii=False))

@pytest.mark.parametrize('replacement,reason',[('Control-X','TOKEN'),('nonzero','NUMBER'),('引擎','GLOSSARY')])
def test_deterministic_invariants_override_match(direct_vm,direct_deploy,replacement,reason):
    c=deploy(direct_vm,direct_deploy)
    old={'TOKEN':'Control-Z','NUMBER':'0','GLOSSARY':'解释器'}[reason]
    # Deliberately synthetic adversarial mutation, not a claimed upstream translation.
    target=TARGET.replace(old,replacement)
    raw=BODIES[1].replace(old,replacement)
    s=spec(target);s['target']['sha256']=hashlib.sha256(raw.encode()).hexdigest()
    c.register('python',json.dumps(s,ensure_ascii=False));serve(direct_vm,target=raw);model(direct_vm)
    c.assess_clause('python','exit')
    clause=c.get_bundle('python')['clauses'][0]
    assert clause['status']=='MISMATCH' and clause['assessment']['reason']==reason
    assert direct_vm.run_validator() is True
    with direct_vm.expect_revert('all clauses'): c.seal('python')

def test_seal_refetches_and_does_not_trust_stale_assessment(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy);assessed(direct_vm,c)
    direct_vm.clear_mocks();serve(direct_vm,target='source changed')
    with direct_vm.expect_revert('SOURCE'): c.seal('python')
    assert c.get_bundle('python')['status']=='OPEN'

def test_owner_withdrawal_revokes_receipt_and_preserves_scope(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy);assessed(direct_vm,c);c.seal('python')
    from gltest.direct import create_address
    with direct_vm.prank(create_address('outside')):
        with direct_vm.expect_revert('owner only'): c.withdraw('python')
        with direct_vm.expect_revert('owner only'): c.register('other',json.dumps(spec()))
    old=c.get_receipt('python');c.withdraw('python')
    assert c.get_receipt('python')['valid'] is False
    assert c.get_receipt('python')['scope_sha256']==old['scope_sha256']
    with direct_vm.expect_revert('not open'): c.seal('python')
    with direct_vm.expect_revert('scope already locked'): c.register('again',json.dumps(spec()))

@pytest.mark.parametrize('modifier',['fuzzy','plural'])
def test_fuzzy_and_plural_targets_are_excluded(direct_vm,direct_deploy,modifier):
    c=deploy(direct_vm,direct_deploy)
    raw=('#, fuzzy\nmsgid '+json.dumps(SOURCE)+'\nmsgstr '+json.dumps(TARGET,ensure_ascii=False)+'\n') if modifier!='plural' else ('msgid "item"\nmsgid_plural "items"\nmsgstr[0] '+json.dumps(TARGET,ensure_ascii=False)+'\n')
    s=spec();s['target']['sha256']=hashlib.sha256(raw.encode()).hexdigest()
    c.register('python',json.dumps(s,ensure_ascii=False));serve(direct_vm,target=raw);model(direct_vm)
    with direct_vm.expect_revert('selected clause'): c.assess_clause('python','exit')

def test_exact_scope_and_state_guards(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy);register(direct_vm,c)
    with direct_vm.expect_revert('all clauses'): c.seal('python')
    with direct_vm.expect_revert('unknown clause'): c.assess_clause('python','undeclared')
    c.assess_clause('python','exit');c.seal('python')
    with direct_vm.expect_revert('not open'): c.assess_clause('python','exit')
    with direct_vm.expect_revert('not open'): c.seal('python')

def test_cosmetic_clause_id_and_token_order_cannot_reroll(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy);register(direct_vm,c)
    s=spec();s['clauses'][0]['id']='renamed';s['clauses'][0]['tokens'].reverse()
    with direct_vm.expect_revert('scope already locked'): c.register('renamed',json.dumps(s))
