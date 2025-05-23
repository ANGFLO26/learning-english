<<<<<<< HEAD
# applearning_EG

# Vocabulary Learning Application

A web application for learning vocabulary with interactive features and progress tracking.

## Features

- User registration and authentication
- Multiple learning modes:
  - Vietnamese → English
  - English → Vietnamese
  - Pronunciation → Both
- Interactive testing system
- Progress tracking and history
- Leaderboard system
- Responsive design

## Prerequisites

- Python 3.7+
- MySQL 5.7+
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd vocabulary-app
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a MySQL database:
```sql
CREATE DATABASE vocabulary_app;
```

5. Configure the database connection:
   - Open `app.py`
   - Update the `SQLALCHEMY_DATABASE_URI` with your MySQL credentials:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/vocabulary_app'
   ```

6. Initialize the database:
```bash
python app.py
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Register a new account or login with existing credentials.

4. Start learning vocabulary by selecting a topic and choosing a learnin
    ├── leaderboard.html
    └── history.html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
>>>>>>> cad6ae5 (Initial commit)
#   l e a r n i n g - e n g l i s h  
 