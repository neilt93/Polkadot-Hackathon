const HDWalletProvider = require('@truffle/hdwallet-provider');
require('dotenv').config();

const privateKey = process.env.PRIVATE_KEY;

module.exports = {
    networks: {
        moonbeam: {
            provider: () => new HDWalletProvider(privateKey, 'https://moonbeam-alpha.api.onfinality.io/public'),
            network_id: 1287, // Moonbase Alpha network ID
            gas: 5500000,
            confirmations: 2,
            timeoutBlocks: 200,
            skipDryRun: true
        }
    },
    compilers: {
        solc: {
            version: "^0.8.0"
        }
    }
};