// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.4;
contract Order {
    address public owner;
    address public buyer;
    address public courier;
    uint256 public cost;

    enum State {CREATED, PAID, PICKED_UP, COMPLETE}
    State public state;

    constructor( address _buyer, uint256 _cost){
        owner = msg.sender;
        buyer = _buyer;
        cost = _cost;
        state = State.CREATED;

    }

    modifier onlyBuyer(){
        require(msg.sender == buyer,"Caller of this function must be buyer.");
        _;
    }

    function pickUpPackage() external{
        require(state == State.PAID, "Order must be paid before being picked up.");
        courier = msg.sender;
        state = State.PICKED_UP;
    }

    function pay() external onlyBuyer payable {
        require(state == State.CREATED, "Order must unpaid to be paid.");
        require(msg.value == cost, "Payement value mast equal to the cost.");
        state = State.PAID;
    }

    function delivered() external onlyBuyer{
        require(state == State.PICKED_UP, "Order must be picked up to be delivered.");
        state == State.COMPLETE;


        uint256 courierAmount = cost * 1 / 5;
        uint256 ownerAmount = cost - courierAmount;
        

        payable(courier).transfer(courierAmount);
        payable(owner).transfer(ownerAmount);
    }
}