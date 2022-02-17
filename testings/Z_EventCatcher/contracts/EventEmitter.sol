// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract EventEmitter {
    event CallEvent(address indexed _from);

    function triggerEvent() public {
        emit CallEvent(msg.sender);
    }
}