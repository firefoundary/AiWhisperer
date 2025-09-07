import pandas as pd
import os
from pathlib import Path
from typing import Dict

# Import Config from same package
from api.config import Config

class DataProcessor:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.raw_dir = self.config.RAW_DATA_DIR
        self.processed_dir = self.config.PROCESSED_DATA_DIR

    def load_kaggle_datasets(self) -> Dict[str, pd.DataFrame]:
        main_files = {
            'prompt_examples_main': 'prompt_examples_dataset.csv',
            'prompt_examples_alt': 'Prompt_Examples.csv',
            'response_examples': 'Response_Examples.csv'
        }
        
        datasets = {}
        for key, filename in main_files.items():
            file_path = self.raw_dir / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    datasets[key] = df
                    print(f"✓ Loaded {filename}: {len(df)} rows")
                except Exception as e:
                    print(f"✗ Error loading {filename}: {e}")
            else:
                print(f"⚠ File not found: {filename}")
        
        return datasets

    def process_all_data(self) -> pd.DataFrame:
        datasets = self.load_kaggle_datasets()
        # Add processing logic here
        return pd.DataFrame()


    def combine_datasets(self, datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Combine multiple Kaggle datasets into unified format"""
        combined_rows = []
        
        # Process prompt_examples_dataset.csv (PRIMARY FILE)
        if 'prompt_examples_main' in datasets:
            df = datasets['prompt_examples_main']
            print(f"Processing main dataset with columns: {list(df.columns)}")
            
            # Adapt to different possible column names
            user_col = None
            optimized_col = None
            
            # Common column name variations
            possible_user_cols = ['prompt', 'original_prompt', 'input_prompt', 'user_input']
            possible_opt_cols = ['optimized_prompt', 'improved_prompt', 'enhanced_prompt', 'better_prompt']
            
            for col in possible_user_cols:
                if col in df.columns:
                    user_col = col
                    break
                    
            for col in possible_opt_cols:
                if col in df.columns:
                    optimized_col = col
                    break
            
            if user_col:
                for _, row in df.iterrows():
                    user_input = str(row.get(user_col, '')).strip()
                    optimized = str(row.get(optimized_col, user_input)).strip() if optimized_col else user_input
                    
                    if len(user_input) > 10:  # Filter short inputs
                        combined_rows.append({
                            'user_input': user_input,
                            'optimized_prompt': optimized,
                            'category': row.get('category', 'general'),
                            'source': 'kaggle_main'
                        })
        
        # Process Prompt_Examples.csv (SECONDARY FILE)
        if 'prompt_examples_alt' in datasets:
            df = datasets['prompt_examples_alt']
            print(f"Processing alt dataset with columns: {list(df.columns)}")
            
            # Similar column detection
            user_col = None
            for col in ['prompt', 'input', 'user_prompt', 'original']:
                if col in df.columns:
                    user_col = col
                    break
            
            if user_col:
                for _, row in df.iterrows():
                    user_input = str(row.get(user_col, '')).strip()
                    
                    if len(user_input) > 10:
                        combined_rows.append({
                            'user_input': user_input,
                            'optimized_prompt': user_input,  # Use same as input if no optimized version
                            'category': 'general',
                            'source': 'kaggle_alt'
                        })
        
        # Create DataFrame
        combined_df = pd.DataFrame(combined_rows)
        
        # Clean data
        if not combined_df.empty:
            combined_df = combined_df.drop_duplicates(subset=['user_input'])
            combined_df = combined_df[combined_df['user_input'].str.len() > 10]
            
        print(f"Combined dataset: {len(combined_df)} rows")
        return combined_df

    def add_website_specific_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add custom website creation examples"""
        website_examples = [
            {
                'user_input': 'Create a website for my bakery',
                'optimized_prompt': 'Create a comprehensive bakery website with: homepage featuring daily specials, complete menu with prices and allergen info, about us page with baker\'s story, online ordering system, location and hours, customer testimonials, and photo gallery of baked goods.',
                'category': 'website_business',
                'source': 'custom'
            },
            {
                'user_input': 'I need a portfolio website for my photography',
                'optimized_prompt': 'Design a professional photography portfolio with: striking homepage showcasing best work, organized galleries by category (weddings, portraits, landscapes), detailed about page with photographer\'s story and approach, services and pricing page, client testimonials, and easy contact form with booking system.',
                'category': 'website_portfolio',
                'source': 'custom'
            },
            {
                'user_input': 'Build a website for my restaurant',
                'optimized_prompt': 'Create a restaurant website featuring: appetizing homepage with hero images, complete menu with descriptions and prices, online reservation system, about page with chef\'s background and restaurant story, location with map and parking info, hours of operation, customer reviews section, and special events page.',
                'category': 'website_business',
                'source': 'custom'
            },
            {
                'user_input': 'Make a website for my consulting business',
                'optimized_prompt': 'Develop a professional consulting website with: authoritative homepage establishing expertise, detailed services page with case studies, about page highlighting experience and credentials, client testimonials and success stories, resources/blog section, clear contact information, and consultation booking system.',
                'category': 'website_business',
                'source': 'custom'
            },
            {
                'user_input': 'Create a blog website for travel stories',
                'optimized_prompt': 'Build a travel blog website with: engaging homepage with featured posts, organized post categories by destination, interactive map of visited places, about page with traveler\'s story, photo galleries, travel tips section, subscription form for updates, and social media integration.',
                'category': 'website_blog',
                'source': 'custom'
            }
        ]
        
        website_df = pd.DataFrame(website_examples)
        return pd.concat([df, website_df], ignore_index=True)

    def save_processed_data(self, df: pd.DataFrame) -> Path:
        """Save the combined and processed dataset"""
        output_path = self.processed_dir / "combined_prompts.csv"
        df.to_csv(output_path, index=False)
        print(f"✓ Saved processed dataset: {output_path} ({len(df)} rows)")
        return output_path

    def process_all_data(self) -> pd.DataFrame:
        """Complete data processing pipeline"""
        print("Starting data processing pipeline...")
        
        # Load datasets
        datasets = self.load_kaggle_datasets()
        
        # Combine datasets
        combined_df = self.combine_datasets(datasets)
        
        # Add website-specific data
        enhanced_df = self.add_website_specific_data(combined_df)
        
        # Save processed data
        self.save_processed_data(enhanced_df)
        
        print("Data processing completed!")
        return enhanced_df
