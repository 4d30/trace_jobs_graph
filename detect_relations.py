#!/usr/bin/env python

import os
import sys
from itertools import islice
from itertools import cycle
import subprocess

import cafs
import trace_index as index
import rels


def generate_candidates(rec):
    candidate_query = {}
    if 'url' in rec:
        candidate_query['url'] = (rec['url'],)
    else:
        return []
    candidate_cids = True
    page_no = 0
    while candidate_cids:
        if page_no > 1:
            break
        candidate_cids = index.search(candidate_query, matchall=False,
                                      page_no=page_no, page_size=100)
        if candidate_cids:
            yield from candidate_cids
        page_no += 1


def match_factory(record):
    def predicate(candidate_cid):
        candidate = cafs.get(candidate_cid)
        if candidate is None:
            return False
        c_url = candidate.get('url', None)
        if c_url is not None:
            return record['url'] == candidate['url']
        else:
            return False
    return predicate


def get_btime(cid):
    path = cafs.get_cid_path(os.getenv('CAFS_ROOT'), cid)
    return float(subprocess.check_output(["stat", "--format=%W", path],
                                         text=True, ).strip())


def earliest_cid(cids):
    return min(cids, key=get_btime)


def process(cafs_cid):
    rec = cafs.get(cafs_cid)
    # predicate = match_factory(rec)
    candidate_cids = generate_candidates(rec)
    # candidate_cids = filter(predicate, candidate_cids)
    matches = tuple(candidate_cids)
    if matches:
        abstraction_cid = earliest_cid(matches)
    else:
        abstraction_cid = cafs_cid
        matches = (cafs_cid,)
    for match_cid in matches:
        rels.put(match_cid, abstraction_cid)
    return matches


def batch_new_observations():

    cafs_records = cafs.walk()
    cafs_records = map(os.path.basename, cafs_records)
    #cafs_records = islice(cafs_records, 2000)    

    rels_records = rels.walk()

    cafs_cid = next(cafs_records, None)
    rels_cid = next(rels_records, None)

    assigned = set()

    twiddle = cycle(('/', '-', '\\', '|', ))
    while cafs_cid is not None:
        sys.stdout.write(f'{next(twiddle)}\r')
        if cafs_cid in assigned:
            cafs_cid = next(cafs_records, None)
            continue

        if rels_cid is None or cafs_cid < rels_cid:
            matches = process(cafs_cid)
            assigned.update(matches)
            cafs_cid = next(cafs_records, None)

        elif cafs_cid > rels_cid:
            rels_cid = next(rels_records, None)

        else:
            cafs_cid = next(cafs_records, None)
            rels_cid = next(rels_records, None)
    rels.build()


def main():
    import time
    t0 = time.time()
    batch_new_observations()
    print(time.time() - t0)
#    cafs_records = cafs.walk()
#    cafs_records = map(os.path.basename, cafs_records)
#    cafs_records = islice(cafs_records, 10000)
#    get_times = []
#    members_times = []
#    total_times = []
#
#
#    for cid in cafs_records:
#        t0 = time.perf_counter()
#        bb = rels.get(cid)
#        t1 = time.perf_counter()
#    
#        mm = tuple(rels.members(bb))
#        t2 = time.perf_counter()
#    
#        get_times.append(t1 - t0)
#        members_times.append(t2 - t1)
#        total_times.append(t2 - t0)
#    
#    print("get:     ", sum(get_times) / len(get_times))
#    print("members: ", sum(members_times) / len(members_times))
#    print("total:   ", sum(total_times) / len(total_times))


if __name__ == '__main__':
    main()
