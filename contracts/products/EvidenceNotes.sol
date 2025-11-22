// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title EvidenceNotes
 * @dev Soulbound NFTs for investment certification and proof of participation
 * These tokens cannot be transferred once minted (soulbound)
 */
contract EvidenceNotes is ERC721, Ownable {
    using Counters for Counters.Counter;

    Counters.Counter private _tokenIds;

    struct NoteData {
        string evidenceHash;      // IPFS hash or data hash
        uint256 amount;           // Investment amount
        uint256 timestamp;        // Creation timestamp
        string productType;       // Type of investment (Fund, Bond, etc.)
        bool isActive;           // Status of the note
    }

    // Token ID to note data
    mapping(uint256 => NoteData) public noteData;

    // User to their token IDs
    mapping(address => uint256[]) public userNotes;

    // Events
    event NoteMinted(address indexed to, uint256 indexed tokenId, string productType, uint256 amount);
    event NoteRevoked(uint256 indexed tokenId);

    constructor() ERC721("Omega Evidence Note", "OENOTE") {}

    /**
     * @dev Mint a soulbound Evidence Note NFT
     * @param to Recipient address
     * @param evidenceHash Hash of the evidence data
     * @param amount Investment amount
     * @param productType Type of investment product
     * @return tokenId The minted token ID
     */
    function mintEvidenceNote(
        address to,
        string memory evidenceHash,
        uint256 amount,
        string memory productType
    ) public onlyOwner returns (uint256) {
        require(to != address(0), "Invalid recipient");
        require(bytes(evidenceHash).length > 0, "Evidence hash required");
        require(amount > 0, "Amount must be positive");

        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();

        _safeMint(to, newTokenId);

        noteData[newTokenId] = NoteData({
            evidenceHash: evidenceHash,
            amount: amount,
            timestamp: block.timestamp,
            productType: productType,
            isActive: true
        });

        userNotes[to].push(newTokenId);

        emit NoteMinted(to, newTokenId, productType, amount);

        return newTokenId;
    }

    /**
     * @dev Batch mint Evidence Notes
     * @param recipients Array of recipient addresses
     * @param evidenceHashes Array of evidence hashes
     * @param amounts Array of investment amounts
     * @param productTypes Array of product types
     */
    function batchMintEvidenceNotes(
        address[] memory recipients,
        string[] memory evidenceHashes,
        uint256[] memory amounts,
        string[] memory productTypes
    ) external onlyOwner {
        require(
            recipients.length == evidenceHashes.length &&
            recipients.length == amounts.length &&
            recipients.length == productTypes.length,
            "Arrays length mismatch"
        );

        for (uint256 i = 0; i < recipients.length; i++) {
            mintEvidenceNote(recipients[i], evidenceHashes[i], amounts[i], productTypes[i]);
        }
    }

    /**
     * @dev Revoke an Evidence Note (mark as inactive)
     * @param tokenId Token ID to revoke
     */
    function revokeNote(uint256 tokenId) external onlyOwner {
        require(_exists(tokenId), "Token does not exist");
        noteData[tokenId].isActive = false;
        emit NoteRevoked(tokenId);
    }

    /**
     * @dev Get all notes for a user
     * @param user User address
     * @return Array of token IDs
     */
    function getUserNotes(address user) external view returns (uint256[] memory) {
        return userNotes[user];
    }

    /**
     * @dev Get note data
     * @param tokenId Token ID
     * @return Note data struct
     */
    function getNoteData(uint256 tokenId) external view returns (NoteData memory) {
        require(_exists(tokenId), "Token does not exist");
        return noteData[tokenId];
    }

    /**
     * @dev Override transfer functions to make tokens soulbound
     */
    function transferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public virtual override {
        revert("EvidenceNotes: Soulbound tokens cannot be transferred");
    }

    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public virtual override {
        revert("EvidenceNotes: Soulbound tokens cannot be transferred");
    }

    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes memory data
    ) public virtual override {
        revert("EvidenceNotes: Soulbound tokens cannot be transferred");
    }

    /**
     * @dev Check if token exists
     */
    function _exists(uint256 tokenId) internal view returns (bool) {
        return tokenId > 0 && tokenId <= _tokenIds.current();
    }

    /**
     * @dev Get total supply
     */
    function totalSupply() external view returns (uint256) {
        return _tokenIds.current();
    }
}
