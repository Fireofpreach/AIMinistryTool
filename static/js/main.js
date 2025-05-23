// Main JavaScript file for the eAI Ministry Tool

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle flash messages timeout
    setTimeout(function() {
        const flashMessages = document.querySelectorAll('.alert-dismissible');
        flashMessages.forEach(function(message) {
            const alert = new bootstrap.Alert(message);
            alert.close();
        });
    }, 5000);  // Auto-dismiss after 5 seconds

    // Search functionality
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = document.getElementById('search-input');
            if (searchInput.value.trim() === '') {
                return false;
            }
            window.location.href = '/resources/library?search=' + encodeURIComponent(searchInput.value);
        });
    }

    // Doctrine comparison module
    setupDoctrineComparisonModule();

    // Sermon builder module
    setupSermonBuilderModule();

    // Counseling module
    setupCounselingModule();

    // Resources module
    setupResourcesModule();
});

// Doctrine Comparison Module Setup
function setupDoctrineComparisonModule() {
    const denomSelector = document.getElementById('denomination-selector');
    if (denomSelector) {
        denomSelector.addEventListener('change', function() {
            const selected = Array.from(this.selectedOptions).map(opt => opt.value);
            if (selected.length > 1) {
                document.getElementById('compare-btn').removeAttribute('disabled');
            } else {
                document.getElementById('compare-btn').setAttribute('disabled', 'disabled');
            }
        });
    }

    const saveComparisonBtn = document.getElementById('save-comparison-btn');
    if (saveComparisonBtn) {
        saveComparisonBtn.addEventListener('click', function() {
            const saveModal = new bootstrap.Modal(document.getElementById('save-comparison-modal'));
            saveModal.show();
        });
    }

    const saveComparisonForm = document.getElementById('save-comparison-form');
    if (saveComparisonForm) {
        saveComparisonForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const title = document.getElementById('comparison-title').value;
            const description = document.getElementById('comparison-description').value;
            
            // Get denominations and topics from the table
            const denoms = [];
            document.querySelectorAll('th.denom-header').forEach(th => {
                denoms.push(th.dataset.denomId);
            });
            
            const topics = [];
            document.querySelectorAll('tr.topic-row').forEach(tr => {
                topics.push(tr.dataset.topic);
            });
            
            // Serialize the comparison results
            const resultsTable = document.querySelector('.comparison-results');
            const resultsData = {};
            
            document.querySelectorAll('tr.topic-row').forEach(tr => {
                const topic = tr.dataset.topic;
                resultsData[topic] = {};
                
                tr.querySelectorAll('td.denom-cell').forEach((td, index) => {
                    const denomName = document.querySelectorAll('th.denom-header')[index].textContent;
                    resultsData[topic][denomName] = {
                        summary: td.querySelector('.belief-summary').textContent,
                        scripture_references: td.querySelector('.scripture-refs').textContent
                    };
                });
            });
            
            // Create form data
            const formData = new FormData();
            formData.append('title', title);
            formData.append('description', description);
            denoms.forEach(denom => formData.append('denominations', denom));
            topics.forEach(topic => formData.append('topics', topic));
            formData.append('results', JSON.stringify(resultsData));
            
            // Submit via fetch API
            fetch('/doctrine/save_comparison', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('save-comparison-modal'));
                    modal.hide();
                    
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success alert-dismissible fade show';
                    alertDiv.innerHTML = `
                        ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    document.querySelector('.main-content').prepend(alertDiv);
                } else {
                    // Show error message
                    document.getElementById('save-error-message').textContent = data.message;
                    document.getElementById('save-error').classList.remove('d-none');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('save-error-message').textContent = 'An error occurred while saving.';
                document.getElementById('save-error').classList.remove('d-none');
            });
        });
    }
}

// Sermon Builder Module Setup
function setupSermonBuilderModule() {
    const generateOutlineBtn = document.getElementById('generate-outline-btn');
    if (generateOutlineBtn) {
        generateOutlineBtn.addEventListener('click', function() {
            const scripture = document.getElementById('scripture_passage').value;
            const theme = document.getElementById('theme').value;
            
            if (!scripture) {
                alert('Please enter a Scripture passage');
                return;
            }
            
            // Show loading indicator
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
            this.disabled = true;
            
            // Call the API
            fetch('/sermon/api/generate_outline', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ scripture, theme })
            })
            .then(response => response.json())
            .then(data => {
                // Reset button
                generateOutlineBtn.innerHTML = 'Generate Outline';
                generateOutlineBtn.disabled = false;
                
                if (data.success) {
                    // Build the outline HTML
                    const outlineContainer = document.getElementById('outline-container');
                    outlineContainer.innerHTML = '';
                    
                    let outlineHtml = '<div class="card"><div class="card-body"><h5>Sermon Outline</h5><ol>';
                    data.outline.forEach(section => {
                        outlineHtml += `<li><strong>${section.title}</strong><ul>`;
                        section.points.forEach(point => {
                            outlineHtml += `<li>${point}</li>`;
                        });
                        outlineHtml += '</ul></li>';
                    });
                    outlineHtml += '</ol></div></div>';
                    
                    outlineContainer.innerHTML = outlineHtml;
                    
                    // Add the outline to the hidden form field
                    document.getElementById('outline').value = JSON.stringify(data.outline);
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                generateOutlineBtn.innerHTML = 'Generate Outline';
                generateOutlineBtn.disabled = false;
                alert('An error occurred while generating the outline.');
            });
        });
    }

    const suggestIllustrationsBtn = document.getElementById('suggest-illustrations-btn');
    if (suggestIllustrationsBtn) {
        suggestIllustrationsBtn.addEventListener('click', function() {
            const theme = document.getElementById('theme').value;
            
            if (!theme) {
                alert('Please enter a sermon theme');
                return;
            }
            
            // Show loading indicator
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Suggesting...';
            this.disabled = true;
            
            // Call the API
            fetch('/sermon/api/suggest_illustrations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ theme })
            })
            .then(response => response.json())
            .then(data => {
                // Reset button
                suggestIllustrationsBtn.innerHTML = 'Suggest Illustrations';
                suggestIllustrationsBtn.disabled = false;
                
                if (data.success) {
                    // Build the illustrations HTML
                    const illustrationsContainer = document.getElementById('illustrations-container');
                    illustrationsContainer.innerHTML = '';
                    
                    let illustrationsHtml = '<div class="card"><div class="card-body"><h5>Suggested Illustrations</h5><ul>';
                    data.illustrations.forEach(illustration => {
                        illustrationsHtml += `<li><strong>${illustration.title}:</strong> ${illustration.description}</li>`;
                    });
                    illustrationsHtml += '</ul></div></div>';
                    
                    illustrationsContainer.innerHTML = illustrationsHtml;
                    
                    // Add the illustrations to the hidden form field
                    document.getElementById('illustrations').value = JSON.stringify(data.illustrations);
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                suggestIllustrationsBtn.innerHTML = 'Suggest Illustrations';
                suggestIllustrationsBtn.disabled = false;
                alert('An error occurred while suggesting illustrations.');
            });
        });
    }
}

// Counseling Module Setup
function setupCounselingModule() {
    const topicSelect = document.getElementById('topic');
    if (topicSelect) {
        topicSelect.addEventListener('change', function() {
            if (this.value) {
                suggestScriptures(this.value);
            }
        });
    }

    const getAdviceBtn = document.getElementById('get-advice-btn');
    if (getAdviceBtn) {
        getAdviceBtn.addEventListener('click', function() {
            const topic = document.getElementById('topic').value;
            const situation = document.getElementById('description').value;
            
            if (!topic) {
                alert('Please select a counseling topic');
                return;
            }
            
            // Show loading indicator
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Getting Advice...';
            this.disabled = true;
            
            // Call the API
            fetch('/counseling/api/counseling_advice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic, situation })
            })
            .then(response => response.json())
            .then(data => {
                // Reset button
                getAdviceBtn.innerHTML = 'Get Counseling Advice';
                getAdviceBtn.disabled = false;
                
                if (data.success) {
                    // Display the advice
                    const adviceContainer = document.getElementById('advice-container');
                    adviceContainer.innerHTML = `
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Counseling Advice</h5>
                                <p>${data.advice}</p>
                            </div>
                        </div>
                    `;
                    adviceContainer.classList.remove('d-none');
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                getAdviceBtn.innerHTML = 'Get Counseling Advice';
                getAdviceBtn.disabled = false;
                alert('An error occurred while getting counseling advice.');
            });
        });
    }
}

function suggestScriptures(topic) {
    const scriptureContainer = document.getElementById('scripture-suggestions');
    if (!scriptureContainer) return;
    
    // Show loading indicator
    scriptureContainer.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div> Loading scripture suggestions...</div>';
    
    // Call the API
    fetch('/counseling/api/suggest_scriptures', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let suggestionsHtml = '<div class="card bg-light mt-3"><div class="card-body"><h6>Suggested Scripture References:</h6><ul>';
            data.scriptures.forEach(scripture => {
                suggestionsHtml += `<li>${scripture} <button type="button" class="btn btn-sm btn-outline-primary add-scripture" data-scripture="${scripture}">Add</button></li>`;
            });
            suggestionsHtml += '</ul></div></div>';
            
            scriptureContainer.innerHTML = suggestionsHtml;
            
            // Add event listeners to the "Add" buttons
            document.querySelectorAll('.add-scripture').forEach(btn => {
                btn.addEventListener('click', function() {
                    const scripture = this.dataset.scripture;
                    const scriptureInput = document.getElementById('scripture_references');
                    let currentScriptures = scriptureInput.value;
                    
                    if (currentScriptures) {
                        if (!currentScriptures.includes(scripture)) {
                            scriptureInput.value = currentScriptures + ', ' + scripture;
                        }
                    } else {
                        scriptureInput.value = scripture;
                    }
                });
            });
        } else {
            scriptureContainer.innerHTML = `<div class="alert alert-warning">${data.message}</div>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        scriptureContainer.innerHTML = '<div class="alert alert-danger">Failed to load scripture suggestions</div>';
    });
}

// Resources Module Setup
function setupResourcesModule() {
    const resourceTypeFilter = document.getElementById('resource-type-filter');
    const topicFilter = document.getElementById('topic-filter');
    
    if (resourceTypeFilter) {
        resourceTypeFilter.addEventListener('change', function() {
            applyResourceFilters();
        });
    }
    
    if (topicFilter) {
        topicFilter.addEventListener('change', function() {
            applyResourceFilters();
        });
    }

    // Search functionality
    const searchInput = document.getElementById('resource-search');
    if (searchInput) {
        const debounceTimeout = 300;
        let timeoutId;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                const searchTerm = this.value.trim();
                
                if (searchTerm.length >= 2) {
                    fetch(`/resources/api/search?q=${encodeURIComponent(searchTerm)}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                displaySearchResults(data.results);
                            }
                        })
                        .catch(error => console.error('Error:', error));
                } else {
                    const resultsContainer = document.getElementById('search-results');
                    if (resultsContainer) {
                        resultsContainer.innerHTML = '';
                        resultsContainer.classList.add('d-none');
                    }
                }
            }, debounceTimeout);
        });
    }
}

function applyResourceFilters() {
    const resourceType = document.getElementById('resource-type-filter').value;
    const topic = document.getElementById('topic-filter').value;
    const searchTerm = document.getElementById('resource-search').value;
    
    let url = '/resources/library?';
    if (resourceType) {
        url += `type=${encodeURIComponent(resourceType)}&`;
    }
    if (topic) {
        url += `topic=${encodeURIComponent(topic)}&`;
    }
    if (searchTerm) {
        url += `search=${encodeURIComponent(searchTerm)}&`;
    }
    
    // Remove trailing & if present
    if (url.endsWith('&')) {
        url = url.slice(0, -1);
    }
    
    window.location.href = url;
}

function displaySearchResults(results) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="p-3">No resources found</div>';
    } else {
        let html = '<div class="list-group">';
        results.forEach(resource => {
            html += `
                <a href="${resource.url}" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${resource.title}</h6>
                        <small>${resource.resource_type}</small>
                    </div>
                    <p class="mb-1">${resource.author || 'Unknown author'}</p>
                    <small>${resource.topic || 'General'}</small>
                </a>
            `;
        });
        html += '</div>';
        resultsContainer.innerHTML = html;
    }
    
    resultsContainer.classList.remove('d-none');
}
