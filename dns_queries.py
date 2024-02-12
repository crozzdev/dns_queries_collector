import sys
import os
import re
import requests
from datetime import datetime
from collections import Counter
import argparse
from typing import Generator
from dotenv import load_dotenv

# Load environment variables

_ = load_dotenv()

LUMU_ENDPOINT = os.getenv("LUMU_ENDPOINT")
LUMU_API_KEY = os.getenv("LUMU_API_KEY")
LUMU_COLLECTOR_ID = os.getenv("LUMU_COLLECTOR_ID")
LUMU_API_QUERY = f"{LUMU_ENDPOINT}/{LUMU_COLLECTOR_ID}/dns/queries?key={LUMU_API_KEY}"
LUMU_HEADERS = {"Content-Type": "application/json"}
TOP_HOSTS = int(os.getenv("TOP_HOSTS"))


# Set up argument parsing for the command line
parser = argparse.ArgumentParser(
    description="Parse BIND log and send data to Lumu Custom Collector API."
)
parser.add_argument("file_path", help="Path to the BIND log file")
args = parser.parse_args()


def parse_line(line: str) -> dict | None:
    """
    Parses a line of DNS query log and extracts the timestamp, client IP, and host.

    Args:
        line (str): The line of DNS query log to parse.

    Returns:
        dict | None: A dictionary containing the parsed information if the line matches the expected format,
                     or None if the line does not match the expected format.
    """
    # Regular expression to match the necessary parts: timestamp, client IP, and host
    pattern = r"(\d+-[a-zA-Z]+-\d+ \d+:\d+:\d+\.\d+) queries: info: client @0x[0-9a-f]+ ([\d\.]+)#\d+ \(([^)]+)\)"
    match = re.search(pattern, line)
    if match:
        timestamp_str = match.group(1)
        client_ip = match.group(2)
        host = match.group(3)
        # Convert timestamp to the required format
        timestamp = datetime.strptime(timestamp_str, "%d-%b-%Y %H:%M:%S.%f")
        timestamp_iso = timestamp.isoformat() + "Z"
        return {"timestamp": timestamp_iso, "client_ip": client_ip, "name": host}
    else:
        return None


def parse_bind_log(file_path: str) -> Generator[dict, None, None]:
    """
    Parses a BIND log file and yields a dictionary for each parsed line.

    Args:
        file_path (str): The path to the BIND log file.

    Yields:
        dict: A dictionary containing the parsed data for each line which is in turn generated
        by the parse_line() function.

    """
    with open(file_path, "r") as file:
        for line in file:
            parsed_data = parse_line(line)
            if parsed_data:
                yield parsed_data


def send_to_lumu(data_chunk: list[dict]) -> requests.Response:
    """
    Sends a data chunk to Lumu API for processing. The body examples is as follow:

    [ { "timestamp": "2021-01-06T14:37:02.228Z", "name": "www.example.com", "client_ip": "192.168.0.103", "client_name": "MACHINE-0987", "type": "A" } ]

    type and client_name are optional and not used in this script.

    Args:
        data_chunk (list[dict]): A list of dictionaries representing the data chunk to be sent.

    Returns:
        requests.Response: The response object returned by the Lumu API.

    Raises:
        None

    """
    formatted_data = [
        data for data in data_chunk if data
    ]  # Ensure all entries are valid
    response = requests.post(LUMU_API_QUERY, json=formatted_data, headers=LUMU_HEADERS)
    if response.status_code != 200:
        print("Error sending data to Lumu")
    return response


def print_statistics(
    client_ips: Counter, queried_hosts: Counter, top_hosts: int
) -> None:
    """
    Prints statistics of DNS queries.

    Args:
        client_ips (Counter): Counter object containing client IP addresses and their counts.
        queried_hosts (Counter): Counter object containing queried hosts and their counts.
        top_hosts (int): The number of top hosts to display.

    Returns:
        None

    Effect:
        Prints the statistics to the console.
    """
    total_records = sum(client_ips.values())
    print(f"Total records {total_records}\n")

    # Client IPs Rank
    print("{:<15} {:<15} {:<10}".format("Client", "IPs", "Rank"))
    print("-" * 40)
    for ip, count in client_ips.most_common(top_hosts):
        percentage = (count / total_records) * 100
        print("{:<15} {:<15} {:.2f}%".format(ip, count, percentage))
    print("-" * 40)

    # Host Rank
    print("\n{:<60} {:<10}".format("Host", "Rank"))
    print("-" * 70)
    for host, count in queried_hosts.most_common(TOP_HOSTS):
        percentage = (count / total_records) * 100
        print("{:<60} {:.2f}%".format(host, percentage))
    print("-" * 70)


def main():
    """
    Main function that collects DNS queries from a log file, processes them, and sends them to Lumu in chunks.
    """

    client_ips = Counter()
    queried_hosts = Counter()
    data_chunk = []

    # we check that the log file is present
    if not os.path.isfile(args.file_path):
        print(f"File {args.file_path} not found.")
        sys.exit(1)

    for record in parse_bind_log(args.file_path):
        data_chunk.append(record)
        client_ips.update([record["client_ip"]])
        queried_hosts.update([record["name"]])

        if len(data_chunk) == 500:
            send_to_lumu(data_chunk)
            data_chunk.clear()

    # Send any remaining records
    if data_chunk:
        send_to_lumu(data_chunk)

    print_statistics(client_ips, queried_hosts, TOP_HOSTS)


if __name__ == "__main__":
    main()
