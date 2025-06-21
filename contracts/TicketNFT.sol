// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract TicketNFT is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    struct TicketInfo {
        uint256 tokenId;
        string uri;
        uint256 price;
        bool isForSale;
    }

    mapping(uint256 => TicketInfo) public tickets;
    uint256[] public allTicketIds;

    constructor() ERC721("NFTTicket", "TKT") {}

    function mintTicket(address recipient, string memory tokenURI, uint256 price) public returns (uint256) {
        _tokenIds.increment();
        uint256 newTicketId = _tokenIds.current();

        _mint(recipient, newTicketId);
        _setTokenURI(newTicketId, tokenURI);

        tickets[newTicketId] = TicketInfo({
            tokenId: newTicketId,
            uri: tokenURI,
            price: price,
            isForSale: true
        });

        allTicketIds.push(newTicketId);

        return newTicketId;
    }

    function buyTicket(uint256 ticketId) public payable {
        address owner = ownerOf(ticketId);
        TicketInfo storage ticket = tickets[ticketId];
        require(ticket.isForSale, "Ticket not for sale");
        require(msg.value >= ticket.price, "Not enough ETH to buy ticket");
        require(msg.sender != owner, "You already own this ticket");

        // Transfer ETH
        payable(owner).transfer(msg.value);

        // Transfer ownership
        _transfer(owner, msg.sender, ticketId);

        // Mark as not for sale
        ticket.isForSale = false;
    }

    // 用户挂出二级市场门票
    function listTicketForResale(uint256 ticketId, uint256 resalePrice) public {
        require(ownerOf(ticketId) == msg.sender, "You don't own this ticket");

        TicketInfo storage ticket = tickets[ticketId];
        ticket.price = resalePrice;
        ticket.isForSale = true;
    }

    // 获取所有门票（前端可筛选）
    function getAllTickets() public view returns (TicketInfo[] memory) {
        TicketInfo[] memory result = new TicketInfo[](allTicketIds.length);
        for (uint i = 0; i < allTicketIds.length; i++) {
            result[i] = tickets[allTicketIds[i]];
        }
        return result;
    }

    // 获取某用户所拥有的票
    function getUserTickets(address user) public view returns (TicketInfo[] memory) {
        uint256 count = balanceOf(user);
        TicketInfo[] memory result = new TicketInfo[](count);
        uint256 index = 0;

        for (uint i = 0; i < allTicketIds.length; i++) {
            if (ownerOf(allTicketIds[i]) == user) {
                result[index] = tickets[allTicketIds[i]];
                index++;
            }
        }

        return result;
    }

    // 获取所有二级市场在售票
    function getResaleTickets() public view returns (TicketInfo[] memory) {
        uint256 resaleCount = 0;
        for (uint i = 0; i < allTicketIds.length; i++) {
            if (tickets[allTicketIds[i]].isForSale) {
                resaleCount++;
            }
        }

        TicketInfo[] memory result = new TicketInfo[](resaleCount);
        uint index = 0;
        for (uint i = 0; i < allTicketIds.length; i++) {
            if (tickets[allTicketIds[i]].isForSale) {
                result[index] = tickets[allTicketIds[i]];
                index++;
            }
        }

        return result;
    }

    // 获取单张票信息
    function getTicket(uint256 tokenId) public view returns (TicketInfo memory) {
        return tickets[tokenId];
    }

    // 获取当前在售票的tokenId数组

}
