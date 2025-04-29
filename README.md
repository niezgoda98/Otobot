# Property Price Analysis Tool

This tool analyzes property prices based on various factors including area, location, and price per square meter. It generates visualizations to help understand the real estate market trends.

## Features

- Analyzes property prices by area ranges (0-60 m², 60-80 m², 80-100 m², 100+ m²)
- Provides location-based analysis
- Generates comprehensive visualizations
- Calculates price per square meter metrics

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/property-analysis.git
cd property-analysis
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your database credentials:
```
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Usage

Run the analysis script:
```bash
python analyze_data.py
```

The script will generate two visualization files:
- `property_analysis.png`: Main dashboard with multiple graphs
- `price_by_city_area.png`: Detailed price analysis by city and area range

## Project Structure

- `analyze_data.py`: Main analysis script
- `requirements.txt`: Python dependencies
- `.env`: Database configuration (not included in repository)
- `.gitignore`: Specifies files to ignore in version control

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 