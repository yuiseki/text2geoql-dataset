[out:json][timeout:30];
area["name:en"="Casablanca"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;