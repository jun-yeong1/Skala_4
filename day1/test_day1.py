import pytest
from pydantic import ValidationError

from day1 import (
    validate_weather,
    validate_country,
    validate_ip,
)

## pytest.fixture 공통 데이터, 설정 공유
# 서울 3일 시간대별 기온, 강수확률 테스트
@pytest.fixture
def weather_data():
    return {
        "latitude": 37.5,
        "longitude": 126.9,
        "hourly": {
            "temperature_2m": [20.1, 21.2],
            "precipitation_probability": [10, 20]
        }
    }

# 한국 국가 정보 테스트
@pytest.fixture
def country_data():
    return {
        "name": {
            "common": "South Korea"
        },
        "population": 51000000
    }
    
# ip 기반 지역 정보 테스트
@pytest.fixture
def ip_data():
    return {
        "country": "United States",
        "city": "Mountain View",
        "query": "8.8.8.8"
    }
    
def test_validate_weather(weather_data):
    result = validate_weather(weather_data)

    assert result["latitude"] == 37.5
    assert len(result["temperature_2m"]) == 2


def test_validate_country(country_data):
    result = validate_country(country_data)

    assert result["common"] == "South Korea"
    assert result["population"] == 51000000


def test_validate_ip(ip_data):
    result = validate_ip(ip_data)

    assert result["city"] == "Mountain View"
    
def test_invalid_weather():

    bad = {
        "latitude": "서울",
        "longitude": 126.9,
        "hourly": {
            "temperature_2m": [20],
            "precipitation_probability": [10]
        }
    }

    with pytest.raises(ValidationError):
        validate_weather(bad)

# parametrize : 여러 입력 케이스 한번에
@pytest.mark.parametrize(
    "population",
    [1000, 1000000, 51000000]
)
def test_country_population(population):

    data = {
        "name": {
            "common": "South Korea"
        },
        "population": population
    }

    result = validate_country(data)

    assert result["population"] == population