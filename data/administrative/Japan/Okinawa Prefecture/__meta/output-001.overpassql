// Important note: SubArea: Japan/Okinawa Prefecture
[out:json][timeout:30];
area["name:en"="Okinawa Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
