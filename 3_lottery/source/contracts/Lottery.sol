// SPDX-License-Identifier: MIT

pragma solidity 0.8.11;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Lottery {
    address payable[] public m_Players;
    uint256 public m_UsdEntryFee; // Precision => 18
    AggregatorV3Interface internal m_EthUsdPriceFeed;

    mapping(address => bool) m_PlayerToHasEntered;
    mapping(address => uint256) m_PlayerToUnclaimedMoney;

    constructor(uint256 _usdEntryFee, address _priceFeedAddress) {
        m_UsdEntryFee = _usdEntryFee * (10**18);
        m_EthUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
    }

    function enter() public payable {
        uint256 entrance_fee = this.getEntranceFee();

        // Players can only enter once.
        // Checks if the msg.sender has already entered.
        require(
            m_PlayerToHasEntered[msg.sender] == false,
            "Player has already entered the lottery."
        );
        // Checks if the amount sent by msg.sender is superior
        // or equal to the entrance fee
        require(msg.value >= entrance_fee, "Invalid amount of $ETH sent.");

        // Make player enter the lottery
        m_Players.push(payable(msg.sender));
        m_PlayerToHasEntered[msg.sender] = true;

        // Send back leftovers.
        uint256 leftovers = msg.value - entrance_fee;
        if (leftovers > 0) {
            bool success = send(leftovers, msg.sender);
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

    function startLottery() public {}

    function endLottery() public {}

    function claim() public {
        // Retrieves unclaimed amount of msg.sender
        uint256 unclaimedMoney = m_PlayerToUnclaimedMoney[msg.sender];
        // Unmaps msg.sender from m_PlayerToUnclaimedMoney.
        delete m_PlayerToUnclaimedMoney[msg.sender];
        // Checks for the unclaimed amount to be > 0.
        require(unclaimedMoney > 0, "Nothing to claim.");
        // Tries sending the unclaimed amount to msg.sender
        bool success = send(unclaimedMoney, msg.sender);

        // Requires success of the claim, otherwise : reverts
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

    // Sends '_amount' wei to the specified '_address'
    function send(uint256 _amount, address _address) internal returns (bool) {
        (bool success, ) = _address.call{value: _amount}("");
        return success;
    }
}
