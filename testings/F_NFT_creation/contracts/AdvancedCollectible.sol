// NFT Contract that generate collectible with random image between predefined set.

// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract AdvancedCollectible is ERC721URIStorage, VRFConsumerBase {
    // VARIABLES
    // --- vrf
    uint256 public m_Fee;
    bytes32 public m_Keyhash;
    // --- member
    uint256 public m_TokenCounter; // Init to zero

    mapping(uint256 => CollectibleType) public m_TokenIdToCollectibleType;
    mapping(CollectibleType => string) public m_TypeToURI;
    mapping(bytes32 => address) internal m_RequestIdToSender;

    // ENUMS
    enum CollectibleType {
        FROLIAN,
        POTATO,
        ALDERIATE
    }

    // EVENTS
    event randomnessRequested(bytes32 requestId);
    event randomnessReceived(
        bytes32 indexed requestId,
        uint256 randomness,
        CollectibleType collectibleType
    );
    event collectibleRequested(bytes32 indexed requestId, address sender);
    event collectibleMinted(
        uint256 indexed tokenId,
        CollectibleType indexed collectibleType,
        string tokenURI,
        address owner
    );

    constructor(
        string memory _name,
        string memory _symbol,
        address _vrfCoordinator,
        address _linkToken,
        uint256 _fee,
        bytes32 _keyhash
    ) ERC721(_name, _symbol) VRFConsumerBase(_vrfCoordinator, _linkToken) {
        // VRFConsumerBase variables
        m_Fee = _fee;
        m_Keyhash = _keyhash;
        // Init type to collectible uri mapping
        m_TypeToURI[
            CollectibleType.FROLIAN
        ] = "https://ipfs.io/ipfs/QmYjNhogVukEobwJDYg9PiGeX9cANmXudVdhvZJTLApR9Y?filename=frolian.json";
        m_TypeToURI[
            CollectibleType.POTATO
        ] = "https://ipfs.io/ipfs/QmXHH6mtYSVBjQ5gCTrMuh5XBL5M74gLTiGYUT39Dz7rwo?filename=mr_patate_marchais.json";
        m_TypeToURI[
            CollectibleType.ALDERIATE
        ] = "https://ipfs.io/ipfs/QmWbNnhSAhtKcGRjeRKJgt2pEJySjgZVmrQe65x73TXZu3?filename=alde_defense.json";
    }

    // METHODS

    function createCollectible() public returns (bytes32) {
        bytes32 requestId = requestRandomness(m_Keyhash, m_Fee);
        emit randomnessRequested(requestId);

        m_RequestIdToSender[requestId] = msg.sender;
        emit collectibleRequested(requestId, msg.sender);

        return requestId;
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        // Get requestData from _requestId
        address requestSender = m_RequestIdToSender[_requestId];
        // Assign type to newTokenId
        CollectibleType newCollectibleType = CollectibleType(
            _randomness % (uint8(type(CollectibleType).max) + 1)
        );
        emit randomnessReceived(_requestId, _randomness, newCollectibleType);

        _mintCollectible(requestSender, newCollectibleType);
    }

    function _mintCollectible(address _sender, CollectibleType _type) internal {
        uint256 newTokenId = m_TokenCounter;

        m_TokenIdToCollectibleType[newTokenId] = _type;
        _safeMint(_sender, newTokenId);
        _setTokenURI(newTokenId, m_TypeToURI[_type]);

        // On minted finished, emit event and update counter
        emit collectibleMinted(newTokenId, _type, m_TypeToURI[_type], _sender);
        m_TokenCounter += 1;
    }
}
