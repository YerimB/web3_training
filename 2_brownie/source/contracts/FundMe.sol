// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract FundMe {
    // TYPES

    struct Funder {
        bool isFunder;
        uint256 amountFunded;
        uint256 index;
    }

    // VARIABLES

    address public m_Owner;
    address[] public m_Funders;
    uint256 m_entranceFeeUSD = 50;
    AggregatorV3Interface public m_PriceFeed;

    mapping(address => Funder) public m_AddressToFunderData;

    // MODIFIERS

    modifier onlyOwner() {
        require(
            msg.sender == m_Owner,
            "Only the owner of the contract can run this function"
        );
        _; // Resume
    }

    modifier onlyFunder() {
        require(
            this._isFunder(msg.sender),
            "Only funders of the contract can run this function"
        );
        _; // Resume
    }

    // METHODS

    constructor(address _priceFeedAddress) {
        m_PriceFeed = AggregatorV3Interface(_priceFeedAddress);
        m_Owner = msg.sender;
    }

    function fund() public payable {
        // Comparison is made in GWEI unit.
        require(
            (msg.value / 10**9) >= this._getEntranceFee(),
            "Try spending more $ETH !"
        );

        // Add funder to data if first time
        if (this._isFunder(msg.sender) == false) {
            m_Funders.push(msg.sender);
            m_AddressToFunderData[msg.sender] = Funder({
                isFunder: true,
                amountFunded: 0,
                index: m_Funders.length - 1
            });
        }
        m_AddressToFunderData[msg.sender].amountFunded += msg.value;
    }

    function withdrawWei(uint256 _amount) public onlyFunder {
        // Checks if the contract has enough funds, if not : BIG EXPLOIT.
        require(
            address(this).balance >= _amount,
            "Contract : Insufficient funds"
        );
        // Checks if the funder has enough funds to withdraw _amount.
        require(
            m_AddressToFunderData[msg.sender].amountFunded >= _amount,
            "You cannot withdraw more than the amount you have founded."
        );

        payable(msg.sender).transfer(_amount);
        m_AddressToFunderData[msg.sender].amountFunded -= _amount;

        if (m_AddressToFunderData[msg.sender].amountFunded == 0) {
            delete (m_Funders[m_AddressToFunderData[msg.sender].index]);
            delete (m_AddressToFunderData[msg.sender]);
        }
    }

    function withdrawGwei(uint256 _amount) public {
        this.withdrawWei(_amount * 10**9);
    }

    function withdrawEth(uint256 _amount) public {
        this.withdrawWei(_amount * 10**18);
    }

    function _setEntranceFee(uint256 _newEntranceFeeUSD) public onlyOwner {
        // Sets the entrance fee in USD
        m_entranceFeeUSD = _newEntranceFeeUSD;
    }

    function _setPriceFeedAddress(address _address) public onlyOwner {
        m_PriceFeed = AggregatorV3Interface(_address);
    }

    // Returns the minimum USD amount in GWEI (or ETH with a precision of 9)
    // to create a successful fund transaction.
    function _getEntranceFee() public view returns (uint256) {
        uint256 ethPrice = this._getPrice();
        // uint256 ethPricePrecision = 10**8;
        // uint256 gweiPrecision = 10**9;
        // uint256 totalPrecision = ethPricePrecision * gweiPrecision;
        uint256 totalPrecision = 10**17;

        return ((m_entranceFeeUSD * totalPrecision) / ethPrice);
    }

    // Gets ETH price in USD with a precision of 8
    function _getPrice() public view returns (uint256) {
        (, int256 answer, , , ) = m_PriceFeed.latestRoundData();
        return uint256(answer);
    }

    // Converts WEI to USD with a precision of 8.
    // Parameter weiAmount has a precision of 18.
    function _weiToUsd(uint256 weiAmount) public view returns (uint256) {
        // Precision of 8 applied to ethPrice.
        uint256 ethPrice = this._getPrice();
        // Divide by (10^10) * (10^8) == (10^18) -> Keeps a precision of 8.
        uint256 usdValue = (ethPrice * weiAmount) / (10**18);

        return usdValue;
    }

    function _gweiToUsd(uint256 gweiAmount) public view returns (uint256) {
        return this._weiToUsd(gweiAmount * (10**9));
    }

    function _ethToUsd(uint256 ethAmount) public view returns (uint256) {
        return this._weiToUsd(ethAmount * (10**18));
    }

    function _isFunder(address _address) public view returns (bool) {
        return m_AddressToFunderData[_address].isFunder;
    }

    function _getVersion() public view returns (uint256) {
        return m_PriceFeed.version();
    }
}
