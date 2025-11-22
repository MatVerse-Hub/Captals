// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MatVerse Evidence NFT
 * @dev ERC721 token for MatVerse evidence notes
 */
contract EvidenceNFT is ERC721, ERC721URIStorage, Ownable {
    uint256 private _tokenIdCounter;

    event NFTMinted(address indexed to, uint256 indexed tokenId, string uri);

    constructor() ERC721("MatVerse Evidence Note", "MVEV") Ownable(msg.sender) {
        _tokenIdCounter = 0;
    }

    /**
     * @dev Mint a new NFT
     * @param to Address to mint to
     * @param tokenId Token ID
     * @param uri Metadata URI (IPFS)
     */
    function safeMint(address to, uint256 tokenId, string memory uri) public onlyOwner {
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        emit NFTMinted(to, tokenId, uri);
    }

    /**
     * @dev Auto-increment mint function
     * @param to Address to mint to
     * @param uri Metadata URI
     */
    function mintNext(address to, string memory uri) public onlyOwner returns (uint256) {
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter += 1;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        emit NFTMinted(to, tokenId, uri);
        return tokenId;
    }

    /**
     * @dev Get current token counter
     */
    function getCurrentTokenId() public view returns (uint256) {
        return _tokenIdCounter;
    }

    // Override required functions
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
