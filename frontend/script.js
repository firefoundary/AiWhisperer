// Configuration - Update these with your actual backend details
const CONFIG = {
    SUPABASE_URL: 'YOUR_SUPABASE_URL', // Replace with your actual Supabase URL
    SUPABASE_ANON_KEY: 'YOUR_SUPABASE_ANON_KEY', // Replace with your actual anon key
    API_BASE_URL: '/api', // Your backend API URL
    GEMINI_API_KEY: 'YOUR_GEMINI_API_KEY' // Replace with your Gemini API key
};

// Supabase client initialization
let supabase;
if (typeof window !== 'undefined' && window.supabase) {
    supabase = window.supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);
}

// Global variables
let currentPromptData = null;
let promptDatabase = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadPromptCount();
});

// Initialize application
async function initializeApp() {
    try {
        await loadPromptDatabase();
        console.log('AiWhisperer initialized successfully');
    } catch (error) {
        console.error('Failed to initialize AiWhisperer:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });

    // Input event listener for real-time validation
    const userIdeaInput = document.getElementById('user-idea');
    if (userIdeaInput) {
        userIdeaInput.addEventListener('input', function() {
            validateInput();
        });
    }
}

// Load prompt count from database
async function loadPromptCount() {
    try {
        let count;
        if (supabase) {
            // Try Supabase first
            const { data, error } = await supabase
                .from('prompt_examples_dataset')
                .select('id', { count: 'exact', head: true });
            
            if (error) throw error;
            count = data || 1450;
        } else {
            // Fallback to API endpoint
            const response = await fetch(`${CONFIG.API_BASE_URL}/prompts/count`);
            const data = await response.json();
            count = data.count || 1450;
        }
        
        // Update all count displays
        updatePromptCounts(count);
    } catch (error) {
        console.error('Error loading prompt count:', error);
        updatePromptCounts(1450); // Fallback count
    }
}

// Update prompt counts throughout the page
function updatePromptCounts(count) {
    const formattedCount = count >= 1000 ? `${Math.floor(count / 100) / 10}k+` : `${count}+`;
    
    const countElements = [
        'prompt-count',
        'dynamic-prompt-count',
        'step-prompt-count'
    ];
    
    countElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = formattedCount;
        }
    });
}

// Load prompt database
async function loadPromptDatabase() {
    try {
        if (supabase) {
            // Load from Supabase
            const { data, error } = await supabase
                .from('prompt_examples_dataset')
                .select('*')
                .limit(1000); // Limit for performance
            
            if (error) throw error;
            promptDatabase = data || [];
        } else {
            // Fallback to API endpoint
            const response = await fetch(`${CONFIG.API_BASE_URL}/prompts`);
            if (!response.ok) throw new Error('Failed to fetch prompts');
            promptDatabase = await response.json();
        }
        
        console.log(`Loaded ${promptDatabase.length} prompts`);
    } catch (error) {
        console.error('Error loading prompt database:', error);
        // Set empty array as fallback
        promptDatabase = [];
    }
}

// Main generate prompt function - updated to match your backend
async function generatePrompt() {
    const userIdea = document.getElementById('user-idea').value.trim();
    const category = document.getElementById('category-filter') ? document.getElementById('category-filter').value : '';
    
    if (!userIdea) {
        alert('Please describe your idea first!');
        return;
    }

    // Show loading state
    showLoadingState();

    try {
        // Call your enhanced backend API
        const response = await fetch(`${CONFIG.API_BASE_URL}/enhanced_prompt_generation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_input: userIdea
            })
        });

        if (!response.ok) {
            throw new Error('Failed to generate prompt');
        }

        const data = await response.json();
        
        if (data.success) {
            // Display the enhanced results
            displayResults(data.generated_template, data.similar_prompts_used, data.context_quality);
            currentPromptData = data.generated_template;
        } else {
            throw new Error(data.error || 'Unknown error occurred');
        }

    } catch (error) {
        console.error('Error generating prompt:', error);
        showErrorState(error.message);
    }
}

// Show loading state
function showLoadingState() {
    const resultsSection = document.getElementById('results-section');
    const loadingState = document.getElementById('loading-state');
    const resultsContent = document.getElementById('results-content');
    const errorState = document.getElementById('error-state');

    if (resultsSection) resultsSection.style.display = 'block';
    if (loadingState) loadingState.style.display = 'block';
    if (resultsContent) resultsContent.style.display = 'none';
    if (errorState) errorState.style.display = 'none';

    // Scroll to results
    if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Display results
function displayResults(generatedPrompt, similarPromptsUsed, contextQuality) {
    const loadingState = document.getElementById('loading-state');
    const resultsContent = document.getElementById('results-content');
    const generatedPromptElement = document.getElementById('generated-prompt');

    // Hide loading, show results
    if (loadingState) loadingState.style.display = 'none';
    if (resultsContent) resultsContent.style.display = 'block';

    // Display generated prompt
    if (generatedPromptElement) {
        generatedPromptElement.innerHTML = `
            <div class="prompt-card">
                <div class="prompt-header">
                    <span class="material-icons">auto_awesome</span>
                    Enhanced AI Prompt
                    ${similarPromptsUsed ? `<small>(Using ${similarPromptsUsed} expert examples)</small>` : ''}
                </div>
                <div class="prompt-text">${generatedPrompt}</div>
                ${contextQuality ? `<div class="context-quality">Context Quality: ${contextQuality}</div>` : ''}
            </div>
        `;
    }
}

// Show error state
function showErrorState(errorMessage) {
    const loadingState = document.getElementById('loading-state');
    const resultsContent = document.getElementById('results-content');
    const errorState = document.getElementById('error-state');

    if (loadingState) loadingState.style.display = 'none';
    if (resultsContent) resultsContent.style.display = 'none';
    if (errorState) {
        errorState.style.display = 'block';
        errorState.innerHTML = `
            <div class="error-message">
                <span class="material-icons">error</span>
                <h3>Error Generating Prompt</h3>
                <p>${errorMessage}</p>
                <button onclick="generatePrompt()" class="btn btn-primary">Try Again</button>
            </div>
        `;
    }
}

// Copy prompt to clipboard
async function copyPrompt() {
    if (!currentPromptData) return;

    try {
        await navigator.clipboard.writeText(currentPromptData);
        
        // Visual feedback
        const copyBtn = event.target.closest('button');
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<span class="material-icons">check</span> Copied!';
        copyBtn.classList.add('success');
        
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.classList.remove('success');
        }, 2000);
        
    } catch (error) {
        console.error('Copy failed:', error);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = currentPromptData;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        alert('Prompt copied to clipboard!');
    }
}

// Regenerate prompt
function regeneratePrompt() {
    generatePrompt();
}

// Input validation
function validateInput() {
    const userIdea = document.getElementById('user-idea');
    const generateBtn = document.getElementById('generate-btn');
    
    if (userIdea && generateBtn) {
        if (userIdea.value.trim().length > 0) {
            generateBtn.disabled = false;
            generateBtn.classList.remove('disabled');
        } else {
            generateBtn.disabled = true;
            generateBtn.classList.add('disabled');
        }
    }
}

// Expose functions globally for HTML onclick handlers
window.generatePrompt = generatePrompt;
window.copyPrompt = copyPrompt;
window.regeneratePrompt = regeneratePrompt;
