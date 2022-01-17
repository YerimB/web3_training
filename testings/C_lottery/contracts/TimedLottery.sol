// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./Lottery.sol";

contract TimedLottery is Lottery {
    uint256 private m_StartTime;
    uint256 private m_EndTime;

    event TimedLotteryStarted(
        uint256 startTime,
        uint256 endTime,
        uint256 usdEntryFee
    );

    event LotteryTimeReached(
        uint256 endTime,
        uint256 currentTime,
        bool isCalculatingWinner
    );

    constructor(
        uint256 _usdEntryFee,
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _linkToken,
        uint256 _fee,
        bytes32 _keyhash
    )
        Lottery(
            _usdEntryFee,
            _priceFeedAddress,
            _vrfCoordinator,
            _linkToken,
            _fee,
            _keyhash
        )
    {}

    function _preEnter() internal override {
        if (m_EndTime > block.timestamp) return;
        // Close lottery entries and emit LotteryTimeReached event.
        m_LotteryState = LotteryState.ENTRIES_CLOSED;
        emit LotteryTimeReached(
            m_EndTime,
            block.timestamp,
            m_LotteryState == LotteryState.CALCULATING_WINNER
        );
    }

    // Lottery starts on function call.
    function startLottery(uint256 _secondsToEnd) public onlyOwner {
        require(
            _secondsToEnd >= 60,
            "Invalid parameter : Minimum lottery time is 60 seconds."
        );
        super.startLottery();
        m_StartTime = block.timestamp;
        m_EndTime = block.timestamp + _secondsToEnd;
    }

    function _postStartLottery() internal override {
        emit TimedLotteryStarted(m_StartTime, m_EndTime, m_UsdEntryFee);
    }

    function startTime() public returns (uint256) {
        return m_StartTime;
    }

    function endTime() public returns (uint256) {
        return m_EndTime;
    }

    function _resetLottery() internal override {
        m_StartTime = 0;
        m_EndTime = 0;
        super._resetLottery();
    }
}
