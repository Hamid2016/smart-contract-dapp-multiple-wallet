// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract Insurance {
    address public owner;
    
    struct Policy {
        string policyName;
        uint256 premium;
        uint256 coverageAmount;
        bool isActive;
    }

    mapping(address => Policy[]) public policies;

    event PolicyCreated(address indexed insured, string policyName, uint256 premium, uint256 coverageAmount);

    constructor() {
        owner = msg.sender; // Set contract owner
    }

    // Add payable modifier and value transfer
    function createPolicy(string memory _policyName, uint256 _premium, uint256 _coverageAmount) public payable {
        require(msg.value == _premium, "Incorrect ETH amount sent");
        
        // Transfer ETH to contract owner
        payable(owner).transfer(msg.value);

        policies[msg.sender].push(Policy({
            policyName: _policyName,
            premium: _premium,
            coverageAmount: _coverageAmount,
            isActive: true
        }));

        emit PolicyCreated(msg.sender, _policyName, _premium, _coverageAmount);
    }

    function getPolicies() public view returns (Policy[] memory) {
        return policies[msg.sender];
    }
}