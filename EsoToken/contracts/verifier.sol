// SPDX-License-Identifier: MIT
// This file is MIT Licensed.
//
// Copyright 2017 Christian Reitwiessner
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
// The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
pragma solidity ^0.8.0;
library Pairing {
    struct G1Point {
        uint X;
        uint Y;
    }
    // Encoding of field elements is: X[0] * z + X[1]
    struct G2Point {
        uint[2] X;
        uint[2] Y;
    }
    /// @return the generator of G1
    function P1() pure internal returns (G1Point memory) {
        return G1Point(1, 2);
    }
    /// @return the generator of G2
    function P2() pure internal returns (G2Point memory) {
        return G2Point(
            [10857046999023057135944570762232829481370756359578518086990519993285655852781,
             11559732032986387107991004021392285783925812861821192530917403151452391805634],
            [8495653923123431417604973247489272438418190587263600148770280649306958101930,
             4082367875863433681332203403145435568316851327593401208105741076214120093531]
        );
    }
    /// @return the negation of p, i.e. p.addition(p.negate()) should be zero.
    function negate(G1Point memory p) pure internal returns (G1Point memory) {
        // The prime q in the base field F_q for G1
        uint q = 21888242871839275222246405745257275088696311157297823662689037894645226208583;
        if (p.X == 0 && p.Y == 0)
            return G1Point(0, 0);
        return G1Point(p.X, q - (p.Y % q));
    }
    /// @return r the sum of two points of G1
    function addition(G1Point memory p1, G1Point memory p2) internal view returns (G1Point memory r) {
        uint[4] memory input;
        input[0] = p1.X;
        input[1] = p1.Y;
        input[2] = p2.X;
        input[3] = p2.Y;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 6, input, 0xc0, r, 0x60)
            // Use "invalid" to make gas estimation work
            switch success case 0 { invalid() }
        }
        require(success);
    }


    /// @return r the product of a point on G1 and a scalar, i.e.
    /// p == p.scalar_mul(1) and p.addition(p) == p.scalar_mul(2) for all points p.
    function scalar_mul(G1Point memory p, uint s) internal view returns (G1Point memory r) {
        uint[3] memory input;
        input[0] = p.X;
        input[1] = p.Y;
        input[2] = s;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 7, input, 0x80, r, 0x60)
            // Use "invalid" to make gas estimation work
            switch success case 0 { invalid() }
        }
        require (success);
    }
    /// @return the result of computing the pairing check
    /// e(p1[0], p2[0]) *  .... * e(p1[n], p2[n]) == 1
    /// For example pairing([P1(), P1().negate()], [P2(), P2()]) should
    /// return true.
    function pairing(G1Point[] memory p1, G2Point[] memory p2) internal view returns (bool) {
        require(p1.length == p2.length);
        uint elements = p1.length;
        uint inputSize = elements * 6;
        uint[] memory input = new uint[](inputSize);
        for (uint i = 0; i < elements; i++)
        {
            input[i * 6 + 0] = p1[i].X;
            input[i * 6 + 1] = p1[i].Y;
            input[i * 6 + 2] = p2[i].X[1];
            input[i * 6 + 3] = p2[i].X[0];
            input[i * 6 + 4] = p2[i].Y[1];
            input[i * 6 + 5] = p2[i].Y[0];
        }
        uint[1] memory out;
        bool success;
        assembly {
            success := staticcall(sub(gas(), 2000), 8, add(input, 0x20), mul(inputSize, 0x20), out, 0x20)
            // Use "invalid" to make gas estimation work
            switch success case 0 { invalid() }
        }
        require(success);
        return out[0] != 0;
    }
    /// Convenience method for a pairing check for two pairs.
    function pairingProd2(G1Point memory a1, G2Point memory a2, G1Point memory b1, G2Point memory b2) internal view returns (bool) {
        G1Point[] memory p1 = new G1Point[](2);
        G2Point[] memory p2 = new G2Point[](2);
        p1[0] = a1;
        p1[1] = b1;
        p2[0] = a2;
        p2[1] = b2;
        return pairing(p1, p2);
    }
    /// Convenience method for a pairing check for three pairs.
    function pairingProd3(
            G1Point memory a1, G2Point memory a2,
            G1Point memory b1, G2Point memory b2,
            G1Point memory c1, G2Point memory c2
    ) internal view returns (bool) {
        G1Point[] memory p1 = new G1Point[](3);
        G2Point[] memory p2 = new G2Point[](3);
        p1[0] = a1;
        p1[1] = b1;
        p1[2] = c1;
        p2[0] = a2;
        p2[1] = b2;
        p2[2] = c2;
        return pairing(p1, p2);
    }
    /// Convenience method for a pairing check for four pairs.
    function pairingProd4(
            G1Point memory a1, G2Point memory a2,
            G1Point memory b1, G2Point memory b2,
            G1Point memory c1, G2Point memory c2,
            G1Point memory d1, G2Point memory d2
    ) internal view returns (bool) {
        G1Point[] memory p1 = new G1Point[](4);
        G2Point[] memory p2 = new G2Point[](4);
        p1[0] = a1;
        p1[1] = b1;
        p1[2] = c1;
        p1[3] = d1;
        p2[0] = a2;
        p2[1] = b2;
        p2[2] = c2;
        p2[3] = d2;
        return pairing(p1, p2);
    }
}

contract Verifier {
    using Pairing for *;
    struct VerifyingKey {
        Pairing.G1Point alpha;
        Pairing.G2Point beta;
        Pairing.G2Point gamma;
        Pairing.G2Point delta;
        Pairing.G1Point[] gamma_abc;
    }
    struct Proof {
        Pairing.G1Point a;
        Pairing.G2Point b;
        Pairing.G1Point c;
    }
    function verifyingKey() pure internal returns (VerifyingKey memory vk) {
        vk.alpha = Pairing.G1Point(uint256(0x2a28372812aa19668118f69f0cf5a96e59209e6b1b327ee82af427408daed2b9), uint256(0x0c01a72c167bb3a2a9e42f6637ca6f7f36da661c05e404321d10bc40dded8270));
        vk.beta = Pairing.G2Point([uint256(0x21554b4de695560b30b8d443e85512c6c0fcea83d4b9cdb57abcb0fa22f421f2), uint256(0x1755eca1a97471eaea0a0e80dcfd9c9dfac7f26c3ca28998164fbb5c45ea8288)], [uint256(0x074cdb960adc694c480e174f98d11e7cf80fd33d58dd7b4cdee5e9a17e0c4f7b), uint256(0x278898bd8cc18def1345c9f9fa74d7384571ee38357835594aaf5ffd1e6beb10)]);
        vk.gamma = Pairing.G2Point([uint256(0x254532a3dcf8b9dc1269e67c016b6bfe451c79a120daafe0ce2135e9b756a6cd), uint256(0x145b73f02967cb36b71ba5bf52c875992b9333fb6f3d34adb99df9a48ae0bd05)], [uint256(0x105f1340557edb99037e807cdd35031f903d8614f8981e193fc4b9cbe3c51fec), uint256(0x2b10b170a3b0ddd838e32ea7e28baf1177777d0340fd767c915663d6948d624a)]);
        vk.delta = Pairing.G2Point([uint256(0x183e87b3aeb1fc565d8308d56276879422f35d2f0b15a7b7317d576664ed2557), uint256(0x26317a9fb04f48947f99cda9d23e69c7ef8b4210006e2afc4408a308d7d1aabf)], [uint256(0x0d09802c95a687f63692ad44c353f82bab46a2694fd4d567fabdbb79877ea0a5), uint256(0x2a10c980407cb319dc3fa4bcc13e55260fccc6a3c753c5b95b0c83e1f56d9890)]);
        vk.gamma_abc = new Pairing.G1Point[](42);
        vk.gamma_abc[0] = Pairing.G1Point(uint256(0x170ecb643c2c7eabd4604f969130b27f1de611f7eb945796013439d9f2e2f358), uint256(0x10e4c41196efdfcf4963277af1b3b0492e8677ebbdc930b7bff930d99f6063c0));
        vk.gamma_abc[1] = Pairing.G1Point(uint256(0x009d66539617c598af5e5faefc54c0aac3f3bfd7160898e0dc8947f4b0f000f6), uint256(0x25a26f760591b8ad5d73a46fbaae6f7ecf35f9e34af3738e1e88069ac0856fbe));
        vk.gamma_abc[2] = Pairing.G1Point(uint256(0x1bede241fba15ef5aca810585ad818402eb729eadba896c7bd3c1961638a2eec), uint256(0x0889e1d70cb30c74ef09fbe641aeef70304e837a9d3a344937acd48cc53b85ea));
        vk.gamma_abc[3] = Pairing.G1Point(uint256(0x290ed180ae93108d4979425aeb0c4472041577cb1d36f64cae08ea92ca0dd251), uint256(0x1656c548f394ad8c7a9e2b579c5eddb689416433b03065fdf8f3a686fdd4b936));
        vk.gamma_abc[4] = Pairing.G1Point(uint256(0x04975b1d23d6fe776185834a77432b13974780770beb4771cc7cb6a2ebe55d65), uint256(0x25cd5fa00452d65a6113bd35bb7bcb51d59f20a3bdfa81b1f5d30e1f50cd0102));
        vk.gamma_abc[5] = Pairing.G1Point(uint256(0x26b41b50b8e5d8b5c4fee3cd506bfad78788219dee938715fd31237c2ca76489), uint256(0x0eb87dfe1ded74e064064258966f530803648b70dd5ab4dcdb50266075f0d2d6));
        vk.gamma_abc[6] = Pairing.G1Point(uint256(0x2661ae05efb6792e7d79bb9954d9ed215f844c403b9a814aec1bf74c0dfedf1b), uint256(0x0afe19edc3583f01a69d2d669e5a7544955c5f877176aaa1d4a3bb7b5fc1f80d));
        vk.gamma_abc[7] = Pairing.G1Point(uint256(0x18720a7fe2bc435d38c737d3b24151eed72e567be17e08a86650a3967ba3bb98), uint256(0x0048b3d5aa8587f6ff2732820a307bc7b9d07b776349322d3e6aabe3a677be9b));
        vk.gamma_abc[8] = Pairing.G1Point(uint256(0x2abdbd7675b6b5ff4553c72571d740008316dc3c5a4fbd909b4da4b226c5048a), uint256(0x16c71caf517c41a025fc1ca0a552953feae1570a304cf2f7f0c6b1cf96e31fba));
        vk.gamma_abc[9] = Pairing.G1Point(uint256(0x251966cd29b94ef30d5b2176d90f763d5aef15163f653885c6ca306217485a5f), uint256(0x21e322f888277eeff2693e073f7deaac8e28fdeeccedc80a2cc5276d4b57fd63));
        vk.gamma_abc[10] = Pairing.G1Point(uint256(0x29ecc2d1e83642989c11b6a50866953a69c45e3080574bb60f5c52697e29a9f9), uint256(0x18e8c2c5ff7be8eb37060617e2e3a46cee27f094b4d24379ad28850210c249bf));
        vk.gamma_abc[11] = Pairing.G1Point(uint256(0x2eb27b0d1ac684e1a7c3b6bfbd50366ff845be5029a8971ddc071cc0146e5aaf), uint256(0x0374dcc365d96329e4cec96ebd05c2a7c38b03735581517ebad6552959f34640));
        vk.gamma_abc[12] = Pairing.G1Point(uint256(0x0bdcf7541dafb906c887021012c5af09c1812f332da2e1a5e87182af20753065), uint256(0x1656c27c7c67c13611c8e4bd5d921650aae5c5664ae627b7c3e97892aa92d3e3));
        vk.gamma_abc[13] = Pairing.G1Point(uint256(0x21968b95f507f67d999d6e4e9a5248ecccb3d77ee0f15bd62647e269eb39b5df), uint256(0x1304f2e828ab67cf216f5a642b86f3908d9acdbeeef9450b853fc1f46cd944e3));
        vk.gamma_abc[14] = Pairing.G1Point(uint256(0x00e50eabeb03fe7ee01a39ce5ec551adda8a3613787a32ce46f8dade2d4c86a1), uint256(0x1ee82d31a9cb7522f814e1f1ff3bf0f85801574276b65f3b0ad2c7aad6ca2cfc));
        vk.gamma_abc[15] = Pairing.G1Point(uint256(0x2b2c34cf4adb33303820370888fdf566b7f74d52a5dfca9dcd82fed52117b1ce), uint256(0x1a08b060d9474274b12e1e4112bd8c79887e584aadad87d1bdb8841481937c0a));
        vk.gamma_abc[16] = Pairing.G1Point(uint256(0x250179b8c5f220a2d159a9d4d9a4877f568c4ee42d695359ab5097452c09ee9b), uint256(0x18eb3ef8e82ef867acb9b2801c121d04f13f97f65aa06099f5100a809d37213d));
        vk.gamma_abc[17] = Pairing.G1Point(uint256(0x00e5f7d42a5dd18f3c260e52ca586373ab6fc59f918a5f5bf7375b2f65673e5b), uint256(0x3053901ccbc3e6324597d15956c9602dbf64d03ad83dca43891707ac80b69fe6));
        vk.gamma_abc[18] = Pairing.G1Point(uint256(0x2973406caab7f97fccc42a0edf71ea425e44af3c55c96526af87e3e9e6f855d0), uint256(0x074f379e2d6c2ce3d5d6820dbe2c363bbd3228fe04b811936d0c70a976b160c1));
        vk.gamma_abc[19] = Pairing.G1Point(uint256(0x1b2653b2d74c45e6d91332ed9d0278edf61b748043f991797cccde6725980f1c), uint256(0x023067ba6f94f2d18e7094b7393eb9ce8f540d57e44e182ffa85d5ec8fc28e62));
        vk.gamma_abc[20] = Pairing.G1Point(uint256(0x1a5560b95599ac85b3a483a14ba5806d4ba970cd1504343d77448502abbca2f2), uint256(0x012cef0ea1278443f96eac243ef9ab195bbe785bf8e3f79a7fdecaffa466e370));
        vk.gamma_abc[21] = Pairing.G1Point(uint256(0x28e50a0d5dcefde447bd4d491f3aafedf3f11664cafcdbf6a56ccf5168614744), uint256(0x178e78b9d16a99ec0b3a47eb8ab0f465607be10b3b49a14a77adbd924c7e2047));
        vk.gamma_abc[22] = Pairing.G1Point(uint256(0x2a891e20e4fdb1fd42a9a3911e3f5aefab4b6c4c7c8c00d81b7601f78c8e6679), uint256(0x160e3082bcf37a7cfc56713bb3c4359c79ea883d47bf4ab18be211b15f8fe3d9));
        vk.gamma_abc[23] = Pairing.G1Point(uint256(0x17f3a3c34dfac676649e1bca1d8a82da5f92b2b038ca76386414e336240ce179), uint256(0x2161b00768616d92db9ec70c994dc31e36f3b36cdae5ad7c7308570fec9f20ee));
        vk.gamma_abc[24] = Pairing.G1Point(uint256(0x0533ec265c7e9d48cd02d602d76a094ddab6b833f3169a2baf74fd0c96a83170), uint256(0x2f951d3b05330ed599ca77f8d8e373ef6883bdb32c6dedbffab48a7a0a219cde));
        vk.gamma_abc[25] = Pairing.G1Point(uint256(0x0e09fcaa57c2cd3bc11e757b0006ed054164ffb6be271278402cde0997fbf480), uint256(0x305d856e5aabef74203f18891f93e82c3959aab612c1d479af27a5cc2636daca));
        vk.gamma_abc[26] = Pairing.G1Point(uint256(0x2b5c6df297f427ac526039a618ad887d5ff13b62b913bc0beb211a874db02a45), uint256(0x150d64a1fc35f460ef7f228b449cb882b81dba0465b2f1a37a05a11d664420db));
        vk.gamma_abc[27] = Pairing.G1Point(uint256(0x1746f640b439d0cdaaa3533f6f67c6793b520d5c5d33ba9b04a941d387225276), uint256(0x1a1d7c190c01d456f76c847185550e83613755d3d4489f0fb24f886ee647656f));
        vk.gamma_abc[28] = Pairing.G1Point(uint256(0x1335e258e43c121eefdb21b79bf3e4c613ade6ffeda7ac5726e32fab338c2926), uint256(0x1a6c5ec190ca607fd34843c9ef55f4849adb7e470315a92aede877afc8c8cbee));
        vk.gamma_abc[29] = Pairing.G1Point(uint256(0x1c15e003988a01af32e849f13879cb5b713ad47fc64335cc7364d278d23f8b12), uint256(0x09661409e4c9ac28c55bfa430e50b85776bb6b36eca13ab1d65a02a3ad6a74e6));
        vk.gamma_abc[30] = Pairing.G1Point(uint256(0x0b6aa87bbb5e4acee3462fc9c17d6587831ebf6085b6ff10b9d9e998a6072b01), uint256(0x212d7b94081d0e225f55d90e3a8246cb39d97b9265d15c219c5bdfd9fe0f55e3));
        vk.gamma_abc[31] = Pairing.G1Point(uint256(0x041ec55cd1a5e6ddf5c0d3e562b564881ef27e06fdb31d2ca0bad567b582891d), uint256(0x13eb30a9743b7d08d0fe37e10c08e498b1a035c2e59d103243b175666d014dcd));
        vk.gamma_abc[32] = Pairing.G1Point(uint256(0x0d0cb14b644d7d2c3f5632fd26c2cd69896ae4b7c7819b77402ac6c32fd6f8ec), uint256(0x17bfaae0cddf3f0e24dc9499335413aca2e3897e53d9bcd2a202c8e732e21e3e));
        vk.gamma_abc[33] = Pairing.G1Point(uint256(0x2780684e638bf183665217a82198daf78116295255586b2b08681f13234fdd15), uint256(0x2370f67059bd8cee7cd9dcd1d52b95dbe976f0bca49b9d668c78dd0bb8551292));
        vk.gamma_abc[34] = Pairing.G1Point(uint256(0x269d622705e9368f5153bb3f22f997fe1254600071611bf0ec87737434c28ddf), uint256(0x2c786a4a710ad8e8a66c4234e8d6ac126d80473a495efea41cfc8966345f9828));
        vk.gamma_abc[35] = Pairing.G1Point(uint256(0x2bdb6ff72368a75d3863cb305b1a9aa98461ca2da92bd6b8d4a1167933300446), uint256(0x0f33fb5e188264ab8cb429495715fffaada8d0a04f1d83311369213179ae6927));
        vk.gamma_abc[36] = Pairing.G1Point(uint256(0x2c54f507880d52d49e214c6292c4b5fa0c43801804f3a59374b89efb9b831506), uint256(0x1f2b1900f8e4ef3b1a696760ddb29fdf9ea8fa88e3251f83cc86a2a5405701a1));
        vk.gamma_abc[37] = Pairing.G1Point(uint256(0x0e7c01a6ec2aad595436baa5e55233375881600a95b6cc00d3dfcc26784dd2f4), uint256(0x0e70aeaa3124a59b70cdd2fafec21e1ca4745603d00ad2092724bffa3f90b2b7));
        vk.gamma_abc[38] = Pairing.G1Point(uint256(0x07dd743fcfeb74cff5ec07d69393d5c5ec20eb4fa5121f626b2a6f8819d66633), uint256(0x2634a9b27435899c39e2e4f129c1781b1ffceac90fe5f8333ead54f4f921adf5));
        vk.gamma_abc[39] = Pairing.G1Point(uint256(0x212d758a969e0f5acad1938103beb6666f00cb14cb89a6e25904f9e3ccda8583), uint256(0x209b590c68e6a27d98b8573fb45b0891b4967c005845fd5c7393311dac03be73));
        vk.gamma_abc[40] = Pairing.G1Point(uint256(0x1362b6fb81320d6e4bbaf5cdd3e82e193d32b90279f7e0e4a0f8b7bfc2817a54), uint256(0x115f3877aeb75e8c24cdeda179a376c017edd623d2a74f84f6f902212b34ae7a));
        vk.gamma_abc[41] = Pairing.G1Point(uint256(0x14b86c5d6cdae5d1236b37ef97868aa6dafc339dbe2c46d8077bcea1a8fad615), uint256(0x0a627b156cafcc509f99574ed5ce4841963767f52342ed8c38cf79fa7f365c97));
    }
    function verify(uint[] memory input, Proof memory proof) internal view returns (uint) {
        uint256 snark_scalar_field = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
        VerifyingKey memory vk = verifyingKey();
        require(input.length + 1 == vk.gamma_abc.length);
        // Compute the linear combination vk_x
        Pairing.G1Point memory vk_x = Pairing.G1Point(0, 0);
        for (uint i = 0; i < input.length; i++) {
            require(input[i] < snark_scalar_field);
            vk_x = Pairing.addition(vk_x, Pairing.scalar_mul(vk.gamma_abc[i + 1], input[i]));
        }
        vk_x = Pairing.addition(vk_x, vk.gamma_abc[0]);
        if(!Pairing.pairingProd4(
             proof.a, proof.b,
             Pairing.negate(vk_x), vk.gamma,
             Pairing.negate(proof.c), vk.delta,
             Pairing.negate(vk.alpha), vk.beta)) return 1;
        return 0;
    }
    function verifyTx(
            Proof memory proof, uint[41] memory input
        ) public view returns (bool r) {
        uint[] memory inputValues = new uint[](41);
        
        for(uint i = 0; i < input.length; i++){
            inputValues[i] = input[i];
        }
        if (verify(inputValues, proof) == 0) {
            return true;
        } else {
            return false;
        }
    }
}
