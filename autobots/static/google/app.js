$(document).ready(function () {

    let hierarchyData = [];  // Declare hierarchyData here
    let allCampaigns = [];
    let allAdGroups = [];
    let allAds = [];



    // Start OAuth Flow
    $("#startAuth").click(function() {
        window.location.href = "/start-auth/";
    });

    // Check URL for email query parameter and display it
    function displayEmailFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const email = urlParams.get('email');
        if (email) {
            $("#emailDisplay").text("Logged in as: " + email);
    
            // Refresh manager dropdown after successful auth
            refreshManagerDropdown();
    
            // Call the fetch functions in parallel
            $.when(fetchAllCampaigns(), fetchAllAdGroups(), fetchAllAds()).done(function() {
                hideSpinner();  // Hide the spinner only after all three requests have completed
            }).fail(function() {
                // Handle any errors from the AJAX calls here
                alert("An error occurred while fetching data.");
                hideSpinner();  // Ensure the spinner is hidden even if there's an error
            });
        }
    }

    displayEmailFromURL();
    

    // Refresh dropdowns based on changes
    $("#managerDropdown").change(function() {
        refreshIndividualAccountDropdown();
        $("#adManagerAccountId").val($(this).val());

    });

    $("#individualAccountDropdown").change(function() {
        refreshCampaignDropdown();
        $("#adAccountId").val($(this).val());
    });

    $("#campaignDropdown").change(function() {
        refreshAdGroupDropdown();
    });

    $("#adGroupDropdown").change(function() {
        refreshAdDropdown();
    });

    

    function refreshManagerDropdown() {
        const email = $("#emailDisplay").text().replace("Logged in as: ", "");
        showSpinner();
        $.get(`/v1/google/ad-accounts/get-ad-accounts/?email=${email}`, function(data) {
            const managerDropdown = $("#managerDropdown");
            // Clear existing options except the first one (Select option)
            managerDropdown.find("option:gt(0)").remove();
            hierarchyData = data;  // Store the data for later use
            data.forEach(function(managerAccount) {
                managerDropdown.append(new Option(managerAccount.descriptive_name, managerAccount.id));
            });
            hideSpinner();  
        });
    }

    function refreshIndividualAccountDropdown() {
        const selectedManagerId = $("#managerDropdown").val();
        const individualDropdown = $("#individualAccountDropdown");
        
        // Clear existing options except the first one (Select option)
        individualDropdown.find("option:gt(0)").remove();
        
        console.log('selectedManagerId:', selectedManagerId);
        console.log('All manager ids:', hierarchyData.map(manager => manager.id));
    
        const selectedManager = hierarchyData.find(manager => String(manager.id) === selectedManagerId); // Ensure comparison is between strings
        console.log('Selected Manager:', selectedManager);
    
        if (selectedManager && selectedManager.individual_accounts) {
            selectedManager.individual_accounts.forEach(function(individualAccount) {
                individualDropdown.append(new Option(individualAccount.descriptive_name, individualAccount.id));
            });
    }
}
function refreshCampaignDropdown() {
    const selectedManagerId = $("#managerDropdown").val();
    const selectedIndividualAccountId = $("#individualAccountDropdown").val();
    const campaignDropdown = $("#campaignDropdown");

    // Clear existing options except the first one (Select option)
    campaignDropdown.find("option:gt(0)").remove();

    // Filter campaigns based on the selected manager and individual account
    const filteredCampaigns = allCampaigns.filter(campaign => 
        campaign.manager_id.toString() === selectedManagerId && 
        campaign.individual_account_id.toString() === selectedIndividualAccountId
    );

    // Populate the dropdown
    filteredCampaigns.forEach(function(campaign) {
        campaignDropdown.append(new Option(campaign.name, campaign.id));
    });
}

function refreshAdGroupDropdown() {
    const selectedManagerId = $("#managerDropdown").val();
    const selectedIndividualAccountId = $("#individualAccountDropdown").val();
    const selectedCampaignId = $("#campaignDropdown").val().split('/').pop();

    const adGroupDropdown = $("#adGroupDropdown");
    // Clear existing options except the first one (Select option)
    adGroupDropdown.find("option:gt(0)").remove();

    // Filter ad groups based on the selected manager, individual account, and campaign
    const filteredAdGroups = allAdGroups.filter(adGroup => 
        adGroup.manager_id.toString() === selectedManagerId &&
        adGroup.individual_account_id.toString() === selectedIndividualAccountId &&
        adGroup.campaign.split('/').pop() === selectedCampaignId
    );

    // Populate the ad group dropdown with the filtered ad groups
    filteredAdGroups.forEach(function(adGroup) {
        adGroupDropdown.append(new Option(adGroup.name, adGroup.id));
    });
}

function refreshAdDropdown() {

    const selectedManagerId = $("#managerDropdown").val();
    const selectedIndividualAccountId = $("#individualAccountDropdown").val();
    const selectedAdGroupId = $("#adGroupDropdown").val();

    const adDropdown = $("#adDropdown");
    // Clear existing options except the first one (Select option)
    adDropdown.find("option:gt(0)").remove();

    // Filter ads based on the selected manager, individual account, and ad group
    const filteredAds = allAds.filter(ad => 
        ad.manager_id.toString() === selectedManagerId &&
        ad.account_id.toString() === selectedIndividualAccountId &&
        ad.ad_group_id.toString() === selectedAdGroupId
    );

    // Populate the ad dropdown with the filtered ads
    filteredAds.forEach(function(ad) {
        const adDisplayName = `${ad.headlines[0]} (${ad.ad_id})`;  // Example display format
        adDropdown.append(new Option(adDisplayName, ad.ad_id));
    });

}


// Fetch and store all campaigns on page load
function fetchAllCampaigns() {
    const email = $("#emailDisplay").text().replace("Logged in as: ", "");
    showSpinner();
    return $.get(`/v1/google/ad-campaigns/list_campaigns/?email=${email}`, function(data) {
        allCampaigns = data;
    });
}

function fetchAllAdGroups() {
    const email = $("#emailDisplay").text().replace("Logged in as: ", "");
    showSpinner();
    return $.get(`/v1/google/ad-groups/ad-groups/?email=${email}`, function(data) {
        allAdGroups = data;
    });
}

function fetchAllAds() {
    const email = $("#emailDisplay").text().replace("Logged in as: ", "");
    showSpinner();
    return $.get(`/v1/google/ads/list-ads/?email=${email}`, function(data) {
        allAds = data;
    });
}


// Create Campaign Button
$("#createCampaignBtn").click(function() {
    $("#createCampaignControls").toggle();
});

// Create Ad Group Button
$("#createAdGroupBtn").click(function() {
    $("#adGroupManagerAccountId").val($("#managerDropdown").val());
    $("#adGroupAccountId").val($("#individualAccountDropdown").val());
    $("#adGroupCampaignId").val($("#campaignDropdown").val());
    $("#createAdGroupControls").toggle();
});

// Create Ad Button
$("#createAdBtn").click(function() {
    $("#createAdControls").toggle();
});

$("#closeCampaignControlsBtn").click(function() {
    $("#createCampaignControls").hide();
});

$("#submitCampaignBtn").click(function() {
    const requestURL = `/v1/google/ad-campaigns/create/?email=${$("#emailDisplay").text().replace("Logged in as: ", "")}`;
    const requestBody = {
        name: $("#campaignName").val(),
        status: $("#campaignStatus").val(),
        advertising_channel_type: $("#advertisingChannelType").val(),
        budget: parseFloat($("#budget").val()),
        budget_delivery_method: $("#budgetDeliveryMethod").val(),
        bidding_strategy_details: {
            enhanced_cpc_opt_in: $("#enhancedCpcOptIn").prop("checked")
        },
        ad_manager_account_id: parseInt($("#managerDropdown").val()),
        ad_account_id: parseInt($("#individualAccountDropdown").val())
    };

    console.log(requestBody);
    showSpinner();
    $.ajax({
        type: "POST",
        url: requestURL,
        data: JSON.stringify(requestBody),
        contentType: "application/json",
        dataType: "json",
        success: function (response) {
            hideSpinner();  // Hide spinner
            alert('Campaign created successfully!');
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log('Error: ' + jqXHR.responseText || errorThrown);
            hideSpinner();  // Hide spinner
        }
    });
});
$("#submitAdGroupBtn").click(function() {
    const requestURL = `/v1/google/ad-groups/ad-group/?email=${$("#emailDisplay").text().replace("Logged in as: ", "")}`;
    const requestBody = {
        name: $("#adGroupName").val(),
        campaign_id: $("#adGroupCampaignId").val(),
        status: $("#adGroupStatus").val(),
        bid_amount: parseFloat($("#adGroupBidAmount").val()),
        ad_manager_account_id: parseInt($("#adGroupManagerAccountId").val()),
        ad_account_id: parseInt($("#adGroupAccountId").val())
    };
    showSpinner();
    $.ajax({
        type: "POST",
        url: requestURL,
        data: JSON.stringify(requestBody),
        contentType: "application/json",
        dataType: "json",
        success: function (response) {
            alert('Ad Group created successfully!');
            hideSpinner();  
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log('Error: ' + jqXHR.responseText || errorThrown);
            hideSpinner();
        }
    });
});
$("#closeAdGroupControlsBtn").click(function() {
    $("#createAdGroupControls").hide();
});
// Create Responsive Ad Button
$("#createAdBtn").click(function() {
    $("#rsaManagerAccountId").val($("#managerDropdown").val());
    $("#rsaAccountId").val($("#individualAccountDropdown").val());
    $("#rsaAdGroupId").val($("#adGroupDropdown").val());
    $("#createResponsiveAdControls").toggle();
});

$("#closeResponsiveAdControlsBtn").click(function() {
    $("#createResponsiveAdControls").hide();
});

$("#submitResponsiveAdBtn").click(function() {
    const requestURL = `/v1/google/ads/create-responsive-ad/?email=${$("#emailDisplay").text().replace("Logged in as: ", "")}`;
    const requestBody = {
        ad_manager_account_id: parseInt($("#rsaManagerAccountId").val()),
        ad_account_id: parseInt($("#rsaAccountId").val()),
        ad_group_id: parseInt($("#rsaAdGroupId").val()),
        headlines: $("#rsaHeadlines").val().split(","),
        descriptions: $("#rsaDescriptions").val().split(","),
        final_url: $("#rsaFinalUrl").val(),
        path1: $("#rsaPath1").val(),
        path2: $("#rsaPath2").val(),
        status: $("#rsaStatus").val()
    };
    showSpinner();
    $.ajax({
        type: "POST",
        url: requestURL,
        data: JSON.stringify(requestBody),
        contentType: "application/json",
        dataType: "json",
        success: function (response) {
            hideSpinner();
            alert('Responsive ad created successfully!');
        },
        error: function (jqXHR, textStatus, errorThrown) {
            hideSpinner();
            console.log('Error: ' + jqXHR.responseText || errorThrown);
        }
    });
});

function showSpinner() {
    $("#loadingSpinner").show();
}

function hideSpinner() {
    $("#loadingSpinner").hide();
}
});