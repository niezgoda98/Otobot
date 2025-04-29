import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'mojehaslo'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_data():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = """
            SELECT 
                price,
                area,
                voie,
                city,
                created_at,
                price/area as price_per_m2
            FROM properties
            WHERE price > 0 AND area > 0
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

def analyze_by_area_ranges(df):
    # Define area ranges
    bins = [0, 60, 80, 100, float('inf')]
    labels = ['0-60 m²', '60-80 m²', '80-100 m²', '100+ m²']
    
    # Create area range column
    df['area_range'] = pd.cut(df['area'], bins=bins, labels=labels)
    
    # Calculate statistics for each range
    area_stats = df.groupby('area_range').agg({
        'price': ['mean', 'median', 'min', 'max'],
        'price_per_m2': ['mean', 'median']
    }).round(2)
    
    return area_stats

def analyze_by_location(df):
    # Group by city and calculate statistics
    location_stats = df.groupby('city').agg({
        'price': ['mean', 'median', 'count'],
        'price_per_m2': ['mean', 'median']
    }).round(2)
    
    return location_stats

def create_visualizations(df):
    # Set style
    plt.style.use('seaborn-v0_8')
    
    # Create area range column for visualization
    bins = [0, 60, 80, 100, float('inf')]
    labels = ['0-60 m²', '60-80 m²', '80-100 m²', '100+ m²']
    df['area_range'] = pd.cut(df['area'], bins=bins, labels=labels)
    
    # Convert created_at to datetime if it's not already
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 20))
    gs = fig.add_gridspec(4, 3)
    
    # Helper function to format y-axis labels
    def format_y_axis(ax, is_price=True):
        if is_price:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}k PLN'))
        else:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f} m²'))
    
    # 1. Price distribution by area range
    ax1 = fig.add_subplot(gs[0, 0])
    sns.boxplot(x='area_range', y='price', data=df, ax=ax1)
    ax1.set_title('Price Distribution by Area Range')
    ax1.set_ylabel('Price')
    ax1.set_xlabel('Area Range')
    format_y_axis(ax1)
    
    # 2. Average price per m² by area range
    ax2 = fig.add_subplot(gs[0, 1])
    avg_price_m2 = df.groupby('area_range')['price_per_m2'].mean()
    avg_price_m2.plot(kind='bar', ax=ax2)
    ax2.set_title('Average Price per m² by Area Range')
    ax2.set_ylabel('Price per m²')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f} PLN/m²'))
    
    # 3. Top 10 cities by average price
    ax3 = fig.add_subplot(gs[0, 2])
    top_cities = df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)
    top_cities.plot(kind='bar', ax=ax3)
    ax3.set_title('Top 10 Cities by Average Price')
    ax3.set_ylabel('Average Price')
    format_y_axis(ax3)
    
    # 4. Price per m² distribution
    ax4 = fig.add_subplot(gs[1, 0])
    sns.histplot(df['price_per_m2'], bins=50, ax=ax4)
    ax4.set_title('Price per m² Distribution')
    ax4.set_xlabel('Price per m²')
    ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f} PLN/m²'))
    
    # 5. Price vs Area Scatter Plot
    ax5 = fig.add_subplot(gs[1, 1])
    sns.scatterplot(x='area', y='price', data=df, alpha=0.5, ax=ax5)
    ax5.set_title('Price vs Area')
    ax5.set_xlabel('Area')
    ax5.set_ylabel('Price')
    format_y_axis(ax5)
    ax5.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f} m²'))
    
    # 6. Price Distribution by City (Box Plot)
    ax7 = fig.add_subplot(gs[2, :])
    top_10_cities = df['city'].value_counts().head(10).index
    city_data = df[df['city'].isin(top_10_cities)]
    sns.boxplot(x='city', y='price', data=city_data, ax=ax7)
    ax7.set_title('Price Distribution in Top 10 Cities')
    ax7.set_xticklabels(ax7.get_xticklabels(), rotation=45)
    ax7.set_ylabel('Price')
    format_y_axis(ax7)
    
    # 7. Area Distribution by City
    ax8 = fig.add_subplot(gs[3, 0])
    sns.boxplot(x='city', y='area', data=city_data, ax=ax8)
    ax8.set_title('Area Distribution in Top 10 Cities')
    ax8.set_xticklabels(ax8.get_xticklabels(), rotation=45)
    ax8.set_ylabel('Area')
    ax8.set_ylim(0, 200)  # Limit y-axis to 200 m²
    format_y_axis(ax8, is_price=False)
    
    # 8. Price per m² by City
    ax9 = fig.add_subplot(gs[3, 1])
    city_price_m2 = city_data.groupby('city')['price_per_m2'].mean().sort_values(ascending=False)
    city_price_m2.plot(kind='bar', ax=ax9)
    ax9.set_title('Average Price per m² by City')
    ax9.set_xticklabels(ax9.get_xticklabels(), rotation=45)
    ax9.set_ylabel('Price per m²')
    ax9.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f} PLN/m²'))
    
    # 9. Property Count by Area Range
    ax10 = fig.add_subplot(gs[3, 2])
    area_counts = df['area_range'].value_counts()
    area_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax10)
    ax10.set_title('Property Distribution by Area Range')
    
    plt.tight_layout()
    plt.savefig('property_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create additional visualization
    # Price per m² by City and Area Range (Bar Chart)
    plt.figure(figsize=(15, 8))
    pivot_table = df.pivot_table(values='price_per_m2', index='city', columns='area_range', aggfunc='mean')
    pivot_table = pivot_table.sort_values(by='100+ m²', ascending=False).head(10)  # Show top 10 cities
    pivot_table.plot(kind='bar', width=0.8)
    plt.title('Average Price per m² by City and Area Range')
    plt.xlabel('City')
    plt.ylabel('Price per m²')
    plt.xticks(rotation=45)
    plt.legend(title='Area Range')
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f} PLN/m²'))
    plt.tight_layout()
    plt.savefig('price_by_city_area.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Get data
    df = get_data()
    if df is None:
        print("Failed to fetch data from database")
        return
    
    # Analyze by area ranges
    print("\nAnalysis by Area Ranges:")
    area_stats = analyze_by_area_ranges(df)
    print(area_stats)
    
    # Analyze by location
    print("\nAnalysis by Location:")
    location_stats = analyze_by_location(df)
    print(location_stats)
    
    # Create visualizations
    create_visualizations(df)
    print("\nVisualizations have been saved as 'property_analysis.png'")

if __name__ == "__main__":
    main()

