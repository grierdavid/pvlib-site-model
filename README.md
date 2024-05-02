# Solar Generation Predictor

This Python project utilizes `pvlib` and a custom forecasting library to predict solar power generation based on various environmental factors at a specific location. The project aims to provide accurate solar generation forecasts to help optimize and plan solar energy usage.

## Features

- **Solar Power Prediction**: Estimate the amount of solar power generation based on historical and forecasted weather data.
- **Custom Environmental Forecasting**: Utilize a custom-built forecasting library to predict key environmental variables such as temperature, irradiance, and humidity.
- **Location Specific**: Tailor predictions to the specific geographic and climatic conditions of any location.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.7 or higher

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/grierdavid/pvlib-site-model.git 
cd pvlib-site-mode
docker build -t site-model .
docker run -it --rm -p 1000:8888 -v $(pwd):/home/jovyan/work site-model
copy from startup:  http://127.0.0.1:8888/lab?token=<session token> 
into browser
navigate to work/experiments.ipynb
