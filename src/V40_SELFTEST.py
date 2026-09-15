import sys
sys.path.insert(0,'app')
import server
assert server.self_test()
a=server.calculation_accuracy({'name':'V4 Test','birth_date':'1997-03-18','birth_time':'10:20','birth_place':'Hambantota','latitude':6.1241,'longitude':81.1185,'timezone_offset':5.5,'analysis_date':'2026-09-14'})
assert a['deterministic'] is True
assert a['timezone_used']==6.0
assert server.localdb_integrity(False)['ok'] is True
print('HELA JYOTISHYA V4.0 SELF TEST: OK')
print('Signature:', a['natal_signature'])
