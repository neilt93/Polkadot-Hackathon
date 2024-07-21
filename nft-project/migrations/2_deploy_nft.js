const NFT = artifacts.require("NFT");

module.exports = async function (deployer, network, accounts) {
    const initialOwner = accounts[0];
    await deployer.deploy(NFT, initialOwner);
};
