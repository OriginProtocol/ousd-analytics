const abiBuyback = {
  "address": "0x4ABA0078ED7f8bC0C4907562B4e59d6137cd0e06",
  "abi": [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "previousGovernor",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "newGovernor",
          "type": "address"
        }
      ],
      "name": "GovernorshipTransferred",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "token",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "swapAmountIn",
          "type": "uint256"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "swapAmountOut",
          "type": "uint256"
        }
      ],
      "name": "OUSDSwapped",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "receiver",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "amountSent",
          "type": "uint256"
        }
      ],
      "name": "OUSDTransferred",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "previousGovernor",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "newGovernor",
          "type": "address"
        }
      ],
      "name": "PendingGovernorshipTransfer",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "RewardsSourceUpdated",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "StrategistUpdated",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "_bps",
          "type": "uint256"
        }
      ],
      "name": "TreasuryBpsUpdated",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "TreasuryManagerUpdated",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "UniswapUpdated",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "claimGovernance",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "ousdAmount",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "minOGVExpected",
          "type": "uint256"
        }
      ],
      "name": "distributeAndSwap",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "governor",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_uniswapAddr",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_strategistAddr",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_treasuryManagerAddr",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_ousd",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_ogv",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_usdt",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_weth9",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_rewardsSource",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "_treasuryBps",
          "type": "uint256"
        }
      ],
      "name": "initialize",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "isGovernor",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "ogv",
      "outputs": [
        {
          "internalType": "contract IERC20",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "ousd",
      "outputs": [
        {
          "internalType": "contract IERC20",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "rewardsSource",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "setRewardsSource",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "setStrategistAddr",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_bps",
          "type": "uint256"
        }
      ],
      "name": "setTreasuryBps",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "setTreasuryManager",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "setUniswapAddr",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "strategistAddr",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "swap",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_newGovernor",
          "type": "address"
        }
      ],
      "name": "transferGovernance",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "token",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "amount",
          "type": "uint256"
        }
      ],
      "name": "transferToken",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "treasuryBps",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "treasuryManager",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "uniswapAddr",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "usdt",
      "outputs": [
        {
          "internalType": "contract IERC20",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "weth9",
      "outputs": [
        {
          "internalType": "contract IERC20",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    }
  ],
  "transactionHash": "0x7e7fde4d4a81ea73424516c344816dd5d1fb4c886dac18957116e7400e886d34",
  "receipt": {
    "to": null,
    "from": "0x58890A9cB27586E83Cb51d2d26bbE18a1a647245",
    "contractAddress": "0x4ABA0078ED7f8bC0C4907562B4e59d6137cd0e06",
    "transactionIndex": 10,
    "gasUsed": "1251127",
    "logsBloom": "0x00000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000000100080404000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000800000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000000000010000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000",
    "blockHash": "0x309bea87f9dcffa24483b4ec7af71dfddf1c9883319189963d8fe0828f53366d",
    "transactionHash": "0x7e7fde4d4a81ea73424516c344816dd5d1fb4c886dac18957116e7400e886d34",
    "logs": [
      {
        "transactionIndex": 10,
        "blockNumber": 17071881,
        "transactionHash": "0x7e7fde4d4a81ea73424516c344816dd5d1fb4c886dac18957116e7400e886d34",
        "address": "0x4ABA0078ED7f8bC0C4907562B4e59d6137cd0e06",
        "topics": [
          "0xc7c0c772add429241571afb3805861fb3cfa2af374534088b76cdb4325a87e9a",
          "0x0000000000000000000000000000000000000000000000000000000000000000",
          "0x00000000000000000000000058890a9cb27586e83cb51d2d26bbe18a1a647245"
        ],
        "data": "0x",
        "logIndex": 59,
        "blockHash": "0x309bea87f9dcffa24483b4ec7af71dfddf1c9883319189963d8fe0828f53366d"
      }
    ],
    "blockNumber": 17071881,
    "cumulativeGasUsed": "2916214",
    "status": 1,
    "byzantium": true
  },
  "args": [],
  "solcInputHash": "d89b9540be0dbf07690736ca4fe26424",
  "metadata": "{\"compiler\":{\"version\":\"0.8.7+commit.e28d00a7\"},\"language\":\"Solidity\",\"output\":{\"abi\":[{\"inputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"previousGovernor\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"newGovernor\",\"type\":\"address\"}],\"name\":\"GovernorshipTransferred\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"swapAmountIn\",\"type\":\"uint256\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"swapAmountOut\",\"type\":\"uint256\"}],\"name\":\"OUSDSwapped\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"receiver\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"amountSent\",\"type\":\"uint256\"}],\"name\":\"OUSDTransferred\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"previousGovernor\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"newGovernor\",\"type\":\"address\"}],\"name\":\"PendingGovernorshipTransfer\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"_address\",\"type\":\"address\"}],\"name\":\"RewardsSourceUpdated\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":false,\"internalType\":\"address\",\"name\":\"_address\",\"type\":\"address\"}],\"name\":\"StrategistUpdated\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"_bps\",\"type\":\"uint256\"}],\"name\":\"TreasuryBpsUpdated\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"_address\",\"type\":\"address\"}],\"name\":\"TreasuryManagerUpdated\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"_address\",\"type\":\"address\"}],\"name\":\"UniswapUpdated\",\"type\":\"event\"},{\"inputs\":[],\"name\":\"claimGovernance\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"ousdAmount\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"minOGVExpected\",\"type\":\"uint256\"}],\"name\":\"distributeAndSwap\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"governor\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"_uniswapAddr\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"_strategistAddr\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"_treasuryManagerAddr\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"_ousd\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"_ogv\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"_usdt\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"_weth9\",\"type\":\"address\"},{\"internalType\":\"address\",\"name\":\"_rewardsSource\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"_treasuryBps\",\"type\":\"uint256\"}],\"name\":\"initialize\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"isGovernor\",\"outputs\":[{\"internalType\":\"bool\",\"name\":\"\",\"type\":\"bool\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"ogv\",\"outputs\":[{\"internalType\":\"contract IERC20\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"ousd\",\"outputs\":[{\"internalType\":\"contract IERC20\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"rewardsSource\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"_address\",\"type\":\"address\"}],\"name\":\"setRewardsSource\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"_address\",\"type\":\"address\"}],\"name\":\"setStrategistAddr\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"_bps\",\"type\":\"uint256\"}],\"name\":\"setTreasuryBps\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"_address\",\"type\":\"address\"}],\"name\":\"setTreasuryManager\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"_address\",\"type\":\"address\"}],\"name\":\"setUniswapAddr\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"strategistAddr\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"swap\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"_newGovernor\",\"type\":\"address\"}],\"name\":\"transferGovernance\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"}],\"name\":\"transferToken\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"treasuryBps\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"treasuryManager\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"uniswapAddr\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"usdt\",\"outputs\":[{\"internalType\":\"contract IERC20\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"weth9\",\"outputs\":[{\"internalType\":\"contract IERC20\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"}],\"devdoc\":{\"kind\":\"dev\",\"methods\":{\"claimGovernance()\":{\"details\":\"Claim Governance of the contract to a new account (`newGovernor`). Can only be called by the new Governor.\"},\"distributeAndSwap(uint256,uint256)\":{\"details\":\"Computes the split of OUSD for treasury and transfers it. And      then execute a swap of OUSD for OGV with the remaining amount      via Uniswap or Uniswap compatible protocol (e.g. Sushiswap).\",\"params\":{\"minOGVExpected\":\"Mininum amount of OGV to receive when swapping*\",\"ousdAmount\":\"OUSD Amount to use from the balance\"}},\"governor()\":{\"details\":\"Returns the address of the current Governor.\"},\"initialize(address,address,address,address,address,address,address,address,uint256)\":{\"params\":{\"_ogv\":\"OGV Proxy Contract Address\",\"_ousd\":\"OUSD Proxy Contract Address\",\"_rewardsSource\":\"Address of RewardsSource contract\",\"_strategistAddr\":\"Address of Strategist multi-sig wallet\",\"_treasuryBps\":\"Percentage of OUSD balance to be sent to treasury\",\"_treasuryManagerAddr\":\"Address that receives the treasury's share of OUSD\",\"_uniswapAddr\":\"Address of Uniswap\",\"_usdt\":\"USDT Address\",\"_weth9\":\"WETH Address\"}},\"isGovernor()\":{\"details\":\"Returns true if the caller is the current Governor.\"},\"setRewardsSource(address)\":{\"details\":\"Sets the address that receives the OGV buyback rewards\",\"params\":{\"_address\":\"Address\"}},\"setStrategistAddr(address)\":{\"details\":\"Set address of Strategist\",\"params\":{\"_address\":\"Address of Strategist\"}},\"setTreasuryBps(uint256)\":{\"details\":\"Set the Treasury's share of OUSD\",\"params\":{\"_bps\":\"Percentage of OUSD balance to be sent to treasury\"}},\"setTreasuryManager(address)\":{\"details\":\"Sets the address that can receive and manage the funds for Treasury\",\"params\":{\"_address\":\"Address\"}},\"setUniswapAddr(address)\":{\"details\":\"Set address of Uniswap for performing liquidation of strategy reward tokens. Setting to 0x0 will pause swaps.\",\"params\":{\"_address\":\"Address of Uniswap\"}},\"swap()\":{\"details\":\"Execute a swap of OGV for OUSD via Uniswap or Uniswap compatible protocol (e.g. Sushiswap)*\"},\"transferGovernance(address)\":{\"details\":\"Transfers Governance of the contract to a new account (`newGovernor`). Can only be called by the current Governor. Must be claimed for this to complete\",\"params\":{\"_newGovernor\":\"Address of the new Governor\"}},\"transferToken(address,uint256)\":{\"params\":{\"amount\":\"amount of the token to be transferred\",\"token\":\"token to be transferered\"}}},\"version\":1},\"userdoc\":{\"kind\":\"user\",\"methods\":{\"transferToken(address,uint256)\":{\"notice\":\"Owner function to withdraw a specific amount of a token\"}},\"version\":1}},\"settings\":{\"compilationTarget\":{\"contracts/buyback/Buyback.sol\":\"Buyback\"},\"evmVersion\":\"london\",\"libraries\":{},\"metadata\":{\"bytecodeHash\":\"ipfs\",\"useLiteralContent\":true},\"optimizer\":{\"enabled\":true,\"runs\":200},\"remappings\":[]},\"sources\":{\"@openzeppelin/contracts/token/ERC20/IERC20.sol\":{\"content\":\"// SPDX-License-Identifier: MIT\\n// OpenZeppelin Contracts v4.4.1 (token/ERC20/IERC20.sol)\\n\\npragma solidity ^0.8.0;\\n\\n/**\\n * @dev Interface of the ERC20 standard as defined in the EIP.\\n */\\ninterface IERC20 {\\n    /**\\n     * @dev Returns the amount of tokens in existence.\\n     */\\n    function totalSupply() external view returns (uint256);\\n\\n    /**\\n     * @dev Returns the amount of tokens owned by `account`.\\n     */\\n    function balanceOf(address account) external view returns (uint256);\\n\\n    /**\\n     * @dev Moves `amount` tokens from the caller's account to `recipient`.\\n     *\\n     * Returns a boolean value indicating whether the operation succeeded.\\n     *\\n     * Emits a {Transfer} event.\\n     */\\n    function transfer(address recipient, uint256 amount) external returns (bool);\\n\\n    /**\\n     * @dev Returns the remaining number of tokens that `spender` will be\\n     * allowed to spend on behalf of `owner` through {transferFrom}. This is\\n     * zero by default.\\n     *\\n     * This value changes when {approve} or {transferFrom} are called.\\n     */\\n    function allowance(address owner, address spender) external view returns (uint256);\\n\\n    /**\\n     * @dev Sets `amount` as the allowance of `spender` over the caller's tokens.\\n     *\\n     * Returns a boolean value indicating whether the operation succeeded.\\n     *\\n     * IMPORTANT: Beware that changing an allowance with this method brings the risk\\n     * that someone may use both the old and the new allowance by unfortunate\\n     * transaction ordering. One possible solution to mitigate this race\\n     * condition is to first reduce the spender's allowance to 0 and set the\\n     * desired value afterwards:\\n     * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729\\n     *\\n     * Emits an {Approval} event.\\n     */\\n    function approve(address spender, uint256 amount) external returns (bool);\\n\\n    /**\\n     * @dev Moves `amount` tokens from `sender` to `recipient` using the\\n     * allowance mechanism. `amount` is then deducted from the caller's\\n     * allowance.\\n     *\\n     * Returns a boolean value indicating whether the operation succeeded.\\n     *\\n     * Emits a {Transfer} event.\\n     */\\n    function transferFrom(\\n        address sender,\\n        address recipient,\\n        uint256 amount\\n    ) external returns (bool);\\n\\n    /**\\n     * @dev Emitted when `value` tokens are moved from one account (`from`) to\\n     * another (`to`).\\n     *\\n     * Note that `value` may be zero.\\n     */\\n    event Transfer(address indexed from, address indexed to, uint256 value);\\n\\n    /**\\n     * @dev Emitted when the allowance of a `spender` for an `owner` is set by\\n     * a call to {approve}. `value` is the new allowance.\\n     */\\n    event Approval(address indexed owner, address indexed spender, uint256 value);\\n}\\n\",\"keccak256\":\"0x61437cb513a887a1bbad006e7b1c8b414478427d33de47c5600af3c748f108da\",\"license\":\"MIT\"},\"@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol\":{\"content\":\"// SPDX-License-Identifier: MIT\\n// OpenZeppelin Contracts v4.4.1 (token/ERC20/utils/SafeERC20.sol)\\n\\npragma solidity ^0.8.0;\\n\\nimport \\\"../IERC20.sol\\\";\\nimport \\\"../../../utils/Address.sol\\\";\\n\\n/**\\n * @title SafeERC20\\n * @dev Wrappers around ERC20 operations that throw on failure (when the token\\n * contract returns false). Tokens that return no value (and instead revert or\\n * throw on failure) are also supported, non-reverting calls are assumed to be\\n * successful.\\n * To use this library you can add a `using SafeERC20 for IERC20;` statement to your contract,\\n * which allows you to call the safe operations as `token.safeTransfer(...)`, etc.\\n */\\nlibrary SafeERC20 {\\n    using Address for address;\\n\\n    function safeTransfer(\\n        IERC20 token,\\n        address to,\\n        uint256 value\\n    ) internal {\\n        _callOptionalReturn(token, abi.encodeWithSelector(token.transfer.selector, to, value));\\n    }\\n\\n    function safeTransferFrom(\\n        IERC20 token,\\n        address from,\\n        address to,\\n        uint256 value\\n    ) internal {\\n        _callOptionalReturn(token, abi.encodeWithSelector(token.transferFrom.selector, from, to, value));\\n    }\\n\\n    /**\\n     * @dev Deprecated. This function has issues similar to the ones found in\\n     * {IERC20-approve}, and its usage is discouraged.\\n     *\\n     * Whenever possible, use {safeIncreaseAllowance} and\\n     * {safeDecreaseAllowance} instead.\\n     */\\n    function safeApprove(\\n        IERC20 token,\\n        address spender,\\n        uint256 value\\n    ) internal {\\n        // safeApprove should only be called when setting an initial allowance,\\n        // or when resetting it to zero. To increase and decrease it, use\\n        // 'safeIncreaseAllowance' and 'safeDecreaseAllowance'\\n        require(\\n            (value == 0) || (token.allowance(address(this), spender) == 0),\\n            \\\"SafeERC20: approve from non-zero to non-zero allowance\\\"\\n        );\\n        _callOptionalReturn(token, abi.encodeWithSelector(token.approve.selector, spender, value));\\n    }\\n\\n    function safeIncreaseAllowance(\\n        IERC20 token,\\n        address spender,\\n        uint256 value\\n    ) internal {\\n        uint256 newAllowance = token.allowance(address(this), spender) + value;\\n        _callOptionalReturn(token, abi.encodeWithSelector(token.approve.selector, spender, newAllowance));\\n    }\\n\\n    function safeDecreaseAllowance(\\n        IERC20 token,\\n        address spender,\\n        uint256 value\\n    ) internal {\\n        unchecked {\\n            uint256 oldAllowance = token.allowance(address(this), spender);\\n            require(oldAllowance >= value, \\\"SafeERC20: decreased allowance below zero\\\");\\n            uint256 newAllowance = oldAllowance - value;\\n            _callOptionalReturn(token, abi.encodeWithSelector(token.approve.selector, spender, newAllowance));\\n        }\\n    }\\n\\n    /**\\n     * @dev Imitates a Solidity high-level call (i.e. a regular function call to a contract), relaxing the requirement\\n     * on the return value: the return value is optional (but if data is returned, it must not be false).\\n     * @param token The token targeted by the call.\\n     * @param data The call data (encoded using abi.encode or one of its variants).\\n     */\\n    function _callOptionalReturn(IERC20 token, bytes memory data) private {\\n        // We need to perform a low level call here, to bypass Solidity's return data size checking mechanism, since\\n        // we're implementing it ourselves. We use {Address.functionCall} to perform this call, which verifies that\\n        // the target address contains contract code and also asserts for success in the low-level call.\\n\\n        bytes memory returndata = address(token).functionCall(data, \\\"SafeERC20: low-level call failed\\\");\\n        if (returndata.length > 0) {\\n            // Return data is optional\\n            require(abi.decode(returndata, (bool)), \\\"SafeERC20: ERC20 operation did not succeed\\\");\\n        }\\n    }\\n}\\n\",\"keccak256\":\"0xc3d946432c0ddbb1f846a0d3985be71299df331b91d06732152117f62f0be2b5\",\"license\":\"MIT\"},\"@openzeppelin/contracts/utils/Address.sol\":{\"content\":\"// SPDX-License-Identifier: MIT\\n// OpenZeppelin Contracts v4.4.1 (utils/Address.sol)\\n\\npragma solidity ^0.8.0;\\n\\n/**\\n * @dev Collection of functions related to the address type\\n */\\nlibrary Address {\\n    /**\\n     * @dev Returns true if `account` is a contract.\\n     *\\n     * [IMPORTANT]\\n     * ====\\n     * It is unsafe to assume that an address for which this function returns\\n     * false is an externally-owned account (EOA) and not a contract.\\n     *\\n     * Among others, `isContract` will return false for the following\\n     * types of addresses:\\n     *\\n     *  - an externally-owned account\\n     *  - a contract in construction\\n     *  - an address where a contract will be created\\n     *  - an address where a contract lived, but was destroyed\\n     * ====\\n     */\\n    function isContract(address account) internal view returns (bool) {\\n        // This method relies on extcodesize, which returns 0 for contracts in\\n        // construction, since the code is only stored at the end of the\\n        // constructor execution.\\n\\n        uint256 size;\\n        assembly {\\n            size := extcodesize(account)\\n        }\\n        return size > 0;\\n    }\\n\\n    /**\\n     * @dev Replacement for Solidity's `transfer`: sends `amount` wei to\\n     * `recipient`, forwarding all available gas and reverting on errors.\\n     *\\n     * https://eips.ethereum.org/EIPS/eip-1884[EIP1884] increases the gas cost\\n     * of certain opcodes, possibly making contracts go over the 2300 gas limit\\n     * imposed by `transfer`, making them unable to receive funds via\\n     * `transfer`. {sendValue} removes this limitation.\\n     *\\n     * https://diligence.consensys.net/posts/2019/09/stop-using-soliditys-transfer-now/[Learn more].\\n     *\\n     * IMPORTANT: because control is transferred to `recipient`, care must be\\n     * taken to not create reentrancy vulnerabilities. Consider using\\n     * {ReentrancyGuard} or the\\n     * https://solidity.readthedocs.io/en/v0.5.11/security-considerations.html#use-the-checks-effects-interactions-pattern[checks-effects-interactions pattern].\\n     */\\n    function sendValue(address payable recipient, uint256 amount) internal {\\n        require(address(this).balance >= amount, \\\"Address: insufficient balance\\\");\\n\\n        (bool success, ) = recipient.call{value: amount}(\\\"\\\");\\n        require(success, \\\"Address: unable to send value, recipient may have reverted\\\");\\n    }\\n\\n    /**\\n     * @dev Performs a Solidity function call using a low level `call`. A\\n     * plain `call` is an unsafe replacement for a function call: use this\\n     * function instead.\\n     *\\n     * If `target` reverts with a revert reason, it is bubbled up by this\\n     * function (like regular Solidity function calls).\\n     *\\n     * Returns the raw returned data. To convert to the expected return value,\\n     * use https://solidity.readthedocs.io/en/latest/units-and-global-variables.html?highlight=abi.decode#abi-encoding-and-decoding-functions[`abi.decode`].\\n     *\\n     * Requirements:\\n     *\\n     * - `target` must be a contract.\\n     * - calling `target` with `data` must not revert.\\n     *\\n     * _Available since v3.1._\\n     */\\n    function functionCall(address target, bytes memory data) internal returns (bytes memory) {\\n        return functionCall(target, data, \\\"Address: low-level call failed\\\");\\n    }\\n\\n    /**\\n     * @dev Same as {xref-Address-functionCall-address-bytes-}[`functionCall`], but with\\n     * `errorMessage` as a fallback revert reason when `target` reverts.\\n     *\\n     * _Available since v3.1._\\n     */\\n    function functionCall(\\n        address target,\\n        bytes memory data,\\n        string memory errorMessage\\n    ) internal returns (bytes memory) {\\n        return functionCallWithValue(target, data, 0, errorMessage);\\n    }\\n\\n    /**\\n     * @dev Same as {xref-Address-functionCall-address-bytes-}[`functionCall`],\\n     * but also transferring `value` wei to `target`.\\n     *\\n     * Requirements:\\n     *\\n     * - the calling contract must have an ETH balance of at least `value`.\\n     * - the called Solidity function must be `payable`.\\n     *\\n     * _Available since v3.1._\\n     */\\n    function functionCallWithValue(\\n        address target,\\n        bytes memory data,\\n        uint256 value\\n    ) internal returns (bytes memory) {\\n        return functionCallWithValue(target, data, value, \\\"Address: low-level call with value failed\\\");\\n    }\\n\\n    /**\\n     * @dev Same as {xref-Address-functionCallWithValue-address-bytes-uint256-}[`functionCallWithValue`], but\\n     * with `errorMessage` as a fallback revert reason when `target` reverts.\\n     *\\n     * _Available since v3.1._\\n     */\\n    function functionCallWithValue(\\n        address target,\\n        bytes memory data,\\n        uint256 value,\\n        string memory errorMessage\\n    ) internal returns (bytes memory) {\\n        require(address(this).balance >= value, \\\"Address: insufficient balance for call\\\");\\n        require(isContract(target), \\\"Address: call to non-contract\\\");\\n\\n        (bool success, bytes memory returndata) = target.call{value: value}(data);\\n        return verifyCallResult(success, returndata, errorMessage);\\n    }\\n\\n    /**\\n     * @dev Same as {xref-Address-functionCall-address-bytes-}[`functionCall`],\\n     * but performing a static call.\\n     *\\n     * _Available since v3.3._\\n     */\\n    function functionStaticCall(address target, bytes memory data) internal view returns (bytes memory) {\\n        return functionStaticCall(target, data, \\\"Address: low-level static call failed\\\");\\n    }\\n\\n    /**\\n     * @dev Same as {xref-Address-functionCall-address-bytes-string-}[`functionCall`],\\n     * but performing a static call.\\n     *\\n     * _Available since v3.3._\\n     */\\n    function functionStaticCall(\\n        address target,\\n        bytes memory data,\\n        string memory errorMessage\\n    ) internal view returns (bytes memory) {\\n        require(isContract(target), \\\"Address: static call to non-contract\\\");\\n\\n        (bool success, bytes memory returndata) = target.staticcall(data);\\n        return verifyCallResult(success, returndata, errorMessage);\\n    }\\n\\n    /**\\n     * @dev Same as {xref-Address-functionCall-address-bytes-}[`functionCall`],\\n     * but performing a delegate call.\\n     *\\n     * _Available since v3.4._\\n     */\\n    function functionDelegateCall(address target, bytes memory data) internal returns (bytes memory) {\\n        return functionDelegateCall(target, data, \\\"Address: low-level delegate call failed\\\");\\n    }\\n\\n    /**\\n     * @dev Same as {xref-Address-functionCall-address-bytes-string-}[`functionCall`],\\n     * but performing a delegate call.\\n     *\\n     * _Available since v3.4._\\n     */\\n    function functionDelegateCall(\\n        address target,\\n        bytes memory data,\\n        string memory errorMessage\\n    ) internal returns (bytes memory) {\\n        require(isContract(target), \\\"Address: delegate call to non-contract\\\");\\n\\n        (bool success, bytes memory returndata) = target.delegatecall(data);\\n        return verifyCallResult(success, returndata, errorMessage);\\n    }\\n\\n    /**\\n     * @dev Tool to verifies that a low level call was successful, and revert if it wasn't, either by bubbling the\\n     * revert reason using the provided one.\\n     *\\n     * _Available since v4.3._\\n     */\\n    function verifyCallResult(\\n        bool success,\\n        bytes memory returndata,\\n        string memory errorMessage\\n    ) internal pure returns (bytes memory) {\\n        if (success) {\\n            return returndata;\\n        } else {\\n            // Look for revert reason and bubble it up if present\\n            if (returndata.length > 0) {\\n                // The easiest way to bubble the revert reason is using memory via assembly\\n\\n                assembly {\\n                    let returndata_size := mload(returndata)\\n                    revert(add(32, returndata), returndata_size)\\n                }\\n            } else {\\n                revert(errorMessage);\\n            }\\n        }\\n    }\\n}\\n\",\"keccak256\":\"0x51b758a8815ecc9596c66c37d56b1d33883a444631a3f916b9fe65cb863ef7c4\",\"license\":\"MIT\"},\"contracts/buyback/Buyback.sol\":{\"content\":\"// SPDX-License-Identifier: MIT\\npragma solidity ^0.8.0;\\n\\nimport { Strategizable } from \\\"../governance/Strategizable.sol\\\";\\nimport \\\"../interfaces/chainlink/AggregatorV3Interface.sol\\\";\\nimport { IERC20 } from \\\"@openzeppelin/contracts/token/ERC20/IERC20.sol\\\";\\nimport { SafeERC20 } from \\\"@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol\\\";\\nimport { UniswapV3Router } from \\\"../interfaces/UniswapV3Router.sol\\\";\\n\\nimport { Initializable } from \\\"../utils/Initializable.sol\\\";\\n\\ncontract Buyback is Initializable, Strategizable {\\n    using SafeERC20 for IERC20;\\n\\n    event UniswapUpdated(address indexed _address);\\n    event RewardsSourceUpdated(address indexed _address);\\n    event TreasuryManagerUpdated(address indexed _address);\\n    event TreasuryBpsUpdated(uint256 _bps);\\n    event OUSDSwapped(\\n        address indexed token,\\n        uint256 swapAmountIn,\\n        uint256 swapAmountOut\\n    );\\n    event OUSDTransferred(address indexed receiver, uint256 amountSent);\\n\\n    // Address of Uniswap\\n    address public uniswapAddr;\\n\\n    // Swap from OUSD\\n    IERC20 public ousd;\\n\\n    // Swap to OGV\\n    IERC20 public ogv;\\n\\n    // USDT for Uniswap path\\n    IERC20 public usdt;\\n\\n    // WETH for Uniswap path\\n    IERC20 public weth9;\\n\\n    // Address that receives rewards\\n    address public rewardsSource;\\n\\n    // Address that receives the treasury's share of OUSD\\n    address public treasuryManager;\\n\\n    // Treasury's share of OUSD fee\\n    uint256 public treasuryBps;\\n\\n    constructor() {\\n        // Make sure nobody owns the implementation contract\\n        _setGovernor(address(0));\\n    }\\n\\n    /**\\n     * @param _uniswapAddr Address of Uniswap\\n     * @param _strategistAddr Address of Strategist multi-sig wallet\\n     * @param _treasuryManagerAddr Address that receives the treasury's share of OUSD\\n     * @param _ousd OUSD Proxy Contract Address\\n     * @param _ogv OGV Proxy Contract Address\\n     * @param _usdt USDT Address\\n     * @param _weth9 WETH Address\\n     * @param _rewardsSource Address of RewardsSource contract\\n     * @param _treasuryBps Percentage of OUSD balance to be sent to treasury\\n     */\\n    function initialize(\\n        address _uniswapAddr,\\n        address _strategistAddr,\\n        address _treasuryManagerAddr,\\n        address _ousd,\\n        address _ogv,\\n        address _usdt,\\n        address _weth9,\\n        address _rewardsSource,\\n        uint256 _treasuryBps\\n    ) external onlyGovernor initializer {\\n        ousd = IERC20(_ousd);\\n        ogv = IERC20(_ogv);\\n        usdt = IERC20(_usdt);\\n        weth9 = IERC20(_weth9);\\n\\n        _setStrategistAddr(_strategistAddr);\\n\\n        _setUniswapAddr(_uniswapAddr);\\n        _setRewardsSource(_rewardsSource);\\n\\n        _setTreasuryManager(_treasuryManagerAddr);\\n        _setTreasuryBps(_treasuryBps);\\n    }\\n\\n    /**\\n     * @dev Set address of Uniswap for performing liquidation of strategy reward\\n     * tokens. Setting to 0x0 will pause swaps.\\n     * @param _address Address of Uniswap\\n     */\\n    function setUniswapAddr(address _address) external onlyGovernor {\\n        _setUniswapAddr(_address);\\n    }\\n\\n    function _setUniswapAddr(address _address) internal {\\n        uniswapAddr = _address;\\n\\n        if (uniswapAddr != address(0)) {\\n            // Give Uniswap unlimited OUSD allowance\\n            ousd.safeApprove(uniswapAddr, type(uint256).max);\\n        }\\n\\n        emit UniswapUpdated(_address);\\n    }\\n\\n    /**\\n     * @dev Sets the address that receives the OGV buyback rewards\\n     * @param _address Address\\n     */\\n    function setRewardsSource(address _address) external onlyGovernor {\\n        _setRewardsSource(_address);\\n    }\\n\\n    function _setRewardsSource(address _address) internal {\\n        require(_address != address(0), \\\"Address not set\\\");\\n        rewardsSource = _address;\\n        emit RewardsSourceUpdated(_address);\\n    }\\n\\n    /**\\n     * @dev Sets the address that can receive and manage the funds for Treasury\\n     * @param _address Address\\n     */\\n    function setTreasuryManager(address _address) external onlyGovernor {\\n        _setTreasuryManager(_address);\\n    }\\n\\n    function _setTreasuryManager(address _address) internal {\\n        require(_address != address(0), \\\"Address not set\\\");\\n        treasuryManager = _address;\\n        emit TreasuryManagerUpdated(_address);\\n    }\\n\\n    /**\\n     * @dev Set the Treasury's share of OUSD\\n     * @param _bps Percentage of OUSD balance to be sent to treasury\\n     */\\n    function setTreasuryBps(uint256 _bps) external onlyGovernor {\\n        _setTreasuryBps(_bps);\\n    }\\n\\n    function _setTreasuryBps(uint256 _bps) internal {\\n        require(_bps <= 10000, \\\"Invalid treasury bips value\\\");\\n        treasuryBps = _bps;\\n        emit TreasuryBpsUpdated(_bps);\\n    }\\n\\n    /**\\n     * @dev Execute a swap of OGV for OUSD via Uniswap or Uniswap compatible\\n     * protocol (e.g. Sushiswap)\\n     **/\\n    function swap() external {\\n        // Disabled for now, will be manually swapped by\\n        // `strategistAddr` using `distributeAndSwap()` method\\n        return;\\n    }\\n\\n    /**\\n     * @dev Computes the split of OUSD for treasury and transfers it. And\\n     *      then execute a swap of OUSD for OGV with the remaining amount\\n     *      via Uniswap or Uniswap compatible protocol (e.g. Sushiswap).\\n     *\\n     * @param ousdAmount OUSD Amount to use from the balance\\n     * @param minOGVExpected Mininum amount of OGV to receive when swapping\\n     **/\\n    function distributeAndSwap(uint256 ousdAmount, uint256 minOGVExpected)\\n        external\\n        onlyGovernorOrStrategist\\n        nonReentrant\\n    {\\n        require(uniswapAddr != address(0), \\\"Exchange address not set\\\");\\n\\n        uint256 amountToTransfer = (ousdAmount * treasuryBps) / 10000;\\n        uint256 swapAmountIn = ousdAmount - amountToTransfer;\\n\\n        if (swapAmountIn > 0) {\\n            require(minOGVExpected > 0, \\\"Invalid minOGVExpected value\\\");\\n\\n            UniswapV3Router.ExactInputParams memory params = UniswapV3Router\\n                .ExactInputParams({\\n                    path: abi.encodePacked(\\n                        ousd,\\n                        uint24(500), // Pool fee, ousd -> usdt\\n                        usdt,\\n                        uint24(500), // Pool fee, usdt -> weth9\\n                        weth9,\\n                        uint24(3000), // Pool fee, weth9 -> ogv\\n                        ogv\\n                    ),\\n                    recipient: rewardsSource,\\n                    deadline: block.timestamp,\\n                    amountIn: swapAmountIn,\\n                    amountOutMinimum: minOGVExpected\\n                });\\n\\n            uint256 amountOut = UniswapV3Router(uniswapAddr).exactInput(params);\\n\\n            emit OUSDSwapped(address(ogv), swapAmountIn, amountOut);\\n        }\\n\\n        if (amountToTransfer > 0) {\\n            ousd.safeTransfer(treasuryManager, amountToTransfer);\\n            emit OUSDTransferred(treasuryManager, amountToTransfer);\\n        }\\n    }\\n\\n    /**\\n     * @notice Owner function to withdraw a specific amount of a token\\n     * @param token token to be transferered\\n     * @param amount amount of the token to be transferred\\n     */\\n    function transferToken(address token, uint256 amount)\\n        external\\n        onlyGovernor\\n        nonReentrant\\n    {\\n        IERC20(token).safeTransfer(_governor(), amount);\\n    }\\n}\\n\",\"keccak256\":\"0xbca66d9a8e2f0f76557a8bba815fb72e2714cab285c36d894d8d530589818887\",\"license\":\"MIT\"},\"contracts/governance/Governable.sol\":{\"content\":\"// SPDX-License-Identifier: MIT\\npragma solidity ^0.8.0;\\n\\n/**\\n * @title OUSD Governable Contract\\n * @dev Copy of the openzeppelin Ownable.sol contract with nomenclature change\\n *      from owner to governor and renounce methods removed. Does not use\\n *      Context.sol like Ownable.sol does for simplification.\\n * @author Origin Protocol Inc\\n */\\ncontract Governable {\\n    // Storage position of the owner and pendingOwner of the contract\\n    // keccak256(\\\"OUSD.governor\\\");\\n    bytes32 private constant governorPosition =\\n        0x7bea13895fa79d2831e0a9e28edede30099005a50d652d8957cf8a607ee6ca4a;\\n\\n    // keccak256(\\\"OUSD.pending.governor\\\");\\n    bytes32 private constant pendingGovernorPosition =\\n        0x44c4d30b2eaad5130ad70c3ba6972730566f3e6359ab83e800d905c61b1c51db;\\n\\n    // keccak256(\\\"OUSD.reentry.status\\\");\\n    bytes32 private constant reentryStatusPosition =\\n        0x53bf423e48ed90e97d02ab0ebab13b2a235a6bfbe9c321847d5c175333ac4535;\\n\\n    // See OpenZeppelin ReentrancyGuard implementation\\n    uint256 constant _NOT_ENTERED = 1;\\n    uint256 constant _ENTERED = 2;\\n\\n    event PendingGovernorshipTransfer(\\n        address indexed previousGovernor,\\n        address indexed newGovernor\\n    );\\n\\n    event GovernorshipTransferred(\\n        address indexed previousGovernor,\\n        address indexed newGovernor\\n    );\\n\\n    /**\\n     * @dev Initializes the contract setting the deployer as the initial Governor.\\n     */\\n    constructor() {\\n        _setGovernor(msg.sender);\\n        emit GovernorshipTransferred(address(0), _governor());\\n    }\\n\\n    /**\\n     * @dev Returns the address of the current Governor.\\n     */\\n    function governor() public view returns (address) {\\n        return _governor();\\n    }\\n\\n    /**\\n     * @dev Returns the address of the current Governor.\\n     */\\n    function _governor() internal view returns (address governorOut) {\\n        bytes32 position = governorPosition;\\n        // solhint-disable-next-line no-inline-assembly\\n        assembly {\\n            governorOut := sload(position)\\n        }\\n    }\\n\\n    /**\\n     * @dev Returns the address of the pending Governor.\\n     */\\n    function _pendingGovernor()\\n        internal\\n        view\\n        returns (address pendingGovernor)\\n    {\\n        bytes32 position = pendingGovernorPosition;\\n        // solhint-disable-next-line no-inline-assembly\\n        assembly {\\n            pendingGovernor := sload(position)\\n        }\\n    }\\n\\n    /**\\n     * @dev Throws if called by any account other than the Governor.\\n     */\\n    modifier onlyGovernor() {\\n        require(isGovernor(), \\\"Caller is not the Governor\\\");\\n        _;\\n    }\\n\\n    /**\\n     * @dev Returns true if the caller is the current Governor.\\n     */\\n    function isGovernor() public view returns (bool) {\\n        return msg.sender == _governor();\\n    }\\n\\n    function _setGovernor(address newGovernor) internal {\\n        bytes32 position = governorPosition;\\n        // solhint-disable-next-line no-inline-assembly\\n        assembly {\\n            sstore(position, newGovernor)\\n        }\\n    }\\n\\n    /**\\n     * @dev Prevents a contract from calling itself, directly or indirectly.\\n     * Calling a `nonReentrant` function from another `nonReentrant`\\n     * function is not supported. It is possible to prevent this from happening\\n     * by making the `nonReentrant` function external, and make it call a\\n     * `private` function that does the actual work.\\n     */\\n    modifier nonReentrant() {\\n        bytes32 position = reentryStatusPosition;\\n        uint256 _reentry_status;\\n        // solhint-disable-next-line no-inline-assembly\\n        assembly {\\n            _reentry_status := sload(position)\\n        }\\n\\n        // On the first call to nonReentrant, _notEntered will be true\\n        require(_reentry_status != _ENTERED, \\\"Reentrant call\\\");\\n\\n        // Any calls to nonReentrant after this point will fail\\n        // solhint-disable-next-line no-inline-assembly\\n        assembly {\\n            sstore(position, _ENTERED)\\n        }\\n\\n        _;\\n\\n        // By storing the original value once again, a refund is triggered (see\\n        // https://eips.ethereum.org/EIPS/eip-2200)\\n        // solhint-disable-next-line no-inline-assembly\\n        assembly {\\n            sstore(position, _NOT_ENTERED)\\n        }\\n    }\\n\\n    function _setPendingGovernor(address newGovernor) internal {\\n        bytes32 position = pendingGovernorPosition;\\n        // solhint-disable-next-line no-inline-assembly\\n        assembly {\\n            sstore(position, newGovernor)\\n        }\\n    }\\n\\n    /**\\n     * @dev Transfers Governance of the contract to a new account (`newGovernor`).\\n     * Can only be called by the current Governor. Must be claimed for this to complete\\n     * @param _newGovernor Address of the new Governor\\n     */\\n    function transferGovernance(address _newGovernor) external onlyGovernor {\\n        _setPendingGovernor(_newGovernor);\\n        emit PendingGovernorshipTransfer(_governor(), _newGovernor);\\n    }\\n\\n    /**\\n     * @dev Claim Governance of the contract to a new account (`newGovernor`).\\n     * Can only be called by the new Governor.\\n     */\\n    function claimGovernance() external {\\n        require(\\n            msg.sender == _pendingGovernor(),\\n            \\\"Only the pending Governor can complete the claim\\\"\\n        );\\n        _changeGovernor(msg.sender);\\n    }\\n\\n    /**\\n     * @dev Change Governance of the contract to a new account (`newGovernor`).\\n     * @param _newGovernor Address of the new Governor\\n     */\\n    function _changeGovernor(address _newGovernor) internal {\\n        require(_newGovernor != address(0), \\\"New Governor is address(0)\\\");\\n        emit GovernorshipTransferred(_governor(), _newGovernor);\\n        _setGovernor(_newGovernor);\\n    }\\n}\\n\",\"keccak256\":\"0x1b2af4d111ebd49acdbdfb4817b90bff752a453576d4e0b03dd5e5954f236c1b\",\"license\":\"MIT\"},\"contracts/governance/Strategizable.sol\":{\"content\":\"// SPDX-License-Identifier: MIT\\npragma solidity ^0.8.0;\\n\\nimport { Governable } from \\\"./Governable.sol\\\";\\n\\ncontract Strategizable is Governable {\\n    event StrategistUpdated(address _address);\\n\\n    // Address of strategist\\n    address public strategistAddr;\\n\\n    // For future use\\n    uint256[50] private __gap;\\n\\n    /**\\n     * @dev Verifies that the caller is either Governor or Strategist.\\n     */\\n    modifier onlyGovernorOrStrategist() {\\n        require(\\n            msg.sender == strategistAddr || isGovernor(),\\n            \\\"Caller is not the Strategist or Governor\\\"\\n        );\\n        _;\\n    }\\n\\n    /**\\n     * @dev Set address of Strategist\\n     * @param _address Address of Strategist\\n     */\\n    function setStrategistAddr(address _address) external onlyGovernor {\\n        _setStrategistAddr(_address);\\n    }\\n\\n    /**\\n     * @dev Set address of Strategist\\n     * @param _address Address of Strategist\\n     */\\n    function _setStrategistAddr(address _address) internal {\\n        strategistAddr = _address;\\n        emit StrategistUpdated(_address);\\n    }\\n}\\n\",\"keccak256\":\"0x7fd5473fd8d117575500c6b8fc1bb94e39a68082143d99da9946aed020a41619\",\"license\":\"MIT\"},\"contracts/interfaces/UniswapV3Router.sol\":{\"content\":\"// SPDX-License-Identifier: MIT\\npragma solidity ^0.8.0;\\n\\n// -- Solididy v0.5.x compatible interface\\ninterface UniswapV3Router {\\n    struct ExactInputParams {\\n        bytes path;\\n        address recipient;\\n        uint256 deadline;\\n        uint256 amountIn;\\n        uint256 amountOutMinimum;\\n    }\\n\\n    /// @notice Swaps `amountIn` of one token for as much as possible of another along the specified path\\n    /// @param params The parameters necessary for the multi-hop swap, encoded as `ExactInputParams` in calldata\\n    /// @return amountOut The amount of the received token\\n    function exactInput(ExactInputParams calldata params)\\n        external\\n        payable\\n        returns (uint256 amountOut);\\n}\\n\",\"keccak256\":\"0x52dc75be15438a258b55b5f9240883ab579ae2119e7d52993ff947699f099646\",\"license\":\"MIT\"},\"contracts/interfaces/chainlink/AggregatorV3Interface.sol\":{\"content\":\"// SPDX-License-Identifier: MIT\\npragma solidity ^0.8.0;\\n\\ninterface AggregatorV3Interface {\\n    function decimals() external view returns (uint8);\\n\\n    function description() external view returns (string memory);\\n\\n    function version() external view returns (uint256);\\n\\n    // getRoundData and latestRoundData should both raise \\\"No data present\\\"\\n    // if they do not have data to report, instead of returning unset values\\n    // which could be misinterpreted as actual reported values.\\n    function getRoundData(uint80 _roundId)\\n        external\\n        view\\n        returns (\\n            uint80 roundId,\\n            int256 answer,\\n            uint256 startedAt,\\n            uint256 updatedAt,\\n            uint80 answeredInRound\\n        );\\n\\n    function latestRoundData()\\n        external\\n        view\\n        returns (\\n            uint80 roundId,\\n            int256 answer,\\n            uint256 startedAt,\\n            uint256 updatedAt,\\n            uint80 answeredInRound\\n        );\\n}\\n\",\"keccak256\":\"0x18fb68de95136c49f3874fe7795a7bda730339198b2816690ddbdf1eacd4e273\",\"license\":\"MIT\"},\"contracts/utils/Initializable.sol\":{\"content\":\"// SPDX-License-Identifier: MIT\\npragma solidity ^0.8.0;\\n\\nabstract contract Initializable {\\n    /**\\n     * @dev Indicates that the contract has been initialized.\\n     */\\n    bool private initialized;\\n\\n    /**\\n     * @dev Indicates that the contract is in the process of being initialized.\\n     */\\n    bool private initializing;\\n\\n    /**\\n     * @dev Modifier to protect an initializer function from being invoked twice.\\n     */\\n    modifier initializer() {\\n        require(\\n            initializing || !initialized,\\n            \\\"Initializable: contract is already initialized\\\"\\n        );\\n\\n        bool isTopLevelCall = !initializing;\\n        if (isTopLevelCall) {\\n            initializing = true;\\n            initialized = true;\\n        }\\n\\n        _;\\n\\n        if (isTopLevelCall) {\\n            initializing = false;\\n        }\\n    }\\n\\n    uint256[50] private ______gap;\\n}\\n\",\"keccak256\":\"0xed91beae8c271cd70d80a9fce9306f1c46b8437cdd1d78ed9b75c067961e5259\",\"license\":\"MIT\"}},\"version\":1}",
  "bytecode": "0x608060405234801561001057600080fd5b506100273360008051602061161f83398151915255565b60008051602061161f833981519152546040516001600160a01b03909116906000907fc7c0c772add429241571afb3805861fb3cfa2af374534088b76cdb4325a87e9a908290a3610085600060008051602061161f83398151915255565b61158b806100946000396000f3fe608060405234801561001057600080fd5b50600436106101425760003560e01c8063773540b3116100b8578063c7af33521161007c578063c7af335214610271578063cf68c9b014610289578063d1c766381461029c578063d38bfff4146102af578063f7240d2f146102c2578063fe47a9f2146102d557600080fd5b8063773540b3146102255780638119c0651461017f578063aea173d514610238578063bb6eb3591461024b578063bebacc8e1461025e57600080fd5b8063344dd6e41161010a578063344dd6e4146101ba5780633cea70d9146101cd5780634dc10ea1146101e057806350879c1c146101f7578063570d8e1d1461020a5780635d36b1901461021d57600080fd5b80630c340a24146101475780631072cbea1461016c578063128a8b0514610181578063142561cf146101945780632f48ab7d146101a7575b600080fd5b61014f6102e8565b6040516001600160a01b0390911681526020015b60405180910390f35b61017f61017a36600461130d565b610305565b005b60665461014f906001600160a01b031681565b60685461014f906001600160a01b031681565b60695461014f906001600160a01b031681565b61017f6101c836600461126c565b6103ce565b606c5461014f906001600160a01b031681565b6101e9606d5481565b604051908152602001610163565b606a5461014f906001600160a01b031681565b60335461014f906001600160a01b031681565b61017f610525565b61017f610233366004611251565b6105cb565b61017f610246366004611251565b6105fb565b61017f610259366004611359565b610628565b60675461014f906001600160a01b031681565b610279610655565b6040519015158152602001610163565b61017f61029736600461138b565b610686565b61017f6102aa366004611251565b610a25565b61017f6102bd366004611251565b610a52565b606b5461014f906001600160a01b031681565b61017f6102e3366004611251565b610af6565b60006103006000805160206115368339815191525490565b905090565b61030d610655565b6103325760405162461bcd60e51b815260040161032990611408565b60405180910390fd5b7f53bf423e48ed90e97d02ab0ebab13b2a235a6bfbe9c321847d5c175333ac4535805460028114156103975760405162461bcd60e51b815260206004820152600e60248201526d1499595b9d1c985b9d0818d85b1b60921b6044820152606401610329565b600282556103c56103b46000805160206115368339815191525490565b6001600160a01b0386169085610b23565b50600190555050565b6103d6610655565b6103f25760405162461bcd60e51b815260040161032990611408565b600054610100900460ff168061040b575060005460ff16155b61046e5760405162461bcd60e51b815260206004820152602e60248201527f496e697469616c697a61626c653a20636f6e747261637420697320616c72656160448201526d191e481a5b9a5d1a585b1a5e995960921b6064820152608401610329565b600054610100900460ff16158015610490576000805461ffff19166101011790555b606780546001600160a01b03808a166001600160a01b0319928316179092556068805489841690831617905560698054888416908316179055606a8054928716929091169190911790556104e389610b8b565b6104ec8a610be0565b6104f583610c59565b6104fe88610ceb565b61050782610d7d565b8015610519576000805461ff00191690555b50505050505050505050565b7f44c4d30b2eaad5130ad70c3ba6972730566f3e6359ab83e800d905c61b1c51db546001600160a01b0316336001600160a01b0316146105c05760405162461bcd60e51b815260206004820152603060248201527f4f6e6c79207468652070656e64696e6720476f7665726e6f722063616e20636f60448201526f6d706c6574652074686520636c61696d60801b6064820152608401610329565b6105c933610e04565b565b6105d3610655565b6105ef5760405162461bcd60e51b815260040161032990611408565b6105f881610b8b565b50565b610603610655565b61061f5760405162461bcd60e51b815260040161032990611408565b6105f881610be0565b610630610655565b61064c5760405162461bcd60e51b815260040161032990611408565b6105f881610d7d565b600061066d6000805160206115368339815191525490565b6001600160a01b0316336001600160a01b031614905090565b6033546001600160a01b03163314806106a257506106a2610655565b6106ff5760405162461bcd60e51b815260206004820152602860248201527f43616c6c6572206973206e6f74207468652053747261746567697374206f722060448201526723b7bb32b93737b960c11b6064820152608401610329565b7f53bf423e48ed90e97d02ab0ebab13b2a235a6bfbe9c321847d5c175333ac4535805460028114156107645760405162461bcd60e51b815260206004820152600e60248201526d1499595b9d1c985b9d0818d85b1b60921b6044820152606401610329565b600282556066546001600160a01b03166107c05760405162461bcd60e51b815260206004820152601860248201527f45786368616e67652061646472657373206e6f742073657400000000000000006044820152606401610329565b6000612710606d54866107d391906114b9565b6107dd9190611497565b905060006107eb82876114d8565b905080156109b357600085116108435760405162461bcd60e51b815260206004820152601c60248201527f496e76616c6964206d696e4f475645787065637465642076616c7565000000006044820152606401610329565b6040805160a081018252606754606954606a546068546bffffffffffffffffffffffff19606094851b811660c0870152607d60ea1b60d4870181905293851b811660d787015260eb86019390935290831b821660ee85015261017760eb1b610102850152821b16610105830152825180830360f9018152610119830184528252606b546001600160a01b039081166020840152428385015290820184905260808201889052606654925163c04b8d5960e01b8152919260009291169063c04b8d599061091390859060040161143f565b602060405180830381600087803b15801561092d57600080fd5b505af1158015610941573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906109659190611372565b60685460408051868152602081018490529293506001600160a01b03909116917f081c85c611b9200aca256ff161405227b5defc7280d21384d580e5d8152b2916910160405180910390a250505b8115610a1957606c546067546109d6916001600160a01b03918216911684610b23565b606c546040518381526001600160a01b03909116907f378347ff600be325e8602c4d2a4f3a88534824a63f8bccf6ef494027f2384cba9060200160405180910390a25b50506001825550505050565b610a2d610655565b610a495760405162461bcd60e51b815260040161032990611408565b6105f881610c59565b610a5a610655565b610a765760405162461bcd60e51b815260040161032990611408565b610a9e817f44c4d30b2eaad5130ad70c3ba6972730566f3e6359ab83e800d905c61b1c51db55565b806001600160a01b0316610abe6000805160206115368339815191525490565b6001600160a01b03167fa39cc5eb22d0f34d8beaefee8a3f17cc229c1a1d1ef87a5ad47313487b1c4f0d60405160405180910390a350565b610afe610655565b610b1a5760405162461bcd60e51b815260040161032990611408565b6105f881610ceb565b6040516001600160a01b038316602482015260448101829052610b8690849063a9059cbb60e01b906064015b60408051601f198184030181529190526020810180516001600160e01b03166001600160e01b031990931692909217909152610ec5565b505050565b603380546001600160a01b0319166001600160a01b0383169081179091556040519081527f869e0abd13cc3a975de7b93be3df1cb2255c802b1cead85963cc79d99f131bee906020015b60405180910390a150565b606680546001600160a01b0319166001600160a01b03831690811790915515610c2257606654606754610c22916001600160a01b039182169116600019610f97565b6040516001600160a01b038216907fca20db57f4368388dd6766259da48cd22a485cba21ee6ec8c519007cb66dfd0390600090a250565b6001600160a01b038116610ca15760405162461bcd60e51b815260206004820152600f60248201526e1059191c995cdcc81b9bdd081cd95d608a1b6044820152606401610329565b606b80546001600160a01b0319166001600160a01b0383169081179091556040517f95561238de8d7836da6d15311c07a2546a1a712b477f44391ddd1e6e0556c6cd90600090a250565b6001600160a01b038116610d335760405162461bcd60e51b815260206004820152600f60248201526e1059191c995cdcc81b9bdd081cd95d608a1b6044820152606401610329565b606c80546001600160a01b0319166001600160a01b0383169081179091556040517fd16d2cf254200e4dc6dc82512e9d11673e06a798c40b90cef7583729b4f7a8d490600090a250565b612710811115610dcf5760405162461bcd60e51b815260206004820152601b60248201527f496e76616c696420747265617375727920626970732076616c756500000000006044820152606401610329565b606d8190556040518181527facc8265fd7b5a534b6871947bfb20b579d23cf318ab16207309a0fa235e450cd90602001610bd5565b6001600160a01b038116610e5a5760405162461bcd60e51b815260206004820152601a60248201527f4e657720476f7665726e6f7220697320616464726573732830290000000000006044820152606401610329565b806001600160a01b0316610e7a6000805160206115368339815191525490565b6001600160a01b03167fc7c0c772add429241571afb3805861fb3cfa2af374534088b76cdb4325a87e9a60405160405180910390a36105f88160008051602061153683398151915255565b6000610f1a826040518060400160405280602081526020017f5361666545524332303a206c6f772d6c6576656c2063616c6c206661696c6564815250856001600160a01b03166110bb9092919063ffffffff16565b805190915015610b865780806020019051810190610f389190611337565b610b865760405162461bcd60e51b815260206004820152602a60248201527f5361666545524332303a204552433230206f7065726174696f6e20646964206e6044820152691bdd081cdd58d8d9595960b21b6064820152608401610329565b8015806110205750604051636eb1769f60e11b81523060048201526001600160a01b03838116602483015284169063dd62ed3e9060440160206040518083038186803b158015610fe657600080fd5b505afa158015610ffa573d6000803e3d6000fd5b505050506040513d601f19601f8201168201806040525081019061101e9190611372565b155b61108b5760405162461bcd60e51b815260206004820152603660248201527f5361666545524332303a20617070726f76652066726f6d206e6f6e2d7a65726f60448201527520746f206e6f6e2d7a65726f20616c6c6f77616e636560501b6064820152608401610329565b6040516001600160a01b038316602482015260448101829052610b8690849063095ea7b360e01b90606401610b4f565b60606110ca84846000856110d4565b90505b9392505050565b6060824710156111355760405162461bcd60e51b815260206004820152602660248201527f416464726573733a20696e73756666696369656e742062616c616e636520666f6044820152651c8818d85b1b60d21b6064820152608401610329565b843b6111835760405162461bcd60e51b815260206004820152601d60248201527f416464726573733a2063616c6c20746f206e6f6e2d636f6e74726163740000006044820152606401610329565b600080866001600160a01b0316858760405161119f91906113d9565b60006040518083038185875af1925050503d80600081146111dc576040519150601f19603f3d011682016040523d82523d6000602084013e6111e1565b606091505b50915091506111f18282866111fc565b979650505050505050565b6060831561120b5750816110cd565b82511561121b5782518084602001fd5b8160405162461bcd60e51b815260040161032991906113f5565b80356001600160a01b038116811461124c57600080fd5b919050565b60006020828403121561126357600080fd5b6110cd82611235565b60008060008060008060008060006101208a8c03121561128b57600080fd5b6112948a611235565b98506112a260208b01611235565b97506112b060408b01611235565b96506112be60608b01611235565b95506112cc60808b01611235565b94506112da60a08b01611235565b93506112e860c08b01611235565b92506112f660e08b01611235565b91506101008a013590509295985092959850929598565b6000806040838503121561132057600080fd5b61132983611235565b946020939093013593505050565b60006020828403121561134957600080fd5b815180151581146110cd57600080fd5b60006020828403121561136b57600080fd5b5035919050565b60006020828403121561138457600080fd5b5051919050565b6000806040838503121561139e57600080fd5b50508035926020909101359150565b600081518084526113c58160208601602086016114ef565b601f01601f19169290920160200192915050565b600082516113eb8184602087016114ef565b9190910192915050565b6020815260006110cd60208301846113ad565b6020808252601a908201527f43616c6c6572206973206e6f742074686520476f7665726e6f72000000000000604082015260600190565b602081526000825160a0602084015261145b60c08401826113ad565b905060018060a01b0360208501511660408401526040840151606084015260608401516080840152608084015160a08401528091505092915050565b6000826114b457634e487b7160e01b600052601260045260246000fd5b500490565b60008160001904831182151516156114d3576114d361151f565b500290565b6000828210156114ea576114ea61151f565b500390565b60005b8381101561150a5781810151838201526020016114f2565b83811115611519576000848401525b50505050565b634e487b7160e01b600052601160045260246000fdfe7bea13895fa79d2831e0a9e28edede30099005a50d652d8957cf8a607ee6ca4aa26469706673582212200ecdda767c1f5ae771eccf91eed3b5693d59fa7fe69e3234a134129e0f0f7e9764736f6c634300080700337bea13895fa79d2831e0a9e28edede30099005a50d652d8957cf8a607ee6ca4a",
  "deployedBytecode": "0x608060405234801561001057600080fd5b50600436106101425760003560e01c8063773540b3116100b8578063c7af33521161007c578063c7af335214610271578063cf68c9b014610289578063d1c766381461029c578063d38bfff4146102af578063f7240d2f146102c2578063fe47a9f2146102d557600080fd5b8063773540b3146102255780638119c0651461017f578063aea173d514610238578063bb6eb3591461024b578063bebacc8e1461025e57600080fd5b8063344dd6e41161010a578063344dd6e4146101ba5780633cea70d9146101cd5780634dc10ea1146101e057806350879c1c146101f7578063570d8e1d1461020a5780635d36b1901461021d57600080fd5b80630c340a24146101475780631072cbea1461016c578063128a8b0514610181578063142561cf146101945780632f48ab7d146101a7575b600080fd5b61014f6102e8565b6040516001600160a01b0390911681526020015b60405180910390f35b61017f61017a36600461130d565b610305565b005b60665461014f906001600160a01b031681565b60685461014f906001600160a01b031681565b60695461014f906001600160a01b031681565b61017f6101c836600461126c565b6103ce565b606c5461014f906001600160a01b031681565b6101e9606d5481565b604051908152602001610163565b606a5461014f906001600160a01b031681565b60335461014f906001600160a01b031681565b61017f610525565b61017f610233366004611251565b6105cb565b61017f610246366004611251565b6105fb565b61017f610259366004611359565b610628565b60675461014f906001600160a01b031681565b610279610655565b6040519015158152602001610163565b61017f61029736600461138b565b610686565b61017f6102aa366004611251565b610a25565b61017f6102bd366004611251565b610a52565b606b5461014f906001600160a01b031681565b61017f6102e3366004611251565b610af6565b60006103006000805160206115368339815191525490565b905090565b61030d610655565b6103325760405162461bcd60e51b815260040161032990611408565b60405180910390fd5b7f53bf423e48ed90e97d02ab0ebab13b2a235a6bfbe9c321847d5c175333ac4535805460028114156103975760405162461bcd60e51b815260206004820152600e60248201526d1499595b9d1c985b9d0818d85b1b60921b6044820152606401610329565b600282556103c56103b46000805160206115368339815191525490565b6001600160a01b0386169085610b23565b50600190555050565b6103d6610655565b6103f25760405162461bcd60e51b815260040161032990611408565b600054610100900460ff168061040b575060005460ff16155b61046e5760405162461bcd60e51b815260206004820152602e60248201527f496e697469616c697a61626c653a20636f6e747261637420697320616c72656160448201526d191e481a5b9a5d1a585b1a5e995960921b6064820152608401610329565b600054610100900460ff16158015610490576000805461ffff19166101011790555b606780546001600160a01b03808a166001600160a01b0319928316179092556068805489841690831617905560698054888416908316179055606a8054928716929091169190911790556104e389610b8b565b6104ec8a610be0565b6104f583610c59565b6104fe88610ceb565b61050782610d7d565b8015610519576000805461ff00191690555b50505050505050505050565b7f44c4d30b2eaad5130ad70c3ba6972730566f3e6359ab83e800d905c61b1c51db546001600160a01b0316336001600160a01b0316146105c05760405162461bcd60e51b815260206004820152603060248201527f4f6e6c79207468652070656e64696e6720476f7665726e6f722063616e20636f60448201526f6d706c6574652074686520636c61696d60801b6064820152608401610329565b6105c933610e04565b565b6105d3610655565b6105ef5760405162461bcd60e51b815260040161032990611408565b6105f881610b8b565b50565b610603610655565b61061f5760405162461bcd60e51b815260040161032990611408565b6105f881610be0565b610630610655565b61064c5760405162461bcd60e51b815260040161032990611408565b6105f881610d7d565b600061066d6000805160206115368339815191525490565b6001600160a01b0316336001600160a01b031614905090565b6033546001600160a01b03163314806106a257506106a2610655565b6106ff5760405162461bcd60e51b815260206004820152602860248201527f43616c6c6572206973206e6f74207468652053747261746567697374206f722060448201526723b7bb32b93737b960c11b6064820152608401610329565b7f53bf423e48ed90e97d02ab0ebab13b2a235a6bfbe9c321847d5c175333ac4535805460028114156107645760405162461bcd60e51b815260206004820152600e60248201526d1499595b9d1c985b9d0818d85b1b60921b6044820152606401610329565b600282556066546001600160a01b03166107c05760405162461bcd60e51b815260206004820152601860248201527f45786368616e67652061646472657373206e6f742073657400000000000000006044820152606401610329565b6000612710606d54866107d391906114b9565b6107dd9190611497565b905060006107eb82876114d8565b905080156109b357600085116108435760405162461bcd60e51b815260206004820152601c60248201527f496e76616c6964206d696e4f475645787065637465642076616c7565000000006044820152606401610329565b6040805160a081018252606754606954606a546068546bffffffffffffffffffffffff19606094851b811660c0870152607d60ea1b60d4870181905293851b811660d787015260eb86019390935290831b821660ee85015261017760eb1b610102850152821b16610105830152825180830360f9018152610119830184528252606b546001600160a01b039081166020840152428385015290820184905260808201889052606654925163c04b8d5960e01b8152919260009291169063c04b8d599061091390859060040161143f565b602060405180830381600087803b15801561092d57600080fd5b505af1158015610941573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906109659190611372565b60685460408051868152602081018490529293506001600160a01b03909116917f081c85c611b9200aca256ff161405227b5defc7280d21384d580e5d8152b2916910160405180910390a250505b8115610a1957606c546067546109d6916001600160a01b03918216911684610b23565b606c546040518381526001600160a01b03909116907f378347ff600be325e8602c4d2a4f3a88534824a63f8bccf6ef494027f2384cba9060200160405180910390a25b50506001825550505050565b610a2d610655565b610a495760405162461bcd60e51b815260040161032990611408565b6105f881610c59565b610a5a610655565b610a765760405162461bcd60e51b815260040161032990611408565b610a9e817f44c4d30b2eaad5130ad70c3ba6972730566f3e6359ab83e800d905c61b1c51db55565b806001600160a01b0316610abe6000805160206115368339815191525490565b6001600160a01b03167fa39cc5eb22d0f34d8beaefee8a3f17cc229c1a1d1ef87a5ad47313487b1c4f0d60405160405180910390a350565b610afe610655565b610b1a5760405162461bcd60e51b815260040161032990611408565b6105f881610ceb565b6040516001600160a01b038316602482015260448101829052610b8690849063a9059cbb60e01b906064015b60408051601f198184030181529190526020810180516001600160e01b03166001600160e01b031990931692909217909152610ec5565b505050565b603380546001600160a01b0319166001600160a01b0383169081179091556040519081527f869e0abd13cc3a975de7b93be3df1cb2255c802b1cead85963cc79d99f131bee906020015b60405180910390a150565b606680546001600160a01b0319166001600160a01b03831690811790915515610c2257606654606754610c22916001600160a01b039182169116600019610f97565b6040516001600160a01b038216907fca20db57f4368388dd6766259da48cd22a485cba21ee6ec8c519007cb66dfd0390600090a250565b6001600160a01b038116610ca15760405162461bcd60e51b815260206004820152600f60248201526e1059191c995cdcc81b9bdd081cd95d608a1b6044820152606401610329565b606b80546001600160a01b0319166001600160a01b0383169081179091556040517f95561238de8d7836da6d15311c07a2546a1a712b477f44391ddd1e6e0556c6cd90600090a250565b6001600160a01b038116610d335760405162461bcd60e51b815260206004820152600f60248201526e1059191c995cdcc81b9bdd081cd95d608a1b6044820152606401610329565b606c80546001600160a01b0319166001600160a01b0383169081179091556040517fd16d2cf254200e4dc6dc82512e9d11673e06a798c40b90cef7583729b4f7a8d490600090a250565b612710811115610dcf5760405162461bcd60e51b815260206004820152601b60248201527f496e76616c696420747265617375727920626970732076616c756500000000006044820152606401610329565b606d8190556040518181527facc8265fd7b5a534b6871947bfb20b579d23cf318ab16207309a0fa235e450cd90602001610bd5565b6001600160a01b038116610e5a5760405162461bcd60e51b815260206004820152601a60248201527f4e657720476f7665726e6f7220697320616464726573732830290000000000006044820152606401610329565b806001600160a01b0316610e7a6000805160206115368339815191525490565b6001600160a01b03167fc7c0c772add429241571afb3805861fb3cfa2af374534088b76cdb4325a87e9a60405160405180910390a36105f88160008051602061153683398151915255565b6000610f1a826040518060400160405280602081526020017f5361666545524332303a206c6f772d6c6576656c2063616c6c206661696c6564815250856001600160a01b03166110bb9092919063ffffffff16565b805190915015610b865780806020019051810190610f389190611337565b610b865760405162461bcd60e51b815260206004820152602a60248201527f5361666545524332303a204552433230206f7065726174696f6e20646964206e6044820152691bdd081cdd58d8d9595960b21b6064820152608401610329565b8015806110205750604051636eb1769f60e11b81523060048201526001600160a01b03838116602483015284169063dd62ed3e9060440160206040518083038186803b158015610fe657600080fd5b505afa158015610ffa573d6000803e3d6000fd5b505050506040513d601f19601f8201168201806040525081019061101e9190611372565b155b61108b5760405162461bcd60e51b815260206004820152603660248201527f5361666545524332303a20617070726f76652066726f6d206e6f6e2d7a65726f60448201527520746f206e6f6e2d7a65726f20616c6c6f77616e636560501b6064820152608401610329565b6040516001600160a01b038316602482015260448101829052610b8690849063095ea7b360e01b90606401610b4f565b60606110ca84846000856110d4565b90505b9392505050565b6060824710156111355760405162461bcd60e51b815260206004820152602660248201527f416464726573733a20696e73756666696369656e742062616c616e636520666f6044820152651c8818d85b1b60d21b6064820152608401610329565b843b6111835760405162461bcd60e51b815260206004820152601d60248201527f416464726573733a2063616c6c20746f206e6f6e2d636f6e74726163740000006044820152606401610329565b600080866001600160a01b0316858760405161119f91906113d9565b60006040518083038185875af1925050503d80600081146111dc576040519150601f19603f3d011682016040523d82523d6000602084013e6111e1565b606091505b50915091506111f18282866111fc565b979650505050505050565b6060831561120b5750816110cd565b82511561121b5782518084602001fd5b8160405162461bcd60e51b815260040161032991906113f5565b80356001600160a01b038116811461124c57600080fd5b919050565b60006020828403121561126357600080fd5b6110cd82611235565b60008060008060008060008060006101208a8c03121561128b57600080fd5b6112948a611235565b98506112a260208b01611235565b97506112b060408b01611235565b96506112be60608b01611235565b95506112cc60808b01611235565b94506112da60a08b01611235565b93506112e860c08b01611235565b92506112f660e08b01611235565b91506101008a013590509295985092959850929598565b6000806040838503121561132057600080fd5b61132983611235565b946020939093013593505050565b60006020828403121561134957600080fd5b815180151581146110cd57600080fd5b60006020828403121561136b57600080fd5b5035919050565b60006020828403121561138457600080fd5b5051919050565b6000806040838503121561139e57600080fd5b50508035926020909101359150565b600081518084526113c58160208601602086016114ef565b601f01601f19169290920160200192915050565b600082516113eb8184602087016114ef565b9190910192915050565b6020815260006110cd60208301846113ad565b6020808252601a908201527f43616c6c6572206973206e6f742074686520476f7665726e6f72000000000000604082015260600190565b602081526000825160a0602084015261145b60c08401826113ad565b905060018060a01b0360208501511660408401526040840151606084015260608401516080840152608084015160a08401528091505092915050565b6000826114b457634e487b7160e01b600052601260045260246000fd5b500490565b60008160001904831182151516156114d3576114d361151f565b500290565b6000828210156114ea576114ea61151f565b500390565b60005b8381101561150a5781810151838201526020016114f2565b83811115611519576000848401525b50505050565b634e487b7160e01b600052601160045260246000fdfe7bea13895fa79d2831e0a9e28edede30099005a50d652d8957cf8a607ee6ca4aa26469706673582212200ecdda767c1f5ae771eccf91eed3b5693d59fa7fe69e3234a134129e0f0f7e9764736f6c63430008070033",
  "devdoc": {
    "kind": "dev",
    "methods": {
      "claimGovernance()": {
        "details": "Claim Governance of the contract to a new account (`newGovernor`). Can only be called by the new Governor."
      },
      "distributeAndSwap(uint256,uint256)": {
        "details": "Computes the split of OUSD for treasury and transfers it. And      then execute a swap of OUSD for OGV with the remaining amount      via Uniswap or Uniswap compatible protocol (e.g. Sushiswap).",
        "params": {
          "minOGVExpected": "Mininum amount of OGV to receive when swapping*",
          "ousdAmount": "OUSD Amount to use from the balance"
        }
      },
      "governor()": {
        "details": "Returns the address of the current Governor."
      },
      "initialize(address,address,address,address,address,address,address,address,uint256)": {
        "params": {
          "_ogv": "OGV Proxy Contract Address",
          "_ousd": "OUSD Proxy Contract Address",
          "_rewardsSource": "Address of RewardsSource contract",
          "_strategistAddr": "Address of Strategist multi-sig wallet",
          "_treasuryBps": "Percentage of OUSD balance to be sent to treasury",
          "_treasuryManagerAddr": "Address that receives the treasury's share of OUSD",
          "_uniswapAddr": "Address of Uniswap",
          "_usdt": "USDT Address",
          "_weth9": "WETH Address"
        }
      },
      "isGovernor()": {
        "details": "Returns true if the caller is the current Governor."
      },
      "setRewardsSource(address)": {
        "details": "Sets the address that receives the OGV buyback rewards",
        "params": {
          "_address": "Address"
        }
      },
      "setStrategistAddr(address)": {
        "details": "Set address of Strategist",
        "params": {
          "_address": "Address of Strategist"
        }
      },
      "setTreasuryBps(uint256)": {
        "details": "Set the Treasury's share of OUSD",
        "params": {
          "_bps": "Percentage of OUSD balance to be sent to treasury"
        }
      },
      "setTreasuryManager(address)": {
        "details": "Sets the address that can receive and manage the funds for Treasury",
        "params": {
          "_address": "Address"
        }
      },
      "setUniswapAddr(address)": {
        "details": "Set address of Uniswap for performing liquidation of strategy reward tokens. Setting to 0x0 will pause swaps.",
        "params": {
          "_address": "Address of Uniswap"
        }
      },
      "swap()": {
        "details": "Execute a swap of OGV for OUSD via Uniswap or Uniswap compatible protocol (e.g. Sushiswap)*"
      },
      "transferGovernance(address)": {
        "details": "Transfers Governance of the contract to a new account (`newGovernor`). Can only be called by the current Governor. Must be claimed for this to complete",
        "params": {
          "_newGovernor": "Address of the new Governor"
        }
      },
      "transferToken(address,uint256)": {
        "params": {
          "amount": "amount of the token to be transferred",
          "token": "token to be transferered"
        }
      }
    },
    "version": 1
  },
  "userdoc": {
    "kind": "user",
    "methods": {
      "transferToken(address,uint256)": {
        "notice": "Owner function to withdraw a specific amount of a token"
      }
    },
    "version": 1
  },
  "storageLayout": {
    "storage": [
      {
        "astId": 23388,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "initialized",
        "offset": 0,
        "slot": "0",
        "type": "t_bool"
      },
      {
        "astId": 23391,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "initializing",
        "offset": 1,
        "slot": "0",
        "type": "t_bool"
      },
      {
        "astId": 23431,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "______gap",
        "offset": 0,
        "slot": "1",
        "type": "t_array(t_uint256)50_storage"
      },
      {
        "astId": 4468,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "strategistAddr",
        "offset": 0,
        "slot": "51",
        "type": "t_address"
      },
      {
        "astId": 4472,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "__gap",
        "offset": 0,
        "slot": "52",
        "type": "t_array(t_uint256)50_storage"
      },
      {
        "astId": 1847,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "uniswapAddr",
        "offset": 0,
        "slot": "102",
        "type": "t_address"
      },
      {
        "astId": 1850,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "ousd",
        "offset": 0,
        "slot": "103",
        "type": "t_contract(IERC20)623"
      },
      {
        "astId": 1853,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "ogv",
        "offset": 0,
        "slot": "104",
        "type": "t_contract(IERC20)623"
      },
      {
        "astId": 1856,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "usdt",
        "offset": 0,
        "slot": "105",
        "type": "t_contract(IERC20)623"
      },
      {
        "astId": 1859,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "weth9",
        "offset": 0,
        "slot": "106",
        "type": "t_contract(IERC20)623"
      },
      {
        "astId": 1861,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "rewardsSource",
        "offset": 0,
        "slot": "107",
        "type": "t_address"
      },
      {
        "astId": 1863,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "treasuryManager",
        "offset": 0,
        "slot": "108",
        "type": "t_address"
      },
      {
        "astId": 1865,
        "contract": "contracts/buyback/Buyback.sol:Buyback",
        "label": "treasuryBps",
        "offset": 0,
        "slot": "109",
        "type": "t_uint256"
      }
    ],
    "types": {
      "t_address": {
        "encoding": "inplace",
        "label": "address",
        "numberOfBytes": "20"
      },
      "t_array(t_uint256)50_storage": {
        "base": "t_uint256",
        "encoding": "inplace",
        "label": "uint256[50]",
        "numberOfBytes": "1600"
      },
      "t_bool": {
        "encoding": "inplace",
        "label": "bool",
        "numberOfBytes": "1"
      },
      "t_contract(IERC20)623": {
        "encoding": "inplace",
        "label": "contract IERC20",
        "numberOfBytes": "20"
      },
      "t_uint256": {
        "encoding": "inplace",
        "label": "uint256",
        "numberOfBytes": "32"
      }
    }
  }
}