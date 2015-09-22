#!/usr/bin/python
import json, re
import random
import sys
from bci import download_history
from transaction import scriptaddr

# Gets the UTXO set of given address. This internally uses address/
# instead of unspent/ because blockchain.info doesn't include bare
# multisig outputs to utxo set
def multisig_utxo(addr):
    history = download_history(addr)
    utxo = to_utxo(addr, history)
    multisig_scripts = extract_multisig_scripts(utxo)
    return dict(utxo=utxo, scripts=multisig_scripts)

# Extract bare multisig addresses their scripts
def extract_multisig_scripts(outs):
    scripts = dict()
    for out in outs:
        if out['type'] == 1:
            scripts[scriptaddr(out['script'])] = out['script']
    return scripts

# Get transaction outputs which are targeted to given address
def to_utxo(addr, txs):
    related = []
    for tx in txs:
        for out in tx["out"]:
            addrs = []
            hit = False
            for key in addr_keys():
                # Stop when no more addresses are found related to this
                if key not in out:
                    break
                if out[key] == addr:
                    hit = True
                addrs.append(out[key])
                del out[key]
            # We are interested only of unspent transactions targeted
            # to this address
            if hit: # and not out['spent']:
                out['addrs'] = addrs
                out['hash'] = tx['hash']
                del out['tx_index'] # Irrelevant data
                related.append(out)
    return related

# Returns generator with the following sequence used by blockchain.info: addr, addr2, addr3
def addr_keys():
    yield "addr"
    i = 2
    while True:
        yield 'addr'+str(i)
        i += 1
