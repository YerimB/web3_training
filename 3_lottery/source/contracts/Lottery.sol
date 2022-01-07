// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBase, Ownable {
    // TYPES
    enum LotteryState {
        CLOSED,
        OPENED,
        CALCULATING_WINNER
    }

    // VARIABLES
    AggregatorV3Interface internal m_EthUsdPriceFeed;
    uint256 public m_Fee;
    bytes32 public m_Keyhash;
    bytes32 public m_RandomRequestId;
    uint256 public m_PreviousRandomness;

    LotteryState public m_LotteryState;
    address payable[] public m_Players;
    address payable public m_Winner;
    uint256 public m_UsdEntryFee; // Precision => 18

    mapping(address => bool) public m_PlayerToHasEntered;
    mapping(address => uint256) public m_PlayerToUnclaimedMoney;

    // EVENTS
    event RandomnessRequested(bytes32 requestId);

    // METHODS
    constructor(
        uint256 _usdEntryFee,
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _linkToken,
        uint256 _fee,
        bytes32 _keyhash
    ) VRFConsumerBase(_vrfCoordinator, _linkToken) {
        m_UsdEntryFee = _usdEntryFee * (10**18);
        m_EthUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        m_LotteryState = LotteryState.CLOSED;
        m_Fee = _fee;
        m_Keyhash = _keyhash;
    }

    function enter() public payable {
        // Check if the lottery is opened.
        require(
            m_LotteryState == LotteryState.OPENED,
            "Lottery has not started yet."
        );

        // Get entrance fee in wei.
        uint256 entrance_fee = this.getEntranceFee();

        // Players can only enter once.
        // Checks if the msg.sender has already entered.
        require(
            m_PlayerToHasEntered[msg.sender] == false,
            "Player has already entered the lottery."
        );
        // Checks if the amount sent by msg.sender is superior
        // or equal to the entrance fee
        require(msg.value >= entrance_fee, "Insufficient amount of $ETH sent.");

        // Make player enter the lottery
        m_Players.push(payable(msg.sender));
        m_PlayerToHasEntered[msg.sender] = true;

        // Send back leftovers.
        uint256 leftovers = msg.value - entrance_fee;
        if (leftovers > 0) {
            bool success = _send(leftovers, msg.sender);
            if (!success) m_PlayerToUnclaimedMoney[msg.sender] += leftovers;
        }
    }

    // Returns the lottery entrance fee in WEI
    function getEntranceFee() public view returns (uint256) {
        // The $ETH price in USD (precision 8)
        uint256 ethPrice = this._getEthPrice();
        // The precision by which the entrey fee is devided
        uint256 precisionKeeper = 10**8;

        return (m_UsdEntryFee * precisionKeeper) / ethPrice;
    }

    function startLottery() public onlyOwner {
        // Checks if lottery is not currently opened.
        require(
            m_LotteryState == LotteryState.CLOSED,
            "Lottery already in progress."
        );
        // Set lottery state to OPENED.
        m_LotteryState = LotteryState.OPENED;
    }

    function endLottery() public onlyOwner {
        // Change lottery state to CALCULATING_WINNER
        m_LotteryState = LotteryState.CALCULATING_WINNER;

        {
            // Bad way to generate random number.
            // uint256(
            //     keccak256(
            //         abi.encodePacked(
            //             nonce, // Predictable (no. txn)
            //             msg.sender, // Known
            //             block.difficulty, // Can be manipulated by the miners :(
            //             block.timestamp // Predictable
            //         )
            //     )
            // ) % players.length;
        } // DO NOT USE !
        // Request a random number.
        m_RandomRequestId = requestRandomness(m_Keyhash, m_Fee);

        emit RandomnessRequested(m_RandomRequestId);

        /*
         * Second part of the lottery gambling and ending takes place
         * in the callback function for requestRandomness().
         * @see fulfillRandomness() function.
         */
    }

    function claim() public {
        // Retrieves unclaimed amount of msg.sender
        uint256 unclaimedMoney = m_PlayerToUnclaimedMoney[msg.sender];
        // Unmaps msg.sender from m_PlayerToUnclaimedMoney.
        delete m_PlayerToUnclaimedMoney[msg.sender];
        // Checks for the unclaimed amount to be > 0.
        require(unclaimedMoney > 0, "Nothing to claim.");
        // Tries sending the unclaimed amount to msg.sender.
        bool success = _send(unclaimedMoney, msg.sender);

        // Requires success of the claim, otherwise : reverts.
        require(
            success == true,
            "Could not transfer claimable funds to message sender."
        );
    }

    // Returns the price of ETH in USD with a precision of 8.
    function _getEthPrice() public view returns (uint256) {
        (, int256 answer, , , ) = m_EthUsdPriceFeed.latestRoundData();
        return uint256(answer);
    }

    // Gets lottery winner among participants and sends the prize.
    function _sendPrizeToWinner(uint256 _winnerIndex) internal {
        // Gets winners address.
        m_Winner = m_Players[_winnerIndex];

        // Sends funds to winner
        _send(address(this).balance, m_Winner);
        _resetLottery();
    }

    // Overrides the fulfillRandomness function from VRFConsumerBase class.
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            m_RandomRequestId == _requestId,
            "Random number request ID doesn't match the active request ID."
        );
        require(
            m_LotteryState == LotteryState.CALCULATING_WINNER,
            "Invalid lottery state detected."
        );
        require(
            _randomness != 0 && _randomness != m_PreviousRandomness,
            "random-not-found"
        );

        _sendPrizeToWinner(_randomness % m_Players.length);

        // Update previously generated random number.
        m_PreviousRandomness = _randomness;
    }

    // Resets lottery.
    function _resetLottery() internal {
        // Reset players related contract variables
        for (uint256 i = 0; i < m_Players.length; ++i)
            delete m_PlayerToHasEntered[m_Players[i]];
        delete m_Players;
        // Set lottery state to closed.
        m_LotteryState = LotteryState.CLOSED;
    }

    // Sends '_amount' wei to the specified '_address'
    function _send(uint256 _amount, address _address) internal returns (bool) {
        (bool success, ) = _address.call{value: _amount}("");
        return success;
    }
}
