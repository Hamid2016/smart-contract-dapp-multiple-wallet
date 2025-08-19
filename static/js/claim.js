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


let map;
let marker;

function openMapModal() {
    document.getElementById('mapModal').style.display = 'block';

    if (!map) {
        map = L.map('map').setView([35.6892, 51.3890], 12); // Tehran

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // 📍 Add location button (no functionality yet)
        L.Control.MyLocation = L.Control.extend({
            onAdd: function(map) {
                const btn = L.DomUtil.create('button');
                btn.innerHTML = '📍';
                btn.title = 'Use My Location';
                btn.style.background = '#fff';
                btn.style.border = '2px solid #ccc';
                btn.style.padding = '1px';
                btn.style.cursor = 'pointer';
                btn.style.borderRadius = '4px';
                btn.style.boxShadow = '0 1px 4px rgba(0,0,0,0.3)';
                // shows current location
                btn.onclick = function() {
                    if (!navigator.geolocation) {
                        alert("Geolocation is not supported by your browser.");
                        return;
                    }

                    navigator.geolocation.getCurrentPosition(
                        function(position) {
                            const lat = position.coords.latitude;
                            const lng = position.coords.longitude;
                            const userLocation = L.latLng(lat, lng);

                            if (marker) {
                                marker.setLatLng(userLocation);
                            } else {
                                marker = L.marker(userLocation).addTo(map);
                            }

                            map.setView(userLocation, 16);

                            // Reverse geocode to get address
                            fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
                                .then(response => response.json())
                                .then(data => {
                                    const address = data.display_name || `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`;
                                    document.getElementById('location').value = address;
                                })
                                .catch(error => {
                                    console.error("Reverse geocoding failed:", error);
                                    document.getElementById('location').value = `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`;
                                });
                        },
                        function(error) {
                            alert("Unable to retrieve your location.");
                        }
                    );
                };
                

                return btn;
            },
            onRemove: function(map) {}
        });

        L.control.myLocation = function(opts) {
            return new L.Control.MyLocation(opts);
        }

        //add searchbox
        L.Control.SearchBox = L.Control.extend({
            onAdd: function(map) {
                const container = L.DomUtil.create('div');
                container.style.background = '#fff';
                container.style.padding = '4px';
                container.style.borderRadius = '4px';
                container.style.boxShadow = '0 1px 4px rgba(0,0,0,0.3)';

                const input = L.DomUtil.create('input', '', container);
                input.id = 'mapSearchInput';// id for searchbox
                input.type = 'text';
                input.placeholder = 'Search location...';
                input.style.width = '160px';
                input.style.padding = '4px';
                input.style.border = '1px solid #ccc';
                input.style.borderRadius = '4px';

                L.DomEvent.disableClickPropagation(container); // Prevent map drag while typing

                return container;
            },
            onRemove: function(map) {}
        });

        L.control.searchBox = function(opts) {
            return new L.Control.SearchBox(opts);
        };

        //location for location btn
        L.control.myLocation({ position: 'topleft' }).addTo(map);

        //location for search
        L.control.searchBox({ position: 'topright' }).addTo(map);

        //
        document.getElementById('mapSearchInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const query = e.target.value.trim();
                if (!query) return;

                fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(results => {
                        if (results.length === 0) {
                            alert("Location not found.");
                            return;
                        }

                        const { lat, lon, display_name } = results[0];
                        const location = L.latLng(lat, lon);

                        if (marker) {
                            marker.setLatLng(location);
                        } else {
                            marker = L.marker(location).addTo(map);
                        }

                        map.setView(location, 14);
                        document.getElementById('location').value = display_name;
                    })
                    .catch(error => {
                        console.error("Search failed:", error);
                        alert("Error searching location.");
                    });
            }
        });



        // 🖱️ Handle map click
        map.on('click', function(e) {
            const { lat, lng } = e.latlng;

            if (marker) {
                marker.setLatLng(e.latlng);
            } else {
                marker = L.marker(e.latlng).addTo(map);
            }

            // 🔍 Reverse geocode to get address
            fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
                .then(response => response.json())
                .then(data => {
                    const address = data.display_name || `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`;
                    document.getElementById('location').value = address;
                })
                .catch(error => {
                    console.error("Reverse geocoding failed:", error);
                    document.getElementById('location').value = `Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`;
                });
        });
    }
}


function closeMapModal() {
    document.getElementById('mapModal').style.display = 'none';
}



//claim button
function submitClaim() {
    alert("Claim submitted!");
    // Add actual submission logic here
}

