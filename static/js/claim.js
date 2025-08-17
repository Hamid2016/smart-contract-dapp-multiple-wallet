// Fetch policy data securely from backend
async function loadPolicyData() {
    try {
            const response = await fetch("/get-policy-data", {
            method: "POST",  // 👈 Changed from GET to POST
            credentials: "include",  // Still required for cookies
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({}),  // Empty body (or add data if needed)
        });

        if (response.ok) {
            const data = await response.json();

            // Display policy info
            document.getElementById('policyName').textContent = data.name;
            document.getElementById('coverageAmount').textContent = data.coverage;
            document.getElementById('premiumAmount').textContent = data.premium;
            document.getElementById('policyStatus').textContent = data.status ? "Active" : "Inactive";
        } else {
            console.error("Failed to load policy data");
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Load data when page opens
loadPolicyData();

//function to not allow claim amount exceed amount coverage amount
function validateClaimAmount(input) {
    const coverage = parseFloat(document.getElementById("coverageAmount").textContent);
    const claim = parseFloat(input.value);
    const warning = document.getElementById("claimWarning");

    if (!isNaN(claim) && claim > coverage) {
        input.value = coverage;
        warning.style.display = "block";
    } else {
        warning.style.display = "none";
    }
}
//claim button
function submitClaim() {
    alert("Claim submitted!");
    // Add actual submission logic here
}