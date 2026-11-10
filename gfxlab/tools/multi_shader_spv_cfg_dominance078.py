#!/usr/bin/env python3
"""GFX078: strict basic-block dominance of SPIR-V blocks, not memory SSA.

A writer block dominating a reader block does NOT prove effective Store->Load
memory dependence, pointer alias freedom, DXBC source equivalence or GPU pixels.
Only anonymous classification counts may escape the private CI runner.
"""
from __future__ import annotations
from collections import deque

MAX_CFG_BLOCKS=4096
MAX_CFG_EDGES=32768
TERMINALS=frozenset({"OpBranch","OpBranchConditional","OpSwitch",
    "OpReturn","OpReturnValue","OpKill","OpUnreachable",
    "OpTerminateInvocation","OpDemoteToHelperInvocationEXT"})

class StrictSpvBlockCfg:
    def __init__(self,records):
        self.blocks={}
        self.entries={}
        self.invalid=set()
        func=None
        current=None
        for name,op,args in records:
            if op=="OpFunction":
                if func is not None: self.invalid.add(func)
                func=name
                current=None
                if not isinstance(func,str):raise ValueError("GFX078_FUNCTION_RESULT_MISSING")
                if func in self.entries:self.invalid.add(func)
                self.entries[func]=None
            elif op=="OpFunctionEnd":
                if func is None:continue
                if current is not None and self.blocks[current][2] is None:
                    self.invalid.add(func)
                func=None
                current=None
            elif op=="OpLabel":
                if func is None or name is None:
                    if func is not None:self.invalid.add(func)
                    continue
                if current is not None and self.blocks[current][2] is None:
                    self.invalid.add(func)
                if name in self.blocks:
                    self.invalid.add(func)
                    self.invalid.add(self.blocks[name][0])
                    continue
                if self.entries[func] is None:self.entries[func]=name
                current=name
                self.blocks[name]=[func,(),None]
            elif current is not None and op in TERMINALS:
                if self.blocks[current][2] is not None:
                    self.invalid.add(func)
                    continue
                if op=="OpBranch":
                    successors=args if len(args)==1 else None
                elif op=="OpBranchConditional":
                    successors=args[1:3] if len(args)>=3 else None
                elif op=="OpSwitch":
                    successors=[args[1],*args[3::2]] if len(args)>=2 and (len(args)-2)%2==0 else None
                else:
                    successors=[] if (op not in {"OpReturnValue"} or len(args)==1) else None
                if successors is None:self.invalid.add(func)
                self.blocks[current][1]=tuple(successors or ())
                self.blocks[current][2]=op
            elif current is not None and self.blocks[current][2] is not None:
                # No instructions may follow the terminating control-flow opcode.
                self.invalid.add(func)
        if func is not None:
            self.invalid.add(func)
        if len(self.blocks)>MAX_CFG_BLOCKS:
            self.invalid.update(self.entries)
        edge_total=sum(len(info[1]) for info in self.blocks.values())
        if edge_total>MAX_CFG_EDGES:
            self.invalid.update(self.entries)
        for block,(function,successors,term) in self.blocks.items():
            if term is None or self.entries.get(function) is None:
                self.invalid.add(function)
            for dest in successors:
                if dest not in self.blocks or self.blocks[dest][0]!=function:
                    self.invalid.add(function)

    def classify(self,writer,reader):
        """One of: same_block / dominates / not_dominates / unknown.

        For a valid single-function CFG, A dominates B if B is reachable from
        the entry and becomes unreachable when A is removed. This is block
        dominance only and must never be conflated with Store-value dominance.
        """
        if writer not in self.blocks or reader not in self.blocks:return "unknown"
        fn=self.blocks[writer][0]
        if self.blocks[reader][0]!=fn or fn in self.invalid:return "unknown"
        entry=self.entries.get(fn)
        if entry is None:return "unknown"
        def reachable(exclude=None):
            found=set();queue=deque([entry])
            while queue:
                n=queue.popleft()
                if n==exclude or n in found:continue
                found.add(n)
                queue.extend(self.blocks[n][1])
            return found
        all_nodes=reachable()
        if writer not in all_nodes or reader not in all_nodes:return "unknown"
        if writer==reader:return "same_block"
        return "dominates" if reader not in reachable(exclude=writer) else "not_dominates"
