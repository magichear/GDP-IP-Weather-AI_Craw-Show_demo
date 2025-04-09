BASEURL = (
    "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?"
)

startYear = 1990

endYear = 2022

SUFFIX = "ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1"


"""
https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?c=122,124,960,423,939,172,132,134,174,178,136,941,946,137,181,138,182,936,961,184,&s=NGDPD,&sy=1990&ey=2022&ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1

https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?c=156,132,134,136,158,112,111,&s=NGDPD,&sy=1990&ey=2022&ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1

https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?a=1&c=001,110,163,119,123,998,510,200,505,903,205,400,603,&s=NGDPD,&sy=1990&ey=2022&ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1

https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?c=513,514,516,522,924,819,534,536,826,544,548,556,867,868,948,518,836,558,565,853,566,862,813,524,578,537,866,869,846,582,&s=NGDPD,&sy=1990&ey=2022&ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1
"""


def getData(startYear, endYear, countryCode):
    query = f"{BASEURL}c={countryCode}&s=NGDPD,&sy={startYear}&ey={endYear}{SUFFIX}"
    print(query)


getData(startYear, endYear, "001,110,163,119,123,998,510,200,505,903,205,400,603")
