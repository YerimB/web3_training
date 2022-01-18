// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract EventEmitter {
    event ContractCreated();
    event CallEvent(address sender);

    constructor() {
        emit ContractCreated();
    }

    function triggerEvent() public {
        emit CallEvent(msg.sender);
    }
}