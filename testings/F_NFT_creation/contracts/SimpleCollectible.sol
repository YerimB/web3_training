// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract SimpleCollectible is ERC721URIStorage {
    uint256 public m_TokenCounter; // Init to zero

    constructor(string memory _name, string memory _symbol)
        ERC721(_name, _symbol)
    {}

    function createCollectible(string memory _tokenURI)
        public
        returns (uint256)
    {
        uint256 newTokenId = m_TokenCounter;
        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, _tokenURI);
        m_TokenCounter += 1;
        return newTokenId;
    }
}
