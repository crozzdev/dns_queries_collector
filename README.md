# BIND Log Parser for Lumu Custom Collector

This Python script automates the parsing of BIND DNS server logs, extracting relevant DNS query information (timestamp, client IP, and queried host), and sending this data to the Lumu Custom Collector API in structured batches (500). Additionally, it provides statistics on the most frequent client IPs and queried hosts (5 hosts by default), offering insights into DNS query patterns within your network.

## Features

- Parses BIND server logs to extract DNS query data.
- Batches and sends extracted data to Lumu's Custom Collector API.
- Prints statistics on frequently queried hosts and client IP addresses.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6+ installed on your system.
- Access to BIND DNS server logs or at least the file containing the logs. The logs file should be located in the same directory as the script.
- A Lumu account with access to Custom Collector API credentials.

## Cloning the Repository

To get started with the BIND Log Parser, clone the repository to your local machine using the following command:

```sh
git clone https://github.com/crozzdev/dns_queries_collector.git
cd dns_queries_collector

```

## Installation

After cloning the repository, navigate into the project directory and install the required dependencies:

```sh
pip install -r requirements.txt

```

This command installs the requests and python-dotenv libraries, which are essential for the script to function.

## Configuration

Create a .env file in the root directory of the project to store sensitive configuration details:

```sh
LUMU_ENDPOINT=https://api.lumu.io/collectors/dns-query
LUMU_API_KEY=your_lumu_api_key_here
LUMU_COLLECTOR_ID=your_collector_id_here
TOP_HOSTS = 5
```

Please take a look at the .env.example file for reference. Replace your_lumu_api_key_here and your_collector_id_here with your actual Lumu API key and collector ID. The TOP_HOSTS variable specifies the number of most frequent queried hosts to display in the statistics, by default it is set to 5.

## Usage

To use the script, run it from the command line, passing the path to your BIND log file as an argument:

```sh
python dns_collector.py /path/to/your/bind/log/file
```

This command will parse the specified BIND log file, send the DNS query data to Lumu in batches, and print out statistics regarding the queries processed.

## Example

```sh
python dns_collector.py logs/bind-dns.log
```

After successful execution, the script will output statistics to the console and send the parsed query data to your specified Lumu Custom Collector.

![Example](https://onedrive.live.com/embed?resid=EB59B09937B52B5D%2176401&authkey=%21AG0EoyPox1mR-8I&width=660)

## Testing

To run the tests, navigate to the project directory and run the following command:

```sh
pytest tests/

```

## Ranking algorithm computational explanation

The computational complexity of the ranking algorithm which is defined in the print_statistics function is primarily determined by the most_common method of the Counter objects client_ips and queried_hosts.

The most_common method in Python's collections.Counter class has a time complexity of O(n log n), where n is the number of unique elements in the Counter object. This is because most_common sorts the elements by their counts.

In the print_statistics function, most_common is called twice, once for client_ips and once for queried_hosts. However, since these calls are not nested and operate on different data, the overall time complexity remains O(n log n).

The rest of the operations in the function (like summing the values in the Counter, calculating percentages, and printing the results) have a time complexity of O(n), which is dominated by the O(n log n) complexity of the most_common method.

So, the overall time complexity of is O(n log n).

## Contact

Crozzdev - <juan.david.tvelez@hotmail> or <crozzdev95@outlook.com>
