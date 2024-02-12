import pytest
import requests_mock
import os
from collections import Counter
from ..dns_queries import parse_line, parse_bind_log, send_to_lumu, print_statistics
from dotenv import load_dotenv

_ = load_dotenv()


def test_parse_line_success():
    line = "23-Jul-2021 14:20:30.123 queries: info: client @0x1234abcd 192.168.1.1#12345 (www.example.com)"
    expected_result = {
        "timestamp": "2021-07-23T14:20:30.123000Z",
        "client_ip": "192.168.1.1",
        "name": "www.example.com",
    }
    assert parse_line(line) == expected_result


def test_parse_line_failure():
    line = "This is not a valid DNS query log line."
    assert parse_line(line) == None


def test_parse_bind_log(tmp_path):
    # Create a temporary BIND log file
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "bind.log"
    p.write_text(
        "23-Jul-2021 14:20:30.123 queries: info: client @0x1234abcd 192.168.1.1#12345 (www.example.com)\n"
    )

    # Call the function with the path to the temporary file
    result = list(parse_bind_log(str(p)))

    # Check the result
    assert len(result) == 1
    assert result[0] == {
        "timestamp": "2021-07-23T14:20:30.123000Z",
        "client_ip": "192.168.1.1",
        "name": "www.example.com",
    }


def test_send_to_lumu():
    LUMU_ENDPOINT = os.getenv("LUMU_ENDPOINT")
    LUMU_API_KEY = os.getenv("LUMU_API_KEY")
    LUMU_COLLECTOR_ID = os.getenv("LUMU_COLLECTOR_ID")
    LUMU_API_QUERY = (
        f"{LUMU_ENDPOINT}/{LUMU_COLLECTOR_ID}/dns/queries?key={LUMU_API_KEY}"
    )
    data_chunk = [
        {
            "timestamp": "2021-01-06T14:37:02.228Z",
            "name": "www.example.com",
            "client_ip": "192.168.0.103",
        }
    ]
    with requests_mock.Mocker() as m:
        m.post(LUMU_API_QUERY, status_code=200)
        response = send_to_lumu(data_chunk)

    assert response.status_code == 200


def test_print_statistics(capfd):
    client_ips = Counter({"192.168.1.1": 5, "192.168.1.2": 3})
    queried_hosts = Counter({"www.example.com": 4, "www.test.com": 2})

    print_statistics(client_ips, queried_hosts, 2)

    captured = capfd.readouterr().out

    assert "Total records 8" in captured
    assert "192.168.1.1" in captured
    assert "5" in captured
    assert "62.50%" in captured
    assert "192.168.1.2" in captured
    assert "3" in captured
    assert "37.50%" in captured
    assert "www.example.com" in captured
    assert "50.00%" in captured
    assert "www.test.com" in captured
    assert "25.00%" in captured
