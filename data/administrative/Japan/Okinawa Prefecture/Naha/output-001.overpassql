[out:json][timeout:30000];
area["name:en"="Okinawa Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Naha"](area.searchArea);
);
out geom;
