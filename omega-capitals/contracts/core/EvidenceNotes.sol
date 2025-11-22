// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

/**
 * @title EvidenceNotes
 * @dev NFT representing immutable evidence notes for portfolio strategies
 * Each token stores metadata URI pointing to IPFS/Arweave with strategy details
 */
contract EvidenceNotes is ERC721Burnable, ERC721URIStorage, Ownable {
    uint256 private _tokenIdCounter;

    // Events
    event EvidenceCreated(uint256 indexed tokenId, address indexed recipient, string uri);
    event EvidenceBurned(uint256 indexed tokenId, address indexed burner);

    constructor() ERC721("EvidenceNote", "EVI") Ownable(msg.sender) {}

    /**
     * @dev Mint new evidence note with metadata URI
     * @param to Recipient address
     * @param uri IPFS/Arweave URI containing evidence data
     * @return tokenId The newly created token ID
     */
    function mint(address to, string memory uri) external onlyOwner returns (uint256) {
        uint256 tokenId = ++_tokenIdCounter;
        _mint(to, tokenId);
        _setTokenURI(tokenId, uri);

        emit EvidenceCreated(tokenId, to, uri);
        return tokenId;
    }

    /**
     * @dev Batch mint multiple evidence notes
     * @param recipients Array of recipient addresses
     * @param uris Array of metadata URIs
     */
    function batchMint(address[] calldata recipients, string[] calldata uris) external onlyOwner {
        require(recipients.length == uris.length, "Length mismatch");

        for (uint256 i = 0; i < recipients.length; i++) {
            mint(recipients[i], uris[i]);
        }
    }

    /**
     * @dev Get total supply of evidence notes
     */
    function totalSupply() external view returns (uint256) {
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
        override(ERC721URIStorage, ERC721)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
        emit EvidenceBurned(tokenId, msg.sender);
    }
}
