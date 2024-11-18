// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;
import "./verifier.sol";
import "hardhat/console.sol";

contract MarginalPrice {
    Verifier verifierContract;

    mapping(address => bytes1[64]) public commits_hash;
    mapping(address => bytes) public commits_encryption;
    address[] public participants;
    uint256 verification_key;
    uint marginal_price;
    Verifier.Proof proof;
    bytes private homomorphic_key;    //publick key of paillier
    bytes auctioneer_key;

    function FetchAllParticipants() view public returns(address[] memory){
        return  participants;   //clear all bids
    }

    function FetchCommitsEncryption(uint index) view public returns(bytes memory){
        require(index< participants.length,"index outrange");
        return commits_encryption[participants[index]];
    }

    function UpdateHomomorphicKey(bytes memory pub_key) public {
        console.log("UpdateHomomorphicKey");
        console.logBytes(pub_key);
        homomorphic_key = pub_key;
        delete  participants;   //clear all bids
    }

    function getHomomorphicKey() view public returns(bytes memory){
        return homomorphic_key;
    }

    function UpdateAuctioneerKey(bytes memory pub_key) public {
        console.log("UpdateAuctioneerKey");
        // console.logBytes(pub_key);
        auctioneer_key = pub_key;
        delete  participants;   //clear all bids
    }

    function getAuctioneerKey() view public returns(bytes memory){
        return auctioneer_key;
    }

    function UploadVerificationKey(uint256 key) public {
        verification_key = key;
    }

    function SubmitCommit(bytes1[64] memory commit_hash,bytes memory commit_encryption) public {
        require(participants.length <= 10);
        commits_hash[msg.sender] = commit_hash;
        commits_encryption[msg.sender] = commit_encryption;
        console.log("SubmitCommit");
        console.logAddress(msg.sender);
        participants.push(msg.sender);
    }

    function UploadMarginalPriceFouce(uint price) public {
        marginal_price = price;
        console.log("UploadMarginalPrice marginal_price is %d",marginal_price);
        delete  participants;   //clear all bids
    }

    function UploadMarginalPrice(Verifier.Proof memory proof_,uint price) public {
        require(verify(proof_,price) == true,"verify fail");
        UploadProof(proof_);
        marginal_price = price;
    }

    function UploadProof(Verifier.Proof memory proof_) public {
        proof = proof_;
    }

    function splituint256(
        bytes1[64] memory data
    ) private pure returns (uint  part1, uint  part2) {
        // 提取前 16 字节 (128 位) 和后 16 字节
        assembly {
            part1 := mload(add(data, 64)) // 提取前 32 字节
            part2 := mload(add(data, 32)) // 提取后 32 字节
        }
        return (part1,part2);
    }

    function verify(Verifier.Proof memory proof_,uint price) public view returns (bool) {
        uint[41] memory public_input;
        public_input[0] = price;
        for (uint i = 0; i < participants.length; i++) {
            public_input[4 * i + 1] = uint256(uint160(participants[i]));
            public_input[4 * i + 2] = 0;
            (public_input[4 * i + 3], public_input[4 * i + 4]) = splituint256(
                commits_hash[participants[i]]
            );
        }
        bool isValid = verifierContract.verifyTx(proof_, public_input);

        return isValid;
    }
}
