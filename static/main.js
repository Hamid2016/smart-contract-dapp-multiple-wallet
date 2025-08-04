let web3;
let userAccount;

document.addEventListener("DOMContentLoaded", function () {
    const statusDiv = document.getElementById("status");
    const connectButton = document.getElementById("connectButton");
    const createPolicyButton = document.getElementById("createPolicyButton");
    const disconnectButton = document.getElementById("disconnectButton");
    const coverageAmount = document.getElementById("coverageAmount");

    // Connect wallet handler
    connectButton.onclick = async function () {
        await connectWallet();
    };

    async function connectWallet() {
        try {
            if (!window.ethereum) {
                alert("No wallet installed.");
                logToBackend("WALLET_CHECK", "No wallet installed.");
                return;
            }
            web3 = new Web3(window.ethereum);
            const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
            userAccount = accounts[0];

            if (!userAccount) {
                alert("Please connect your wallet first.");
                logToBackend("WALLET_ERROR", "Please connect your wallet first.");
                return;
            }

            statusDiv.innerText = `Connecting: ${userAccount}`;
            const message = "Confirm wallet connection";
            const signature = await window.ethereum.request({
                method: "personal_sign",
                params: [message, userAccount],
            });

            const response = await fetch("/connect-wallet", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ address: userAccount, signature: signature }),
            });
            const data = await response.json();
            alert(data.message);
            statusDiv.textContent = `Connected: ${userAccount}`;
            connectButton.disabled = true;
            logToBackend("WALLET_CONNECTED", userAccount);
        } catch (error) {
            statusDiv.textContent = `Error: ${error.message}`;
            logToBackend("WALLET_CONNECTION_ERROR", error.message);
        }
    }

    createPolicyButton.addEventListener("click", async function () {
        if (!userAccount) {
            alert("Please connect your wallet first.");
            logToBackend("WALLET_ERROR", "Please connect your wallet first.");
            return;
        }

        const policyName = document.getElementById("policyName").value;
        const premium = parseFloat(document.getElementById("premium").value);
        const coverageAmount = parseFloat(document.getElementById("coverageAmount").value);

        if (!policyName || isNaN(premium) || isNaN(coverageAmount)) {
            alert("Please fill in all fields correctly.");
            logToBackend("FILL_ALL_FIEILDS", "Please fill in all fields correctly.");
            return;
        }

        try {
            const chainId = await web3.eth.getChainId();
            if (chainId !== 11155111) {
                await window.ethereum.request({
                    method: 'wallet_switchEthereumChain',
                    params: [{ chainId: '0xaa36a7' }]
                });
            }

            const response = await fetch(`/create-policy`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    address: userAccount,
                    policy_name: policyName,
                    premium: premium,
                    coverage_amount: coverageAmount,
                }),
            });

            const txData = await response.json();
            if (!txData.to) {
                alert("Transaction error: Missing 'to' address.");
                console.error("Transaction data missing 'to' field:", txData);
                logToBackend("TRANSACTION_MISSING_TO", "No to address");
                return;
            }

            txData.from = userAccount;
            txData.value = web3.utils.toHex(txData.value);
            txData.gas = web3.utils.toHex(txData.gas);
            txData.maxFeePerGas = web3.utils.toHex(txData.maxFeePerGas);
            txData.maxPriorityFeePerGas = web3.utils.toHex(txData.maxPriorityFeePerGas);

            const signedTx = await web3.eth.sendTransaction(txData);
            console.log("Transaction result:", signedTx);
            alert(`Transaction sent! TxHash: ${signedTx.transactionHash}`);
            logToBackend("TRANSACTION_SENT", `Hash is ${signedTx.transactionHash}`);
        } catch (error) {
            console.error("Transaction failed:", error);
            alert("Transaction failed. Check console for details.");
            logToBackend("TRANSACTION_FAILED",`Error is ${error}`)
        }
    });

    disconnectButton.addEventListener("click", async function () {
        if (confirm("Are you sure you want to disconnect your wallet and revoke permissions?")) {
            try {
                await window.ethereum.request({
                    method: "wallet_revokePermissions",
                    params: [{ eth_accounts: {} }],
                });

                userAccount = null;
                web3 = null;
                statusDiv.innerText = "Not Connected";
                connectButton.disabled = false;

                alert("Wallet disconnected. You may need to reconnect manually next time.");
                logToBackend("WALLET_DISCONNECTED", "You may need to reconnect manually next time. ");

            } catch (error) {
                console.error("Failed to revoke permissions:", error);
                alert("Could not revoke permissions automatically.");
                logToBackend("REVOKE_PERMISSION_ERROR","Could not revoke permissions")
                window.location.reload();
            }
        }
    });

    window.getPolicies = async function () {
        try {
            document.getElementById("policyTable").innerHTML = "";
            const response = await fetch("/get-policies", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ address: userAccount }),
            });
            const policies = await response.json();

            if (!userAccount) {
                alert("Please connect your wallet first.");
                logToBackend("WALLET_CHECK", "No wallet installed.");
                return;
            }

            let policyList = "";
            policies.forEach(policy => {
                const premiumInEther = web3.utils.fromWei(policy.premium.toString(), 'ether');
                const coverageAmountInEther = web3.utils.fromWei(policy.coverageAmount.toString(), 'ether');
                policyList += `
                    <tr>
                        <td>${policy.policyName}</td>
                        <td>${premiumInEther}</td>
                        <td>${coverageAmountInEther}</td>
                        <td>${policy.isActive ? "Active" : "Inactive"}</td>
                        <td>Claim</td>
                    </tr>
                `;
            });

            document.getElementById("policyTable").innerHTML = policyList;
            logToBackend("GET_POLICY","Response 200")
        } catch (error) {
            console.error("Error fetching policies", error);
            alert("Error fetching policies");
            logToBackend("ERROR_POLICIES","Error fetching policies")
        }
    };
});

// Enable create button when checkbox is checked
document.getElementById('policyCheck').addEventListener('change', function() {
    document.getElementById('createPolicyButton').disabled = !this.checked;
});

// Validate coverage amount range
function validateRange(input) {
    const value = parseFloat(input.value);
    if (value < 50000000) input.value = 50000000;
    if (value > 1000000000) input.value = 1000000000;
}

// Update coverage label dynamically
document.addEventListener("DOMContentLoaded", function() {
    const input = document.getElementById('coverageAmount');
    const label = document.getElementById('policyLabel');

    input.addEventListener('input', function() {
        const value = this.value || '0';
        label.textContent = `تعهد جبران خسارت بدنه ماشین ناشی از تصادف تا سقف ${value} ریال است. جهت خرید، لطفاً تیک را فعال کنید`;
    });
});


function logToBackend(eventType, message) {
    fetch("/frontend-log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            event: eventType,
            message: message
        })
    })
    .then(res => res.json())
    .then(data => {
        console.log("Log response:", data.status); // Optional for debugging
    })
    .catch(err => console.error("Log failed:", err));
}