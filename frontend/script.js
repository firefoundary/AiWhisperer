// Configuration - Update these with your actual backend details
const CONFIG = {
    SUPABASE_URL: 'YOUR_SUPABASE_URL', // Replace with your actual Supabase URL
    SUPABASE_ANON_KEY: 'YOUR_SUPABASE_ANON_KEY', // Replace with your actual anon key
    API_BASE_URL: '/api', // Replace with your backend API URL
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

// Generate prompt function
async function generatePrompt() {
    const userIdea = document.getElementById('user-idea').value.trim();
    const category = document.getElementById('category-filter').value;
    
    if (!userIdea) {
        alert('Please describe your idea first!');
        return;
    }
    
    // Show loading state
    showLoadingState();
    
    try {
        // Generate prompt using AI
        const generatedPrompt = await callGeminiAPI(userIdea, category);
        
        // Find similar prompts from database
        const similarPrompts = await findSimilarPrompts(userIdea, category);
        
        // Display results
        displayResults(generatedPrompt, similarPrompts);
        
    } catch (error) {
        console.error('Error generating prompt:', error);
        showErrorState();
    }
}

// Call Gemini API for prompt generation
async function callGeminiAPI(userIdea, category = '') {
    try {
        const systemPrompt = `You are an expert prompt engineer. Based on the user's idea and the database of expert prompts, create an optimized AI prompt that will help them achieve their goal.

User's idea: "${userIdea}"
Category: "${category || 'General'}"

Create a well-structured, clear, and effective prompt that incorporates best practices for AI interaction. The prompt should be specific, actionable, and include relevant context.

Return only the optimized prompt text, nothing else.`;

        // Use your backend API to call Gemini
        const response = await fetch(`${CONFIG.API_BASE_URL}/generate-prompt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_idea: userIdea,
                category: category,
                system_prompt: systemPrompt
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate prompt');
        }
        
        const data = await response.json();
        return data.generated_prompt || 'Error generating prompt';
        
    } catch (error) {
        console.error('Gemini API error:', error);
        
        // Fallback: create a basic prompt template
        return createFallbackPrompt(userIdea, category);
    }
}

// Create fallback prompt if API fails
function createFallbackPrompt(userIdea, category) {
    const templates = {
        marketing: `Create compelling marketing content for: ${userIdea}. Focus on engaging your target audience, highlighting key benefits, and including a clear call-to-action.`,
        content: `Generate high-quality content about: ${userIdea}. Ensure it's informative, well-structured, and engaging for your intended audience.`,
        coding: `Help me with: ${userIdea}. Provide clean, well-documented code with explanations and best practices.`,
        business: `Assist with business planning for: ${userIdea}. Include strategic considerations, potential challenges, and actionable recommendations.`,
        creative: `Create creative content for: ${userIdea}. Be imaginative, original, and capture the essence of what I'm looking for.`,
        analysis: `Analyze and provide insights on: ${userIdea}. Include data-driven observations, patterns, and actionable conclusions.`
    };
    
    return templates[category] || `Help me with: ${userIdea}. Provide detailed, actionable guidance that addresses my specific needs and goals.`;
}

// Find similar prompts from database
async function findSimilarPrompts(userIdea, category, limit = 3) {
    try {
        if (supabase && promptDatabase.length > 0) {
            // Simple text matching - you can enhance this with proper NLP
            let filteredPrompts = promptDatabase;
            
            // Filter by category if specified
            if (category) {
                filteredPrompts = promptDatabase.filter(prompt => 
                    prompt.category && prompt.category.toLowerCase() === category.toLowerCase()
                );
            }
            
            // Simple keyword matching
            const keywords = userIdea.toLowerCase().split(' ').filter(word => word.length > 3);
            const scoredPrompts = filteredPrompts.map(prompt => {
                const promptText = (prompt.prompt_text || prompt.content || '').toLowerCase();
                const score = keywords.reduce((acc, keyword) => {
                    return acc + (promptText.includes(keyword) ? 1 : 0);
                }, 0);
                return { ...prompt, similarity_score: score };
            });
            
            // Sort by similarity and return top results
            return scoredPrompts
                .filter(p => p.similarity_score > 0)
                .sort((a, b) => b.similarity_score - a.similarity_score)
                .slice(0, limit);
        }
        
        return [];
    } catch (error) {
        console.error('Error finding similar prompts:', error);
        return [];
    }
}

// Show loading state
function showLoadingState() {
    const resultsSection = document.getElementById('results-section');
    const loadingState = document.getElementById('loading-state');
    const resultsContent = document.getElementById('results-content');
    const errorState = document.getElementById('error-state');
    
    resultsSection.style.display = 'block';
    loadingState.style.display = 'block';
    resultsContent.style.display = 'none';
    errorState.style.display = 'none';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Display results
function displayResults(generatedPrompt, similarPrompts) {
    const loadingState = document.getElementById('loading-state');
    const resultsContent = document.getElementById('results-content');
    const generatedPromptElement = document.getElementById('generated-prompt');
    const promptSuggestions = document.getElementById('prompt-suggestions');
    
    // Hide loading, show results
    loadingState.style.display = 'none';
    resultsContent.style.display = 'block';
    
    // Display generated prompt
    generatedPromptElement.innerHTML = `
        <div class="prompt-card">
            <div class="prompt-header">
                <span class="material-icons">auto_awesome</span>
                <span>AI-Generated Prompt</span>
            </div>
            <div class="prompt-text">${generatedPrompt}</div>
        </div>
    `;
    
    // Store current prompt for copying
    currentPromptData = generatedPrompt;
    
    // Display similar prompts
    if (similarPrompts && similarPrompts.length > 0) {
        promptSuggestions.innerHTML = similarPrompts.map(prompt => `
            <div class="suggestion-card" onclick="usePromptTemplate('${prompt.id}')">
                <div class="suggestion-header">
                    <span class="suggestion-title">${prompt.title || 'Expert Template'}</span>
                    <span class="suggestion-category">${prompt.category || 'General'}</span>
                </div>
                <div class="suggestion-preview">
                    ${(prompt.prompt_text || prompt.content || '').substring(0, 100)}...
                </div>
            </div>
        `).join('');
    } else {
        promptSuggestions.innerHTML = '<p class="no-suggestions">No similar templates found, but your generated prompt is ready to use!</p>';
    }
}

// Show error state
function showErrorState() {
    const loadingState = document.getElementById('loading-state');
    const resultsContent = document.getElementById('results-content');
    const errorState = document.getElementById('error-state');
    
    loadingState.style.display = 'none';
    resultsContent.style.display = 'none';
    errorState.style.display = 'block';
}

// Copy prompt to clipboard
async function copyPrompt() {
    if (!currentPromptData) return;
    
    try {
        await navigator.clipboard.writeText(currentPromptData);
        
        // Visual feedback
        const copyBtn = event.target.closest('button');
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<span class="material-icons">check</span>Copied!';
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
    }
}

// Regenerate prompt
function regeneratePrompt() {
    generatePrompt();
}

// Use prompt template
async function usePromptTemplate(promptId) {
    try {
        let promptData;
        
        if (supabase) {
            const { data, error } = await supabase
                .from('prompt_examples_dataset')
                .select('*')
                .eq('id', promptId)
                .single();
            
            if (error) throw error;
            promptData = data;
        } else {
            const response = await fetch(`${CONFIG.API_BASE_URL}/prompts/${promptId}`);
            promptData = await response.json();
        }
        
        if (promptData) {
            currentPromptData = promptData.prompt_text || promptData.content;
            
            // Update the generated prompt display
            const generatedPromptElement = document.getElementById('generated-prompt');
            generatedPromptElement.innerHTML = `
                <div class="prompt-card">
                    <div class="prompt-header">
                        <span class="material-icons">school</span>
                        <span>Expert Template: ${promptData.title || 'Professional Prompt'}</span>
                    </div>
                    <div class="prompt-text">${currentPromptData}</div>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading prompt template:', error);
    }
}

// Validate input
function validateInput() {
    const userIdea = document.getElementById('user-idea').value.trim();
    const generateBtn = document.getElementById('generate-btn');
    
    if (userIdea.length > 0) {
        generateBtn.disabled = false;
        generateBtn.classList.remove('disabled');
    } else {
        generateBtn.disabled = true;
        generateBtn.classList.add('disabled');
    }
}

// Utility functions
function scrollToPromptGenerator() {
    const section = document.getElementById('prompt-generator');
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

function showDemo() {
    const demoContent = document.getElementById('demo-content');
    const processing = document.getElementById('processing-demo');
    const output = document.getElementById('output-demo');
    
    // Reset demo
    processing.style.display = 'none';
    output.style.display = 'none';
    
    // Show processing
    setTimeout(() => {
        processing.style.display = 'flex';
    }, 500);
    
    // Show output
    setTimeout(() => {
        processing.style.display = 'none';
        output.style.display = 'flex';
    }, 2500);
    
    // Reset after demo
    setTimeout(() => {
        output.style.display = 'none';
    }, 5000);
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Application error:', e.error);
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
});
