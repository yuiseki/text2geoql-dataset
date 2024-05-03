[out:json][timeout:30000];
area["name:en"="Okinawa Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
